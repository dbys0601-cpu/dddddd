import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from ..config import Settings, get_settings
from ..dependencies import get_artifact_store, get_triage_service
from ..models.schemas import (
    CatchProbeCallbackPayload,
    CatchProbeCallbackResponse,
    ErrorResponse,
    IngestResponse,
    MetadataPayload,
    TriageReport,
)
from ..services.storage import ArtifactStore
from ..services.triage import TriageService
from ..utils.security import (
    ensure_allowed_extension,
    read_upload_with_limit,
    require_api_key,
    sanitize_filename,
)


router = APIRouter()


def _deserialize_metadata(metadata: Optional[str]) -> MetadataPayload:
    if not metadata:
        return MetadataPayload()
    try:
        payload = json.loads(metadata)
        return MetadataPayload.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ge?ersiz metadata JSON: {exc}",
        ) from exc


@router.post(
    "/ingest",
    response_model=IngestResponse,
    responses={
        401: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
    },
)
async def ingest_email(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(default=None),
    api_key: Optional[str] = Header(default=None, alias="X-API-KEY"),
    triage_service: TriageService = Depends(get_triage_service),
    settings: Settings = Depends(get_settings),
) -> IngestResponse:
    require_api_key(api_key, settings.api_keys)
    sanitized = sanitize_filename(file.filename)
    ensure_allowed_extension(sanitized)
    file_bytes = await read_upload_with_limit(file, settings.max_file_size_bytes)
    metadata_payload = _deserialize_metadata(metadata)
    report = await triage_service.analyze(file_bytes, sanitized, metadata_payload)
    return IngestResponse(status="accepted", report=report)


@router.post(
    "/catchprobe/ingest",
    response_model=IngestResponse,
    responses={
        401: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
    },
)
async def catchprobe_ingest(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(default=None),
    api_key: Optional[str] = Header(default=None, alias="X-CATCHPROBE-APIKEY"),
    triage_service: TriageService = Depends(get_triage_service),
    settings: Settings = Depends(get_settings),
) -> IngestResponse:
    require_api_key(api_key, settings.catchprobe_api_keys)
    sanitized = sanitize_filename(file.filename)
    ensure_allowed_extension(sanitized)
    file_bytes = await read_upload_with_limit(file, settings.max_file_size_bytes)
    metadata_payload = _deserialize_metadata(metadata)
    report = await triage_service.analyze(file_bytes, sanitized, metadata_payload)
    return IngestResponse(status="accepted", report=report)


@router.post(
    "/catchprobe/callback",
    response_model=CatchProbeCallbackResponse,
)
async def catchprobe_callback(
    payload: CatchProbeCallbackPayload,
) -> CatchProbeCallbackResponse:
    # In a real deployment we would pull the file from S3 here. For now we simply acknowledge.
    message = (
        f"S3 olay? al?nd?: bucket={payload.bucket}, key={payload.key}, size={payload.size}"
    )
    return CatchProbeCallbackResponse(status="processed", message=message)


@router.get(
    "/report/{ticket_id}",
    response_model=TriageReport,
    responses={404: {"model": ErrorResponse}},
)
async def get_report(
    ticket_id: str,
    store: ArtifactStore = Depends(get_artifact_store),
) -> TriageReport:
    report = await store.get_report(ticket_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rapor bulunamad?")
    return report


@router.get(
    "/artifact/{artifact_hash}",
    responses={404: {"model": ErrorResponse}},
)
async def get_artifact(
    artifact_hash: str,
    store: ArtifactStore = Depends(get_artifact_store),
):
    artifact = await store.get_artifact(artifact_hash)
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact bulunamad?")
    return FileResponse(
        path=artifact.path,
        filename=artifact.filename,
        media_type=artifact.content_type,
    )

