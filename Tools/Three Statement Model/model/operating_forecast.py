"""
model/operating_forecast.py
===========================
Manufacturing FP&A 3-Statement Financial Model - Operating Forecast Engine.

Builds complete 7-period operating forecast (F26A through F32P):
- F26A is the baseline synthetic actual period (no growth applied to base assumptions)
- F27E through F32P are forward estimates and projections compounding from F26A
- Volume compounding by product (MT)
- ASP compounding via ASP inflation (INR/MT)
- Revenue build by product and portfolio total (INR and INR Cr)
- Raw Material (RM) and Other Variable Cost (OVC) compounding via independent inflation
- Total Contribution (Revenue - RM - OVC) in INR and INR Cr
- Fixed Operating Costs escalated via fixed-cost inflation in INR and INR Cr
- Operating Profitability (EBITDA) in INR, INR Cr, and EBITDA Margin %
"""

import pandas as pd
from model.assumptions import ModelAssumptions
from model.periods import STANDARD_PERIODS


def build_operating_forecast(assumptions: ModelAssumptions) -> pd.DataFrame:
    """
    Produces complete 7-period operating forecast DataFrame mapped to central reporting periods.
    """
    records = []

    # Baseline product-level unit costs (INR/MT)
    base_rm_per_tonne_a = assumptions.product_a_base_rm_cost_per_tonne_inr
    base_ovc_per_tonne_a = assumptions.product_a_base_ovc_cost_per_tonne_inr

    base_rm_per_tonne_b = assumptions.product_b_base_rm_cost_per_tonne_inr
    base_ovc_per_tonne_b = assumptions.product_b_base_ovc_cost_per_tonne_inr

    # Annual inflation rates
    asp_inf = assumptions.inflation.asp_inflation_rate
    rm_inf = assumptions.inflation.rm_inflation_rate
    ovc_inf = assumptions.inflation.ovc_inflation_rate
    fc_inf = assumptions.inflation.fixed_cost_inflation_rate

    # Track running volume from period to period
    prev_vol_a = assumptions.product_a.base_volume_tonnes
    prev_vol_b = assumptions.product_b.base_volume_tonnes

    for idx, p in enumerate(STANDARD_PERIODS):
        period_id = p.period_id
        classification = p.classification
        display_label = p.display_label
        fiscal_year = p.fiscal_year

        if idx == 0:
            # ---------------------------------------------------------
            # Period 0: F26A (Synthetic / Illustrative Actual Baseline)
            # ---------------------------------------------------------
            vol_a = assumptions.product_a.base_volume_tonnes
            vol_b = assumptions.product_b.base_volume_tonnes
            asp_a = assumptions.product_a.base_asp_inr_per_tonne
            asp_b = assumptions.product_b.base_asp_inr_per_tonne
            rm_per_tonne_a = base_rm_per_tonne_a
            ovc_per_tonne_a = base_ovc_per_tonne_a
            rm_per_tonne_b = base_rm_per_tonne_b
            ovc_per_tonne_b = base_ovc_per_tonne_b
            fixed_operating_costs = assumptions.base_fixed_costs_inr
            prev_vol_a = vol_a
            prev_vol_b = vol_b
        else:
            # ---------------------------------------------------------
            # Periods 1 to 6: F27E through F32P (Estimate & Projections)
            # ---------------------------------------------------------
            step = idx  # number of compounding periods from baseline
            growth_idx = idx - 1  # 0 to 5 for the 6 forward growth rates
            g_rate_a = assumptions.product_a.annual_volume_growth_rates[growth_idx]
            g_rate_b = assumptions.product_b.annual_volume_growth_rates[growth_idx]

            vol_a = prev_vol_a * (1.0 + g_rate_a)
            vol_b = prev_vol_b * (1.0 + g_rate_b)
            prev_vol_a = vol_a
            prev_vol_b = vol_b

            asp_factor = (1.0 + asp_inf) ** step
            asp_a = assumptions.product_a.base_asp_inr_per_tonne * asp_factor
            asp_b = assumptions.product_b.base_asp_inr_per_tonne * asp_factor

            rm_factor = (1.0 + rm_inf) ** step
            ovc_factor = (1.0 + ovc_inf) ** step
            rm_per_tonne_a = base_rm_per_tonne_a * rm_factor
            ovc_per_tonne_a = base_ovc_per_tonne_a * ovc_factor
            rm_per_tonne_b = base_rm_per_tonne_b * rm_factor
            ovc_per_tonne_b = base_ovc_per_tonne_b * ovc_factor

            fc_factor = (1.0 + fc_inf) ** step
            fixed_operating_costs = assumptions.base_fixed_costs_inr * fc_factor

        total_vol = vol_a + vol_b

        # Revenue
        rev_a = vol_a * asp_a
        rev_b = vol_b * asp_b
        total_revenue = rev_a + rev_b

        # Variable Costs
        rm_cost_a = vol_a * rm_per_tonne_a
        ovc_cost_a = vol_a * ovc_per_tonne_a
        total_var_a = rm_cost_a + ovc_cost_a

        rm_cost_b = vol_b * rm_per_tonne_b
        ovc_cost_b = vol_b * ovc_per_tonne_b
        total_var_b = rm_cost_b + ovc_cost_b

        total_rm_cost = rm_cost_a + rm_cost_b
        total_ovc_cost = ovc_cost_a + ovc_cost_b
        total_variable_cost = total_rm_cost + total_ovc_cost

        # Contribution Margins
        contribution_a = rev_a - total_var_a
        contribution_b = rev_b - total_var_b
        total_contribution = total_revenue - total_variable_cost

        # EBITDA
        ebitda = total_contribution - fixed_operating_costs

        # Cr metrics & Margin
        revenue_cr = total_revenue / 10_000_000.0
        rm_cost_cr = total_rm_cost / 10_000_000.0
        ovc_cost_cr = total_ovc_cost / 10_000_000.0
        contribution_cr = total_contribution / 10_000_000.0
        fixed_cost_cr = fixed_operating_costs / 10_000_000.0
        ebitda_cr = ebitda / 10_000_000.0
        ebitda_margin_pct = (ebitda / total_revenue) * 100.0 if total_revenue > 0 else 0.0

        records.append({
            "Period": period_id,
            "Classification": classification,
            "Display_Label": display_label,
            "Year": fiscal_year,
            # Product A Operations
            "Product_A_Volume_Tonnes": vol_a,
            "Product_A_ASP_INR_per_Tonne": asp_a,
            "Product_A_Revenue_INR": rev_a,
            "Product_A_RM_Cost_per_Tonne_INR": rm_per_tonne_a,
            "Product_A_OVC_Cost_per_Tonne_INR": ovc_per_tonne_a,
            "Product_A_RM_Cost_INR": rm_cost_a,
            "Product_A_OVC_Cost_INR": ovc_cost_a,
            "Product_A_Contribution_INR": contribution_a,
            # Product B Operations
            "Product_B_Volume_Tonnes": vol_b,
            "Product_B_ASP_INR_per_Tonne": asp_b,
            "Product_B_Revenue_INR": rev_b,
            "Product_B_RM_Cost_per_Tonne_INR": rm_per_tonne_b,
            "Product_B_OVC_Cost_per_Tonne_INR": ovc_per_tonne_b,
            "Product_B_RM_Cost_INR": rm_cost_b,
            "Product_B_OVC_Cost_INR": ovc_cost_b,
            "Product_B_Contribution_INR": contribution_b,
            # Portfolio Totals (INR)
            "Total_Volume_Tonnes": total_vol,
            "Total_Revenue_INR": total_revenue,
            "Total_RM_Cost_INR": total_rm_cost,
            "Total_OVC_Cost_INR": total_ovc_cost,
            "Total_Contribution_INR": total_contribution,
            "Fixed_Operating_Costs_INR": fixed_operating_costs,
            "EBITDA_INR": ebitda,
            # Portfolio Reporting Metrics (Crores & Margin %)
            "Revenue_Cr": revenue_cr,
            "RM_Cost_Cr": rm_cost_cr,
            "OVC_Cost_Cr": ovc_cost_cr,
            "Contribution_Cr": contribution_cr,
            "Fixed_Cost_Cr": fixed_cost_cr,
            "EBITDA_Cr": ebitda_cr,
            "EBITDA_Margin_Pct": ebitda_margin_pct,
        })

    return pd.DataFrame(records)