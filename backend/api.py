from __future__ import annotations

import importlib
import json
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger("ai-surveillance")

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
UPLOADS = ROOT / "backend" / "uploads"
OUTPUTS = ROOT / "backend" / "outputs"
MAX_UPLOAD_BYTES = 200 * 1024 * 1024
UPLOADS.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

app = FastAPI(title="AI Surveillance API", version="0.1.0")

# ✅ CHANGED: CORS now reads from an Environment Variable on Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "*")], 
    allow_methods=["*"],
    allow_headers=["*"]
)


def _load_pipeline():
    """Load a user-supplied adapter without importing the heavy models at startup."""
    module_name = os.getenv("AI_PIPELINE_MODULE", "backend.pipeline_adapter")
    try:
        module = importlib.import_module(module_name)
        return getattr(module, "run_pipeline")
    except (ImportError, AttributeError):
        return None


def _value(row: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if isinstance(row, dict) and name in row:
            return row[name]
        if hasattr(row, name):
            return getattr(row, name)
    return default


def normalize_event(row: Any) -> dict[str, Any]:
    event = str(_value(row, "event_type", "event", "detail", default="detection"))
    confidence = _value(row, "confidence", "conf")
    if confidence is not None:
        confidence = float(confidence)
    severity = "critical" if event.lower() in {"fire", "smoke", "fight", "violence", "worker_down", "structural_alert"} else "warning"
    return {
        "event_type": event,
        "label": str(_value(row, "label", "detail", default=event)),
        "confidence": confidence,
        "severity": str(_value(row, "severity", default=severity)),
        "frame": _value(row, "frame"),
        "time_s": _value(row, "time_s"),
        "source": _value(row, "source", default="uploaded_media"),
    }


def normalize_result(result: Any, original_name: str, original_path: Path) -> dict[str, Any]:
    if isinstance(result, tuple):
        output_path, event_log = result[0], result[1]
    else:
        output_path = result.get("output_path")
        event_log = result.get("event_log", [])
    rows = event_log.to_dict("records") if hasattr(event_log, "to_dict") else list(event_log or [])
    output = Path(output_path) if output_path else None
    annotated_url = None
    original_url = None
    original_destination = UPLOADS / original_path.name
    original_url = f"/uploads/{original_destination.name}"
    if output and output.exists():
        if output.suffix.lower() in {".mp4", ".mov", ".avi", ".mkv"}:
            output = browser_safe_video(output)
        destination = OUTPUTS / output.name
        if output.resolve() != destination.resolve():
            shutil.copy2(output, destination)
        annotated_url = f"/media/{destination.name}"
    media_type = "video" if (output and output.suffix.lower() in {".mp4", ".mov", ".avi", ".mkv"}) else "image"
    return {"source": original_name, "media_type": media_type, "original_url": original_url, "annotated_url": annotated_url, "detections": [normalize_event(row) for row in rows]}


def browser_safe_video(source: Path) -> Path:
    """Transcode notebook output to an HTML5-compatible H.264 MP4."""
    try:
        from imageio_ffmpeg import get_ffmpeg_exe

        safe_path = source.with_name(f"browser_{source.stem}.mp4")
        command = [
            get_ffmpeg_exe(), "-y", "-i", str(source), "-c:v", "libx264",
            "-preset", "fast", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-c:a", "aac", "-b:a", "128k", str(safe_path),
        ]
        subprocess.run(command, check=True, capture_output=True)
        return safe_path
    except Exception:
        logger.exception("Could not transcode annotated video %s", source)
        return source


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "pipeline_configured": _load_pipeline() is not None}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)) -> dict[str, Any]:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".avi", ".mkv"}:
        raise HTTPException(415, "Unsupported media type")
    run_pipeline = _load_pipeline()
    if run_pipeline is None:
        raise HTTPException(503, "AI pipeline adapter is not configured")
    target = UPLOADS / f"{next(tempfile._get_candidate_names())}{suffix}"
    with target.open("wb") as destination:
        total = 0
        while chunk := await file.read(1024 * 1024):
            total += len(chunk)
            if total > MAX_UPLOAD_BYTES:
                target.unlink(missing_ok=True)
                raise HTTPException(413, "Media file exceeds the 200 MB limit")
            destination.write(chunk)
    try:
        return normalize_result(run_pipeline(str(target)), file.filename or target.name, target)
    except Exception as exc:
        logger.exception("AI pipeline failed for %s", file.filename)
        raise HTTPException(422, "AI analysis failed") from exc


app.mount("/media", StaticFiles(directory=OUTPUTS), name="media")
app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")

# ✅ CHANGED: The line below was deleted because your frontend is on Netlify.
# app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")tml=True), name="frontend")
