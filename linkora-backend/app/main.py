from __future__ import annotations

import asyncio
import hmac
import ipaddress
import os
import shutil
import socket
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import urlsplit

import yt_dlp
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

APP_VERSION = "0.1.0"
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "/tmp/linkora-downloads"))
MAX_FILE_BYTES = int(os.getenv("MAX_FILE_BYTES", str(500 * 1024 * 1024)))
MAX_ACTIVE_JOBS = int(os.getenv("MAX_ACTIVE_JOBS", "2"))
JOB_RETENTION_SECONDS = int(os.getenv("JOB_RETENTION_SECONDS", "7200"))
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="LINKORA Download API", version=APP_VERSION, docs_url=None, redoc_url=None, openapi_url=None)
allowed_origins = [v.strip() for v in os.getenv("LINKORA_ALLOWED_ORIGINS", "").split(",") if v.strip()]
if allowed_origins:
    app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=False,
                       allow_methods=["GET", "POST"], allow_headers=["Content-Type", "X-LINKORA-API-KEY"])

jobs: dict[str, dict] = {}
jobs_lock = threading.RLock()
download_semaphore = threading.Semaphore(1)


class DownloadRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)
    format: str = "best"


def require_api_key(x_linkora_api_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("LINKORA_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Download service is not configured")
    if not x_linkora_api_key or not hmac.compare_digest(x_linkora_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def validate_public_url(raw_url: str) -> str:
    try:
        parsed = urlsplit(raw_url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Enter a valid public HTTP or HTTPS media URL")
        host = parsed.hostname.rstrip(".").lower()
        if host == "youtu.be" or host.endswith((".youtube.com", ".youtube-nocookie.com")) or host == "youtube.com":
            raise ValueError("Use YouTube Studio or Google Takeout for your own uploads; LINKORA does not extract YouTube streams")
        if host in {"localhost", "localhost.localdomain"} or host.endswith((".localhost", ".local", ".internal", ".test", ".invalid")):
            raise ValueError("Private and local network addresses are not allowed")
        try:
            literal_ip = ipaddress.ip_address(host)
        except ValueError:
            literal_ip = None
        if literal_ip is not None:
            if not literal_ip.is_global:
                raise ValueError("Private and non-public IP addresses are not allowed")
        else:
            records = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
            addresses = {record[4][0].split("%", 1)[0] for record in records}
            if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
                raise ValueError("The link host does not resolve exclusively to public addresses")
        return raw_url.strip()
    except (ValueError, OSError, socket.gaierror) as exc:
        raise HTTPException(status_code=400, detail=str(exc) or "Invalid media URL") from exc


def prune_old_jobs() -> None:
    cutoff = time.time() - JOB_RETENTION_SECONDS
    with jobs_lock:
        expired = [jid for jid, job in jobs.items()
                   if job.get("finished_at", job.get("created_at", time.time())) < cutoff
                   and job.get("status") in {"finished", "error"}]
        for jid in expired:
            jobs.pop(jid, None)
            shutil.rmtree(DOWNLOAD_DIR / jid, ignore_errors=True)


def public_job(job: dict) -> dict:
    return {
        "id": job["id"], "status": job["status"], "progress": job.get("progress", 0),
        "title": job.get("title"), "filename": job.get("filename"),
        "filesize": job.get("filesize"), "error": job.get("error"),
        "created_at": job["created_at"], "finished_at": job.get("finished_at"),
        "download_url": f"/api/downloads/{job['id']}/file" if job.get("status") == "finished" else None,
    }


def base_ydl_options() -> dict:
    return {
        "noplaylist": True, "no_warnings": True, "quiet": True, "ignoreerrors": False,
        "socket_timeout": 20, "retries": 2, "fragment_retries": 2,
        "max_filesize": MAX_FILE_BYTES, "nocheckcertificate": False, "cachedir": False,
        "cookiefile": None, "outtmpl": str(DOWNLOAD_DIR / "metadata-only" / "%(id)s.%(ext)s"),
    }


def run_download(job_id: str, url: str, output_format: str) -> None:
    job_dir = DOWNLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    def progress_hook(data: dict) -> None:
        with jobs_lock:
            job = jobs.get(job_id)
            if not job:
                return
            if data.get("status") == "downloading":
                total = data.get("total_bytes") or data.get("total_bytes_estimate")
                downloaded = data.get("downloaded_bytes", 0)
                job["status"] = "downloading"
                job["progress"] = round(min(99, downloaded * 100 / total), 1) if total else 0
                job["filesize"] = total
            elif data.get("status") == "finished":
                job["status"] = "processing"
                job["progress"] = 99

    options = base_ydl_options()
    options["outtmpl"] = str(job_dir / "%(title).80s-%(id)s.%(ext)s")
    options["progress_hooks"] = [progress_hook]
    options["format"] = "bestvideo*+bestaudio/best" if output_format == "best" else "bestaudio/best"
    if output_format == "mp3":
        options["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]

    try:
        with download_semaphore:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
                title = info.get("title") if isinstance(info, dict) else None
            candidates = [p for p in job_dir.iterdir() if p.is_file()
                          and not p.name.endswith((".part", ".ytdl", ".temp"))]
            if not candidates:
                raise RuntimeError("The source did not produce a downloadable file")
            file_path = max(candidates, key=lambda item: item.stat().st_size)
            if file_path.stat().st_size > MAX_FILE_BYTES:
                file_path.unlink(missing_ok=True)
                raise RuntimeError("The file exceeds the configured size limit")
            with jobs_lock:
                jobs[job_id].update(status="finished", progress=100, title=title or file_path.stem,
                                    filename=file_path.name, filesize=file_path.stat().st_size,
                                    file_path=str(file_path), finished_at=time.time())
    except Exception as exc:
        with jobs_lock:
            if job_id in jobs:
                jobs[job_id].update(status="error", error=str(exc)[:500], finished_at=time.time())


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "LINKORA Download API", "version": APP_VERSION,
            "api_key_configured": bool(os.getenv("LINKORA_API_KEY"))}


@app.post("/api/info", dependencies=[Depends(require_api_key)])
async def inspect_media(request: DownloadRequest) -> dict:
    if request.format not in {"best", "mp3"}:
        raise HTTPException(status_code=400, detail="Unsupported output format")
    url = validate_public_url(request.url)

    def inspect() -> dict:
        options = base_ydl_options()
        options["skip_download"] = True
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(url, download=False)
        if not isinstance(info, dict):
            raise RuntimeError("No media information was returned")
        formats = []
        for item in (info.get("formats") or [])[-20:]:
            formats.append({"format_id": item.get("format_id"), "ext": item.get("ext"),
                            "resolution": item.get("resolution") or item.get("format_note"),
                            "filesize": item.get("filesize") or item.get("filesize_approx"),
                            "has_audio": item.get("acodec") not in (None, "none"),
                            "has_video": item.get("vcodec") not in (None, "none")})
        return {"title": info.get("title"), "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"), "extractor": info.get("extractor_key") or info.get("extractor"),
                "formats": formats}

    try:
        return await asyncio.to_thread(inspect)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)[:300]) from exc


@app.post("/api/downloads", status_code=202, dependencies=[Depends(require_api_key)])
def create_download(request: DownloadRequest, background_tasks: BackgroundTasks) -> dict:
    if request.format not in {"best", "mp3"}:
        raise HTTPException(status_code=400, detail="Unsupported output format")
    prune_old_jobs()
    url = validate_public_url(request.url)
    with jobs_lock:
        active = sum(1 for job in jobs.values() if job["status"] in {"queued", "downloading", "processing"})
        if active >= MAX_ACTIVE_JOBS:
            raise HTTPException(status_code=429, detail="Download queue is full. Try again shortly.")
        job_id = uuid.uuid4().hex
        job = {"id": job_id, "status": "queued", "progress": 0, "created_at": time.time(), "format": request.format}
        jobs[job_id] = job
    background_tasks.add_task(run_download, job_id, url, request.format)
    return public_job(job)


@app.get("/api/downloads", dependencies=[Depends(require_api_key)])
def list_downloads() -> dict:
    prune_old_jobs()
    with jobs_lock:
        result = sorted(jobs.values(), key=lambda item: item["created_at"], reverse=True)
        return {"items": [public_job(job) for job in result]}


@app.get("/api/downloads/{job_id}", dependencies=[Depends(require_api_key)])
def get_download(job_id: str) -> dict:
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Download not found or expired")
        return public_job(job)


@app.get("/api/downloads/{job_id}/file", dependencies=[Depends(require_api_key)])
def get_download_file(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job or job.get("status") != "finished" or not job.get("file_path"):
            raise HTTPException(status_code=404, detail="Download is not ready or has expired")
        path = Path(job["file_path"])
        if not path.is_file() or path.parent.resolve() != (DOWNLOAD_DIR / job_id).resolve():
            raise HTTPException(status_code=404, detail="Downloaded file is no longer available")
        return FileResponse(path, filename=job.get("filename") or path.name)
