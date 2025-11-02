type TranslationKey = keyof typeof tr;

const tr = {
  app_title: "CatchProbe E-posta Y\u00fckleme",
  upload_instruction: "Dosyalar\u0131n\u0131z\u0131 s\u00fcr\u00fckleyip b\u0131rak\u0131n veya se\u00e7in",
  upload_subtitle: ".eml ve .msg uzant\u0131l\u0131 dosyalar (maksimum 20MB)",
  add_files: "Dosya se\u00e7",
  files_header: "Se\u00e7ilen Dosyalar",
  remove: "Kald\u0131r",
  cancel: "\u0130ptal",
  upload: "Y\u00fcklemeyi Ba\u015flat",
  uploading: "Y\u00fckleniyor",
  processing: "\u0130\u015fleniyor",
  done: "Tamamland\u0131",
  reset: "Yeni parti y\u00fckle",
  api_key_label: "API anahtar\u0131",
  ticket_id_label: "Ticket ID",
  severity_label: "\u00d6ncelik ipucu",
  severity_low: "D\u00fc\u015f\u00fck",
  severity_medium: "Orta",
  severity_high: "Y\u00fcksek",
  severity_critical: "Kritik",
  notes_label: "Notlar",
  endpoint_label: "Hedef u\u00e7 nokta",
  endpoint_direct: "Do\u011frudan ingest ( /ingest )",
  endpoint_catchprobe: "CatchProbe webhook ( /catchprobe/ingest )",
  endpoint_hint_direct: "\u0130stekler do\u011frudan triage servisine g\u00f6nderilir.",
  endpoint_hint_catchprobe: "\u0130stekler CatchProbe webhook u\u00e7 noktas\u0131na g\u00f6nderilir.",
  hash_label: "SHA-256",
  size_label: "Boyut",
  type_label: "T\u00fcr",
  status_label: "Durum",
  progress_label: "\u0130lerleme",
  error_prefix: "Hata",
  toast_upload_success: "{name} ba\u015far\u0131yla y\u00fcklendi",
  toast_upload_error: "{name} y\u00fcklenemedi",
  toast_copy_success: "Panoya kopyaland\u0131",
  toast_copy_error: "Kopyalama ba\u015far\u0131s\u0131z",
  classification_benign: "Zarars\u0131z",
  classification_suspicious: "\u015euheli",
  classification_malicious: "K\u00f6t\u00fc ama\u00e7l\u0131",
  report_title: "Rapor \u00d6nizlemesi",
  ioc_section: "IOC e\u015fle\u015fmeleri",
  attachments_section: "Ek \u00f6zetleri",
  download_json: "JSON indir",
  copy_json: "JSON kopyala",
  view_raw: "Ham veriyi g\u00f6r\u00fcnt\u00fcle",
  close: "Kapat",
  totalling: "Toplam {count} dosya",
  queue_idle: "Haz\u0131r",
  queue_uploading: "Y\u00fckleniyor",
  queue_processing: "\u0130\u015fleniyor",
  queue_done: "Tamamland\u0131",
  invalid_type: "Yaln\u0131zca .eml veya .msg kabul edilir",
  file_too_large: "Dosya 20MB \u00fcst\u00fcnde",
  hashing: "Hash hesaplan\u0131yor",
  ready: "Haz\u0131r",
  dark_mode: "Koyu mod",
  light_mode: "A\u00e7\u0131k mod",
  api_key_required: "API anahtar\u0131 gerekli"
} as const;

export function t(key: TranslationKey, params?: Record<string, string | number>): string {
  let template = tr[key] ?? key;
  if (params) {
    Object.entries(params).forEach(([placeholder, value]) => {
      template = template.replace(`{${placeholder}}`, String(value));
    });
  }
  return template;
}

export type { TranslationKey };

