# Toolwise Daily — candidate keyword and SERP map

**Date:** 24 November 2026  
**Status:** Directional desk research only — not a paid keyword validation export.

## Measurement integrity

No numeric search-volume, keyword-difficulty, CPC, Similarweb traffic, ranking or trend claims are made in this document. A third-party directory (Toolseq) publishes very large monthly-search estimates for tool terms, but its methodology and source data were not independently verified; those numbers are deliberately excluded from planning.

The clusters below are selected from repeated tool categories and tasks appearing across current tool directories and a 2026 guide to popular online tasks. This demonstrates market presence and competitor coverage, not measured demand.

## Competitor/SERP observations

- PDF workflows are prominent across iLovePDF, Smallpdf, TinyWow and the sampled multi-tool directories. Intent is usually transactional/task completion: the searcher wants to upload/select files and receive a usable output.
- Image conversion/compression/resizing and background removal are repeatedly represented in current directories. Browser-side processing and transparent upload/privacy behavior can differentiate the product.
- QR generation, password generation, word counting, unit conversion and calculators appear across multiple sampled directories and 2026 tool roundups.
- Developer utility directories repeatedly feature JSON format/validation, Base64, regex, timestamps, CSV/JSON conversion and XML/HTML utilities. These are technically feasible and can be privacy-friendly.
- Generic AI tool directories are very competitive. Toolwise Daily should prioritise specific tasks with demonstrable output, explain model/provider limits and avoid thin prompt-only pages.

## Candidate keyword clusters and release priority

Priority is a product judgement based on visible competitor coverage, implementation feasibility and the clarity of user intent. It is not a search-volume ranking.

| Cluster | Candidate primary intents | Priority | Main competitors / SERP types | Implementation notes |
|---|---|---|---|---|
| PDF core | merge PDF; split PDF; compress PDF; PDF to JPG; JPG to PDF; rotate PDF; delete PDF pages | P1 | iLovePDF, Smallpdf, TinyWow | Keep processing in browser where possible. Clearly disclose that structural PDF re-saving is not true image recompression. |
| Image core | compress image; resize image; crop image; JPG to PNG; PNG to JPG; WebP converter; HEIC to JPG | P1 | TinyPNG, CloudConvert, Convertio, multi-tool directories | Browser Canvas/WebCodecs where supported; preserve EXIF only when intended and disclose metadata behavior. |
| QR & credentials | QR code generator; Wi-Fi QR code; password generator | P1 | QR-focused generators, multi-tool directories | QR needs export and error-correction controls. Passwords must use cryptographic randomness, never Math.random. |
| Text basics | word counter; character counter; case converter; remove duplicate lines; slug generator | P1 | RapidTables, text utility sites | Fast, no upload; robust Unicode handling and copy/download. |
| Everyday calculators | percentage calculator; age calculator; unit converter; date difference; GST calculator | P1 | Calculator sites, India utility sites | Verify formulas and localization; GST is India-specific and needs clear inclusive/exclusive handling. |
| Developer basics | JSON formatter; JSON validator; Base64 encode/decode; regex tester; UUID generator; Unix timestamp converter | P1 | Dev utility directories | Use safe parsing, clear errors and local-only handling for pasted data. |
| SEO utilities | meta tag generator; robots.txt generator; SERP snippet preview; sitemap generator; title length checker | P2 | SEO tool suites and SERP preview utilities | Explain that previews are approximations and do not guarantee Google display/ranking. |
| File/data converters | CSV to JSON; JSON to CSV; XML to JSON; YAML to JSON; Markdown to HTML | P2 | Converter suites and developer directories | Preserve encoding, quoting, nested data and large-file limits. |
| Video/audio | MP4 to MP3; video to GIF; audio trimmer; MP3 cutter; video compressor | P2 | CloudConvert, media converters | Browser codec support varies; use workers/WASM and disclose output limitations. |
| AI productivity | AI summarizer; email writer; title generator; prompt formatter; keyword extractor | P2 | AI writing tools and AI directories | Requires server-side proxy, rate limiting, transparent usage caps and privacy disclosure. |
| Finance/business | EMI calculator; GST calculator; income tax calculator; SIP calculator; invoice generator | P2 | Calculator directories and finance publishers | Tax/finance calculations need jurisdiction, tax-year and assumptions prominently stated. |
| Security/network | hash generator; JWT decoder; DNS lookup; IP lookup; SSL checker; URL encoder | P2/P3 | Developer/security utilities | Never imply a local decoder validates a token's authenticity. Avoid storing submitted secrets. |

## First 100 candidate scope

This is a **proposed build shortlist**, not a claim that 100 keyword opportunities have been measured. Final ordering should be adjusted after keyword metrics, SERP review and a tool feasibility audit.

1. Merge PDF
2. Split PDF
3. Compress PDF (honest structural mode vs real recompression)
4. PDF to JPG
5. JPG to PDF
6. Rotate PDF
7. Delete PDF pages
8. PDF page counter
9. PDF metadata viewer
10. PDF unlock/protection helper (only if safe/legal handling and clear limitations)
11. Image compressor
12. Image resizer
13. Image cropper
14. Image rotator
15. JPG to PNG
16. PNG to JPG
17. WebP to JPG
18. JPG to WebP
19. HEIC to JPG
20. Image dimension checker
21. QR code generator
22. Wi-Fi QR generator
23. Password generator
24. Word counter
25. Character counter
26. Sentence counter
27. Case converter
28. Remove duplicate lines
29. Text to slug converter
30. Word frequency counter
31. Text reverser
32. Lorem ipsum generator
33. Percentage calculator
34. Age calculator
35. GST calculator
36. Discount calculator
37. Profit margin calculator
38. Unit converter
39. Date difference calculator
40. Time duration calculator
41. Number to words converter
42. Random number generator
43. JSON formatter
44. JSON validator
45. Base64 encoder
46. Base64 decoder
47. Regex tester
48. UUID generator
49. Unix timestamp converter
50. URL encoder
51. URL decoder
52. HTML entity encoder
53. HTML entity decoder
54. XML formatter
55. XML to JSON converter
56. JSON to CSV converter
57. CSV to JSON converter
58. YAML to JSON converter
59. Markdown to HTML converter
60. Text diff checker
61. Meta tag generator
62. Robots.txt generator
63. XML sitemap generator
64. SERP snippet preview
65. Title tag length checker
66. Meta description length checker
67. Open Graph preview
68. Canonical URL checker
69. Hreflang tag generator
70. Schema markup generator
71. EMI calculator
72. Loan repayment calculator
73. Compound interest calculator
74. SIP calculator
75. Income tax calculator (India; tax year and regime must be explicit)
76. Salary to hourly calculator
77. Tip calculator
78. BMI calculator
79. Calorie calculator (with appropriate disclaimers)
80. Scientific calculator
81. MP4 to MP3 converter
82. Video to GIF converter
83. Audio trimmer
84. MP3 cutter
85. Video compressor
86. Audio format converter
87. AI text summarizer
88. AI email writer
89. AI title generator
90. AI prompt formatter
91. AI keyword extractor
92. Invoice generator
93. Resume text extractor/checker
94. Color picker
95. Color contrast checker
96. Gradient generator
97. HEX to RGB converter
98. Time zone converter
99. Stopwatch
100. Pomodoro timer

## Keyword validation worksheet — required fields

Before approving each tool landing page, record:

- Primary keyword and close variants
- Target country and language
- Search volume and source/date
- Keyword difficulty and source/date
- CPC only if a reliable source provides it
- 12-month trend and seasonality
- SERP intent and dominant result types
- Top 5 relevant ranking URLs and their page types
- Whether an existing Toolwise Daily page already targets the same intent
- Canonical URL and internal-link targets
- Tool feasibility, dependency size, privacy and testing status

## Stop/go rule

A candidate moves into the first release only when:
1. The search intent is distinct and not cannibalised by an existing page.
2. The tool can produce a real, verifiable result.
3. The implementation and maintenance cost is acceptable.
4. The page can add unique instructions, examples, limits and privacy information.
5. Keyword/SERP evidence is recorded, or the candidate is explicitly marked as a strategic utility rather than an SEO-demand bet.

## Sources reviewed

- 2026 online-tool roundup: https://jobbit.uk/en/blog/free-online-tools-most-googled-2026
- Current 130+ tool directory and category mix: https://www.clacify.com/
- Current 145+ tool directory and category mix: https://proit.tools/
- Current 90-tool privacy-first directory: https://opentoolslibrary.com/
- Current 197-tool directory and browser processing positioning: https://zerofeetools.com/
- Google Search spam policies: https://developers.google.com/search/docs/essentials/spam-policies
- Google helpful content guidance: https://developers.google.com/search/docs/fundamentals/creating-helpful-content

## Outstanding measurement dependencies

- Similarweb account credits restored or plan upgraded.
- OpenSEO organisation credits restored for keyword metrics.
- Search Console connected to the Toolwise Daily SEO project and verified property.
