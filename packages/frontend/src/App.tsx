import { useMemo, useState } from "react";

import { DarkModeToggle } from "./components/DarkModeToggle";
import { MetaForm, defaultMetadataState } from "./components/MetaForm";
import { ReportCard } from "./components/ReportCard";
import { ToastProvider } from "./components/Toast";
import { UploadRunner } from "./components/UploadRunner";
import { UploadZone } from "./components/UploadZone";
import { UploadProvider, useUploadContext } from "./context/UploadContext";
import { t } from "./i18n";
import type { UploadMetadataState } from "./types";

function UploadPage() {
  const [metadata, setMetadata] = useState<UploadMetadataState>(defaultMetadataState);
  const { files } = useUploadContext();

  const completedReports = useMemo(
    () => files.filter((file) => file.report),
    [files]
  );
  const isBusy = useMemo(
    () =>
      files.some((file) => ["uploading", "processing"].includes(file.status)),
    [files]
  );

  return (
    <div className="mx-auto flex min-h-full max-w-6xl flex-col gap-8 px-4 pb-12 pt-10">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">
            {t("app_title")}
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            CatchProbe portal\u0131ndan gelen \u015f\u00fcpheli e-postalar\u0131 g\u00fcvenle inceleyin.
          </p>
        </div>
        <DarkModeToggle />
      </header>

      <UploadZone disabled={isBusy} />

      <MetaForm value={metadata} onChange={setMetadata} disabled={isBusy} />

      <UploadRunner metadata={metadata} />

      {completedReports.length > 0 && (
        <section className="mt-10 space-y-6">
          {completedReports.map((file) => (
            file.report && <ReportCard key={file.id} report={file.report} />
          ))}
        </section>
      )}
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <UploadProvider>
        <UploadPage />
      </UploadProvider>
    </ToastProvider>
  );
}

