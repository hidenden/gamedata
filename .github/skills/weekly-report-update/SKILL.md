---
name: weekly-report-update
description: "Update the Japanese prose cells in gamedata's Marimo weekly report from live data and annotation context. Use when revising weekly_report.py articles; not for publishing or general notebook edits."
---

# Weekly Report Update

Update the prose in `notebook/report/weekly_report.py` while preserving the report's established editorial voice and notebook behavior.

## Live notebook

Use the `marimo-pair` skill to work with an existing live Marimo session. The user may supply its URL; otherwise, ask for the session URL. Do not start a new Marimo server unless the user explicitly requests one. If the connection must run outside the sandbox, use the provided marimo-pair connection script with the required approval.

## Editorial workflow

1. Obtain `md_summaries` from the live notebook. Treat each item's `description` as the required scope of its Markdown cell and its `calc_cells` as primary evidence.
2. Inspect the relevant calculation cells and any other notebook data needed to make the prose accurate. Update the specified Markdown cells, or all cells described by `md_summaries` when the user requests a full update.
3. Match the existing Japanese wording, level of detail, and section structure unless the user asks for a different editorial direction. Ground factual claims in the live data. Web research is allowed when background context is useful.
4. When mentioning an annotation event, use its `desc` value when it is non-empty; otherwise use the event's `note`. Append the event's `annotation_date` immediately after the event name in `(M/D)` format, for example `Nintendo Direct 2026.9.9(9/9)`. Do not invent annotation details or dates.

### Forecast consistency

When prose mentions an annual forecast based on a 52-week average, calculate it directly from the live kernel's weekly sales data. Use the sum of `units` for the 52 weeks ending on or before `report_date` (equivalently, `mean(units) * 52`), and ensure that the number in the prose matches that result.

- Do not use chart guide lines, existing prose, or manually entered forecast values as the source.
- Limit this check to prose cells that state a forecast; do not rerun or validate every chart or dataset.
- Record the 52-week window's start date, end date, and total in a concise check while drafting.
- If the previous report's forecast is available and the change is large or counterintuitive, inspect only the week leaving and the week entering the rolling window, then explain the change in prose when useful.

## Boundaries and handoff

Do not run `pub_marimo.py`, export HTML, or publish files unless the user explicitly asks. After editing, report the updated cells, the principal data points used, and any claims that need the user's editorial review.
