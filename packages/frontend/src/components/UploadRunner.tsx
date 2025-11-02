import axios from "axios";
import { useMemo, useRef, useState } from "react";

import { t } from "../i18n";
import { useUploadContext } from "../context/UploadContext";
import type { UploadMetadataState } from "../types";
import { uploadEmail } from "../utils/api";
import { useToast } from "./Toast";
import { FileList } from "./FileList";

type QueueState = "idle" | "uploading" | "processing" | "done";

const queueLabels: Record<QueueState, string> = {
  idle: t("queue_idle"),
  uploading: t("queue_uploading"),
  processing: t("queue_processing"),
  done: t("queue_done")
};

interface UploadRunnerProps {
  metadata: UploadMetadataState;
}

export function UploadRunner({ metadata }: UploadRunnerProps) {
  const { files, updateFile, reset } = useUploadContext();
  const { pushToast } = useToast();
  const controllers = useRef(new Map<string, AbortController>());
  const [queueState, setQueueState] = useState<QueueState>("idle");

  const hasReadyFiles = useMemo(
    () =>
      files.some((file) =>
        ["ready", "error", "cancelled"].includes(file.status)
      ),
    [files]
  );

  const startUpload = async () => {
    if (!files.length) return;
    if (!metadata.apiKey && import.meta.env.VITE_REQUIRE_API_KEY !== "false") {
      pushToast(t("api_key_required"), "error");
      return;
    }

    setQueueState("uploading");

    for (const file of files) {
      if (!controllers.current) break;
      if (!file.sha256 || file.status === "done") continue;
      const controller = new AbortController();
      controllers.current.set(file.id, controller);
      updateFile(file.id, {
        status: "uploading",
        progress: 0,
        error: undefined
      });

      try {
        const report = await uploadEmail({
          endpoint: metadata.endpoint,
          apiKey: metadata.apiKey || undefined,
          file: file.file,
          metadata: {
            ticket_id: metadata.ticketId || undefined,
            severity_hint: metadata.severity || undefined,
            notes: metadata.notes || undefined
          },
          signal: controller.signal,
          onProgress: (progress) => {
            updateFile(file.id, {
              progress,
              status: progress >= 100 ? "processing" : "uploading"
            });
          }
        });

        updateFile(file.id, {
          status: "done",
          progress: 100,
          report
        });
        pushToast(t("toast_upload_success", { name: file.name }));
      } catch (error) {
        if (axios.isCancel(error)) {
          updateFile(file.id, { status: "cancelled", progress: 0 });
        } else {
          const message =
            error instanceof Error ? error.message : "Bilinmeyen hata";
          updateFile(file.id, {
            status: "error",
            error: message,
            progress: 0
          });
          pushToast(t("toast_upload_error", { name: file.name }), "error");
        }
      } finally {
        controllers.current.delete(file.id);
      }
    }

    setQueueState("done");
  };

  const cancelUpload = (id: string) => {
    const controller = controllers.current.get(id);
    controller?.abort();
    controllers.current.delete(id);
  };

  const resetAll = () => {
    controllers.current.forEach((controller) => controller.abort());
    controllers.current.clear();
    reset();
    setQueueState("idle");
  };

  return (
    <section className="mt-6 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="text-sm text-slate-600 dark:text-slate-300">
          {t("status_label")}: {queueLabels[queueState]}
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white shadow enabled:hover:bg-primary-dark disabled:cursor-not-allowed disabled:opacity-60"
            onClick={startUpload}
            disabled={!hasReadyFiles || queueState === "uploading"}
          >
            {t("upload")}
          </button>
          <button
            type="button"
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            onClick={resetAll}
          >
            {t("reset")}
          </button>
        </div>
      </div>

      <p className="text-xs text-slate-500 dark:text-slate-400">
        {metadata.endpoint === "direct"
          ? t("endpoint_hint_direct")
          : t("endpoint_hint_catchprobe")}
      </p>

      <FileList files={files} onCancel={cancelUpload} />
    </section>
  );
}

