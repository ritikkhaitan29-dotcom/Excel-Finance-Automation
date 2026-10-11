"""
model/working_capital.py
========================
Manufacturing FP&A 3-Statement Financial Model - Working Capital Schedule.

Defines operational working capital balances and cash cycles across all 7 periods:
1. Trade Receivables = (Revenue / 365) * receivable_days
2. COGS = Total RM Cost + Total OVC Cost + Fixed Operating Costs
   Inventory = (COGS / 365) * inventory_days
3. Purchases Base = Total RM Cost + Total OVC Cost
   Trade Payables = (Purchases Base / 365) * payable_days
4. Net Working Capital (NWC) = Receivables + Inventory - Payables
5. Change in NWC = NWC_t - NWC_{t-1}
"""

from typing import Dict, List, Tuple
import pandas as pd
from model.assumptions import ModelAssumptions


def build_working_capital_schedule(
    assumptions: ModelAssumptions,
    operating_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Computes working capital balances, turnover days, and NWC changes.
    """
    records = []

    rec_days = assumptions.working_capital.receivable_days
    inv_days = assumptions.working_capital.inventory_days
    pay_days = assumptions.working_capital.payable_days

    # FY24/25 Anchor Baseline
    base_rev = assumptions.total_base_revenue_inr
    base_rm = assumptions.total_base_rm_cost_inr
    base_ovc = assumptions.total_base_ovc_cost_inr
    base_fc = assumptions.base_fixed_costs_inr
    base_cogs = base_rm + base_ovc + base_fc
    base_purchases = base_rm + base_ovc

    base_ar = (base_rev / 365.0) * rec_days
    base_inv = (base_cogs / 365.0) * inv_days
    base_ap = (base_purchases / 365.0) * pay_days
    base_nwc = (base_ar + base_inv) - base_ap

    prev_nwc = base_nwc

    for i in range(len(operating_df)):
        period_id = operating_df.loc[i, "Period"]
        classification = operating_df.loc[i, "Classification"]
        display_label = operating_df.loc[i, "Display_Label"]
        year = operating_df.loc[i, "Year"]

        rev = operating_df.loc[i, "Total_Revenue_INR"]
        rm = operating_df.loc[i, "Total_RM_Cost_INR"]
        ovc = operating_df.loc[i, "Total_OVC_Cost_INR"]
        fc = operating_df.loc[i, "Fixed_Operating_Costs_INR"]

        cogs = rm + ovc + fc
        purchases = rm + ovc

        ar = (rev / 365.0) * rec_days
        inv = (cogs / 365.0) * inv_days
        ap = (purchases / 365.0) * pay_days

        nwc = (ar + inv) - ap
        delta_nwc = nwc - prev_nwc

        records.append({
            "Period": period_id,
            "Classification": classification,
            "Display_Label": display_label,
            "Year": year,
            "COGS_INR": cogs,
            "Purchases_INR": purchases,
            "Trade_Receivables_INR": ar,
            "Inventory_INR": inv,
            "Trade_Payables_INR": ap,
            "Net_Working_Capital_INR": nwc,
            "Change_in_NWC_INR": delta_nwc,
            # INR Crores reporting metrics
            "COGS_Cr": cogs / 10_000_000.0,
            "Purchases_Cr": purchases / 10_000_000.0,
            "Trade_Receivables_Cr": ar / 10_000_000.0,
            "Inventory_Cr": inv / 10_000_000.0,
            "Trade_Payables_Cr": ap / 10_000_000.0,
            "Net_Working_Capital_Cr": nwc / 10_000_000.0,
            "Change_in_NWC_Cr": delta_nwc / 10_000_000.0,
            # Cycle metrics
            "DSO_Days": rec_days,
            "DIO_Days": inv_days,
            "DPO_Days": pay_days,
            "Cash_Conversion_Cycle_Days": rec_days + inv_days - pay_days,
        })

        prev_nwc = nwc

    return pd.DataFrame(records)