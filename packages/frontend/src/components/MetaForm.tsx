import { ChangeEvent } from "react";

import { t } from "../i18n";
import type { EndpointOption, UploadMetadataState } from "../types";
import { DEFAULT_ENDPOINT, REQUIRE_API_KEY } from "../utils/api";

interface MetaFormProps {
  value: UploadMetadataState;
  onChange: (next: UploadMetadataState) => void;
  disabled?: boolean;
}

const severityOptions: Array<{ value: UploadMetadataState["severity"]; label: string }> = [
  { value: "", label: "-" },
  { value: "low", label: t("severity_low") },
  { value: "medium", label: t("severity_medium") },
  { value: "high", label: t("severity_high") },
  { value: "critical", label: t("severity_critical") }
];

const endpointOptions: Array<{ value: EndpointOption; label: string; description: string }> = [
  { value: "direct", label: t("endpoint_direct"), description: "POST /ingest" },
  {
    value: "catchprobe",
    label: t("endpoint_catchprobe"),
    description: "POST /catchprobe/ingest"
  }
];

export function MetaForm({ value, onChange, disabled }: MetaFormProps) {
  const update = (patch: Partial<UploadMetadataState>) => {
    onChange({ ...value, ...patch });
  };

  return (
    <section className="mt-8 grid gap-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950/40">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-slate-700 dark:text-slate-200">{t("ticket_id_label")}</span>
          <input
            type="text"
            value={value.ticketId}
            onChange={(event) => update({ ticketId: event.target.value })}
            placeholder="CPT-123"
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            disabled={disabled}
          />
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-slate-700 dark:text-slate-200">{t("api_key_label")}</span>
          <input
            type="password"
            value={value.apiKey}
            onChange={(event) => update({ apiKey: event.target.value })}
            placeholder={REQUIRE_API_KEY ? t("api_key_required") : "opsiyonel"}
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            disabled={disabled}
            required={REQUIRE_API_KEY}
            aria-required={REQUIRE_API_KEY}
          />
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-slate-700 dark:text-slate-200">{t("severity_label")}</span>
          <select
            value={value.severity}
            onChange={(event: ChangeEvent<HTMLSelectElement>) =>
              update({ severity: event.target.value as UploadMetadataState["severity"] })
            }
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            disabled={disabled}
          >
            {severityOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-slate-700 dark:text-slate-200">{t("notes_label")}</span>
          <input
            type="text"
            value={value.notes}
            onChange={(event) => update({ notes: event.target.value })}
            placeholder="K\u0131sa bir not ekleyin"
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            disabled={disabled}
          />
        </label>
      </div>

      <fieldset className="flex flex-col gap-4">
        <legend className="text-sm font-medium text-slate-700 dark:text-slate-200">
          {t("endpoint_label")}
        </legend>
        <div className="grid gap-3 md:grid-cols-2">
          {endpointOptions.map((option) => (
            <label
              key={option.value}
              className={`flex cursor-pointer flex-col gap-1 rounded-lg border px-4 py-3 text-sm shadow-sm transition ${
                value.endpoint === option.value
                  ? "border-primary bg-primary/10"
                  : "border-slate-300 hover:border-primary/60 dark:border-slate-700"
              }`}
            >
              <div className="flex items-center gap-2">
                <input
                  type="radio"
                  name="endpoint"
                  value={option.value}
                  checked={value.endpoint === option.value}
                  onChange={() => update({ endpoint: option.value })}
                  disabled={disabled}
                />
                <span className="font-semibold text-slate-800 dark:text-slate-100">
                  {option.label}
                </span>
              </div>
              <span className="text-xs text-slate-500 dark:text-slate-400">
                {option.description}
              </span>
            </label>
          ))}
        </div>
      </fieldset>
    </section>
  );
}

export function defaultMetadataState(): UploadMetadataState {
  return {
    ticketId: "",
    severity: "",
    notes: "",
    apiKey: "",
    endpoint: DEFAULT_ENDPOINT
  };
}

