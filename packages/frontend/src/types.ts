export type EndpointOption = "direct" | "catchprobe";

export interface VirusTotalResult {
  malicious_engines: number;
  total_engines: number;
  scan_id: string;
  scanned_at: string;
  permalink?: string | null;
}

export interface AttachmentReport {
  filename: string;
  mime_type?: string | null;
  size: number;
  sha256: string;
  yara_matches: string[];
  vt_result?: VirusTotalResult | null;
}

export interface URLInsight {
  original: string;
  expanded?: string | null;
  domain?: string | null;
  status_code?: number | null;
  risk_hint?: string | null;
}

export interface IOCMatches {
  domains: string[];
  urls: string[];
  ips: string[];
  hashes: string[];
}

export interface MetadataPayload {
  ticket_id?: string;
  severity_hint?: "low" | "medium" | "high" | "critical";
  notes?: string;
}

export interface TriageReport {
  ticket_id: string;
  triage_score: number;
  classification: "benign" | "suspicious" | "malicious";
  reasons: string[];
  summary?: string | null;
  metadata: MetadataPayload;
  subject?: string | null;
  from_address?: string | null;
  to_addresses: string[];
  cc_addresses: string[];
  received_at: string;
  analysis_completed_at: string;
  authentication: {
    spf?: string | null;
    dkim?: string | null;
    dmarc?: string | null;
  };
  url_insights: URLInsight[];
  ioc_matches: IOCMatches;
  attachments: AttachmentReport[];
  artifact_hashes: string[];
  raw_headers: Record<string, string>;
  hashes: Record<string, string>;
}

export type FileStatus =
  | "hashing"
  | "ready"
  | "uploading"
  | "processing"
  | "done"
  | "error"
  | "cancelled";

export interface FileItem {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  sha256?: string;
  status: FileStatus;
  progress: number;
  error?: string;
  report?: TriageReport;
}

export interface UploadMetadataState {
  ticketId: string;
  severity: "" | "low" | "medium" | "high" | "critical";
  notes: string;
  apiKey: string;
  endpoint: EndpointOption;
}

