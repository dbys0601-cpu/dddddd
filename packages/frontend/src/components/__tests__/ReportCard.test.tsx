import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ReportCard } from "../../components/ReportCard";
import { ToastProvider } from "../../components/Toast";
import type { TriageReport } from "../../types";

const baseReport: TriageReport = {
  ticket_id: "TST-001",
  triage_score: 72,
  classification: "malicious",
  reasons: ["SPF ba\u015far\u0131s\u0131z", "YARA e\u015fle\u015fmesi"],
  summary: "",
  metadata: { ticket_id: "TST-001", severity_hint: "high", notes: "" },
  subject: "Fatura bilgisi",
  from_address: "attacker@example.com",
  to_addresses: ["victim@example.com"],
  cc_addresses: [],
  received_at: new Date().toISOString(),
  analysis_completed_at: new Date().toISOString(),
  authentication: { spf: "fail", dkim: "pass", dmarc: "fail" },
  url_insights: [],
  ioc_matches: { domains: ["bad.example"], urls: [], ips: [], hashes: [] },
  attachments: [
    {
      filename: "invoice.docm",
      mime_type: "application/vnd.ms-word",
      size: 1024,
      sha256: "abc123",
      yara_matches: ["SuspiciousMacro"],
      vt_result: {
        malicious_engines: 5,
        total_engines: 70,
        scan_id: "mock",
        scanned_at: new Date().toISOString(),
        permalink: null
      }
    }
  ],
  artifact_hashes: ["abc123"],
  raw_headers: { From: "attacker@example.com" },
  hashes: { sha256: "filehash" }
};

describe("ReportCard", () => {
  beforeEach(() => {
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      configurable: true
    });
  });

  it("renders classification badge and attachment summary", () => {
    render(
      <ToastProvider>
        <ReportCard report={baseReport} />
      </ToastProvider>
    );

    expect(screen.getByText(/TST-001/)).toBeInTheDocument();
    expect(screen.getByText(/72/)).toBeInTheDocument();
    expect(screen.getByText("invoice.docm")).toBeInTheDocument();
    expect(screen.getByText(/VirusTotal:/i)).toBeInTheDocument();
  });

  it("copies JSON to clipboard", async () => {
    render(
      <ToastProvider>
        <ReportCard report={baseReport} />
      </ToastProvider>
    );

    await userEvent.click(screen.getByRole("button", { name: /JSON kopyala/i }));
    expect(navigator.clipboard.writeText).toHaveBeenCalled();
  });

  it("shows raw headers modal", async () => {
    render(
      <ToastProvider>
        <ReportCard report={baseReport} />
      </ToastProvider>
    );

    await userEvent.click(screen.getByRole("button", { name: /Ham veriyi/i }));
    expect(screen.getByText(/Ham Ba\u015fl\u0131klar/i)).toBeInTheDocument();
  });
});

