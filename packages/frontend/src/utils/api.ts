import axios from "axios";

import type { EndpointOption, MetadataPayload, TriageReport } from "../types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
export const DEFAULT_ENDPOINT = (import.meta.env.VITE_DEFAULT_ENDPOINT as EndpointOption) ?? "direct";
export const REQUIRE_API_KEY = (import.meta.env.VITE_REQUIRE_API_KEY ?? "true") !== "false";

const endpointMap: Record<EndpointOption, string> = {
  direct: "/ingest",
  catchprobe: "/catchprobe/ingest"
};

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000
});

interface UploadEmailParams {
  endpoint: EndpointOption;
  apiKey?: string;
  file: File;
  metadata: MetadataPayload;
  signal?: AbortSignal;
  onProgress?: (progress: number) => void;
}

export async function uploadEmail({
  endpoint,
  apiKey,
  file,
  metadata,
  signal,
  onProgress
}: UploadEmailParams): Promise<TriageReport> {
  const url = endpointMap[endpoint];
  const formData = new FormData();
  formData.append("file", file);
  formData.append("metadata", JSON.stringify(metadata));

  const headers: Record<string, string> = {};
  if (endpoint === "direct") {
    if (apiKey) headers["X-API-KEY"] = apiKey;
  } else {
    if (apiKey) headers["X-CATCHPROBE-APIKEY"] = apiKey;
  }

  const response = await client.post(url, formData, {
    headers,
    signal,
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        const percent = Math.round((event.loaded / event.total) * 100);
        onProgress(percent);
      }
    }
  });
  if (!response.data?.report) {
    throw new Error(response.data?.message ?? "Rapor al?namad?");
  }
  return response.data.report as TriageReport;
}

