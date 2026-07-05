# Workbook Beautification

## Overview

The Workbook Beautification tool is an Excel VBA macro designed to automatically apply a consistent formatting standard across every worksheet in an Excel workbook.

Instead of manually formatting individual sheets, the macro processes the workbook in a single run by adjusting layout, applying borders, formatting headers and standardising numeric formats.

The objective is to improve readability while reducing the repetitive effort involved in preparing workbooks for reporting or review.

---

## Problem Statement

Financial workbooks often contain multiple worksheets that require consistent formatting before they can be shared with management, clients or other stakeholders.

Formatting each worksheet manually is repetitive, time-consuming and prone to inconsistencies.

This macro automates those repetitive formatting tasks to produce a cleaner and more uniform workbook.

---

## What the Macro Does

For every populated worksheet in the active workbook, the macro:

- Automatically adjusts row heights and column widths using AutoFit.
- Applies thin light-grey borders to the used range.
- Formats the first row as a header with:
  - Bold text
  - Light grey background
  - Horizontal centre alignment
  - Vertical centre alignment
- Detects percentage values and formats them as **0.00%**.
- Formats other numeric values using the **#,##0.00** number format.
- Skips empty worksheets automatically.

---
## Workflow

1. Open the workbook to be formatted.
2. Run the `BeautifyWorkbook` macro.
3. The macro processes every populated worksheet.
4. Formatting is applied automatically.
5. A confirmation message is displayed when processing is complete.

---

## Typical Use Cases

- Financial statements
- MIS reports
- Budget and forecast workbooks
- Internal management reports
- Client deliverables
- Working papers

---

## Requirements

- Microsoft Excel
- Macros enabled
- Workbook must contain at least one populated worksheet

---

## Benefits

- Eliminates repetitive formatting tasks.
- Creates a consistent appearance across worksheets.
- Improves workbook readability.
- Reduces manual effort before sharing reports.
- Standardises numeric presentation.

---

## Technical Notes

- Written in Microsoft Excel VBA.
- Operates on the active workbook.
- Automatically ignores empty worksheets.
- Formats only the populated range of each worksheet.
- Preserves date values while formatting numeric cells.
- Restores Excel application settings after execution.
- Displays a completion message after successful processing.

---

## Current Status

**Status:** Completed

Future enhancements may include configurable formatting templates, custom themes, font selection, freeze panes and additional report styling options.

---

## Screenshots

Screenshots demonstrating the workbook before and after formatting will be added here.
