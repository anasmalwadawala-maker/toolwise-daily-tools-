# LINKORA — Toolwise Daily

A lightweight, mobile-first direct media-link checker and downloader interface, designed to sit alongside Toolwise Daily.

## Current MVP capabilities
- Accepts public HTTP/HTTPS URLs.
- Detects common social/streaming domains and explains that protected media extraction is not supported.
- Checks direct file URLs using browser CORS-enabled HEAD requests.
- Offers a direct-download link when the source allows browser access.
- Offers an open-source fallback when CORS or source restrictions prevent inspection.
- Supports common video, audio, image and document extensions.
- No account, link history, server upload or platform credentials.

## Important limitations
This is a browser-only MVP. It is **not** a universal social-media downloader and does not extract media from Instagram, TikTok, Facebook, X, YouTube or other protected services. Browser downloads depend on the source server's CORS headers, response type, browser behavior and the user's permissions. Some cross-origin download attributes may be ignored by browsers; the open-source fallback is provided for those cases.

No DRM, paywall, login, private-content or access-control bypass is implemented. Only save content you own, have permission to download, or that the publisher expressly offers.

## Run locally
Open `index.html` in a modern browser. No build step or package installation is required.

## Deploy to Cloudflare Pages
1. Connect this GitHub repository to Cloudflare Pages.
2. Choose the `feature/linkora-mvp` branch for preview, or merge the reviewed changes to `main` for production.
3. Set the project root directory to `linkora`.
4. Leave the build command blank; use the root directory itself as the output directory (static HTML).
5. Deploy and test the resulting `*.pages.dev` URL on mobile and desktop.
6. Add the deployed URL to the LINKORA page in Toolwise Daily WordPress.

Cloudflare Pages Free currently documents a 500-builds/month limit, 20,000 files per site and 25 MiB maximum per file. Review current plan limits before launch: https://developers.cloudflare.com/pages/platform/limits/

## WordPress integration
Keep the existing WordPress site as the main brand and content hub. Add a LINKORA link from the WordPress tool directory/navigation to the deployed Cloudflare Pages URL. WordPress.com Free does not need to host the application code.
