import json
from email.message import EmailMessage

import pytest


def build_sample_email() -> bytes:
    msg = EmailMessage()
    msg["Subject"] = "Test Invoice"
    msg["From"] = "attacker@example.com"
    msg["To"] = "victim@example.com"
    msg["Authentication-Results"] = "spf=fail dkim=pass dmarc=fail"
    msg.set_content("Merhaba, acil ?deme yapman?z gerekiyor. http://malicious.example")
    msg.add_attachment(
        b"AutoOpen malicious macro",
        maintype="text",
        subtype="plain",
        filename="macro.txt",
    )
    return msg.as_bytes()


def test_ingest_success(client):
    payload = build_sample_email()
    response = client.post(
        "/ingest",
        headers={"X-API-KEY": "local-api-key"},
        files={"file": ("sample.eml", payload, "message/rfc822")},
        data={"metadata": json.dumps({"ticket_id": "TCK-123"})},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "accepted"
    report = body["report"]
    assert report["ticket_id"] == "TCK-123"
    assert report["classification"] in {"suspicious", "malicious", "benign"}
    assert report["attachments"]

    artifact_hashes = report["artifact_hashes"]
    assert artifact_hashes

    # Retrieve report via GET
    get_report = client.get(f"/report/{report['ticket_id']}")
    assert get_report.status_code == 200
    assert get_report.json()["ticket_id"] == report["ticket_id"]

    # Retrieve first artifact
    artifact_response = client.get(f"/artifact/{artifact_hashes[0]}")
    assert artifact_response.status_code == 200
    assert artifact_response.content


def test_missing_api_key(client):
    payload = build_sample_email()
    response = client.post(
        "/ingest",
        files={"file": ("sample.eml", payload, "message/rfc822")},
    )
    assert response.status_code == 401


def test_file_too_large(client):
    oversized = b"A" * (3 * 1024 * 1024)  # 3 MB, above configured 2 MB limit
    response = client.post(
        "/ingest",
        headers={"X-API-KEY": "local-api-key"},
        files={"file": ("large.eml", oversized, "message/rfc822")},
    )
    assert response.status_code == 413


def test_report_not_found(client):
    response = client.get("/report/UNKNOWN")
    assert response.status_code == 404

