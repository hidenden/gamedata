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
4. When mentioning an annotation event, use its `desc` value when it is non-empty; otherwise use the event's `note`. Do not invent annotation details.

## Boundaries and handoff

Do not run `pub_marimo.py`, export HTML, or publish files unless the user explicitly asks. After editing, report the updated cells, the principal data points used, and any claims that need the user's editorial review.
