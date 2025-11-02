import { useCallback } from "react";

import { t } from "../i18n";
import { useUploadContext } from "../context/UploadContext";
import type { FileItem } from "../types";
import { formatBytes } from "../utils/hash";

interface FileListProps {
  files: FileItem[];
  onCancel?: (id: string) => void;
}

const statusLabels: Record<FileItem["status"], string> = {
  hashing: t("hashing"),
  ready: t("ready"),
  uploading: t("uploading"),
  processing: t("processing"),
  done: t("done"),
  error: t("error_prefix"),
  cancelled: t("cancel")
};

export function FileList({ files, onCancel }: FileListProps) {
  const { removeFile } = useUploadContext();

  const handleRemove = useCallback(
    (id: string) => {
      removeFile(id);
    },
    [removeFile]
  );

  if (!files.length) {
    return null;
  }

  return (
    <div className="mt-8 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{t("files_header")}</h2>
        <span className="text-sm text-slate-500 dark:text-slate-400">
          {t("totalling", { count: files.length })}
        </span>
      </div>
      <div className="overflow-hidden rounded-lg border border-slate-200 dark:border-slate-800">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
          <thead className="bg-slate-100 dark:bg-slate-900/40">
            <tr className="text-left text-sm font-medium text-slate-600 dark:text-slate-400">
              <th className="px-4 py-3">{t("files_header")}</th>
              <th className="px-4 py-3">{t("size_label")}</th>
              <th className="px-4 py-3">{t("type_label")}</th>
              <th className="px-4 py-3">{t("hash_label")}</th>
              <th className="px-4 py-3">{t("status_label")}</th>
              <th className="px-4 py-3">{t("progress_label")}</th>
              <th className="px-4 py-3" aria-label={t("remove")}></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 bg-white text-sm dark:divide-slate-800 dark:bg-slate-950/40">
            {files.map((file) => (
              <tr key={file.id} className="align-middle">
                <td className="px-4 py-3 font-medium text-slate-900 dark:text-slate-100">
                  {file.name}
                </td>
                <td className="px-4 py-3 text-slate-600 dark:text-slate-300">
                  {formatBytes(file.size)}
                </td>
                <td className="px-4 py-3 text-slate-600 dark:text-slate-300">
                  {file.type || "-"}
                </td>
                <td className="px-4 py-3 text-xs font-mono text-slate-500 dark:text-slate-400">
                  {file.sha256 ?? "-"}
                </td>
                <td className="px-4 py-3 text-slate-600 dark:text-slate-300">
                  {file.error ? `${t("error_prefix")}: ${file.error}` : statusLabels[file.status]}
                </td>
                <td className="px-4 py-3">
                  <div className="h-2 w-32 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                    <div
                      className={`h-full transition-all ${
                        file.status === "error"
                          ? "bg-rose-500"
                          : file.status === "done"
                          ? "bg-emerald-500"
                          : "bg-primary"
                      }`}
                      style={{ width: `${file.progress}%` }}
                    ></div>
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  {file.status === "uploading" ? (
                    <button
                      type="button"
                      className="text-sm font-medium text-rose-500 hover:text-rose-600"
                      onClick={() => onCancel?.(file.id)}
                    >
                      {t("cancel")}
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="text-sm font-medium text-slate-500 hover:text-slate-700"
                      onClick={() => handleRemove(file.id)}
                    >
                      {t("remove")}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

