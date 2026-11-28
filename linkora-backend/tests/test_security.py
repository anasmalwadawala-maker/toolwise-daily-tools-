import os
import socket
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import main as linkora_main
from app.main import (DownloadRequest, require_api_key, validate_options, validate_public_url,
                      create_download, cancel_download, retry_download, list_downloads, get_download_file)
from fastapi import BackgroundTasks
from fastapi import HTTPException


class UrlValidationTests(unittest.TestCase):
    def test_rejects_non_http_scheme(self):
        with self.assertRaises(HTTPException):
            validate_public_url("file:///etc/passwd")

    def test_rejects_youtube_for_official_owner_export(self):
        with self.assertRaises(HTTPException):
            validate_public_url("https://youtu.be/example")

    def test_rejects_localhost(self):
        with self.assertRaises(HTTPException):
            validate_public_url("http://localhost/private")

    def test_rejects_loopback_ip(self):
        with self.assertRaises(HTTPException):
            validate_public_url("http://127.0.0.1/file.mp4")

    def test_rejects_credentials_in_url(self):
        with self.assertRaises(HTTPException):
            validate_public_url("https://user:pass@example.com/file.mp4")

    def test_accepts_public_host(self):
        answer = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
        with patch("app.main.socket.getaddrinfo", return_value=answer):
            self.assertEqual(validate_public_url("https://example.com/video.mp4"), "https://example.com/video.mp4")

    def test_rejects_mixed_public_and_private_dns_answers(self):
        answer = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.8", 443)),
        ]
        with patch("app.main.socket.getaddrinfo", return_value=answer):
            with self.assertRaises(HTTPException):
                validate_public_url("https://example.com/video.mp4")


class DownloadOptionTests(unittest.TestCase):
    def test_accepts_supported_quality_and_subtitle_options(self):
        request = DownloadRequest(url="https://example.com/video", quality="720",
                                  subtitles=True, automatic_subtitles=True,
                                  subtitle_languages=["en", "en-US"], thumbnail=True)
        validate_options(request)

    def test_rejects_unsupported_quality(self):
        request = DownloadRequest(url="https://example.com/video", quality="2160")
        with self.assertRaises(HTTPException):
            validate_options(request)

    def test_rejects_invalid_subtitle_language(self):
        request = DownloadRequest(url="https://example.com/video", subtitle_languages=["../../etc"])
        with self.assertRaises(HTTPException):
            validate_options(request)

    def test_rejects_quality_for_mp3(self):
        request = DownloadRequest(url="https://example.com/audio", format="mp3", quality="720")
        with self.assertRaises(HTTPException):
            validate_options(request)

    def test_accepts_bounded_playlist_request(self):
        request = DownloadRequest(url="https://example.com/list", playlist_mode=True, playlist_limit=12,
                                  playlist_items=[1, 3, 5])
        validate_options(request)

    def test_rejects_playlist_items_without_playlist_mode(self):
        request = DownloadRequest(url="https://example.com/list", playlist_items=[1, 2])
        with self.assertRaises(HTTPException):
            validate_options(request)

    def test_rejects_duplicate_playlist_items(self):
        request = DownloadRequest(url="https://example.com/list", playlist_mode=True, playlist_items=[2, 2])
        with self.assertRaises(HTTPException):
            validate_options(request)

    def test_rejects_playlist_limit_over_cap(self):
        with self.assertRaises(Exception):
            DownloadRequest(url="https://example.com/list", playlist_mode=True, playlist_limit=26)


class HistoryPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db = linkora_main.HISTORY_DB_PATH
        linkora_main.HISTORY_DB_PATH = Path(self.temp_dir.name) / "history.sqlite3"
        linkora_main.jobs.clear()
        linkora_main.cancel_events.clear()

    def tearDown(self):
        linkora_main.jobs.clear()
        linkora_main.cancel_events.clear()
        linkora_main.HISTORY_DB_PATH = self.original_db
        self.temp_dir.cleanup()

    def test_persists_and_restores_finished_history(self):
        job = {"id": "a" * 32, "status": "finished", "progress": 100,
               "created_at": time.time(), "finished_at": time.time(),
               "title": "Example", "filename": "example.mp4",
               "file_path": str(Path(self.temp_dir.name) / "missing.mp4")}
        linkora_main.persist_job(job)
        linkora_main.restore_jobs()
        restored = linkora_main.jobs[job["id"]]
        self.assertEqual(restored["title"], "Example")
        self.assertEqual(restored["status"], "expired")

    def test_marks_in_progress_jobs_interrupted_after_restart(self):
        job = {"id": "b" * 32, "status": "downloading", "progress": 35,
               "created_at": time.time()}
        linkora_main.persist_job(job)
        linkora_main.restore_jobs()
        restored = linkora_main.jobs[job["id"]]
        self.assertEqual(restored["status"], "error")
        self.assertIn("restarted", restored["error"])


class DownloadLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db = linkora_main.HISTORY_DB_PATH
        self.original_dir = linkora_main.DOWNLOAD_DIR
        linkora_main.HISTORY_DB_PATH = Path(self.temp_dir.name) / "history.sqlite3"
        linkora_main.DOWNLOAD_DIR = Path(self.temp_dir.name) / "downloads"
        linkora_main.DOWNLOAD_DIR.mkdir()
        linkora_main.jobs.clear()
        linkora_main.cancel_events.clear()
        self.addCleanup(self.cleanup_state)

    def cleanup_state(self):
        linkora_main.jobs.clear()
        linkora_main.cancel_events.clear()
        linkora_main.HISTORY_DB_PATH = self.original_db
        linkora_main.DOWNLOAD_DIR = self.original_dir
        self.temp_dir.cleanup()

    @patch("app.main.validate_public_url", return_value="https://example.com/video.mp4")
    def test_create_download_persists_queued_job(self, _validate):
        task_queue = BackgroundTasks()
        result = create_download(DownloadRequest(url="https://example.com/video.mp4"), task_queue)
        self.assertEqual(result["status"], "queued")
        self.assertIn(result["id"], linkora_main.jobs)
        self.assertEqual(len(task_queue.tasks), 1)
        with linkora_main.sqlite3.connect(linkora_main.HISTORY_DB_PATH) as connection:
            count = connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        self.assertEqual(count, 1)

    def test_cancel_marks_job_and_sets_event(self):
        job_id = "c" * 32
        job = {"id": job_id, "status": "downloading", "progress": 20, "created_at": time.time()}
        linkora_main.jobs[job_id] = job
        linkora_main.cancel_events[job_id] = linkora_main.threading.Event()
        result = cancel_download(job_id)
        self.assertEqual(result["status"], "cancelling")
        self.assertTrue(linkora_main.cancel_events[job_id].is_set())

    @patch("app.main.validate_public_url", return_value="https://example.com/video.mp4")
    def test_retry_creates_new_job_from_failed_request(self, _validate):
        old_id = "d" * 32
        old = {"id": old_id, "status": "error", "progress": 0, "created_at": time.time(),
               "request": DownloadRequest(url="https://example.com/video.mp4").model_dump()}
        linkora_main.jobs[old_id] = old
        task_queue = BackgroundTasks()
        result = retry_download(old_id, task_queue)
        self.assertNotEqual(result["id"], old_id)
        self.assertEqual(result["status"], "queued")
        self.assertEqual(len(task_queue.tasks), 1)
        self.assertIn(result["id"], linkora_main.jobs)

    def test_history_lists_jobs_newest_first(self):
        now = time.time()
        for job_id, created in [("e" * 32, now - 10), ("f" * 32, now)]:
            linkora_main.jobs[job_id] = {"id": job_id, "status": "error",
                                        "progress": 0, "created_at": created}
        result = list_downloads()
        self.assertEqual([item["id"] for item in result["items"]], ["f" * 32, "e" * 32])

    def test_file_download_requires_finished_job(self):
        job_id = "1" * 32
        linkora_main.jobs[job_id] = {"id": job_id, "status": "queued", "progress": 0,
                                    "created_at": time.time()}
        with self.assertRaises(HTTPException) as caught:
            get_download_file(job_id)
        self.assertEqual(caught.exception.status_code, 404)

    def test_file_download_serves_only_file_inside_job_folder(self):
        job_id = "2" * 32
        job_dir = linkora_main.DOWNLOAD_DIR / job_id
        job_dir.mkdir()
        media = job_dir / "sample.mp4"
        media.write_bytes(b"test-media")
        linkora_main.jobs[job_id] = {"id": job_id, "status": "finished", "progress": 100,
                                    "created_at": time.time(), "file_path": str(media),
                                    "filename": media.name}
        response = get_download_file(job_id)
        self.assertEqual(response.path, str(media))


class ApiKeyTests(unittest.TestCase):
    def test_requires_configured_key(self):
        with patch.dict(os.environ, {"LINKORA_API_KEY": ""}):
            with self.assertRaises(HTTPException) as caught:
                require_api_key("anything")
            self.assertEqual(caught.exception.status_code, 503)

    def test_rejects_wrong_key(self):
        with patch.dict(os.environ, {"LINKORA_API_KEY": "secret-value"}):
            with self.assertRaises(HTTPException) as caught:
                require_api_key("wrong")
            self.assertEqual(caught.exception.status_code, 401)

    def test_accepts_correct_key(self):
        with patch.dict(os.environ, {"LINKORA_API_KEY": "secret-value"}):
            self.assertIsNone(require_api_key("secret-value"))


if __name__ == "__main__":
    unittest.main()
