# Finance Automation Tools Portfolio

This directory serves as the catalog and architectural index for the corporate finance automation tools, financial modeling engines, and Excel productivity utilities included in this portfolio.

Each tool is designed as an independent, modular solution addressing core enterprise reporting, modeling consistency, and workflow efficiency challenges.

---

## Available Tools

| Tool | Status | Technology Stack | Primary Corporate Finance Use Case | Documentation |
| :--- | :--- | :--- | :--- | :--- |
| **[Three Statement Model](Three%20Statement%20Model/)** | Demonstration / Proof of Concept | Python (tested on 3.14.7) / Streamlit / Pandas / Plotly | Interactive 7-period three-statement FP&A engine with dynamic operating drivers, lagged capex depreciation, liquidity sweeps, Schedule III-style presentation, and automated balance-sheet equilibrium and cash-flow reconciliation checks. | [View Manual](Three%20Statement%20Model/README.md) |
| **[Workbook Beautification](Workbook%20Beautification/)** | Production Ready | Excel VBA (.bas / .xlsm) | Instant presentation standardization across multi-tab financial packs, working papers, and management MIS reports. | [View Manual](Workbook%20Beautification/readme.md) |

---

## Detailed Tool Summaries

### 1. [Three Statement FP&A Model](Three%20Statement%20Model/)
- **Inputs**: Configurable product volumes, average selling prices, raw material & variable cost inflation, working capital turnover days (DSO, DIO, DPO), annual capital expenditures, debt facility parameters, and dividend payout policies.
- **Outputs**: Fully integrated Income Statement, Balance Sheet, and Cash Flow Statement (Indirect Method) across 7 periods (F26A synthetic baseline, F27E illustrative estimate, F28P–F32P projections), Schedule III-style presentation, automated integrity metrics (balance check variance < 1e-6 INR), interactive Streamlit dashboard, and an illustrative 10-sheet Excel financial review pack.
- **Target Audience**: Corporate FP&A teams, financial modelers, investment analysts, and corporate finance recruiters.

### 2. [Workbook Beautification Engine](Workbook%20Beautification/)
- **Inputs**: Raw, unformatted multi-tab Excel workbooks containing financial schedules, trial balances, or management reports.
- **Outputs**: Uniform presentation featuring subtle borders (RGB(200, 200, 200)), soft-grey headers (RGB(217, 217, 217)), dynamic AutoFit layouts, and intelligent detection of currency vs. percentage numbers without altering formulas.
- **Target Audience**: Financial reporting analysts, controllers, and auditors preparing executive board decks and working papers.

---

## Standards for Future Tools

New tools added to this repository should adhere to the following portfolio conventions:
1. **Dedicated Directory**: Each tool must reside within its own subdirectory under Tools/ (e.g., Tools/<Tool Name>/).
2. **Independent Documentation**: Every tool directory must contain a standalone README.md documenting its overview, status, technology stack, architecture, step-by-step setup, and known limitations.
3. **Explicit Demonstration Status**: If a tool uses synthetic or illustrative data, it must clearly display a demo/proof-of-concept disclaimer distinguishing it from production corporate systems.
4. **Reproducibility & Zero Machine Coupling**: Dependencies must be declared (equirements.txt, VBA modules, etc.), and file paths must remain relative and portable across platforms.
5. **No Confidential Data**: All sample datasets and workbooks must use synthetic data with no client, employer, or proprietary operational details.