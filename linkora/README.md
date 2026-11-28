# LINKORA — Toolwise Daily

A lightweight, mobile-first direct media-link checker and downloader interface, designed to sit alongside Toolwise Daily.

## Current MVP capabilities
- Accepts public HTTP/HTTPS URLs only; rejects credentials and common private/local network address ranges.
- Detects known social/streaming domains and refuses protected-media extraction.
- Checks direct file URLs with a CORS-enabled HEAD request, with a byte-range GET fallback for servers that do not support HEAD (405/501).
- Re-checks the final redirected URL before offering a download; rejects redirects to blocked social or private/local destinations.
- Streams downloads and enforces the 100 MiB cap while reading, rather than waiting until the entire file is buffered.
- Sanitizes the suggested download filename, preferring a safe Content-Disposition filename when exposed by the server.
- Offers an open-source fallback when browser CORS/source restrictions prevent inspection.
- Supports common video, audio, image and document extensions.
- No account, link history, server upload, cookies or platform credentials.

## Important limitations
This is a browser-only direct-file MVP. It is **not** a universal social-media downloader and does not extract media from Instagram, TikTok, Facebook, X, YouTube or other protected services. Browser downloads depend on the source server's CORS headers, response type, browser behavior and the user's permissions. Some cross-origin download attributes may be ignored by browsers; the open-source fallback is provided for those cases.

No DRM, paywall, login, private-content or access-control bypass is implemented. Only save content you own, have permission to download, or that the publisher expressly offers. The 100 MiB limit is a browser-memory safeguard, not a promise that every supported file will download successfully.

## Run locally
Open `index.html` in a modern browser. No build step or package installation is required.

## QA checklist before deployment
- [ ] Valid public direct MP4, MP3, JPG, PNG, PDF and ZIP URLs.
- [ ] Invalid URL, non-HTTP(S) scheme, URL credentials and localhost/private IPv4/IPv6 addresses.
- [ ] Known social/streaming host and a redirect that ends at a blocked host.
- [ ] HEAD success; HEAD 405/501 with a byte-range response; CORS-denied source.
- [ ] Redirect to a valid public direct file and redirect to a private/local address.
- [ ] Declared file size above 100 MiB and streamed body that crosses 100 MiB without Content-Length.
- [ ] Safe filename from URL and Content-Disposition, including path separators/control characters.
- [ ] Slow network, interrupted stream, browser without readable streams.
- [ ] Android Chrome and desktop Chrome; verify download behavior and open-source fallback.
- [ ] Regression check that the separate 50 Toolwise Daily tools remain unchanged.

Do not mark any test as passed until it has been run against a deployed preview on the target browsers. Static source checks are not a substitute for end-to-end testing.

## Deploy to Cloudflare Pages (free static hosting)
1. Connect this GitHub repository to Cloudflare Pages.
2. Use the `linkora/reliability-hardening` branch for a preview deployment. Do not switch production to this branch until the preview passes QA and is separately approved.
3. Set the project root directory to `linkora`.
4. Leave the build command blank; set the output directory to the project root itself (`.`).
5. Deploy a preview and test the resulting `*.pages.dev` URL on mobile and desktop.
6. Only after testing and separate launch approval, merge to `main` and configure production.

Cloudflare Pages plan limits can change; check the current official limits before launch: https://developers.cloudflare.com/pages/platform/limits/

## WordPress integration
Keep the existing WordPress site as the main brand and content hub. The LINKORA WordPress page remains a draft. After the preview is verified and the user separately approves integration, add the deployed preview/production URL to the draft page and verify the rendered page. Do not publish without separate explicit approval.
