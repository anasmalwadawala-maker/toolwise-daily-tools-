import os
import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import DownloadRequest, require_api_key, validate_options, validate_public_url
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
