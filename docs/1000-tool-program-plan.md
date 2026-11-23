# Toolwise Daily — 1,000-tool program plan

**Status:** Planning only. No application code has been changed in this branch.  
**Planning branch:** `planning/1000-tool-wordpress-roadmap`  
**Date:** 23 November 2026

## 1. Product decision

Build Toolwise Daily as a **WordPress-led hybrid**:

- **WordPress.com** remains the editorial, SEO, trust and discovery layer: homepage, category hubs, tool explainers, tutorials, comparisons, editorial standards, privacy and contact pages.
- **The existing static tool application** remains the execution layer, hosted separately (current GitHub Pages deployment; assess Cloudflare Pages as the next host before migration).
- Every WordPress tool landing page links directly to its matching app route, e.g. `?tool=merge-pdf`. Do not promise an embedded tool experience on the current Free plan.
- The product is hybrid: genuinely free browser-first utilities plus a smaller, clearly labelled set of AI-assisted tools. No API keys in browser code; AI requests require a protected server-side proxy, rate limits, transparent limits and a real cost model.

This is the most compatible route with the current WordPress.com Simple/Free environment. WordPress.com says custom JavaScript is available on plugin-enabled plans after hosting features are activated; Free sites restrict script and iframe code. Until the plan changes, use ordinary links from WordPress to the external tool app rather than a fragile iframe or pasted script.

## 2. Repository baseline

Repository: https://github.com/anasmalwadawala-maker/toolwise-daily-tools-  
Live app reference supplied by owner: https://anasmalwadawala-maker.github.io/toolwise-daily-tools-/?tool=merge-pdf

Observed repository state:
- Public repository, default branch `main`, owner has push/admin permissions.
- Root contains `index.html` (about 35.7 KB) and `README.md` (about 2.4 KB).
- README describes **50 tools across 5 categories**: PDF, Image, Text, Calculators, Creator & SEO.
- Current app is a single-page, vanilla HTML/CSS/JavaScript application. Tool routing uses the `tool` query parameter and supports the supplied `merge-pdf` route.
- Browser-side image/text processing and PDF/QR libraries loaded from public CDNs are documented. The README explicitly warns that PDF “compression” is structural re-saving, not image downsampling, and may not reduce file size.
- This is a useful prototype, not yet a maintainable 1,000-tool product architecture. Separate tool definitions, execution modules, tests, build tooling, accessibility checks and release checks are needed.

## 3. 1,000-tool catalogue allocation

These are **capacity targets for the product catalogue**, not a claim that the keywords or individual tools have already been validated. Each proposed tool must pass the acceptance gate in section 7 before it is marked live.

| Category | Target tools |
|---|---:|
| AI productivity and writing | 100 |
| PDF and document utilities | 90 |
| Image utilities | 85 |
| Text and writing utilities | 80 |
| Calculators | 80 |
| Developer utilities | 80 |
| SEO and webmaster utilities | 65 |
| Video utilities | 55 |
| File format converters | 50 |
| Audio utilities | 45 |
| Finance and business calculators | 45 |
| Education and mathematics | 40 |
| Security and privacy utilities | 30 |
| Color and design utilities | 30 |
| QR and barcode utilities | 25 |
| Date and time utilities | 25 |
| Network and DNS utilities | 20 |
| Social media utilities | 20 |
| Geography and travel utilities | 15 |
| Everyday utilities | 20 |
| **Total** | **1,000** |

## 4. Competitive position

The market is crowded. The product should not try to win by copying a giant catalogue. Its defensible angle is **clear, useful, privacy-conscious tools with transparent limitations and practical beginner instructions**.

Reference competitors:
- **iLovePDF:** strong PDF task coverage, workflow depth, cloud integrations and desktop/mobile options.
- **TinyWow:** wide PDF, file-conversion, image and AI catalogue; explicitly advertises 150+ tools and a premium tier.
- **RapidTables:** broad calculators, conversions, math, text and web-development utilities.
- **Smallpdf:** strong PDF workflow brand and polished task-focused UX.
- **Toolify, Futurepedia, Future Tools, There's An AI For That and TopAI.tools:** relevant AI discovery competitors; their breadth and discovery features exceed Toolwise Daily's current directory.

A saved OpenSEO competitive-landscape report dated 23 Nov 2026 estimates India organic visibility for five AI directories. The figures are third-party estimates, **not Similarweb measurements and not audited analytics**:
- There's An AI For That: 86,297 estimated organic visits/month; 4,918 ranking keywords.
- Futurepedia: 36,623; 744.
- Toolify: 24,667; 4,310.
- Future Tools: 15,347; 466.
- TopAI.tools: 779; 449.
- Toolwise Daily returned no domain data in that report.

Interpretation: do not compete on breadth alone. Win with verified tool functionality, task-led navigation, free-plan and privacy comparisons, honest tool limitations, use-case tutorials and strong internal linking.

## 5. Keyword research status — do not treat as validated

**Not complete.** OpenSEO's existing competitive-landscape report says the follow-on keyword/ranking batch was blocked by the organisation credit limit. No keyword list or keyword metrics are currently saved to the Toolwise Daily OpenSEO project. Search Console is not connected in that project. Similarweb research is also currently unavailable because the connected account has exhausted its credits.

Therefore:
- Do not publish invented search volumes, keyword difficulty, CPC, traffic, Similarweb ranks or trend percentages.
- Treat seed clusters such as “merge PDF”, “compress PDF”, “PDF to Word”, “image compressor”, “image to WebP”, “word counter”, “percentage calculator”, “GST calculator”, “JSON formatter”, “QR code generator”, “meta tag generator”, “robots.txt generator” and “AI summarizer” as **candidate topics only**.
- Before deciding the first 100–1,000 indexable landing pages, collect country/language-specific volume, KD, CPC, 12-month trend, SERP intent and competitor URLs. Start with India-English and then validate US-English separately if global reach is the goal.
- Map one primary intent to one canonical landing page. Consolidate close variants rather than creating near-duplicate pages.

## 6. WordPress information architecture

Keep the existing WordPress editorial layer and avoid creating 1,000 thin pages in one publishing burst.

Recommended structure:
- `/free-online-tools/` — main directory hub and search by task/category.
- `/tools/pdf/`, `/tools/image/`, `/tools/text/`, `/tools/calculators/`, etc. — category hubs with curated, useful summaries.
- `/tools/<tool-name>/` — individual landing pages only after tool acceptance and keyword/intent validation.
- `/tutorials/` — task-led how-to content and examples.
- Existing About, Contact, Privacy Policy, Affiliate Disclosure and Editorial Standards pages remain visible and linked.

Each tool landing page should contain:
1. Clear title/H1 and one-sentence outcome.
2. A prominent **Open tool** link to the matching app route.
3. A genuinely useful explanation of inputs, outputs, supported formats, limits and example use.
4. Step-by-step instructions and a worked example where appropriate.
5. Privacy/data-handling statement specific to that tool.
6. Relevant FAQs based on real user questions, not boilerplate.
7. Links to closely related tools and tutorials.
8. Accurate title/meta description, canonical URL and valid structured data only when appropriate.

The WordPress Free plan cannot host the app's custom JavaScript or arbitrary iframe embed in a normal page. Keep the tool runtime external unless the owner later upgrades to a plugin-enabled plan and activates hosting features.

## 7. Tool acceptance and release gates

A tool is not “functional” merely because it has a card, title or generator button. Each tool must pass:

- **Correctness:** representative happy-path, edge-case and invalid-input tests.
- **Real output:** downloadable/copyable/exportable result, not a fake CTA or placeholder.
- **Limits:** file size, page count, supported formats and known caveats shown before use.
- **Privacy:** prefer in-browser processing; if server processing is necessary, disclose what is uploaded, retention and deletion policy.
- **Security:** validate MIME/type and size, sanitize user-provided text, avoid unsafe HTML insertion, keep secrets server-side.
- **Accessibility:** keyboard operation, labels, visible focus, useful error messages and mobile layout.
- **Performance:** lazy-load heavy libraries per tool, avoid loading all dependencies on the directory home page.
- **Observability:** measure successful completions and errors without collecting document contents or sensitive inputs.
- **SEO:** index only useful, stable pages with distinct intent and substantive instructions. No mass-generated near-duplicate pages.

## 8. Technical repository plan — before implementation

Refactor the single-file prototype into a modular app:
- `src/app/`: router, search, category navigation and shared layout.
- `src/catalog/`: typed tool metadata, category IDs, routes, tags and availability.
- `src/tools/<category>/<tool-id>/`: isolated UI and implementation per tool.
- `src/lib/`: shared file handling, validation, download, clipboard, formatting and error utilities.
- `src/workers/`: Web Workers for CPU-heavy browser tasks.
- `tests/unit/` and `tests/e2e/`: tool correctness, routing and accessibility checks.
- `docs/`: product brief, keyword map, tool catalogue, architecture decisions and release checklist.

Recommended implementation baseline: TypeScript, Vite, modular CSS or a lightweight utility CSS system, browser-native APIs where possible, Web Workers for expensive tasks, and Playwright/Vitest for automated checks. Keep the current public URL routes stable or add redirects before changing route structure.

AI-assisted tools should be isolated behind a serverless API gateway with environment-managed keys, per-IP/user quotas, request validation, abuse controls and explicit provider/cost disclosures. Do not ship AI features that rely on a secret embedded in public JavaScript.

## 9. Build sequence

The owner has selected a 1,000-tool target. The build will be delivered in verified waves, not by shipping 1,000 untested cards:
- **Wave 0 — foundations:** repository structure, design system, catalogue schema, route compatibility, test harness, analytics events and privacy/security rules.
- **Wave 1 — core 100:** the strongest cross-category tasks after keyword and SERP validation; include existing 50 where they pass tests, repair limitations and replace weak tools.
- **Wave 2 — 250 cumulative:** expand the categories with demonstrated demand and acceptable implementation effort.
- **Wave 3 — 500 cumulative:** add file/media, developer, SEO and AI modules with separate dependency and cost budgets.
- **Wave 4 — 1,000 cumulative:** only add tools with distinct user jobs, tested outputs, supportable privacy/cost profiles and useful landing-page content.

The 1,000-tool target is a product roadmap, not a promise that all 1,000 pages will be indexed or attract traffic. Monitor Search Console impressions/clicks and actual completion rates before expanding each wave.

## 10. Immediate blockers and next decision

1. Re-open keyword metrics when OpenSEO credits are available; validate the seed clusters and competitor SERPs before final tool ordering.
2. Re-run Similarweb competitor traffic, engagement, geography, ranking and keyword analysis after Similarweb credits are restored. Keep its figures in a separate column from OpenSEO estimates.
3. Connect Toolwise Daily's Search Console property to the SEO project to get first-party query/page performance.
4. Confirm whether the app should stay on GitHub Pages for now or move to Cloudflare Pages after the current architecture review.
5. Only after research data and Wave 1 scope are approved, start implementation. This branch currently contains planning documents only.
