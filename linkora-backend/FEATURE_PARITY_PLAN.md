# LINKORA MeTube-Style Feature Parity Roadmap

Status: development scope on `linkora/metube-feature-parity`. This document does not authorize a production launch, WordPress publication, or merging any pull request.

## Goal

Build an independently implemented, mobile-first LINKORA experience inspired by the user-facing capabilities of MeTube, using yt-dlp and FFmpeg where source-platform rules permit. Do not copy MeTube source code or assets. MeTube is AGPL-3.0; review the exact licenses of every dependency and bundled artifact before redistribution.

## Target feature set

1. **Single media items** — inspect a supported public media page, show title/thumbnail/duration and available formats, then queue an authorized download.
2. **Playlists and channels** — inspect collections, show item counts and entries, allow selected items or a bounded batch, and show per-item progress. Respect extractor and source-platform restrictions.
3. **Video and audio** — choose best available, bounded quality/resolution, audio-only and supported audio conversion formats (subject to installed FFmpeg codecs).
4. **Subtitles and metadata** — optional manually selectable subtitle languages, automatic captions where offered, embed/sidecar subtitles, metadata and thumbnail writing where supported.
5. **Thumbnail-only save** — save an available public thumbnail as a separate output.
6. **Queue and history** — queued, running, processing, completed and failed states; progress, retry, cancel, clear-history and safe file retrieval.
7. **Per-job options** — output type, format/quality, subtitle choices, playlist item limit, filename template and a safe subfolder under the download directory.
8. **Presets and defaults** — server-managed named presets and safe global defaults. Never expose arbitrary shell commands or unrestricted yt-dlp options to anonymous visitors.
9. **Subscriptions** — subscribe to eligible public channel/playlist feeds, check on a configurable schedule, deduplicate seen items and queue newly published items. Subscriptions must be opt-in, rate-limited and pauseable/deletable.
10. **Responsive interface** — Toolwise Daily visual identity, phone-first controls, light/dark/auto theme, accessible status and clear legal/size/retention notices.
11. **Operations** — API authentication, per-client quotas, rate limiting, job limits, cleanup, audit-safe logs, health checks and deployment tests.

## Required restrictions

- Do not bypass DRM, encryption, paywalls, login requirements, private-content controls, or technical access controls.
- Do not accept browser cookies, session tokens, passwords, or account credentials.
- Do not enable YouTube third-party stream extraction. For a user's own YouTube uploads, direct them to YouTube Studio or Google Takeout. A creator's permission alone does not override the platform's terms.
- Do not promise that every site or URL works. Extractor support and source terms vary and change.
- Validate URL destinations and enforce network-level egress restrictions; DNS checks alone are not sufficient SSRF protection.
- Do not expose arbitrary yt-dlp option overrides to public users.
- Keep all changes on this development branch. Do not merge, deploy to production, publish the WordPress page, or enable public launch without separate user approval.

## Hosting reality

The current Render Free service has an ephemeral filesystem and may sleep/restart. Its in-memory queue and downloaded files are temporary. Reliable subscriptions, history, and durable downloads require persistent storage and a scheduler/worker design; do not represent the free preview as production-grade persistent hosting. Keep free-tier limitations visible in the UI.

## Delivery approach

- Phase 1: data model and API for rich per-job options, format inspection, collection inspection, bounded batch jobs, subtitles and thumbnails.
- Phase 2: robust queue lifecycle (cancel/retry/concurrency), persistent metadata abstraction, cleanup and tests.
- Phase 3: subscription scheduler, deduplication, pause/resume/delete and tests.
- Phase 4: Toolwise-styled UI for the above features, mobile/accessibility QA and end-to-end tests on explicitly authorized test media.
- Phase 5: security review, dependency/license review, hosting feasibility and preview acceptance report.

A phase is complete only after tests and an actual supported-media end-to-end test pass. CI success alone is not proof that downloads work.
