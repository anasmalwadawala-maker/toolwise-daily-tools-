# Toolwise Daily — 50 Free Online Tools

A mobile-first static website containing 50 browser utilities across PDF, image, text, calculators, and creator/SEO categories.

## Run locally
Open `index.html` in a modern browser. PDF and QR functions load libraries from CDNs and therefore require an internet connection.

## Deploy
Upload `index.html` to the root of a public GitHub repository. In repository Settings → Pages, choose Deploy from a branch, select `main` and `/(root)`, then Save.

## Tool notes
- Most text and calculator tools run entirely in the browser.
- Image tools use the browser canvas API.
- PDF tools use pdf-lib and PDF.js from cdnjs.
- QR tools use QRCode.js from cdnjs.
- PDF compression currently re-saves PDF objects; it does not promise a smaller file or image downsampling.
- PDF to JPG renders up to 10 pages per run.
- Do not upload confidential files to websites unless you trust the environment. This prototype processes supported files locally in the browser.
- Verify all outputs before relying on them.

## Licences and attribution
This implementation is original code for Toolwise Daily. It does not bundle third-party source code. Runtime libraries are loaded from their respective CDNs; review their licences and terms before commercial production use:
- pdf-lib: https://github.com/Hopding/pdf-lib
- PDF.js: https://github.com/mozilla/pdf.js
- QRCode.js: https://github.com/davidshimjs/qrcodejs

## Important hosting note
GitHub Pages is suitable for static project/demo hosting. GitHub's current documentation says Pages is not intended as free hosting for a site primarily directed at running a commercial business or SaaS. Review the GitHub Pages limits and terms before using it as the production host for a monetised tool business.
