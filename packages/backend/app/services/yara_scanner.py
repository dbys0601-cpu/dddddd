from __future__ import annotations

import threading
from pathlib import Path
from typing import Dict, List, Optional

import yara
from loguru import logger


class YaraScanner:
    def __init__(self, rules_dir: Path) -> None:
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._rules: Optional[yara.Rules] = None
        self._cache_key: Optional[float] = None
        self._load_rules()

    def _current_key(self) -> float:
        return max((path.stat().st_mtime for path in self._iter_rule_files()), default=0.0)

    def _iter_rule_files(self):
        yield from self.rules_dir.glob("*.yar*")

    def _load_rules(self) -> None:
        file_map: Dict[str, str] = {}
        for index, path in enumerate(self._iter_rule_files()):
            file_map[f"rule_{index}"] = str(path)
        if not file_map:
            # Generate a default rule to avoid compilation errors
            default_rule = self.rules_dir / "default.yar"
            if not default_rule.exists():
                default_rule.write_text(
                    "rule AlwaysTrue { condition: true }\n",
                    encoding="utf-8",
                )
            file_map["default"] = str(default_rule)

        try:
            self._rules = yara.compile(filepaths=file_map)
            self._cache_key = self._current_key()
            logger.debug("Loaded YARA rules from %s", self.rules_dir)
        except yara.YaraError as exc:  # pragma: no cover - defensive
            logger.error("Failed to compile YARA rules: %s", exc)
            raise

    def _ensure_rules(self) -> None:
        with self._lock:
            if self._rules is None:
                self._load_rules()
                return
            current_key = self._current_key()
            if current_key and current_key != self._cache_key:
                self._load_rules()

    def scan_bytes(self, data: bytes) -> List[str]:
        if not data:
            return []
        self._ensure_rules()
        assert self._rules is not None
        try:
            matches = self._rules.match(data=data)
        except yara.Error as exc:  # pragma: no cover - defensive
            logger.warning("YARA scan failed: %s", exc)
            return []
        return sorted({match.rule for match in matches})

