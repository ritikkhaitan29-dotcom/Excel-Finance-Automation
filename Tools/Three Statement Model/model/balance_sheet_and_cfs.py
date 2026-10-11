from typing import Dict, List, Tuple
import pandas as pd
from model.assumptions import ModelAssumptions
from model.periods import STANDARD_PERIODS

def build_integrated_financial_system(
    assumptions: ModelAssumptions,
    operating_df: pd.DataFrame,
    depr_df: pd.DataFrame,
    wc_df: pd.DataFrame,
    opening_cash_inr: float = 50_000_000.0,
    share_capital_inr: float = 150_000_000.0,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    n_periods = len(STANDARD_PERIODS)
    
    base_rev = assumptions.total_base_revenue_inr
    base_rm = assumptions.total_base_rm_cost_inr
    base_ovc = assumptions.total_base_ovc_cost_inr
    base_fc = assumptions.base_fixed_costs_inr
    base_cogs = base_rm + base_ovc + base_fc
    base_purchases = base_rm + base_ovc

    init_ar = (base_rev / 365.0) * assumptions.working_capital.receivable_days
    init_inv = (base_cogs / 365.0) * assumptions.working_capital.inventory_days
    init_ap = (base_purchases / 365.0) * assumptions.working_capital.payable_days

    init_net_ppe = depr_df.loc[0, 'Beginning_Net_PPE_INR']
    init_lt_debt = assumptions.long_term_debt.opening_balance_inr
    init_st_debt = assumptions.short_term_debt.opening_balance_inr
    init_liquid_inv = 0.0

    init_total_assets = opening_cash_inr + init_liquid_inv + init_ar + init_inv + init_net_ppe
    init_total_liab = init_ap + init_lt_debt + init_st_debt
    init_retained_earnings = init_total_assets - init_total_liab - share_capital_inr

    current_cash = opening_cash_inr
    current_liquid_inv = init_liquid_inv
    current_st_debt = init_st_debt
    current_lt_debt = init_lt_debt
    current_re = init_retained_earnings

    lt_rate = assumptions.long_term_debt.annual_interest_rate
    st_rate = assumptions.short_term_debt.annual_interest_rate
    tenure = float(assumptions.lt_debt_repayment_tenure_years)
    annual_lt_repayment = init_lt_debt / tenure if tenure > 0 else 0.0
    tax_rate = assumptions.corporate_tax_rate
    min_cash_req = float(assumptions.minimum_cash_inr)
    payout_ratio = float(assumptions.dividend_payout_ratio)

    debt_records = []
    is_records = []
    cfs_records = []
    bs_records = []

    for i, p in enumerate(STANDARD_PERIODS):
        period_id = p.period_id
        classification = p.classification
        display_label = p.display_label
        year = p.fiscal_year

        beg_lt_debt = current_lt_debt
        beg_st_debt = current_st_debt

        if period_id == 'F26A':
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
        st_interest = beg_st_debt * st_rate
        total_interest = lt_interest + st_interest

        rev = operating_df.loc[i, 'Total_Revenue_INR']
        rm = operating_df.loc[i, 'Total_RM_Cost_INR']
        ovc = operating_df.loc[i, 'Total_OVC_Cost_INR']
        contrib = operating_df.loc[i, 'Total_Contribution_INR']
        fc = operating_df.loc[i, 'Fixed_Operating_Costs_INR']
        ebitda = operating_df.loc[i, 'EBITDA_INR']
        depr = depr_df.loc[i, 'Depreciation_INR']
        ebit = ebitda - depr
        pbt = ebit - total_interest
        tax = max(0.0, pbt * tax_rate) if pbt > 0 else 0.0
        pat = pbt - tax

        is_records.append({
            'Period': period_id,
            'Classification': classification,
            'Display_Label': display_label,
            'Year': year,
            'Revenue_INR': rev,
            'RM_Cost_INR': rm,
            'OVC_Cost_INR': ovc,
            'Total_Variable_Cost_INR': rm + ovc,
            'Contribution_INR': contrib,
            'Fixed_Operating_Costs_INR': fc,
            'EBITDA_INR': ebitda,
            'Depreciation_INR': depr,
            'EBIT_INR': ebit,
            'Interest_Expense_INR': total_interest,
            'PBT_INR': pbt,
            'Tax_Expense_INR': tax,
            'Net_Profit_INR': pat,
            'Revenue_Cr': rev / 10_000_000.0,
            'RM_Cost_Cr': rm / 10_000_000.0,
            'OVC_Cost_Cr': ovc / 10_000_000.0,
            'Contribution_Cr': contrib / 10_000_000.0,
            'Fixed_Operating_Costs_Cr': fc / 10_000_000.0,
            'EBITDA_Cr': ebitda / 10_000_000.0,
            'Depreciation_Cr': depr / 10_000_000.0,
            'EBIT_Cr': ebit / 10_000_000.0,
            'Interest_Expense_Cr': total_interest / 10_000_000.0,
            'PBT_Cr': pbt / 10_000_000.0,
            'Tax_Expense_Cr': tax / 10_000_000.0,
            'Net_Profit_Cr': pat / 10_000_000.0,
            'EBITDA_Margin_Pct': (ebitda / rev) * 100.0 if rev > 0 else 0.0,
            'EBIT_Margin_Pct': (ebit / rev) * 100.0 if rev > 0 else 0.0,
            'Net_Margin_Pct': (pat / rev) * 100.0 if rev > 0 else 0.0,
        })

        capex = depr_df.loc[i, 'Capex_INR']
        delta_nwc = wc_df.loc[i, 'Change_in_NWC_INR']
        interest_paid = total_interest

        cfo = pat + depr + total_interest - delta_nwc
        cfi = -capex

        beg_cash = current_cash
        beg_liquid_inv = current_liquid_inv
        cash_pre_financing = beg_cash + beg_liquid_inv + cfo + cfi - lt_repayment - interest_paid

        target_dividend = pat * payout_ratio if pat > 0 else 0.0
        max_distributable = max(0.0, cash_pre_financing - min_cash_req)
        actual_dividend = min(target_dividend, max_distributable)
        cash_post_dividend = cash_pre_financing - actual_dividend

        if cash_post_dividend < min_cash_req:
            deficit = min_cash_req - cash_post_dividend
            st_debt_draw = deficit
            st_debt_repay = 0.0
            end_st_debt = beg_st_debt + st_debt_draw
            end_liquid_inv = 0.0
            end_cash = min_cash_req
        else:
            surplus = cash_post_dividend - min_cash_req
            st_debt_draw = 0.0
            st_debt_repay = min(beg_st_debt, surplus)
            end_st_debt = beg_st_debt - st_debt_repay
            remaining_surplus = surplus - st_debt_repay
            end_liquid_inv = remaining_surplus
            end_cash = min_cash_req

        net_st_debt_movement = end_st_debt - beg_st_debt
        cff = -lt_repayment + net_st_debt_movement - interest_paid - actual_dividend

        total_beg_liquidity = beg_cash + beg_liquid_inv
        total_end_liquidity = end_cash + end_liquid_inv

        cfs_records.append({
            'Period': period_id,
            'Classification': classification,
            'Display_Label': display_label,
            'Year': year,
            'Net_Profit_INR': pat,
            'Depreciation_INR': depr,
            'Interest_Expense_Addback_INR': total_interest,
            'Change_in_NWC_INR': -delta_nwc,
            'CFO_INR': cfo,
            'Capex_INR': -capex,
            'CFI_INR': cfi,
            'LT_Debt_Repayment_INR': -lt_repayment,
            'ST_Debt_Net_Draw_INR': net_st_debt_movement,
            'Interest_Paid_INR': -interest_paid,
            'Dividends_Paid_INR': -actual_dividend,
            'CFF_INR': cff,
            'Net_Change_in_Cash_INR': total_end_liquidity - total_beg_liquidity,
            'Beginning_Cash_INR': total_beg_liquidity,
            'Ending_Cash_INR': total_end_liquidity,
            'Cash_Only_Beginning_INR': beg_cash,
            'Cash_Only_Ending_INR': end_cash,
            'Liquid_Investments_Beginning_INR': beg_liquid_inv,
            'Liquid_Investments_Ending_INR': end_liquid_inv,
            'Net_Profit_Cr': pat / 10_000_000.0,
            'Depreciation_Cr': depr / 10_000_000.0,
            'Interest_Expense_Addback_Cr': total_interest / 10_000_000.0,
            'Change_in_NWC_Cr': -delta_nwc / 10_000_000.0,
            'CFO_Cr': cfo / 10_000_000.0,
            'Capex_Cr': -capex / 10_000_000.0,
            'CFI_Cr': cfi / 10_000_000.0,
            'LT_Debt_Repayment_Cr': -lt_repayment / 10_000_000.0,
            'ST_Debt_Net_Draw_Cr': net_st_debt_movement / 10_000_000.0,
            'Interest_Paid_Cr': -interest_paid / 10_000_000.0,
            'Dividends_Paid_Cr': -actual_dividend / 10_000_000.0,
            'CFF_Cr': cff / 10_000_000.0,
            'Net_Change_in_Cash_Cr': (total_end_liquidity - total_beg_liquidity) / 10_000_000.0,
            'Beginning_Cash_Cr': total_beg_liquidity / 10_000_000.0,
            'Ending_Cash_Cr': total_end_liquidity / 10_000_000.0,
            'Cash_Only_Ending_Cr': end_cash / 10_000_000.0,
            'Liquid_Investments_Ending_Cr': end_liquid_inv / 10_000_000.0,
        })

        total_debt_closing = end_lt_debt + end_st_debt
        debt_records.append({
            'Period': period_id,
            'Classification': classification,
            'Display_Label': display_label,
            'Year': year,
            'Beginning_Long_Term_Debt_INR': beg_lt_debt,
            'LT_Principal_Repayment_INR': lt_repayment,
            'Ending_Long_Term_Debt_INR': end_lt_debt,
            'Long_Term_Debt_INR': end_lt_debt,
            'Total_Long_Term_Debt_Outstanding_INR': end_lt_debt,
            'CMLTD_INR': cmltd,
            'Non_Current_LT_Debt_INR': non_current_lt_debt,
            'Beginning_Short_Term_Debt_INR': beg_st_debt,
            'Short_Term_Debt_Net_Draw_INR': net_st_debt_movement,
            'Ending_Short_Term_Debt_INR': end_st_debt,
            'Short_Term_Debt_INR': end_st_debt,
            'Total_Debt_INR': total_debt_closing,
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
            'Beginning_Short_Term_Debt_Cr': beg_st_debt / 10_000_000.0,
            'Short_Term_Debt_Net_Draw_Cr': net_st_debt_movement / 10_000_000.0,
            'Ending_Short_Term_Debt_Cr': end_st_debt / 10_000_000.0,
            'Short_Term_Debt_Cr': end_st_debt / 10_000_000.0,
            'Total_Debt_Cr': total_debt_closing / 10_000_000.0,
            'LT_Interest_Expense_Cr': lt_interest / 10_000_000.0,
            'ST_Interest_Expense_Cr': st_interest / 10_000_000.0,
            'Total_Interest_Expense_Cr': total_interest / 10_000_000.0,
        })

        ar = wc_df.loc[i, 'Trade_Receivables_INR']
        inv = wc_df.loc[i, 'Inventory_INR']
        ap = wc_df.loc[i, 'Trade_Payables_INR']
        net_ppe = depr_df.loc[i, 'Ending_Net_PPE_INR']

        end_re = current_re + pat - actual_dividend
        total_equity = share_capital_inr + end_re

        total_current_assets = end_cash + end_liquid_inv + ar + inv
        total_assets = total_current_assets + net_ppe

        total_current_liabilities = ap + end_st_debt + cmltd
        total_liabilities = total_current_liabilities + non_current_lt_debt
        total_liab_equity = total_liabilities + total_equity

        balance_check = total_assets - total_liab_equity

        bs_records.append({
            'Period': period_id,
            'Classification': classification,
            'Display_Label': display_label,
            'Year': year,
            'Cash_and_Equivalents_INR': end_cash,
            'Liquid_Investments_INR': end_liquid_inv,
            'Trade_Receivables_INR': ar,
            'Inventory_INR': inv,
            'Total_Current_Assets_INR': total_current_assets,
            'Net_Fixed_Assets_INR': net_ppe,
            'Total_Assets_INR': total_assets,
            'Trade_Payables_INR': ap,
            'Short_Term_Debt_INR': end_st_debt,
            'CMLTD_INR': cmltd,
            'Total_Current_Liabilities_INR': total_current_liabilities,
            'Long_Term_Debt_INR': non_current_lt_debt,
            'Total_Long_Term_Debt_Outstanding_INR': end_lt_debt,
            'Total_Liabilities_INR': total_liabilities,
            'Share_Capital_INR': share_capital_inr,
            'Retained_Earnings_INR': end_re,
            'Total_Shareholders_Equity_INR': total_equity,
            'Total_Liabilities_and_Equity_INR': total_liab_equity,
            'Balance_Check_INR': balance_check,
            'Cash_and_Equivalents_Cr': end_cash / 10_000_000.0,
            'Liquid_Investments_Cr': end_liquid_inv / 10_000_000.0,
            'Trade_Receivables_Cr': ar / 10_000_000.0,
            'Inventory_Cr': inv / 10_000_000.0,
            'Total_Current_Assets_Cr': total_current_assets / 10_000_000.0,
            'Net_Fixed_Assets_Cr': net_ppe / 10_000_000.0,
            'Total_Assets_Cr': total_assets / 10_000_000.0,
            'Trade_Payables_Cr': ap / 10_000_000.0,
            'Short_Term_Debt_Cr': end_st_debt / 10_000_000.0,
            'CMLTD_Cr': cmltd / 10_000_000.0,
            'Total_Current_Liabilities_Cr': total_current_liabilities / 10_000_000.0,
            'Long_Term_Debt_Cr': non_current_lt_debt / 10_000_000.0,
            'Total_Long_Term_Debt_Outstanding_Cr': end_lt_debt / 10_000_000.0,
            'Total_Liabilities_Cr': total_liabilities / 10_000_000.0,
            'Share_Capital_Cr': share_capital_inr / 10_000_000.0,
            'Retained_Earnings_Cr': end_re / 10_000_000.0,
            'Total_Shareholders_Equity_Cr': total_equity / 10_000_000.0,
            'Total_Liabilities_and_Equity_Cr': total_liab_equity / 10_000_000.0,
            'Balance_Check_Cr': balance_check / 10_000_000.0,
        })

        current_cash = end_cash
        current_liquid_inv = end_liquid_inv
        current_st_debt = end_st_debt
        current_lt_debt = end_lt_debt
        current_re = end_re

    return pd.DataFrame(debt_records), pd.DataFrame(is_records), pd.DataFrame(cfs_records), pd.DataFrame(bs_records)

def build_cfs_and_balance_sheet(
    assumptions: ModelAssumptions,
    is_df: pd.DataFrame,
    wc_df: pd.DataFrame,
    depr_df: pd.DataFrame,
    debt_df: pd.DataFrame,
    opening_cash_inr: float = 50_000_000.0,
    share_capital_inr: float = 150_000_000.0,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    from model.operating_forecast import build_operating_forecast
    op_df = build_operating_forecast(assumptions)
    _, _, cfs_df, bs_df = build_integrated_financial_system(
        assumptions, op_df, depr_df, wc_df, opening_cash_inr, share_capital_inr
    )
    return cfs_df, bs_df
