import { useMemo, useState } from "react";

import { t } from "../i18n";
import type { AttachmentReport, TriageReport } from "../types";
import { useToast } from "./Toast";

interface ReportCardProps {
  report: TriageReport;
}

const classificationStyles: Record<string, string> = {
  benign: "border-emerald-500/40 bg-emerald-500/10 text-emerald-600",
  suspicious: "border-amber-500/40 bg-amber-500/10 text-amber-600",
  malicious: "border-rose-500/40 bg-rose-500/10 text-rose-600"
};

function formatDate(date: string): string {
  try {
    return new Intl.DateTimeFormat("tr-TR", {
      dateStyle: "medium",
      timeStyle: "short"
    }).format(new Date(date));
  } catch (error) {
    return date;
  }
}

export function ReportCard({ report }: ReportCardProps) {
  const [showRaw, setShowRaw] = useState(false);
  const { pushToast } = useToast();

  const classificationKey = `classification_${report.classification}` as const;
  const classificationClass = classificationStyles[report.classification] ??
    "border-slate-500/40 bg-slate-500/10 text-slate-600";
  const topReasons = useMemo(() => report.reasons.slice(0, 3), [report.reasons]);

  const downloadJson = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: "application/json"
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${report.ticket_id}-report.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const copyJson = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(report, null, 2));
      pushToast(t("toast_copy_success"));
    } catch (error) {
      pushToast(t("toast_copy_error"), "error");
    }
  };

  const renderAttachments = (attachments: AttachmentReport[]) => (
    <div className="mt-4 space-y-2">
      {attachments.map((attachment) => (
        <div
          key={attachment.sha256}
          className="rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700"
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="font-medium text-slate-800 dark:text-slate-100">
              {attachment.filename}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400">
              {attachment.mime_type ?? ""}
            </div>
          </div>
          <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            SHA-256: {attachment.sha256}
          </div>
          {attachment.yara_matches.length > 0 && (
            <div className="mt-2 text-xs text-rose-500">
              YARA: {attachment.yara_matches.join(", ")}
            </div>
          )}
          {attachment.vt_result && (
            <div className="mt-2 text-xs text-slate-500 dark:text-slate-300">
              VirusTotal: {attachment.vt_result.malicious_engines}/
              {attachment.vt_result.total_engines} motor
            </div>
          )}
        </div>
      ))}
    </div>
  );

  const rawHeaders = useMemo(
    () => JSON.stringify(report.raw_headers, null, 2),
    [report.raw_headers]
  );

  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow-md dark:border-slate-800 dark:bg-slate-950/40">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
            {t("report_title")} ? {report.ticket_id}
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {report.subject ?? "(Konu yok)"}
          </p>
        </div>
        <div className={`rounded-full border px-4 py-1 text-sm font-medium ${classificationClass}`}>
          {t(classificationKey)} ? {report.triage_score}
        </div>
      </header>

      <section className="mt-4 grid gap-4 md:grid-cols-2">
        <div className="space-y-2 text-sm text-slate-600 dark:text-slate-300">
          <div>
            <span className="font-medium">G\u00f6nderen:</span> {report.from_address ?? "-"}
          </div>
          <div>
            <span className="font-medium">Al\u0131c\u0131lar:</span> {report.to_addresses.join(", ") || "-"}
          </div>
          <div>
            <span className="font-medium">Al\u0131nma:</span> {formatDate(report.received_at)}
          </div>
          <div>
            <span className="font-medium">Tamamlanma:</span> {formatDate(report.analysis_completed_at)}
          </div>
        </div>

        <div className="space-y-2 text-sm text-slate-600 dark:text-slate-300">
          <div>
            <span className="font-medium">SPF:</span> {report.authentication.spf ?? "-"}
          </div>
          <div>
            <span className="font-medium">DKIM:</span> {report.authentication.dkim ?? "-"}
          </div>
          <div>
            <span className="font-medium">DMARC:</span> {report.authentication.dmarc ?? "-"}
          </div>
        </div>
      </section>

      {topReasons.length > 0 && (
        <section className="mt-4">
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200">Temel Nedenler</h4>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600 dark:text-slate-300">
            {topReasons.map((reason, index) => (
              <li key={`${reason}-${index}`}>{reason}</li>
            ))}
          </ul>
        </section>
      )}

      <section className="mt-4">
        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
          {t("ioc_section")}
        </h4>
        <div className="mt-2 flex flex-wrap gap-2 text-xs">
          {[...report.ioc_matches.urls, ...report.ioc_matches.domains, ...report.ioc_matches.ips, ...report.ioc_matches.hashes].map((ioc) => (
            <span key={ioc} className="rounded-full bg-slate-100 px-3 py-1 text-slate-700 dark:bg-slate-800 dark:text-slate-200">
              {ioc}
            </span>
          ))}
          {report.ioc_matches.urls.length === 0 &&
            report.ioc_matches.domains.length === 0 &&
            report.ioc_matches.ips.length === 0 &&
            report.ioc_matches.hashes.length === 0 && (
              <span className="text-slate-500 dark:text-slate-400">IOC bulunmad\u0131</span>
            )}
        </div>
      </section>

      {report.attachments.length > 0 && (
        <section className="mt-4">
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
            {t("attachments_section")}
          </h4>
          {renderAttachments(report.attachments)}
        </section>
      )}

      <div className="mt-6 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={downloadJson}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
        >
          {t("download_json")}
        </button>
        <button
          type="button"
          onClick={copyJson}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
        >
          {t("copy_json")}
        </button>
        <button
          type="button"
          onClick={() => setShowRaw(true)}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
        >
          {t("view_raw")}
        </button>
      </div>

      {showRaw && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 p-6">
          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white p-6 shadow-xl dark:bg-slate-950">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Ham Ba\u015fl\u0131klar</h4>
              <button
                type="button"
                onClick={() => setShowRaw(false)}
                className="text-sm font-medium text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-slate-100"
              >
                {t("close")}
              </button>
            </div>
            <pre className="mt-4 overflow-x-auto rounded-lg bg-slate-900 p-4 text-xs text-slate-100">
              {rawHeaders}
            </pre>
          </div>
        </div>
      )}
    </article>
  );
}

