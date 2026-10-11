from typing import Dict, List, Tuple
import pandas as pd
from model.assumptions import ModelAssumptions
from model.periods import STANDARD_PERIODS

def build_depreciation_schedule(assumptions: ModelAssumptions) -> pd.DataFrame:
    records = []
    existing_annual_depr = 0.0
    existing_gross_asset_val = 0.0

    for asset in assumptions.fixed_assets:
        existing_annual_depr += asset.annual_depreciation_inr
        existing_gross_asset_val += asset.gross_asset_value_inr

    opening_gross_ppe = existing_gross_asset_val
    opening_accum_depr = existing_gross_asset_val * 0.20
    opening_net_ppe = opening_gross_ppe - opening_accum_depr

    current_beg_gross = opening_gross_ppe
    current_beg_accum = opening_accum_depr
    current_beg_net = opening_net_ppe

    annual_capex = assumptions.annual_capex_inr
    capex_life = float(assumptions.capex_useful_life_years)
    capex_salvage = float(assumptions.capex_salvage_value_pct)
    addition_depr_rate = (1.0 - capex_salvage) / capex_life if capex_life > 0 else 0.0

    additions_history = []

    for i, p in enumerate(STANDARD_PERIODS):
        depr_from_additions = sum(cap * addition_depr_rate for cap in additions_history)
        period_depreciation = existing_annual_depr + depr_from_additions
        period_capex = annual_capex if i > 0 else 0.0

        ending_gross_ppe = current_beg_gross + period_capex
        ending_accum_depr = current_beg_accum + period_depreciation
        ending_net_ppe = ending_gross_ppe - ending_accum_depr

        row = {
            'Period': p.period_id,
            'Classification': p.classification,
            'Display_Label': p.display_label,
            'Year': p.fiscal_year,
            'Beginning_Gross_PPE_INR': current_beg_gross,
            'Beginning_Accum_Depr_INR': current_beg_accum,
            'Beginning_Net_PPE_INR': current_beg_net,
            'Capex_INR': period_capex,
            'Depreciation_Existing_INR': existing_annual_depr,
            'Depreciation_Additions_INR': depr_from_additions,
            'Depreciation_INR': period_depreciation,
            'Ending_Gross_PPE_INR': ending_gross_ppe,
            'Ending_Accum_Depr_INR': ending_accum_depr,
            'Ending_Net_PPE_INR': ending_net_ppe,
            'Beginning_Gross_PPE_Cr': current_beg_gross / 10_000_000.0,
            'Beginning_Accum_Depr_Cr': current_beg_accum / 10_000_000.0,
            'Beginning_Net_PPE_Cr': current_beg_net / 10_000_000.0,
            'Capex_Cr': period_capex / 10_000_000.0,
            'Depreciation_Existing_Cr': existing_annual_depr / 10_000_000.0,
            'Depreciation_Additions_Cr': depr_from_additions / 10_000_000.0,
            'Depreciation_Cr': period_depreciation / 10_000_000.0,
            'Ending_Gross_PPE_Cr': ending_gross_ppe / 10_000_000.0,
            'Ending_Accum_Depr_Cr': ending_accum_depr / 10_000_000.0,
            'Ending_Net_PPE_Cr': ending_net_ppe / 10_000_000.0,
        }

        for asset in assumptions.fixed_assets:
            cat_clean = asset.category_name.replace(' ', '_').replace('&', 'and')
            row[f'Depr_{cat_clean}_INR'] = asset.annual_depreciation_inr
            row[f'Depr_{cat_clean}_Cr'] = asset.annual_depreciation_inr / 10_000_000.0

        records.append(row)
        additions_history.append(period_capex)
        current_beg_gross = ending_gross_ppe
        current_beg_accum = ending_accum_depr
        current_beg_net = ending_net_ppe

    return pd.DataFrame(records)

def build_debt_schedule(assumptions: ModelAssumptions) -> pd.DataFrame:
    records = []
    opening_lt_debt = assumptions.long_term_debt.opening_balance_inr
    opening_st_debt = assumptions.short_term_debt.opening_balance_inr
    tenure = float(assumptions.lt_debt_repayment_tenure_years)
    annual_lt_repayment = opening_lt_debt / tenure if tenure > 0 else 0.0

    lt_rate = assumptions.long_term_debt.annual_interest_rate
    st_rate = assumptions.short_term_debt.annual_interest_rate

    current_lt_debt = opening_lt_debt
    current_st_debt = opening_st_debt

    n_periods = len(STANDARD_PERIODS)
    for i, p in enumerate(STANDARD_PERIODS):
        beg_lt_debt = current_lt_debt

        if p.period_id == 'F26A':
            lt_repayment = 0.0
            end_lt_debt = beg_lt_debt
            cmltd = min(end_lt_debt, annual_lt_repayment)
            non_current_lt_debt = max(0.0, end_lt_debt - cmltd)
        else:
            lt_repayment = min(beg_lt_debt, annual_lt_repayment)
            end_lt_debt = beg_lt_debt - lt_repayment
            next_lt_repayment = min(end_lt_debt, annual_lt_repayment) if i < n_periods - 1 else 0.0
            cmltd = next_lt_repayment
            non_current_lt_debt = max(0.0, end_lt_debt - cmltd)

        lt_interest = beg_lt_debt * lt_rate
        st_interest = current_st_debt * st_rate
        total_interest = lt_interest + st_interest
        total_debt = end_lt_debt + current_st_debt

        records.append({
            'Period': p.period_id,
            'Classification': p.classification,
            'Display_Label': p.display_label,
            'Year': p.fiscal_year,
            'Beginning_Long_Term_Debt_INR': beg_lt_debt,
            'LT_Principal_Repayment_INR': lt_repayment,
            'Ending_Long_Term_Debt_INR': end_lt_debt,
            'Long_Term_Debt_INR': end_lt_debt,
            'Total_Long_Term_Debt_Outstanding_INR': end_lt_debt,
            'CMLTD_INR': cmltd,
            'Non_Current_LT_Debt_INR': non_current_lt_debt,
            'Short_Term_Debt_INR': current_st_debt,
            'Beginning_Short_Term_Debt_INR': current_st_debt,
            'Ending_Short_Term_Debt_INR': current_st_debt,
            'Total_Debt_INR': total_debt,
            'LT_Interest_Expense_INR': lt_interest,
            'ST_Interest_Expense_INR': st_interest,
            'Total_Interest_Expense_INR': total_interest,
            'Beginning_Long_Term_Debt_Cr': beg_lt_debt / 10_000_000.0,
            'LT_Principal_Repayment_Cr': lt_repayment / 10_000_000.0,
            'Ending_Long_Term_Debt_Cr': end_lt_debt / 10_000_000.0,
            'Long_Term_Debt_Cr': end_lt_debt / 10_000_000.0,
            'Total_Long_Term_Debt_Outstanding_Cr': end_lt_debt / 10_000_000.0,
            'CMLTD_Cr': cmltd / 10_000_000.0,
            'Non_Current_LT_Debt_Cr': non_current_lt_debt / 10_000_000.0,
            'Short_Term_Debt_Cr': current_st_debt / 10_000_000.0,
            'Beginning_Short_Term_Debt_Cr': current_st_debt / 10_000_000.0,
            'Ending_Short_Term_Debt_Cr': current_st_debt / 10_000_000.0,
            'Total_Debt_Cr': total_debt / 10_000_000.0,
            'LT_Interest_Expense_Cr': lt_interest / 10_000_000.0,
            'ST_Interest_Expense_Cr': st_interest / 10_000_000.0,
            'Total_Interest_Expense_Cr': total_interest / 10_000_000.0,
        })
        current_lt_debt = end_lt_debt

    return pd.DataFrame(records)
