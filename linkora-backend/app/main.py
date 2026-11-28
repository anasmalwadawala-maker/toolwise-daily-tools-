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
import zipfile
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
cancel_events: dict[str, threading.Event] = {}
download_semaphore = threading.Semaphore(1)


class DownloadRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)
    format: str = "best"
    quality: str = "best"
    subtitles: bool = False
    automatic_subtitles: bool = False
    subtitle_languages: list[str] = Field(default_factory=lambda: ["en"], max_length=5)
    thumbnail: bool = False
    embed_metadata: bool = True
    playlist_mode: bool = False
    playlist_limit: int = Field(default=10, ge=1, le=25)
    playlist_items: list[int] = Field(default_factory=list, max_length=25)


def validate_options(request: DownloadRequest) -> None:
    if request.format not in {"best", "mp3"}:
        raise HTTPException(status_code=400, detail="Unsupported output format")
    if request.quality not in {"best", "1080", "720", "480", "360"}:
        raise HTTPException(status_code=400, detail="Unsupported video quality")
    if request.format == "mp3" and request.quality != "best":
        raise HTTPException(status_code=400, detail="Video quality does not apply to MP3")
    for language in request.subtitle_languages:
        if not language or len(language) > 20 or not all(c.isalnum() or c in "-_*" for c in language):
            raise HTTPException(status_code=400, detail="Invalid subtitle language")
    if any(item < 1 or item > 10000 for item in request.playlist_items):
        raise HTTPException(status_code=400, detail="Playlist item numbers must be between 1 and 10000")
    if len(set(request.playlist_items)) != len(request.playlist_items):
        raise HTTPException(status_code=400, detail="Duplicate playlist item numbers are not allowed")
    if request.playlist_items and not request.playlist_mode:
        raise HTTPException(status_code=400, detail="Enable playlist mode before selecting playlist items")


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


def run_download(job_id: str, url: str, request: DownloadRequest) -> None:
    job_dir = DOWNLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    if cancel_events.get(job_id, threading.Event()).is_set():
        with jobs_lock:
            if job_id in jobs:
                jobs[job_id].update(status="cancelled", error="Download cancelled", finished_at=time.time())
        return

    def progress_hook(data: dict) -> None:
        if cancel_events.get(job_id, threading.Event()).is_set():
            raise yt_dlp.utils.DownloadError("Download cancelled by user")
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
    options["noplaylist"] = not request.playlist_mode
    if request.playlist_mode:
        options["playlistend"] = request.playlist_limit
        options["max_downloads"] = request.playlist_limit
        if request.playlist_items:
            options["playlist_items"] = ",".join(str(item) for item in request.playlist_items)
    options["outtmpl"] = str(job_dir / "%(title).80s-%(id)s.%(ext)s")
    options["progress_hooks"] = [progress_hook]
    if request.format == "mp3":
        options["format"] = "bestaudio/best"
        options["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
    else:
        height = request.quality
        if height == "best":
            options["format"] = "bestvideo*+bestaudio/best"
        else:
            options["format"] = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
    if request.subtitles:
        options["writesubtitles"] = True
        options["subtitleslangs"] = request.subtitle_languages
        options["subtitlesformat"] = "best"
    if request.automatic_subtitles:
        options["writeautomaticsub"] = True
        options["subtitleslangs"] = request.subtitle_languages
    if request.thumbnail:
        options["writethumbnail"] = True
    if request.embed_metadata:
        options["addmetadata"] = True

    try:
        with download_semaphore:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
                title = info.get("title") if isinstance(info, dict) else None
            if cancel_events.get(job_id, threading.Event()).is_set():
                raise RuntimeError("Download cancelled by user")
            candidates = [p for p in job_dir.iterdir() if p.is_file()
                          and not p.name.endswith((".part", ".ytdl", ".temp"))
                          and not p.suffix.lower() in {".vtt", ".srt", ".ass", ".lrc", ".jpg", ".jpeg", ".png", ".webp"}]
            if not candidates:
                raise RuntimeError("The source did not produce a downloadable file")
            total_bytes = sum(p.stat().st_size for p in candidates)
            if total_bytes > MAX_FILE_BYTES:
                raise RuntimeError("The combined download exceeds the configured size limit")
            if len(candidates) > 1:
                archive = job_dir / "linkora-playlist.zip"
                with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                    for item in candidates:
                        bundle.write(item, arcname=item.name)
                file_path = archive
            else:
                file_path = candidates[0]
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
                cancelled = cancel_events.get(job_id, threading.Event()).is_set() or "cancelled by user" in str(exc).lower()
                jobs[job_id].update(status="cancelled" if cancelled else "error", error=("Download cancelled" if cancelled else str(exc)[:500]), finished_at=time.time())


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "LINKORA Download API", "version": APP_VERSION,
            "api_key_configured": bool(os.getenv("LINKORA_API_KEY"))}


@app.post("/api/info", dependencies=[Depends(require_api_key)])
async def inspect_media(request: DownloadRequest) -> dict:
    validate_options(request)
    url = validate_public_url(request.url)

    def inspect() -> dict:
        options = base_ydl_options()
        options["noplaylist"] = False
        options["playlistend"] = 25
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
                "formats": formats, "subtitles": sorted((info.get("subtitles") or {}).keys()),
                "automatic_subtitles": sorted((info.get("automatic_captions") or {}).keys()),
                "is_playlist": bool(info.get("_type") in {"playlist", "multi_video"}),
                "playlist_count": info.get("playlist_count") or len(info.get("entries") or []),
                "playlist_preview": [{"title": item.get("title"), "id": item.get("id")}
                                     for item in (info.get("entries") or [])[:25] if isinstance(item, dict)]}

    try:
        return await asyncio.to_thread(inspect)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)[:300]) from exc


@app.post("/api/downloads", status_code=202, dependencies=[Depends(require_api_key)])
def create_download(request: DownloadRequest, background_tasks: BackgroundTasks) -> dict:
    validate_options(request)
    prune_old_jobs()
    url = validate_public_url(request.url)
    with jobs_lock:
        active = sum(1 for job in jobs.values() if job["status"] in {"queued", "downloading", "processing"})
        if active >= MAX_ACTIVE_JOBS:
            raise HTTPException(status_code=429, detail="Download queue is full. Try again shortly.")
        job_id = uuid.uuid4().hex
        job = {"id": job_id, "status": "queued", "progress": 0, "created_at": time.time(),
               "format": request.format, "quality": request.quality, "request": request.model_dump()}
        jobs[job_id] = job
        cancel_events[job_id] = threading.Event()
    background_tasks.add_task(run_download, job_id, url, request)
    return public_job(job)


@app.post("/api/downloads/{job_id}/cancel", dependencies=[Depends(require_api_key)])
def cancel_download(job_id: str) -> dict:
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Download not found or expired")
        if job.get("status") in {"finished", "error", "cancelled"}:
            raise HTTPException(status_code=409, detail="This download can no longer be cancelled")
        cancel_events.setdefault(job_id, threading.Event()).set()
        job["status"] = "cancelling"
        return public_job(job)


@app.post("/api/downloads/{job_id}/retry", status_code=202, dependencies=[Depends(require_api_key)])
def retry_download(job_id: str, background_tasks: BackgroundTasks) -> dict:
    with jobs_lock:
        old = jobs.get(job_id)
        if not old:
            raise HTTPException(status_code=404, detail="Download not found or expired")
        if old.get("status") not in {"error", "cancelled"} or not old.get("request"):
            raise HTTPException(status_code=409, detail="Only failed or cancelled downloads can be retried")
        active = sum(1 for item in jobs.values() if item["status"] in {"queued", "downloading", "processing", "cancelling"})
        if active >= MAX_ACTIVE_JOBS:
            raise HTTPException(status_code=429, detail="Download queue is full. Try again shortly.")
        request = DownloadRequest(**old["request"])
        new_id = uuid.uuid4().hex
        new_job = {"id": new_id, "status": "queued", "progress": 0, "created_at": time.time(),
                   "format": request.format, "quality": request.quality, "request": request.model_dump()}
        jobs[new_id] = new_job
        cancel_events[new_id] = threading.Event()
    background_tasks.add_task(run_download, new_id, validate_public_url(request.url), request)
    return public_job(new_job)


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

