# Weekly report instructions

These instructions apply to work in `notebook/report/`.

- `weekly_report.py` is a Marimo notebook. Keep its cell structure and ordinary report-generation behavior intact unless the task explicitly requests structural changes.
- For article updates, use `md_summaries`: `description` defines each Markdown cell's intended content and `calc_cells` identify its primary evidence.
- Preserve the existing Japanese editorial tone and the article's existing section structure unless asked otherwise. Base quantitative claims on notebook data.
- When an annotation is mentioned, prefer a non-empty `desc`; use `note` only when `desc` is unavailable.
- Use an existing live Marimo session when one is supplied. Do not start a new server merely to update articles.
- Do not run `pub_marimo.py`, export HTML, or write publication output unless the user explicitly requests publishing.
