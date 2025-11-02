import { ChangeEvent, DragEvent, useCallback, useState } from "react";

import { t } from "../i18n";
import { useToast } from "./Toast";
import { useUploadContext } from "../context/UploadContext";

const MAX_SIZE = 20 * 1024 * 1024;
const ACCEPTED_EXTENSIONS = [".eml", ".msg"];

interface UploadZoneProps {
  disabled?: boolean;
}

export function UploadZone({ disabled }: UploadZoneProps) {
  const { addFiles } = useUploadContext();
  const { pushToast } = useToast();
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = useCallback(
    (fileList: FileList | null) => {
      if (!fileList) return;
      const files = Array.from(fileList);
      const valid: File[] = [];
      files.forEach((file) => {
        const lower = file.name.toLowerCase();
        const allowed = ACCEPTED_EXTENSIONS.some((ext) => lower.endsWith(ext));
        if (!allowed) {
          pushToast(`${file.name}: ${t("invalid_type")}`, "error");
          return;
        }
        if (file.size > MAX_SIZE) {
          pushToast(`${file.name}: ${t("file_too_large")}`, "error");
          return;
        }
        valid.push(file);
      });
      if (valid.length) {
        addFiles(valid);
      }
    },
    [addFiles, pushToast]
  );

  const onDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      if (disabled) return;
      setIsDragging(false);
      handleFiles(event.dataTransfer.files);
    },
    [disabled, handleFiles]
  );

  const onDragOver = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (disabled) return;
    setIsDragging(true);
  }, [disabled]);

  const onDragLeave = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
  }, []);

  const onInputChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      if (disabled) return;
      handleFiles(event.target.files);
      event.target.value = "";
    },
    [disabled, handleFiles]
  );

  return (
    <div className="w-full">
      <label
        htmlFor="upload-input"
        className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-12 text-center transition-colors ${
          isDragging
            ? "border-primary bg-primary/10"
            : "border-slate-400/40 dark:border-slate-700"
        } ${disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer"}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        aria-disabled={disabled}
      >
        <p className="text-lg font-semibold">{t("upload_instruction")}</p>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          {t("upload_subtitle")}
        </p>
        <button
          type="button"
          className="mt-6 inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white shadow hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary/70 focus:ring-offset-2 focus:ring-offset-slate-100 dark:focus:ring-offset-slate-900"
          disabled={disabled}
          onClick={() => {
            if (disabled) return;
            (document.getElementById("upload-input") as HTMLInputElement | null)?.click();
          }}
        >
          {t("add_files")}
        </button>
        <input
          id="upload-input"
          type="file"
          accept=".eml,.msg"
          multiple
          className="hidden"
          onChange={onInputChange}
          disabled={disabled}
        />
      </label>
    </div>
  );
}

