# Excel Finance Automation

> Production-ready Excel VBA utilities designed to automate repetitive corporate reporting tasks, enforce consistent financial formatting, and improve FP&A / accounting workflow efficiency.

![Domain](https://img.shields.io/badge/Domain-Corporate%20Finance%20%7C%20FP%26A-blue)
![Technology](https://img.shields.io/badge/Platform-Microsoft%20Excel%20VBA-success)
![Author](https://img.shields.io/badge/Author-Chartered%20Accountant-brightgreen)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## Executive Summary

Finance professionals, auditors, and FP&A analysts often spend hours manually formatting workbooks, aligning columns, adjusting border styles, and standardizing numerical scales before sharing reports with leadership or clients.

This repository provides **practical, plug-and-play Excel VBA tools** built to eliminate manual cosmetic work and ensure institutional presentation standards across multi-sheet workbooks in a single click.

---

## At a Glance

| Aspect | Detail |
|:---|:---|
| **Primary Domain** | Financial Reporting, FP&A, Audit Working Papers & MIS |
| **Tool Included** | **Workbook Beautification Engine** |
| **Delivery Formats** | VBA Module (`.bas`) & Macro-Enabled Template (`.xlsm`) |
| **Core Capabilities** | Dynamic range detection, AutoFit, soft-border styling, header formatting, auto-detection of percentages vs. currency numbers |
| **Execution Speed** | Sub-second optimization using disabled screen updates & manual calculation toggles |

---

## Repository Structure

```text
Excel-Finance-Automation
│
├── README.md
│     Project summary, business value, and quick start guide
│
├── Project/
│     Background, design rationale, and reporting objectives
│
└── Tools/
      └── Workbook Beautification/
            ├── BeautifyWorkbook.bas       (VBA source code module)
            ├── WorkbookBeautification.xlsm (Pre-configured macro template)
            ├── Before-Formatting.png     (Raw unformatted data preview)
            ├── After-Formatting.png      (Clean, formatted output preview)
            └── readme.md                 (Technical documentation & usage steps)
```

---

## Featured Tool: Workbook Beautification Engine

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

---

## Quick Start / How to Use

### Method 1: Using the Pre-Configured Workbook (`.xlsm`)
1. Download or open [`WorkbookBeautification.xlsm`](Tools/Workbook%20Beautification/WorkbookBeautification.xlsm).
2. Paste or import your financial data into the sheets.
3. Press **Alt + F8**, select `BeautifyWorkbook`, and click **Run**.

### Method 2: Importing into Your Existing Financial Model (`.bas`)
1. Open your target Excel workbook.
2. Press **Alt + F11** to open the VBA Editor.
3. Click **File > Import File...** and select [`BeautifyWorkbook.bas`](Tools/Workbook%20Beautification/BeautifyWorkbook.bas).
4. Run `BeautifyWorkbook` anytime from Excel's Macro menu (**Alt + F8**).

---

## Resume / CV Application

This project demonstrates practical finance transformation and workflow optimization:
- **Time Savings:** Reduces report preparation turnaround from 15–20 minutes per complex pack to 1 second.
- **Quality Control:** Ensures 100% aesthetic consistency across multi-tab executive deliverables and audit schedules.
- **Process Automation:** Shows hands-on capability in automating accounting processes directly within standard enterprise software.

---

## Author

Chartered Accountant specializing in financial analysis, corporate finance, FP&A workflows, and practical finance automation.
