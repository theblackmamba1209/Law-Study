# Sinag · Codal Studio

Philippine law, studied one provision at a time. The verbatim codal text is the backbone. Each provision has:

- **Read**: the verbatim text, with highlighting for duties and powers, conditions, exceptions, numbers and periods, penalties, and definitions. Cross-references link to the article they cite.
- **Study guide**: an automatic reading guide that sorts each sentence into rule, condition, exception and consequence. The highest-yield provisions also have plain-language explanations, elements, exam traps and self-tests.
- **Recall**: three levels of cloze, first-letter cues, or writing the provision from memory with a word-by-word comparison.
- **Spaced review**: rate each recall (Again / Hard / Good / Easy) and the provision comes back just before you would forget it.
- **Cases**: every case your textbooks cite under that provision, with the page in your copy, plus digests for the leading cases.
- **Amendments**: for the RPC, NIRC and a few others, the amended wording is shown verbatim from the amending law.
- **Drill**: interleaved practice across codes, including "name that provision" and a numbers-and-periods drill.

## What's inside

`data/catalog.json` lists 114 instruments (about 12,441 provisions), grouped by Bar subject. Each code is a file in `data/codes/`. Case indexes are in `data/cases/`, and study guides are in `data/notes/`. `data/proofreading.json` is the correction log.

| Source | Used for |
|---|---|
| The LawPhil Project (Arellano Law Foundation), via the LawCodex mirror | most statutes, the 1987 Constitution, RPC, Civil Code, special laws |
| DOLE, *Labor Code of the Philippines, Renumbered* (2022) | Labor Code |
| Your PDF of EO 209 | Family Code (its fonts were scrambled; the text layer was decoded and checked against OCR) |
| Your scanned EO 292 | Administrative Code (OCR; sections still needing a check are marked) |
| Your textbooks | case indexes only: names, citations, pages. The authors' text is not reproduced. |

None of these is the official text. Before citing a provision, check the Official Gazette or a certified copy.

## Proofreading

- Watermarks and markup were removed.
- The numbering was checked for gaps, duplicates and merged provisions.
- Automatic flags catch repeated words, unbalanced parentheses and words split by a stray space.
- Civil Code Arts. 1157–1439 were compared word by word with the codal text printed in De Leon.
- Ten Civil Code articles that the online text had run into the preceding article were separated out again, using the source's own words: 213, 298, 437, 548, 578, 1602, 1622, 1634, 2075 and 2120. The same was done for run-ons in the CMTA and RA 9485, and for 19 Administrative Code sections lost in OCR.
- RPC Arts. 2 and 3 were corrected, and Arts. 266-A to 266-D (RA 8353) were added.

Every change appears on the provision it touches, with its basis. Use **Report a text error** on any provision. Your reports are collected under Progress.

## Hosting

The site is static, with no build step. It runs from the repository root.

**GitHub Pages**: Settings → Pages → Deploy from branch → `main` / root.

**Cloudflare Pages**, either way:
1. Dashboard: Workers & Pages → Create → Pages → Connect to Git → pick this repository. Leave the framework preset at *None* and the build command empty, and set the output directory to `/`. Every push to `main` then redeploys.
2. Or from GitHub Actions: add repository secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. `.github/workflows/cloudflare-pages.yml` then deploys on every push.

`_headers` sets security headers on Cloudflare. GitHub Pages ignores it.

### Optional AI tutor (Cloudflare only)

`functions/api/tutor.js` adds "Explain simply" and "Ask about this provision" buttons, grounded on the verbatim text of the provision on screen. To enable them, open the Cloudflare Pages project → Settings → Variables and Secrets and add:

- `ANTHROPIC_API_KEY`: your API key (encrypted)
- `TUTOR_PASSCODE`: any passphrase. The app asks for it once per device.
- `TUTOR_MODEL` (optional): defaults to `claude-sonnet-5-5`

Without these, or on GitHub Pages, the tutor stays hidden. Usage is billed to your API account.

## Progress and privacy

Progress, notes and bookmarks live in your browser's local storage. GitHub Pages and Cloudflare are different addresses, so each keeps its own copy. To move between them, use **Progress → Back up my work** on one and **Restore** on the other.

## The previous app

The encrypted Sinag Learning Studio (Edition 13) is preserved unchanged at `/legacy/`.

## Rebuilding the data

The scripts in `tools/` rebuild everything from the sources. They need the LawCodex mirror (`git clone https://github.com/LawCodex/ph`), the PDFs, `pdftotext`, `pdfplumber` and `tesseract`. The order is:

```
python3 tools/build_labor.py      # after tools/extract_labor.py
python3 tools/build_family*.py    # font decoding of the Family Code PDF
python3 tools/build_admin.py      # after OCR (tools/ocr_pages.py)
python3 tools/build_data.py site/data
python3 tools/build_cases.py      # after OCR of the textbooks (tools/ocr_book.py)
python3 tools/build_data.py site/data   # again, to register case and note files
```

To correct a word, add an entry to `tools/errata.json` (`replace`, `insert` or `note`) with its basis. Then rebuild.
