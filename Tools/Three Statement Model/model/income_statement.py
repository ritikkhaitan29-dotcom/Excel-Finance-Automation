"""
model/income_statement.py
=========================
Manufacturing FP&A 3-Statement Financial Model - Income Statement Builder.

Integrates operating forecast, depreciation, debt, and corporate taxes.
Mapped strictly to central reporting periods (F26A, F27E, F28P...).
"""

import pandas as pd
from model.assumptions import ModelAssumptions


def build_income_statement(
    assumptions: ModelAssumptions,
    operating_df: pd.DataFrame,
    depr_df: pd.DataFrame,
    debt_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Constructs the multi-period Income Statement.
    """
    records = []
    tax_rate = assumptions.corporate_tax_rate

    for i in range(len(operating_df)):
        period_id = operating_df.loc[i, "Period"]
        classification = operating_df.loc[i, "Classification"]
        display_label = operating_df.loc[i, "Display_Label"]
        year = operating_df.loc[i, "Year"]

        rev = operating_df.loc[i, "Total_Revenue_INR"]
        rm = operating_df.loc[i, "Total_RM_Cost_INR"]
        ovc = operating_df.loc[i, "Total_OVC_Cost_INR"]
        contrib = operating_df.loc[i, "Total_Contribution_INR"]
        fc = operating_df.loc[i, "Fixed_Operating_Costs_INR"]
        ebitda = operating_df.loc[i, "EBITDA_INR"]

        depr = depr_df.loc[i, "Depreciation_INR"]
        ebit = ebitda - depr

        interest = debt_df.loc[i, "Total_Interest_Expense_INR"]
        pbt = ebit - interest

        # Corporate income tax with loss floor
        tax = max(0.0, pbt * tax_rate) if pbt > 0 else 0.0
        pat = pbt - tax

        records.append({
            "Period": period_id,
            "Classification": classification,
            "Display_Label": display_label,
            "Year": year,
            "Revenue_INR": rev,
            "RM_Cost_INR": rm,
            "OVC_Cost_INR": ovc,
            "Total_Variable_Cost_INR": rm + ovc,
            "Contribution_INR": contrib,
            "Fixed_Operating_Costs_INR": fc,
            "EBITDA_INR": ebitda,
            "Depreciation_INR": depr,
            "EBIT_INR": ebit,
            "Interest_Expense_INR": interest,
            "PBT_INR": pbt,
            "Tax_Expense_INR": tax,
            "Net_Profit_INR": pat,
            # INR Crores reporting metrics
            "Revenue_Cr": rev / 10_000_000.0,
            "RM_Cost_Cr": rm / 10_000_000.0,
            "OVC_Cost_Cr": ovc / 10_000_000.0,
            "Contribution_Cr": contrib / 10_000_000.0,
            "Fixed_Operating_Costs_Cr": fc / 10_000_000.0,
            "EBITDA_Cr": ebitda / 10_000_000.0,
            "Depreciation_Cr": depr / 10_000_000.0,
            "EBIT_Cr": ebit / 10_000_000.0,
            "Interest_Expense_Cr": interest / 10_000_000.0,
            "PBT_Cr": pbt / 10_000_000.0,
            "Tax_Expense_Cr": tax / 10_000_000.0,
            "Net_Profit_Cr": pat / 10_000_000.0,
            # Margin Percentages
            "EBITDA_Margin_Pct": (ebitda / rev) * 100.0 if rev > 0 else 0.0,
            "EBIT_Margin_Pct": (ebit / rev) * 100.0 if rev > 0 else 0.0,
            "Net_Margin_Pct": (pat / rev) * 100.0 if rev > 0 else 0.0,
        })

    return pd.DataFrame(records)