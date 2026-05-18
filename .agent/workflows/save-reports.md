---
description: Automatically save all financial analysis reports to the Reports folder
---

## When to Trigger

This workflow should run **automatically at the end of every conversation** that produces financial analysis artifacts. It applies when any of the following are generated:

- Model updates (e.g., `/model-update`)
- Morning notes (e.g., `/morning-note`)
- Valuation reports
- Stock screening / watchlist analysis
- Macro stress tests
- Portfolio snapshots
- Comparative analysis reports
- Any other stock/market research output

## Steps

// turbo
1. Create a date-stamped subfolder in the Reports directory:
   ```
   D:\Projects\Antigravity\Financial AI\Reports\YYYY-MM-DD\
   ```
   Use the current date. If the folder already exists, reuse it.

// turbo
2. Copy all financial analysis artifacts generated during this conversation to the date-stamped folder. Common artifact filenames include:
   - `*_model_update.md`
   - `*_valuation_models.md`
   - `morning_note_*.md`
   - `*_macro_stress_test.md`
   - `portfolio_snapshot.md`
   - `selection_vs_alternatives.md`
   - `watchlist_screening.md`
   - Any other `.md` files related to stock/financial analysis

// turbo
3. Create or update a `README.md` index file in the date-stamped folder listing all reports with descriptions.

// turbo
4. Confirm to the user that reports have been saved, listing the file count and folder path.

## Folder Structure

```
D:\Projects\Antigravity\Financial AI\Reports\
├── 2026-03-17\
│   ├── README.md
│   ├── portfolio_snapshot.md
│   ├── morning_note_portfolio.md
│   ├── beta_model_update.md
│   └── ...
├── 2026-03-18\
│   ├── README.md
│   └── ...
```

## Important Notes

- Always use the current date for the subfolder name (YYYY-MM-DD format)
- If multiple analyses happen on the same day, append to the existing folder
- Do NOT delete or overwrite previous days' reports
- The README.md should be regenerated each time to reflect the complete contents
