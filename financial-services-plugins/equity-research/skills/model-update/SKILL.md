# Model Update

description: Update financial models with new data — quarterly earnings, management guidance, macro changes, or revised assumptions. Adjusts estimates, recalculates valuation, and flags material changes. Use after earnings, guidance updates, or when assumptions need refreshing. Triggers on "update model", "plug earnings", "refresh estimates", "update numbers for [company]", "new guidance", or "revise estimates".

## Workflow

### Step 1: Identify What Changed

Determine the update trigger:
- **Earnings release**: New quarterly actuals to plug in
- **Guidance change**: Company updated forward outlook
- **Estimate revision**: Analyst changing assumptions based on new data
- **Macro update**: Interest rates, FX, commodity prices changed
- **Event-driven**: M&A, restructuring, new product, management change

### Step 2: Plug New Data

#### After Earnings
Update the model with reported actuals:

| Line Item | Prior Estimate | Actual | Delta | Notes |
|-----------|---------------|--------|-------|-------|
| Revenue | | | | |
| Gross Margin | | | | |
| Operating Expenses | | | | |
| EBITDA | | | | |
| EPS | | | | |
| [Key metric 1] | | | | |
| [Key metric 2] | | | | |

**Segment Detail** (if applicable):
- Update each segment's revenue and margin
- Note any segment mix shifts

**Balance Sheet / Cash Flow Updates**:
- Cash and debt balances
- Share count (buybacks, dilution)
- Capex actual vs. estimate
- Working capital changes

### Step 3: Revise Forward Estimates

Based on the new data, adjust forward estimates:

| | Old FY Est | New FY Est | Change | Old Next FY | New Next FY | Change |
|---|-----------|-----------|--------|------------|------------|--------|
| Revenue | | | | | | |
| EBITDA | | | | | | |
| EPS | | | | | | |

**Key Assumption Changes:**
- What assumptions are you changing and why?
- Revenue growth rate: old → new (reason)
- Margin assumption: old → new (reason)
- Any new items (restructuring charges, one-time gains, etc.)

### Step 4: Multi-Model Valuation (12 Models)

Run all applicable models and present as a unified fair value dashboard. Skip models that are not meaningful (e.g., P/E for pre-revenue companies). Always state the **average fair value** across all applicable models.

#### Category A: Relative Valuation — Peer Multiples

Use sector comparables to derive implied fair value per share.

| # | Model | Formula | Applicable When |
|---|-------|---------|-----------------|
| 1 | **EV / Revenue** | Peer avg EV/Rev × Company Rev ÷ Shares | Revenue-generating companies |
| 2 | **EV / EBIT** | Peer avg EV/EBIT × Company EBIT ÷ Shares | Profitable companies (EBIT > 0) |
| 3 | **EV / EBITDA** | Peer avg EV/EBITDA × Company EBITDA ÷ Shares | EBITDA-positive companies |
| 4 | **P/E Multiples** | Peer avg P/E × Company EPS | EPS-positive companies |
| 5 | **Price / Sales** | Peer avg P/S × Company Rev/Share | All revenue-generating companies |
| 6 | **Price / Book** | Peer avg P/B × Company Book Value/Share | Companies with meaningful book value |

#### Category B: Asset & Backlog-Based

| # | Model | Formula | Applicable When |
|---|-------|---------|-----------------|
| 7 | **Net Asset Value (NAV)** | (Cash + PP&E + IP - Debt) ÷ Shares | All — establishes absolute floor |
| 8 | **Cash + Backlog** | (Cash + probability-weighted backlog) ÷ Shares | Companies with order backlogs |

#### Category C: DCF Models

| # | Model | Key Assumptions | Applicable When |
|---|-------|-----------------|-----------------|
| 9 | **5Y DCF Revenue Exit** | Revenue CAGR, terminal EV/Rev multiple, WACC | All |
| 10 | **5Y DCF EBITDA Exit** | Rev CAGR, target EBITDA margin, terminal EV/EBITDA, WACC | Near-profitability companies |
| 11 | **5Y DCF Growth Exit** | Aggressive rev CAGR (bull case), lower terminal multiple | High-growth companies |
| 12 | **10Y DCF EBITDA Exit** | Longer horizon, profitability by year 5+, EBITDA margin at maturity | Pre-revenue / early-stage |

#### Output Format

Present results as a visual dashboard:

```
Fair Value Summary: $XX.XX (N models)

Model                       Fair Value    vs. Current
──────────────────────────  ──────────    ───────────
EV / Revenue (Peer Avg)       $XX.XX        +XX%
EV / EBITDA (Peer Avg)        $XX.XX        +XX%
P/E Multiples                 $XX.XX        +XX%
Price / Sales                 $XX.XX        +XX%
Price / Book                  $XX.XX        +XX%
Net Asset Value               $XX.XX        +XX%
5Y DCF Revenue Exit           $XX.XX        +XX%
5Y DCF EBITDA Exit            $XX.XX        +XX%
10Y DCF EBITDA Exit           $XX.XX        +XX%
...
```

Include a visual bar chart showing the range from lowest to highest model estimate, with current price marked.

#### Company Archetype Guide

Select the right models based on company type:

**🟢 Mature Profitable** (e.g., AMZN, GOOG, NFLX, INFY)
- Use **all 6 relative models** (A1–A6) — full financial statements available
- Use **NAV** (B7) for absolute floor
- Primary DCF: **5Y DCF EBITDA Exit** (C10)
- Most reliable models: **P/E** and **EV/EBITDA**
- Peers: Select 3–5 direct competitors in same sector and size bracket
- WACC: **8–10%**

**🟡 High-Growth Pre-Profit** (e.g., IONQ)
- Use: EV/Revenue (A2), Price/Sales (A4), Price/Book (A6)
- Skip: P/E (A5), EV/EBIT (A1), EV/EBITDA (A3) — mark "N/A — negative earnings"
- Use: NAV (B7), 5Y DCF Revenue Exit (C9), 5Y DCF Growth Exit (C11)
- Most reliable models: **EV/Revenue** and **DCF Revenue Exit**
- Peers: Match by revenue scale + growth rate, not just sector
- WACC: **12–15%** (higher risk premium)

**🔴 Pre-Revenue** (e.g., BETA, ACHR, JOBY)
- Use: Price/Book (A6), NAV (B7), Cash + Backlog (B8)
- Use: All DCF models (C9–C12) — prefer **10Y horizon**
- Skip: All earnings-based models (A1, A3, A5) — mark "N/A — pre-revenue"
- Add: Comparable peer EV/Revenue using 2–3 named sector peers
- Most reliable models: **NAV** (floor) and **10Y DCF** (ceiling)
- Peers: Name specific eVTOL/sector comps (e.g., JOBY, ACHR, EVE for eVTOL)
- WACC: **12–18%** (highest risk)
- **Always state**: "All models above NAV carry execution risk"

**🟣 Binary-Outcome Biotech** (e.g., NTLA)
- Use: Price/Book (A6), NAV (B7), EV/Revenue if any (A2)
- Add: **Pipeline NPV** — sum risk-adjusted NPVs per drug candidate
- Apply **probability of approval** (Phase 3: ~50–60%, Phase 2: ~30%)
- Skip: P/E, EV/EBITDA — mark "N/A — clinical stage"
- Most reliable models: **Risk-adjusted DCF** and **Pipeline NPV**
- Peers: Match by therapeutic area and pipeline stage
- **Flag**: "Binary catalyst ahead — valuation swings ±50% on trial outcome"

#### Analyst Consensus Cross-Check

Always compare your multi-model average to the Street consensus:

| Source | Price Target | Rating |
|--------|-------------|--------|
| Analyst 1 (Firm) | $XX | Buy/Hold/Sell |
| Analyst 2 (Firm) | $XX | Buy/Hold/Sell |
| **Consensus Avg** | **$XX** | |
| **Your Multi-Model Avg** | **$XX** | |

Note: If your estimate diverges >20% from consensus, explain why.

### Step 5: Summary & Action

**Estimate Change Summary:**
- One paragraph: what changed, why, and what it means for the stock
- Is this a thesis-changing event or noise?

**Rating / Price Target:**
- Maintain or change rating?
- New price target (if changed) with methodology
- Upside/downside to current price

### Step 6: Output

- Updated Excel model (if user provides the existing model)
- Estimate change summary (markdown or Word)
- Updated price target derivation

## Important Notes

- Always reconcile your estimates to the company's reported figures before projecting forward
- Note any non-recurring items and whether your estimates are GAAP or adjusted
- Track your estimate revision history — it shows your analytical progression
- If the quarter was noisy, separate signal from noise in your estimate changes
- Check consensus after updating — how do your revised estimates compare to the Street?
- Share count matters — dilution from stock comp, converts, or buybacks can materially affect EPS
