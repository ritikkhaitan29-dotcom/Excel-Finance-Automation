# Excel Finance Automation & Financial Modeling Portfolio

> Practical corporate finance automation tools, financial modeling engines, and workflow optimization utilities developed by a Chartered Accountant.

![Domain](https://img.shields.io/badge/Domain-Corporate%20Finance%20%7C%20FP%26A-blue)
![Technology](https://img.shields.io/badge/Platform-Python%20%7C%20Excel%20VBA-success)
![Author](https://img.shields.io/badge/Author-Chartered%20Accountant-brightgreen)
![Status](https://img.shields.io/badge/Status-Portfolio-brightgreen)

---

## Executive Summary

Finance professionals, auditors, and FP&A analysts frequently navigate two operational challenges:
1. **Cosmetic Reporting Bottlenecks:** Expending repetitive hours manually formatting multi-tab review packs, standardizing borders, aligning headers, and tuning decimal layouts in Microsoft Excel.
2. **Financial Modeling Fragmentation:** Managing complex multi-period financial projections across disconnected spreadsheets where formula breaks, circularity, and broken statement linkages obscure operational insights.

This repository provides **practical, modular finance automation tools** designed to solve both challenges:
- **Workbook Beautification Engine:** A production-ready, one-click Excel VBA utility enforcing institutional formatting across multi-tab workbooks without altering formulas.
- **Three-Statement FP&A Financial Model:** An interactive Python and Streamlit modeling engine demonstrating dynamic operating drivers, lagged capex depreciation, liquidity sweeps, Schedule III-style financial statements, and automated balance-sheet equilibrium and cash-flow reconciliation checks.

---

## Tools Portfolio Index

```text
Excel-Finance-Automation/
├── README.md                           # Portfolio overview, tool directory & quick links
├── LICENSE                             # MIT License
├── Project/                            # Background & business rationale for Excel automation
│   └── readme.md
└── Tools/                              # Modular directory of independent finance tools
    ├── readme.md                       # Comprehensive tools catalog and engineering standards
    ├── Three Statement Model/          # Python/Streamlit 3-Statement FP&A Model (Interactive Demo)
    │   ├── README.md
    │   ├── app.py
    │   ├── requirements.txt
    │   ├── docs/financial-methodology.md
    │   ├── model/
    │   ├── outputs/
    │   └── tests/
    └── Workbook Beautification/        # Enterprise Excel VBA Multi-Tab Formatting Utility
        ├── BeautifyWorkbook.bas
        ├── WorkbookBeautification.xlsm
        ├── Before-Formatting.png
        ├── After-Formatting.png
        └── readme.md
```

---

## Available Tools

| Tool | Domain & Technology | Status | Key Deliverable | Documentation |
| :--- | :--- | :--- | :--- | :--- |
| **[Workbook Beautification](Tools/Workbook%20Beautification/)** | **Excel VBA (`.bas` / `.xlsm`)**<br>Institutional Multi-Tab Formatting Utility | Production Ready | One-click aesthetic standardization across multi-tab financial packs, working papers, and management MIS reports with zero formula disruption. | [View Tool Manual](Tools/Workbook%20Beautification/readme.md) |
| **[Three Statement Model](Tools/Three%20Statement%20Model/)** | **Python (tested on 3.14.7) / Streamlit / Pandas / Plotly**<br>Integrated FP&A Financial Modeling Engine | Demonstration / Proof of Concept | Dynamic 7-period financial forecast (F26A synthetic baseline, F27E illustrative estimate, F28P–F32P projections), editable operating drivers and assumption-driven forecasts, lagged capex depreciation, liquidity sweeps, Schedule III-style financial statements, and automated balance-sheet equilibrium and cash-flow reconciliation checks. | [View Model Manual](Tools/Three%20Statement%20Model/README.md) |

---

## Tool 1: Workbook Beautification Engine (Excel VBA)

The **Workbook Beautification** macro standardizes every populated worksheet in an active workbook without affecting raw data formulas.

### Visual Comparison

| Before Formatting | After Formatting |
|:---:|:---:|
| Raw, misaligned numbers, inconsistent column widths, no headers | Auto-fitted columns, soft grey borders, bold centered headers, clean comma-separated decimals |
| ![Before](Tools/Workbook%20Beautification/Before-Formatting.png) | ![After](Tools/Workbook%20Beautification/After-Formatting.png) |

### Key Features
- **Dynamic Range Detection:** Automatically locates the exact populated boundaries of each worksheet using `Cells.Find`—safely bypassing empty sheets.
- **Smart Number Formatting:** Distinguishes between percentage fields (`0.00%`) and standard financial metrics (`#,##0.00`), while preserving date cells.
- **Institutional Visual Standards:** Replaces harsh black gridlines with subtle grey borders (`RGB(200, 200, 200)`) and formats header rows with light-grey fills (`RGB(217, 217, 217)`).
- **Execution Performance:** Suspends screen updating, alerts, and automatic calculation during execution for instant results across large workbooks.

### How to Use

#### Method 1: Using the Pre-Configured Workbook (`.xlsm`)
1. Download or open [`WorkbookBeautification.xlsm`](Tools/Workbook%20Beautification/WorkbookBeautification.xlsm).
2. Paste or import your financial data into the sheets.
3. Press **Alt + F8**, select `BeautifyWorkbook`, and click **Run**.

#### Method 2: Importing into Your Existing Financial Model (`.bas`)
1. Open your target Excel workbook.
2. Press **Alt + F11** to open the VBA Editor.
3. Click **File > Import File...** and select [`BeautifyWorkbook.bas`](Tools/Workbook%20Beautification/BeautifyWorkbook.bas).
4. Run `BeautifyWorkbook` anytime from Excel's Macro menu (**Alt + F8**).

---

## Tool 2: Integrated Three-Statement FP&A Model (Python & Streamlit)

> **Project status: Demonstration / proof of concept**
> This project demonstrates an interactive three-statement FP&A modelling workflow using synthetic, illustrative data. It showcases financial modelling logic, integrated financial statements, configurable assumptions, and automated validation. It is not a production-ready corporate planning system, an audited financial model, or a representation of any employer's actual financial information. The assumptions, calculations, interface, controls, and reporting requirements may need to be added to, modified, or replaced based on actual business usage, company-specific policies, applicable accounting standards, and user feedback.

### Key Capabilities
- **Integrated Three Statements**: Dynamically links the Income Statement, Balance Sheet, and Cash Flow Statement (Indirect Method) across seven reporting periods (F26A synthetic baseline, F27E illustrative estimate, F28P–F32P projections).
- **Non-Circulating Interest Engine**: Uses sequential beginning-of-period debt balances to calculate interest without circular references.
- **Lagged Depreciation**: Year-end capital expenditure additions convention; new additions incur zero depreciation in the year of purchase, with straight-line depreciation beginning in the following financial year.
- **Dynamic Liquidity Management**: Automatic cash waterfall enforcing a minimum operating cash balance (INR 5.0 Cr default), drawing short-term debt upon cash shortfalls and sweeping surplus cash into liquid investments.
- **Automated Verification**: Built-in test suite (19 automated tests) verifying mathematical balance sheet equilibrium (variance < 1e-6 INR) and cash reconciliation.

### Quick Start
```powershell
cd "Tools/Three Statement Model"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -v
streamlit run app.py
```
- For technical details and accounting conventions, see the [Three Statement Model README](Tools/Three%20Statement%20Model/README.md) and [Financial Methodology Manual](Tools/Three%20Statement%20Model/docs/financial-methodology.md).

---

## Portfolio Standards & Engineering Principles

- **Accounting Integrity First**: Calculations mirror financial modeling discipline; balance sheet equilibrium and cash reconciliation are programmatically tested without claiming to constitute an audit.
- **Deterministic & Verifiable**: Financial logic is explicitly documented, unit-tested, and reproducible without hidden dependencies.
- **Synthetic & Safe**: All scenarios, business models, and datasets are strictly illustrative and synthetic. No proprietary or confidential corporate data is utilized.
- **Modular Expansion**: Each tool added to `Tools/` operates independently with dedicated documentation, test cases, and dependency definitions.

---

## License

This repository is distributed under the [MIT License](LICENSE).

---

## Author & Contact

**Chartered Accountant** specializing in corporate financial analysis, financial modeling, FP&A transformation, and practical finance automation.
