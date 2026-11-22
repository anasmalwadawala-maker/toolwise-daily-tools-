# Toolwise Daily — 50 Free Online Tools

A responsive, mobile-first browser tools directory built with HTML, CSS and vanilla JavaScript.

## Included tools

- **PDF (10):** Merge PDF, Compress PDF (structural re-save; not guaranteed smaller), Split PDF / page extraction, JPG to PDF, PDF to JPG, PDF Page Extractor, Rotate PDF, Delete PDF Pages, PDF Page Calculator, PDF Metadata Viewer.
- **Image (10):** Image Compressor, Image Resizer, JPG to PNG, PNG to JPG, WebP to JPG, Image Cropper, Image to PDF, Image Rotator, Image to Base64, Image Dimension Checker.
- **Text (10):** Word Counter, Character Counter, Case Converter, Remove Duplicate Lines, Text to Slug Converter, Word Frequency Counter, Sentence Counter, Reading Time Calculator, Lorem Ipsum Generator, Text Reverser.
- **Calculators (10):** Percentage Calculator, Age Calculator, GST Calculator, Discount Calculator, Profit Margin Calculator, Unit Converter, Date Difference Calculator, Time Duration Calculator, Number to Words Converter, Random Number Generator.
- **Creator & SEO (10):** QR Code Generator, Wi-Fi QR Generator, WhatsApp Link Generator, YouTube Thumbnail Size Checker, Instagram Image Size Checker, YouTube Title Generator, Instagram Caption Generator, Meta Description Generator, SERP Preview Tool, Robots.txt Generator.

## Run locally

Open `index.html` in a modern browser. Some PDF and QR features load libraries from public CDNs, so an internet connection is needed for those features. Image and text processing runs in the browser.

## Important limitations

- PDF compression re-saves the PDF with object streams; it does not downsample images and may not reduce the file size.
- PDF-to-JPG currently renders at most 10 pages per run. Browser download permissions may affect multiple downloads.
- The title, caption and meta-description generators use simple templates, not generative AI.
- This is a static front-end package. It has no account system, server-side storage, analytics, ads or affiliate tracking.
- Do not use browser tools with sensitive documents unless you understand the browser and third-party library dependencies.

## Deployment

Upload `index.html` to a static host that permits your intended use. Review the host's terms, especially before monetizing. WordPress.com Free does not allow arbitrary custom JavaScript in normal page content, so host this tool app separately and link to it from your WordPress site.
