# Financial Modeling Methodology & Calculation Manual

## 1. Scope & Demonstration Notice

> **Project status: Demonstration / proof of concept**  
> This financial model demonstrates an interactive multi-period three-statement financial modeling workflow using synthetic, illustrative data. It showcases dynamic driver-based forecasting, senior debt amortisation, beginning-debt interest coupling, liquidity sweep mechanics, lagged capital expenditure depreciation, Schedule III-style financial statement presentation, and automated balance-sheet equilibrium and cash-flow reconciliation checks. It is not an audited production planning model or a representation of any employer''s confidential operational data.

---

## 2. Model Timeline & Period Conventions

The model covers **seven chronological annual reporting periods**:
- **F26A (Index 0)**: Synthetic baseline representing the historical base period of the enterprise.
- **F27E (Index 1)**: Illustrative estimate / near-term forecast period.
- **F28P through F32P (Indices 2–6)**: Long-range financial projection periods.

All periods follow a sequential roll-forward logic where each period inherits the balance sheet ending balances of the preceding period.

---

## 3. Operating Forecast & Revenue Drivers

### A. Volume & Revenue Mechanics
Revenue is driven bottom-up by two distinct product lines:
- **Product A**: Base volume x annual volume growth rate x Average Selling Price (ASP).
- **Product B**: Base volume x annual volume growth rate x ASP.

`	ext
Product Volume(t) = Product Volume(t-1) * (1 + Volume Growth Rate(t))
Product ASP(t) = Product ASP(t-1) * (1 + Selling Price Inflation(t))
Total Revenue(t) = Sum of (Volume(i, t) * ASP(i, t))
`

### B. Cost of Goods Sold (COGS) & Variable Operating Costs
Variable operating expenses are modeled as configured percentages of total revenue, escalated by price and expense inflation indices:
- **Raw Material Costs**: Modeled via a baseline raw material percentage of revenue (52.0% default), subject to annual raw material inflation (4.0% default).
- **Other Variable Costs (OVC)**: Modeled via a baseline other variable cost percentage of revenue (9.0% default), subject to annual variable cost inflation (3.5% default).

*(Note: The model uses aggregate revenue-percentage and inflation indices. It does not model granular physical consumption metrics such as per-tonne power kWh, fuel liters, or freight ton-kilometer rates).*

### C. Fixed Operating Expenses & EBITDA
- **Fixed Operating Costs**: Baseline fixed operational and SG&A expenses (INR 12.0 Cr default), escalating annually by the general fixed-cost inflation rate (5.0% default).
- **EBITDA**: Gross Operating Revenue minus Raw Material Costs, Other Variable Costs, and Fixed Operating Overheads.

`	ext
EBITDA(t) = Revenue(t) - Raw Material Costs(t) - Other Variable Costs(t) - Fixed Operating Costs(t)
`

---

## 4. Working Capital Schedules

Working capital operates on standard turnover days against annual operating line items (using a 365-day convention):

1. **Trade Receivables (Debtors)**:
   `	ext
   Trade Receivables(t) = (Revenue(t) / 365) * DSO
   `
2. **Raw Material & Finished Goods Inventory**:
   `	ext
   Inventory(t) = (Raw Material Costs(t) / 365) * DIO
   `
3. **Trade Payables (Creditors)**:
   `	ext
   Trade Payables(t) = (Raw Material Costs(t) / 365) * DPO
   `
4. **Working Capital Cash Impact**:
   Operating cash generation reflects the balance sheet delta:
   `	ext
   Delta NWC(t) = (Delta Trade Receivables(t) + Delta Inventory(t)) - Delta Trade Payables(t)
   `
   An increase in current assets consumes operating cash; an increase in trade payables provides non-interest-bearing operating cash.

---

## 5. Fixed Assets, Capex Timing & Lagged Depreciation

### A. Asset Register & Existing Depreciation
Baseline fixed assets are categorized into:
- **Plant & Machinery**: 15-year straight-line depreciation, 5.0% salvage value.
- **Factory Buildings**: 30-year straight-line depreciation, 5.0% salvage value.
- **Utilities & Heavy Equipment**: 10-year straight-line depreciation, 2.0% salvage value.

### B. Capex Timing & Lagged Depreciation Mechanics
- **F26A Synthetic Baseline**: Receives strictly zero forecast capex additions (INR 0.0).
- **F27E–F32P Forecast Capex**: Configured annual capex is capitalized at period year-end.
- **Year-End Capitalization Convention**: Because additions occur at the close of the financial year, **new capex additions incur 0.0 depreciation during the year of purchase**.
- **Lagged Depreciation**: Depreciation on new capex additions commences in the immediately following period (t+1) over the configured capex useful life (15 years default, 5.0% salvage value).

### C. PPE Roll-Forward Reconciliation
For every period t:
`	ext
Ending Gross PPE(t) = Beginning Gross PPE(t) + Capex(t)
Ending Accum Depreciation(t) = Beginning Accum Depreciation(t) + Depreciation(t)
Ending Net PPE(t) = Ending Gross PPE(t) - Ending Accum Depreciation(t)
Ending Net PPE(t) = Beginning Net PPE(t) + Capex(t) - Depreciation(t)
`

---

## 6. Debt Amortization, Interest & Liquidity Sweep

### A. Senior Long-Term Debt Amortization
- Initial long-term debt balance is amortized in equal annual principal tranches over the configured repayment tenure (5 years default).
- Principal repayments begin in F27E (Year 2) and amortize down to zero.
- **Current Maturities of Long-Term Debt (CMLTD)**: The principal due in period t+1 is carved out of non-current liabilities and classified as a Current Liability on the Balance Sheet.

### B. Interest Expense Timing Convention
- **Long-Term Debt Interest**: Calculated on the beginning-of-period outstanding balance:
  `	ext
  LT Interest(t) = Beginning LT Debt(t) * Annual Interest Rate
  `
- **Short-Term Debt Interest**: Calculated on the beginning-of-period short-term debt balance:
  `	ext
  ST Interest(t) = Beginning ST Debt(t) * Annual Interest Rate
  `
- **Sequential Traceability**: Current-period draws or repayments alter the closing balance, which rolls into period t+1 opening balance and dictates period t+1 interest. This eliminates circular calculation references while ensuring borrowing decisions directly impact future financing costs.

### C. Liquidity Sweep & Short-Term Revolver Mechanics
Each period executes an automated cash waterfall:
1. **Operating Cash Flow (CFO)** and **Investing Cash Flow (CFI)** are combined with mandatory senior debt service to determine available cash pre-financing.
2. **Short-Term Revolver Borrowing**:
   If available cash post-dividend is below the **Minimum Cash Requirement** (INR 5.0 Cr default):
   - The cash shortfall is drawn from the Short-Term Debt facility.
   - The short-term borrowing mechanism is unconstrained by an artificial borrowing ceiling (no facility limit is enforced in the model engine).
3. **Surplus Cash Sweep**:
   If available cash post-dividend exceeds the Minimum Cash Requirement:
   - Surplus cash is applied first to prepay outstanding short-term debt.
   - Any remaining excess cash is held on the Balance Sheet as **Liquid Investments** (cash equivalents).
   - *(Note: Liquid investments in the model do not earn interest income or treasury yield; other income is 0.0).*

---

## 7. Tax, Retained Earnings & Dividends

- **Earnings Before Tax (PBT)**: EBITDA - Depreciation - Total Finance Costs.
- **Corporate Tax**: Accrued at standard effective corporate tax rate (25.17% default) on positive PBT. Zero tax expense in loss-making periods.
- **Profit After Tax (PAT)**: PBT - Corporate Tax.
- **Dividend Policy & Minimum-Cash Interaction**:
  - The default dividend payout ratio is **0.0%** (configurable in assumptions).
  - When a positive payout ratio is configured, target dividends are calculated as PAT * Payout Ratio for positive PAT periods.
  - **Prudential Liquidity Cap**: In the cash waterfall, actual dividends are constrained by distributable liquidity:
    `	ext
    Max Distributable = max(0.0, Cash Pre-Financing - Minimum Cash Requirement)
    Actual Dividend = min(Target Dividend, Max Distributable)
    `
    Dividends are never funded via short-term debt borrowing; if available cash pre-financing is insufficient to maintain the minimum cash buffer, dividends are curtailed to zero.
- **Retained Earnings Roll-Forward**:
  `	ext
  Ending Retained Earnings(t) = Beginning Retained Earnings(t) + PAT(t) - Actual Dividends(t)
  `

---

## 8. Integrated Cash Flow Statement & Balance Sheet Equilibrium

The cash flow statement is presented using the **Indirect Method**:
1. **Cash Flow from Operating Activities (CFO)**:
   PAT + Non-Cash Depreciation + Interest Expense Addback - Working Capital Changes.
2. **Cash Flow from Investing Activities (CFI)**:
   Capex additions (negative cash outflow).
3. **Cash Flow from Financing Activities (CFF)**:
   Long-term debt principal repayments (negative) + Net short-term debt movement - Finance costs paid (negative) - Dividends distributed (negative).
4. **Closing Cash & Liquid Investments**:
   `	ext
   Closing Total Liquidity(t) = Opening Total Liquidity(t) + Net Cash Flow(t)
   `

### Mathematical Balance Sheet Equilibrium
Total Assets must strictly equal Total Liabilities plus Shareholders Equity for all seven periods:
`	ext
Total Assets(t) - (Total Liabilities(t) + Total Shareholders Equity(t)) = 0.00
`
Automated model checks verify that the maximum balance sheet variance across all periods is less than 1e-6 INR.

---

## 9. Accounting Scope & Known Omissions

To maintain transparent portfolio standards, the following accounting treatments are deliberately omitted from this demonstration model:
- **Ind AS 116 (Leases)**: Does not capitalize operating leases as Right-of-Use (ROU) assets or model corresponding lease liabilities.
- **Ind AS 12 (Income Taxes)**: Does not model timing differences, Deferred Tax Assets (DTA), or Deferred Tax Liabilities (DTL).
- **Ind AS 19 (Employee Benefits)**: Does not model actuarial valuation of gratuity or leave encashment obligations.
- **Ind AS 109 (Financial Instruments)**: Debt is modeled on nominal contractual terms without effective interest rate (EIR) fee amortization.
- **Statutory Presentation**: The Schedule III-style financial statement views follow standard statutory headings for analytical clarity but do not constitute formal statutory audit disclosures or full accounting compliance certifications.