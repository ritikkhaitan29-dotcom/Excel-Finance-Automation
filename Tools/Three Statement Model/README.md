# Integrated Three-Statement FP&A Financial Model

> **Project status: Demonstration / proof of concept**  
> This project demonstrates an interactive three-statement FP&A modelling workflow using synthetic, illustrative data. It showcases financial modelling logic, integrated financial statements, configurable assumptions, and automated validation. It is not a production-ready corporate planning system, an audited financial model, or a representation of any employer''s actual financial information. The assumptions, calculations, interface, controls, and reporting requirements may need to be added to, modified, or replaced based on actual business usage, company-specific policies, applicable accounting standards, and user feedback.

---

## 1. Overview & Objective

In corporate financial planning and analysis (FP&A), financial modeling often suffers from disconnected spreadsheets, broken formula linkages, and lack of dynamic balance between the Income Statement, Balance Sheet, and Cash Flow Statement.

This application provides a **modular, Python-based financial modeling engine** paired with an interactive **Streamlit dashboard**. It models a multi-product manufacturing business across a 7-period timeline:
- **F26A**: Synthetic baseline period.
- **F27E**: Illustrative estimate / near-term forecast period.
- **F28P – F32P**: Five-year strategic planning projections.

The model enforces mathematical balance-sheet equilibrium, indirect-method cash flow reconciliation, and dynamic liquidity management.

---

## 2. Implemented Features

The application implements the following core modeling capabilities:

- **Interactive Assumption Drivers**: Live configuration via interactive controls in the Model Assumptions Manager for product volume growth rates, average selling prices (ASP), raw material and operating cost inflation, working capital turnover days, capital expenditure, and debt parameters.
- **Operating Forecast**: Dynamic volume-price drivers for Product A and Product B, scaling raw material costs, other variable expenses, and fixed plant SG&A.
- **Schedule III-Style Income Statement**: Multi-step P&L from EBITDA down through Depreciation, PBIT, Finance Costs, PBT, and Effective Corporate Tax to Profit After Tax (PAT).
- **Fixed Asset Register & Lagged Depreciation**: Categorized asset register (Plant & Machinery at 5% salvage, Factory Buildings at 5% salvage, Utilities & Heavy Equipment at 2% salvage). Year-end capex additions convention incurs zero depreciation in the year of purchase; straight-line depreciation begins in the subsequent financial year.
- **Working Capital Cycle**: Dynamic Trade Receivables (DSO), Inventory (DIO), and Trade Payables (DPO) schedules directly driving operating cash flow.
- **Senior Debt Amortisation & CMLTD**: Structured long-term debt repayment schedules with automatic carve-out of Current Maturities of Long-Term Debt (CMLTD) into current liabilities.
- **Short-Term Debt & Liquidity Sweep**: Automatic cash waterfall enforcing a minimum operating cash balance (INR 5.0 Cr default). Cash shortfalls trigger short-term debt borrowing (unconstrained by an artificial facility limit); cash surpluses prepay short-term debt and sweep into liquid investments (which hold cash equivalents without interest yield).
- **Sequential Interest Coupling**: Interest expense computed strictly on beginning-of-period debt balances, ensuring sequential traceability and eliminating circular calculation references.
- **Tax, Dividends & Retained Earnings**: Configurable dividend payout ratio (default 0.0%), where actual dividends are constrained by distributable cash above the minimum cash requirement, backed by a complete retained earnings roll-forward.
- **Automated Model Checks**: Built-in verification testing balance sheet equilibrium (Total Assets = Total Liabilities + Equity with variance < 1e-6 INR) and cash flow reconciliation across all seven periods.

---

## 3. Technology Stack

- **Core Engine**: Python (tested on Python 3.14.7; standard dataclasses, modular calculation engine)
- **Data Manipulation**: pandas, 
umpy
- **Dashboard Interface**: streamlit
- **Visualisations**: plotly (interactive waterfall and balance sheet composition charts)
- **Spreadsheet Generation**: openpyxl (available for review pack generation)
- **Testing Framework**: pytest (19 automated unit and integration tests)

*(Note: Dependencies are listed in 
equirements.txt as unpinned package names).*

---

## 4. Project Architecture

`	ext
Tools/Three Statement Model/
├── README.md                           # Tool documentation, usage instructions & verification
├── app.py                              # Streamlit dashboard interface & assumption controls
├── requirements.txt                    # Unpinned Python runtime and test dependencies
├── docs/
│   └── financial-methodology.md        # Technical calculation manual & accounting boundaries
├── model/                              # Core financial modeling engine package
│   ├── __init__.py                     # Package exports
│   ├── assumptions.py                  # Strongly typed assumptions dataclasses & defaults
│   ├── periods.py                      # 7-period timeline & classification metadata
│   ├── operating_forecast.py           # Volume, ASP, revenue, COGS & EBITDA schedules
│   ├── working_capital.py              # Working capital schedule & operating cash impact
│   ├── depreciation_and_debt.py        # Depreciation schedule, senior debt amortisation & CMLTD
│   ├── income_statement.py             # Multi-step Income Statement generation
│   ├── balance_sheet_and_cfs.py        # Indirect CFS, cash sweep & Balance Sheet generation
│   ├── schedule_iii.py                 # Schedule III-style financial statement mapping
│   └── engine.py                       # Integration orchestrator & automated balance checks
├── outputs/                            # Illustrative financial review pack deliverables
│   ├── financial_review_pack.xlsx      # 10-sheet consolidated financial review workbook
│   └── financial_review_summary.md     # Baseline financial summary & metrics report
└── tests/
    └── test_model_integration.py       # 19 automated integration and regression tests
`

---

## 5. Installation & Quick Start

### Prerequisites
- Python 3.14.7 (or compatible Python 3 environment) installed on Windows, macOS, or Linux.
- Git (optional, for cloning).

### Step-by-Step Setup (Windows / PowerShell)

1. **Navigate to the tool directory**:
   `powershell
   cd  Tools/Three Statement Model
   `

2. **Create and activate a virtual environment**:
   `powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   `

3. **Install dependencies**:
   `powershell
   pip install -r requirements.txt
   `

4. **Run the automated test suite**:
   `powershell
   python -m pytest -v
   `
   *(All 19 tests must pass).*

5. **Launch the interactive Streamlit application**:
   `powershell
   streamlit run app.py
   `
   The application will open in your default browser at http://localhost:8501.

---

## 6. Financial Methodology

For a complete breakdown of mathematical formulas, accounting conventions, roll-forward proofs, and debt coupling mechanics, see the companion document:
- [Financial Modeling Methodology & Calculation Manual](docs/financial-methodology.md)

---

## 7. Model Validation & Automated Tests

The model includes 19 automated regression and integration tests (	ests/test_model_integration.py) covering key calculations, integrations, and regression cases:
1. **7-Period Timeline & Labels**: Verifies F26A through F32P reporting classifications.
2. **Balance Sheet Equilibrium**: Tests Total Assets == Total Liabilities + Equity across all periods.
3. **Cash Flow Reconciliation**: Verifies Closing Cash == Opening Cash + Net Cash Flow.
4. **Retained Earnings Roll-Forward**: Verifies Ending RE == Beginning RE + PAT - Dividends.
5. **Statement Linkages**: Confirms EBITDA, PAT, Gross PPE, and Debt flow between statements.
6. **Schedule III-Style Presentation**: Validates presentation line items for Balance Sheet, P&L, and CFS.
7. **Assumption Propagation**: Tests that edits to volumes, prices, capex, or costs propagate downstream.
8. **Capex Timing & Lagged Depreciation**: Validates that F26A receives zero capex, additions incur zero depreciation in the addition year, and depreciation begins in year t+1.
9. **Debt Amortisation & CMLTD**: Verifies principal repayment schedules and balance sheet reclassification.
10. **Indirect Cash Flow Presentation**: Confirms gross interest presentation and operating adjustments.
11. **Short-Term Debt & Liquidity Sweep**: Tests revolver drawdowns during cash deficits and sweeps during surpluses.
12. **Dividend Liquidity Caps**: Validates that dividends are restricted when cash approaches minimum buffers.
13. **Interest Coupling**: Confirms beginning-of-period debt balances dictate interest without circularity.

---

## 8. Known Limitations & Accounting Boundaries

This demonstration model focuses on core three-statement operational dynamics. The following enterprise treatments are not currently included:
- **No Ind AS 116 Lease Accounting**: Operating leases are not capitalized into Right-of-Use (ROU) assets or lease liabilities.
- **No Deferred Tax Accounting (Ind AS 12)**: Deferred tax assets and liabilities are not modeled.
- **No Actuarial Employee Obligations (Ind AS 19)**: Retirement benefits and gratuity provisions are omitted.
- **Nominal Debt Terms (Ind AS 109)**: Debt is modeled on nominal contractual terms without effective interest rate (EIR) fee amortization.
- **Statutory Disclosures**: The Schedule III-style views follow standard headings for analytical clarity but do not constitute formal statutory audit disclosures or full accounting compliance certifications.

---

## 9. Proposed Roadmap (Future Enhancements)

The following extensions are proposed concepts, not currently implemented features:
- [ ] **Multi-Scenario Comparison View**: Side-by-side comparative views of Base, Bull, and Bear cases in the Streamlit UI.
- [ ] **Sensitivity Heatmaps**: Two-way interactive sensitivity grids for EBITDA margins vs. volume growth.
- [ ] **Dynamic Debt Covenants**: Real-time alerts for DSCR (Debt Service Coverage Ratio) and Interest Coverage thresholds.
- [ ] **Discounted Cash Flow (DCF) Module**: Integrated enterprise valuation, WACC calculation, and sensitivity tables.
- [ ] **Exportable Review Workbook**: Dedicated UI download button for generating refreshed Excel packs directly from live web session states.

---

## 10. Feedback & Contributions

Feedback, edge-case test proposals, and feature requests are welcome. Please open an issue or pull request in the repository. Note that any proposed formula or accounting modifications must maintain balance-sheet equilibrium and pass all 19 integration tests before merging.