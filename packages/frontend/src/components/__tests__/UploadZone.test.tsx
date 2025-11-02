import { webcrypto } from "node:crypto";

import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

import { UploadRunner } from "../../components/UploadRunner";
import { UploadZone } from "../../components/UploadZone";
import { ToastProvider } from "../../components/Toast";
import { UploadProvider } from "../../context/UploadContext";
import { defaultMetadataState } from "../../components/MetaForm";

describe("UploadZone", () => {
  beforeAll(() => {
    Object.defineProperty(globalThis, "crypto", {
      value: webcrypto,
      configurable: true
    });
    vi.spyOn(globalThis.crypto, "randomUUID").mockReturnValue("test-id");
  });

  beforeEach(() => {
    vi.spyOn(globalThis.crypto.subtle, "digest").mockResolvedValue(
      new Uint8Array(32).buffer
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  function renderWithProviders() {
    return render(
      <ToastProvider>
        <UploadProvider>
          <UploadZone />
          <UploadRunner metadata={defaultMetadataState()} />
        </UploadProvider>
      </ToastProvider>
    );
  }

  it("adds valid .eml files to the queue", async () => {
    renderWithProviders();
    const input = document.querySelector("input[type='file']") as HTMLInputElement;

    const file = new File(["demo"], "example.eml", { type: "message/rfc822" });
    fireEvent.change(input, { target: { files: [file] } });

    expect(await screen.findByText("example.eml")).toBeInTheDocument();
  });

  it("shows an error toast for unsupported file types", async () => {
    renderWithProviders();
    const input = document.querySelector("input[type='file']") as HTMLInputElement;

    const file = new File(["demo"], "example.pdf", { type: "application/pdf" });
    fireEvent.change(input, { target: { files: [file] } });

    expect(
      await screen.findByText(/Yaln\u0131zca \\.eml veya \\.msg kabul edilir/i)
    ).toBeInTheDocument();
  });
});

