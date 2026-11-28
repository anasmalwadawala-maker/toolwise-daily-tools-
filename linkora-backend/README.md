# LINKORA Download API (backend preview)

A separate, independently written FastAPI service for LINKORA. It uses the yt-dlp Python package as a download engine and FFmpeg for media processing. It is inspired by the workflow of MeTube, but this directory does not copy MeTube's AGPL-3.0 application code.

## What is included

- Public health check at GET /health.
- API-key-protected media inspection at POST /api/info.
- API-key-protected download queue at POST /api/downloads.
- Queue status at GET /api/downloads and GET /api/downloads/{id}.
- File retrieval at GET /api/downloads/{id}/file.
- Video/audio selection (best or MP3), progress updates, a 500 MiB default file cap and a small queue.
- YouTube URLs are intentionally rejected; use YouTube Studio or Google Takeout for your own uploads.
- No cookie import, browser-session access, login automation, DRM removal, paywall bypass or private-content access.

This is a backend foundation, not a promise that every platform or URL will work. Extractors change and individual services can block or prohibit downloading. Only use it for content you own, are authorized to download, or that the source expressly makes available for download. A creator's permission does not automatically override a platform's terms.

## Run locally with Docker

1. Set a long random API key in your environment.
2. Build and run:

    docker build -t linkora-api ./linkora-backend
    docker run --rm -p 8080:8080 \
      -e LINKORA_API_KEY='replace-with-a-long-random-secret' \
      -e LINKORA_ALLOWED_ORIGINS='http://localhost:5500' \
      linkora-api

3. Check http://localhost:8080/health.
4. Send the key in the X-LINKORA-API-KEY header for every /api/* request.

Example:

    curl -X POST http://localhost:8080/api/info \
      -H 'Content-Type: application/json' \
      -H 'X-LINKORA-API-KEY: replace-with-a-long-random-secret' \
      -d '{"url":"https://example.com/public-media-file.mp4","format":"best"}'

## Free preview hosting: important limits

A Render free web service can run a Docker container, but it spins down after 15 minutes without traffic, takes about a minute to wake, can restart, and has an ephemeral filesystem. Downloaded files and in-memory queue state are therefore temporary and may disappear. Free instances also have very limited CPU and memory. This is suitable for a private technical preview only, not a reliable public downloader or long-term file storage.

The included render.yaml is a deployment blueprint, not a deployed service. Do not deploy publicly until the API is placed behind a trusted same-origin proxy, secrets are configured, abuse controls and network-egress protections are reviewed, and real download tests are completed. Never put LINKORA_API_KEY in browser JavaScript or a public repository.


## Connect the backend to the LINKORA preview

After creating the Render service, keep it private to preview use. In the Cloudflare Pages project for LINKORA, add these as **Preview** environment variables only:

- LINKORA_BACKEND_URL: the HTTPS origin of the Render service (no path suffix).
- LINKORA_API_KEY: the same strong random secret configured in the Render service.

The Pages Function at linkora/functions/api/engine/[[path]].js injects the secret server-side. The browser never receives the API key. Do not set Production variables or enable production deployments while the public launch is on hold. Re-deploy the allowed preview branch only after the backend and secrets are configured.

## Security notes and remaining work

- The API requires a secret key and validates the submitted URL and its DNS answers before extraction.
- DNS checks alone are not a complete SSRF defense: DNS rebinding and secondary URLs requested by extractors require additional network-level egress controls. Do not expose this API directly to the public internet as-is.
- Add per-user quotas, rate limiting, job cancellation, automatic file cleanup, persistent job storage, and a secure Cloudflare Pages Function proxy before public launch.
- Restrict supported domains or enforce a network egress allowlist in the production environment.
- The API deliberately does not accept cookies or authenticated browser sessions.
- The API is currently single-process with in-memory jobs and one download at a time.

## Licensing

The MeTube project is licensed under AGPL-3.0. This backend does not reuse its source code. It uses the yt-dlp Python package, whose source/PyPI distributions are licensed under the Unlicense; bundled release executables and optional components can have additional third-party licensing terms. FFmpeg and other dependencies also have their own licences. Review the licences of the exact artifacts used for any redistribution.

- MeTube: https://github.com/alexta69/metube
- yt-dlp licensing: https://github.com/yt-dlp/yt-dlp#licensing
