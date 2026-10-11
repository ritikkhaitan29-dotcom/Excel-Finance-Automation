"""
tests/test_model_integration.py
================================
Automated audit tests for the manufacturing FP&A 3-statement model:
1. 7-period model horizon verification: F26A, F27E, F28P, F29P, F30P, F31P, F32P
2. Data classifications: F26A is Synthetic Actual, F27E is Illustrative Estimate, F28P-F32P are Projections
3. Balance sheet equilibrium: Total Assets == Total Liabilities + Shareholders Equity with 0.00 variance
4. Cash flow statement reconciliation: Net change in cash matches ending - beginning cash across all 7 periods
5. Retained earnings roll-forward across all 7 periods
6. Statement linkage: Net profit identical across IS and CFS
7. Schedule III Division II presentation structure and non-current / current classifications
8. Comprehensive editable assumptions test: Verifies that changing each assumption changes downstream schedules while unedited assumptions are preserved
"""

import pytest
from model.assumptions import (
    ModelAssumptions,
    ProductAssumption,
    VariableCostAssumption,
    InflationAssumption,
    FixedAssetInput,
    DebtFacilityInput,
    WorkingCapitalAssumption,
)
from model.periods import STANDARD_PERIODS, get_period_ids, get_display_labels
from model.engine import run_full_model


def test_seven_reporting_periods_and_classifications():
    """Verify that the model produces exactly 7 periods with correct classifications and no false actuals."""
    result = run_full_model()
    expected_ids = ["F26A", "F27E", "F28P", "F29P", "F30P", "F31P", "F32P"]
    actual_ids = result.income_statement["Period"].tolist()
    assert actual_ids == expected_ids
    assert len(result.income_statement) == 7
    assert len(result.balance_sheet) == 7
    assert len(result.cash_flow_statement) == 7
    assert len(result.operating_forecast) == 7
    assert len(result.working_capital_schedule) == 7
    assert len(result.depreciation_schedule) == 7
    assert len(result.debt_schedule) == 7

    # Check classifications: F26A must be synthetic actual, F27E must be illustrative estimate
    classifications = result.income_statement["Classification"].tolist()
    assert classifications[0] == "Synthetic / Illustrative Actual"
    assert classifications[1] == "Illustrative Estimate"
    for c in classifications[2:]:
        assert c == "Projection"


def test_balance_sheet_equilibrium_all_seven_periods():
    """Verify that Total Assets strictly equal Total Liabilities and Shareholders Equity (0.00 variance) for all 7 periods."""
    result = run_full_model()
    max_variance = result.balance_sheet["Balance_Check_INR"].abs().max()
    assert max_variance < 0.001, f"Balance sheet variance detected: INR {max_variance}"
    assert result.audit.balance_sheet_balanced is True


def test_cash_flow_reconciliation_all_seven_periods():
    """Verify that Net Change in Cash perfectly matches Ending Cash minus Beginning Cash across all 7 periods."""
    result = run_full_model()
    cfs = result.cash_flow_statement
    for i in range(len(cfs)):
        diff = cfs.loc[i, "Ending_Cash_INR"] - cfs.loc[i, "Beginning_Cash_INR"]
        net_change = cfs.loc[i, "Net_Change_in_Cash_INR"]
        assert abs(diff - net_change) < 0.001, f"Cash reconciliation failure in period {cfs.loc[i, 'Period']}"
    assert result.audit.cash_reconciled is True


def test_retained_earnings_roll_forward():
    """Verify that Retained Earnings rolls forward cleanly period-over-period across all 7 periods."""
    result = run_full_model()
    bs = result.balance_sheet
    is_df = result.income_statement
    for i in range(1, len(bs)):
        beg_re = bs.loc[i - 1, "Retained_Earnings_INR"]
        np_val = is_df.loc[i, "Net_Profit_INR"]
        end_re = bs.loc[i, "Retained_Earnings_INR"]
        assert abs(end_re - (beg_re + np_val)) < 0.001, f"Retained earnings mismatch in period {bs.loc[i, 'Period']}"
    assert result.audit.retained_earnings_reconciled is True


def test_statement_linkages():
    """Verify that Net Profit is strictly identical between the Income Statement and Cash Flow Statement."""
    result = run_full_model()
    assert (result.income_statement["Net_Profit_INR"] == result.cash_flow_statement["Net_Profit_INR"]).all()
    assert result.audit.is_to_cfs_reconciled is True


def test_schedule_iii_presentations():
    """Verify Schedule III presentation structures have correct row keys, 7 period columns, and no unsupported labels."""
    result = run_full_model()
    bs_sch3 = result.schedule_iii_balance_sheet
    pl_sch3 = result.schedule_iii_profit_and_loss
    cf_sch3 = result.schedule_iii_cash_flow

    assert bs_sch3.shape[1] == 7
    assert pl_sch3.shape[1] == 7
    assert cf_sch3.shape[1] == 7

    assert "TOTAL ASSETS" in bs_sch3.index
    assert "TOTAL EQUITY AND LIABILITIES" in bs_sch3.index
    assert "I. Revenue from Operations" in pl_sch3.index
    assert "    Other Operating Overheads (Factory & Administrative)" in pl_sch3.index
    # Verify we do NOT claim unsupported specific employee benefits breakdown
    assert "Employee Benefits Expense" not in pl_sch3.index
    assert "VII. Profit for the Period (PAT) (V - VI)" in pl_sch3.index


def test_editable_assumptions_individual_propagation():
    """Verify that editing specific assumptions propagates to downstream schedules while unedited assumptions remain unchanged."""
    base_m = ModelAssumptions()
    base_res = run_full_model(base_m)

    # 1. Test Tax Rate change
    tax_modified_m = ModelAssumptions(corporate_tax_rate=0.30)
    tax_res = run_full_model(tax_modified_m)
    assert tax_res.income_statement.loc[0, "Revenue_INR"] == base_res.income_statement.loc[0, "Revenue_INR"]
    assert tax_res.income_statement.loc[0, "PBT_INR"] == base_res.income_statement.loc[0, "PBT_INR"]
    assert tax_res.income_statement.loc[0, "Tax_Expense_INR"] > base_res.income_statement.loc[0, "Tax_Expense_INR"]
    assert tax_res.audit.balance_sheet_balanced is True

    # 2. Test Debt Interest Rate change
    debt_modified_m = ModelAssumptions(
        long_term_debt=DebtFacilityInput(
            facility_type="Long-Term Debt",
            opening_balance_inr=250_000_000.0,
            annual_interest_rate=0.12  # Higher interest rate
        )
    )
    debt_res = run_full_model(debt_modified_m)
    assert debt_res.debt_schedule.loc[0, "Total_Interest_Expense_INR"] > base_res.debt_schedule.loc[0, "Total_Interest_Expense_INR"]
    assert debt_res.audit.balance_sheet_balanced is True

    # 3. Test Working Capital Days change
    wc_modified_m = ModelAssumptions(
        working_capital=WorkingCapitalAssumption(
            inventory_days=80.0,  # Higher inventory days
            receivable_days=50.0,
            payable_days=60.0
        )
    )
    wc_res = run_full_model(wc_modified_m)
    assert wc_res.working_capital_schedule.loc[0, "Inventory_INR"] > base_res.working_capital_schedule.loc[0, "Inventory_INR"]
    assert wc_res.audit.balance_sheet_balanced is True

    # 4. Test Capex change
    capex_modified_m = ModelAssumptions(annual_capex_inr=20_000_000.0)  # INR 2.0 Cr annual capex
    capex_res = run_full_model(capex_modified_m)
    assert capex_res.depreciation_schedule.loc[0, "Capex_INR"] == 0.0
    assert capex_res.cash_flow_statement.loc[0, "Capex_INR"] == 0.0
    assert capex_res.depreciation_schedule.loc[1, "Capex_INR"] == 20_000_000.0
    assert capex_res.cash_flow_statement.loc[1, "Capex_INR"] == -20_000_000.0
    assert capex_res.audit.balance_sheet_balanced is True

def test_regression_partial_edits_preserve_unrelated_assumptions():
    # Verify that changing one assumption strictly preserves all other assumptions and propagates downstream
    base = ModelAssumptions()
    new_growth_a = list(base.product_a.annual_volume_growth_rates)
    new_growth_a[3] = 0.15
    mod1 = ModelAssumptions(
        product_a=ProductAssumption(
            name=base.product_a.name,
            base_volume_tonnes=base.product_a.base_volume_tonnes,
            annual_volume_growth_rates=new_growth_a,
            base_asp_inr_per_tonne=base.product_a.base_asp_inr_per_tonne
        ),
        fixed_assets=base.fixed_assets,
        annual_capex_inr=base.annual_capex_inr,
        long_term_debt=base.long_term_debt,
        short_term_debt=base.short_term_debt,
        working_capital=base.working_capital,
        base_fixed_costs_inr=base.base_fixed_costs_inr,
        corporate_tax_rate=base.corporate_tax_rate
    )
    assert mod1.product_b.annual_volume_growth_rates == base.product_b.annual_volume_growth_rates
    assert mod1.fixed_assets == base.fixed_assets
    assert mod1.annual_capex_inr == base.annual_capex_inr
    assert mod1.base_fixed_costs_inr == base.base_fixed_costs_inr
    res1 = run_full_model(mod1)
    base_res = run_full_model(base)
    assert res1.operating_forecast.loc[0, 'Product_A_Volume_Tonnes'] == base_res.operating_forecast.loc[0, 'Product_A_Volume_Tonnes']
    assert res1.operating_forecast.loc[4, 'Product_A_Volume_Tonnes'] > base_res.operating_forecast.loc[4, 'Product_A_Volume_Tonnes']
    assert (res1.operating_forecast['Product_B_Volume_Tonnes'] == base_res.operating_forecast['Product_B_Volume_Tonnes']).all()
    assert res1.audit.balance_sheet_balanced is True

def test_regression_fixed_assets_and_debt_propagation():
    # Verify that changing fixed asset register and debt parameters propagates into depreciation debt and statements
    base = ModelAssumptions()
    mod_fa = list(base.fixed_assets)
    mod_fa[0] = FixedAssetInput(
        category_name=base.fixed_assets[0].category_name,
        gross_asset_value_inr=500_000_000.0,
        useful_life_years=20,
        salvage_value_pct=0.05
    )
    mod_m = ModelAssumptions(
        fixed_assets=mod_fa,
        annual_capex_inr=base.annual_capex_inr,
        long_term_debt=DebtFacilityInput(
            facility_type=base.long_term_debt.facility_type,
            opening_balance_inr=300_000_000.0,
            annual_interest_rate=0.10
        ),
        base_fixed_costs_inr=150_000_000.0,
    )
    assert mod_m.product_a == base.product_a
    assert mod_m.product_b == base.product_b
    assert mod_m.working_capital == base.working_capital
    res = run_full_model(mod_m)
    assert res.operating_forecast.loc[0, 'Fixed_Operating_Costs_INR'] == 150_000_000.0
    assert res.debt_schedule.loc[0, 'Long_Term_Debt_INR'] == 300_000_000.0
    assert res.debt_schedule.loc[0, 'LT_Interest_Expense_INR'] == 30_000_000.0
    assert res.audit.balance_sheet_balanced is True
def test_capex_timing_and_lagged_depreciation():
    base = ModelAssumptions(annual_capex_inr=0.0)
    base_res = run_full_model(base)

    capex_val = 100_000_000.0
    capex_m = ModelAssumptions(
        annual_capex_inr=capex_val,
        capex_useful_life_years=10,
        capex_salvage_value_pct=0.0
    )
    res = run_full_model(capex_m)
    depr_df = res.depreciation_schedule

    # F26A (Period 0): Synthetic actual receives zero forecast capex
    assert depr_df.loc[0, "Capex_INR"] == 0.0
    assert depr_df.loc[0, "Depreciation_Additions_INR"] == 0.0
    assert depr_df.loc[0, "Ending_Gross_PPE_INR"] == depr_df.loc[0, "Beginning_Gross_PPE_INR"]

    # F27E (Period 1): Configured annual capex applies; year-end capex incurs 0 depreciation in F27E
    assert depr_df.loc[1, "Capex_INR"] == capex_val
    assert depr_df.loc[1, "Depreciation_Additions_INR"] == 0.0
    assert depr_df.loc[1, "Ending_Gross_PPE_INR"] == depr_df.loc[1, "Beginning_Gross_PPE_INR"] + capex_val

    # Depreciation on F27E capex begins in F28P (Period 2)
    assert depr_df.loc[2, "Depreciation_Additions_INR"] == pytest.approx(10_000_000.0)
    assert depr_df.loc[3, "Depreciation_Additions_INR"] == pytest.approx(20_000_000.0)

    # Reconcile Gross PPE, Net PPE, and accumulated depreciation across all periods
    for i in range(len(depr_df)):
        assert depr_df.loc[i, "Ending_Gross_PPE_INR"] == pytest.approx(
            depr_df.loc[i, "Beginning_Gross_PPE_INR"] + depr_df.loc[i, "Capex_INR"]
        )
        assert depr_df.loc[i, "Ending_Accum_Depr_INR"] == pytest.approx(
            depr_df.loc[i, "Beginning_Accum_Depr_INR"] + depr_df.loc[i, "Depreciation_INR"]
        )
        assert depr_df.loc[i, "Ending_Net_PPE_INR"] == pytest.approx(
            depr_df.loc[i, "Ending_Gross_PPE_INR"] - depr_df.loc[i, "Ending_Accum_Depr_INR"]
        )
        assert depr_df.loc[i, "Ending_Net_PPE_INR"] == pytest.approx(
            depr_df.loc[i, "Beginning_Net_PPE_INR"] + depr_df.loc[i, "Capex_INR"] - depr_df.loc[i, "Depreciation_INR"]
        )
    assert res.audit.balance_sheet_balanced is True


def test_long_term_debt_amortization_and_cmltd():
    m = ModelAssumptions(
        long_term_debt=DebtFacilityInput(
            facility_type='Long-Term Debt',
            opening_balance_inr=250_000_000.0,
            annual_interest_rate=0.10
        ),
        lt_debt_repayment_tenure_years=5
    )
    res = run_full_model(m)
    ds = res.debt_schedule

    assert ds.loc[0, 'Beginning_Long_Term_Debt_INR'] == 250_000_000.0
    assert ds.loc[0, 'LT_Principal_Repayment_INR'] == 0.0
    assert ds.loc[0, 'Ending_Long_Term_Debt_INR'] == 250_000_000.0
    assert ds.loc[0, 'CMLTD_INR'] == 50_000_000.0

    assert ds.loc[1, 'Beginning_Long_Term_Debt_INR'] == 250_000_000.0
    assert ds.loc[1, 'LT_Principal_Repayment_INR'] == 50_000_000.0
    assert ds.loc[1, 'Ending_Long_Term_Debt_INR'] == 200_000_000.0
    assert ds.loc[1, 'CMLTD_INR'] == 50_000_000.0
    assert ds.loc[1, 'Non_Current_LT_Debt_INR'] == 150_000_000.0

    assert ds.loc[5, 'Ending_Long_Term_Debt_INR'] == 0.0
    assert ds.loc[6, 'Ending_Long_Term_Debt_INR'] == 0.0
    assert ds.loc[6, 'LT_Principal_Repayment_INR'] == 0.0
    assert (ds['Ending_Long_Term_Debt_INR'] >= 0.0).all()

    assert ds.loc[1, 'LT_Interest_Expense_INR'] == 250_000_000.0 * 0.10
    assert ds.loc[2, 'LT_Interest_Expense_INR'] == 200_000_000.0 * 0.10
    assert ds.loc[3, 'LT_Interest_Expense_INR'] == 150_000_000.0 * 0.10

    assert res.audit.balance_sheet_balanced is True


def test_interest_and_cash_flow_presentation_ind_as_7():
    m = ModelAssumptions()
    res = run_full_model(m)
    cfs = res.cash_flow_statement
    is_df = res.income_statement

    for i in range(len(cfs)):
        pat = is_df.loc[i, 'Net_Profit_INR']
        depr = is_df.loc[i, 'Depreciation_INR']
        interest = is_df.loc[i, 'Interest_Expense_INR']
        wc_chg = cfs.loc[i, 'Change_in_NWC_INR']

        assert cfs.loc[i, 'CFO_INR'] == pytest.approx(pat + depr + interest + wc_chg)
        assert cfs.loc[i, 'Interest_Paid_INR'] == pytest.approx(-interest)

    assert res.audit.cash_reconciled is True
    assert res.audit.balance_sheet_balanced is True


def test_minimum_cash_and_short_term_debt_revolver():
    m = ModelAssumptions(
        minimum_cash_inr=50_000_000.0,
        short_term_debt=DebtFacilityInput('Short-Term Debt', opening_balance_inr=80_000_000.0, annual_interest_rate=0.0975)
    )
    res = run_full_model(m)
    bs = res.balance_sheet

    for i in range(1, len(bs)):
        assert bs.loc[i, 'Cash_and_Equivalents_INR'] == pytest.approx(50_000_000.0)

    st_debt_series = bs['Short_Term_Debt_INR'].tolist()
    liquid_inv_series = bs['Liquid_Investments_INR'].tolist()
    assert min(st_debt_series) == 0.0
    assert max(liquid_inv_series) > 0.0
    assert res.audit.balance_sheet_balanced is True


def test_cash_deficit_triggers_st_debt_drawdown():
    m = ModelAssumptions(
        annual_capex_inr=700_000_000.0,
        minimum_cash_inr=50_000_000.0,
        short_term_debt=DebtFacilityInput('Short-Term Debt', opening_balance_inr=80_000_000.0, annual_interest_rate=0.0975)
    )
    res = run_full_model(m)
    bs = res.balance_sheet

    assert bs['Short_Term_Debt_INR'].max() > 80_000_000.0
    for i in range(1, len(bs)):
        assert bs.loc[i, 'Cash_and_Equivalents_INR'] == pytest.approx(50_000_000.0)
    assert res.audit.balance_sheet_balanced is True


def test_dividends_flow_and_cash_cap():
    m = ModelAssumptions(
        dividend_payout_ratio=0.30,
        minimum_cash_inr=50_000_000.0
    )
    res = run_full_model(m)
    cfs = res.cash_flow_statement
    is_df = res.income_statement

    for i in range(1, len(cfs)):
        pat = is_df.loc[i, 'Net_Profit_INR']
        div_paid = abs(cfs.loc[i, 'Dividends_Paid_INR'])
        if pat > 0:
            assert div_paid > 0.0
            assert div_paid <= pat * 0.30 + 0.01

    assert res.audit.retained_earnings_reconciled is True
    assert res.audit.balance_sheet_balanced is True
def test_single_assumption_edit_preserves_all_others_phase3():
    # Verify that editing only a new Phase 3 assumption leaves all unrelated assumptions intact
    base = ModelAssumptions()
    mod = ModelAssumptions(dividend_payout_ratio=0.45)

    assert mod.product_a == base.product_a
    assert mod.product_b == base.product_b
    assert mod.variable_costs == base.variable_costs
    assert mod.inflation == base.inflation
    assert mod.fixed_assets == base.fixed_assets
    assert mod.long_term_debt == base.long_term_debt
    assert mod.short_term_debt == base.short_term_debt
    assert mod.working_capital == base.working_capital
    assert mod.base_fixed_costs_inr == base.base_fixed_costs_inr
    assert mod.corporate_tax_rate == base.corporate_tax_rate
    assert mod.capex_useful_life_years == base.capex_useful_life_years
    assert mod.lt_debt_repayment_tenure_years == base.lt_debt_repayment_tenure_years
    assert mod.minimum_cash_inr == base.minimum_cash_inr

    res = run_full_model(mod)
    assert res.audit.balance_sheet_balanced is True


def test_phase4_st_debt_interest_coupling_on_repayment():
    res = run_full_model(ModelAssumptions())
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet
    cfs_df = res.cash_flow_statement

    assert debt_df.loc[0, 'Beginning_Short_Term_Debt_INR'] == 80_000_000.0
    assert debt_df.loc[0, 'Ending_Short_Term_Debt_INR'] == 0.0
    assert bs_df.loc[0, 'Short_Term_Borrowings_INR'] == 0.0
    assert is_df.loc[0, 'Short_Term_Interest_Expense_INR'] == 80_000_000.0 * 0.0975

    for i in range(1, len(debt_df)):
        assert debt_df.loc[i, 'Beginning_Short_Term_Debt_INR'] == 0.0
        assert debt_df.loc[i, 'Ending_Short_Term_Debt_INR'] == 0.0
        assert bs_df.loc[i, 'Short_Term_Borrowings_INR'] == 0.0
        assert is_df.loc[i, 'Short_Term_Interest_Expense_INR'] == 0.0

    assert res.audit.balance_sheet_balanced is True
    assert res.audit.cash_flow_reconciled is True


def test_phase4_st_debt_interest_coupling_on_drawdown():
    m = ModelAssumptions(
        capex_f28p_inr=180_000_000.0,
        minimum_cash_inr=50_000_000.0,
        short_term_debt=ShortTermDebtAssumptions(opening_balance_inr=80_000_000.0, interest_rate=0.10)
    )
    res = run_full_model(m)
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet

    drawn_f28p = debt_df.loc[2, 'Short_Term_Debt_Net_Draw_INR']
    end_debt_f28p = debt_df.loc[2, 'Ending_Short_Term_Debt_INR']
    assert end_debt_f28p > 0.0
    assert bs_df.loc[2, 'Short_Term_Borrowings_INR'] == end_debt_f28p

    assert debt_df.loc[3, 'Beginning_Short_Term_Debt_INR'] == end_debt_f28p
    expected_f29p_interest = end_debt_f28p * 0.10
    assert abs(is_df.loc[3, 'Short_Term_Interest_Expense_INR'] - expected_f29p_interest) < 0.01

    assert res.audit.balance_sheet_balanced is True


def test_phase4_st_debt_interest_coupling_on_repayment():
    res = run_full_model(ModelAssumptions())
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet

    # F26A:
    assert debt_df.loc[0, 'Beginning_Short_Term_Debt_INR'] == 80_000_000.0
    assert debt_df.loc[0, 'Ending_Short_Term_Debt_INR'] == 0.0
    assert bs_df.loc[0, 'Short_Term_Debt_INR'] == 0.0
    assert abs(debt_df.loc[0, 'ST_Interest_Expense_INR'] - (80_000_000.0 * 0.0975)) < 0.01

    # F27E through F32P:
    for i in range(1, len(debt_df)):
        assert debt_df.loc[i, 'Beginning_Short_Term_Debt_INR'] == 0.0
        assert debt_df.loc[i, 'Ending_Short_Term_Debt_INR'] == 0.0
        assert bs_df.loc[i, 'Short_Term_Debt_INR'] == 0.0
        assert debt_df.loc[i, 'ST_Interest_Expense_INR'] == 0.0

    # Balance sheet balances and cash flow reconciles across all seven periods
    assert res.audit.balance_sheet_balanced is True
    assert res.audit.cash_flow_reconciled is True


def test_phase4_st_debt_interest_coupling_on_drawdown():
    # Set capex very high in F28P (index 2) to force a deficit and ST debt draw
    m = ModelAssumptions(
        capex_f28p_inr=180_000_000.0,
        minimum_cash_inr=50_000_000.0,
        short_term_debt=DebtAssumptions(opening_balance_inr=80_000_000.0, interest_rate=0.10)
    )
    res = run_full_model(m)
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet

    # F28P (index 2): capex triggers draw
    drawn_f28p = debt_df.loc[2, 'Short_Term_Debt_Net_Draw_INR']
    end_debt_f28p = debt_df.loc[2, 'Ending_Short_Term_Debt_INR']
    assert end_debt_f28p > 0.0
    assert bs_df.loc[2, 'Short_Term_Debt_INR'] == end_debt_f28p

    # F29P (index 3): Beginning ST debt must equal F28P Ending ST debt
    assert debt_df.loc[3, 'Beginning_Short_Term_Debt_INR'] == end_debt_f28p
    expected_f29p_st_interest = end_debt_f28p * 0.10
    assert abs(debt_df.loc[3, 'ST_Interest_Expense_INR'] - expected_f29p_st_interest) < 0.01

    # Full statement audits pass
    assert res.audit.balance_sheet_balanced is True


def test_phase4_st_debt_interest_coupling_on_repayment():
    res = run_full_model(ModelAssumptions())
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet

    # F26A:
    assert debt_df.loc[0, 'Beginning_Short_Term_Debt_INR'] == 80_000_000.0
    assert debt_df.loc[0, 'Ending_Short_Term_Debt_INR'] == 0.0
    assert bs_df.loc[0, 'Short_Term_Debt_INR'] == 0.0
    assert abs(debt_df.loc[0, 'ST_Interest_Expense_INR'] - (80_000_000.0 * 0.0975)) < 0.01

    # F27E through F32P:
    for i in range(1, len(debt_df)):
        assert debt_df.loc[i, 'Beginning_Short_Term_Debt_INR'] == 0.0
        assert debt_df.loc[i, 'Ending_Short_Term_Debt_INR'] == 0.0
        assert bs_df.loc[i, 'Short_Term_Debt_INR'] == 0.0
        assert debt_df.loc[i, 'ST_Interest_Expense_INR'] == 0.0

    # Balance sheet balances and cash flow reconciles across all seven periods
    assert res.audit.balance_sheet_balanced is True
    assert res.audit.cash_reconciled is True


def test_phase4_st_debt_interest_coupling_on_drawdown():
    # Set capex very high in F28P (index 2) to force a deficit and ST debt draw
    m = ModelAssumptions(
        capex_f28p_inr=180_000_000.0,
        minimum_cash_inr=50_000_000.0,
        short_term_debt=DebtFacilityInput(opening_balance_inr=80_000_000.0, interest_rate=0.10)
    )
    res = run_full_model(m)
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet

    # F28P (index 2): capex triggers draw
    drawn_f28p = debt_df.loc[2, 'Short_Term_Debt_Net_Draw_INR']
    end_debt_f28p = debt_df.loc[2, 'Ending_Short_Term_Debt_INR']
    assert end_debt_f28p > 0.0
    assert bs_df.loc[2, 'Short_Term_Debt_INR'] == end_debt_f28p

    # F29P (index 3): Beginning ST debt must equal F28P Ending ST debt
    assert debt_df.loc[3, 'Beginning_Short_Term_Debt_INR'] == end_debt_f28p
    expected_f29p_st_interest = end_debt_f28p * 0.10
    assert abs(debt_df.loc[3, 'ST_Interest_Expense_INR'] - expected_f29p_st_interest) < 0.01

    # Full statement audits pass
    assert res.audit.balance_sheet_balanced is True


def test_phase4_st_debt_interest_coupling_on_repayment():
    res = run_full_model(ModelAssumptions())
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet

    # F26A:
    assert debt_df.loc[0, 'Beginning_Short_Term_Debt_INR'] == 80_000_000.0
    assert debt_df.loc[0, 'Ending_Short_Term_Debt_INR'] == 0.0
    assert bs_df.loc[0, 'Short_Term_Debt_INR'] == 0.0
    assert abs(debt_df.loc[0, 'ST_Interest_Expense_INR'] - (80_000_000.0 * 0.0975)) < 0.01

    # F27E through F32P:
    for i in range(1, len(debt_df)):
        assert debt_df.loc[i, 'Beginning_Short_Term_Debt_INR'] == 0.0
        assert debt_df.loc[i, 'Ending_Short_Term_Debt_INR'] == 0.0
        assert bs_df.loc[i, 'Short_Term_Debt_INR'] == 0.0
        assert debt_df.loc[i, 'ST_Interest_Expense_INR'] == 0.0

    # Balance sheet balances and cash flow reconciles across all seven periods
    assert res.audit.balance_sheet_balanced is True
    assert res.audit.cash_reconciled is True


def test_phase4_st_debt_interest_coupling_on_drawdown():
    # Set capex very high in F28P (index 2) to force a deficit and ST debt draw
    m = ModelAssumptions(
        capex_f28p_inr=180_000_000.0,
        minimum_cash_inr=50_000_000.0,
        short_term_debt=DebtFacilityInput(facility_type='Working Capital / CC / OD', opening_balance_inr=80_000_000.0, annual_interest_rate=0.10)
    )
    res = run_full_model(m)
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet

    # F28P (index 2): capex triggers draw
    drawn_f28p = debt_df.loc[2, 'Short_Term_Debt_Net_Draw_INR']
    end_debt_f28p = debt_df.loc[2, 'Ending_Short_Term_Debt_INR']
    assert end_debt_f28p > 0.0
    assert bs_df.loc[2, 'Short_Term_Debt_INR'] == end_debt_f28p

    # F29P (index 3): Beginning ST debt must equal F28P Ending ST debt
    assert debt_df.loc[3, 'Beginning_Short_Term_Debt_INR'] == end_debt_f28p
    expected_f29p_st_interest = end_debt_f28p * 0.10
    assert abs(debt_df.loc[3, 'ST_Interest_Expense_INR'] - expected_f29p_st_interest) < 0.01

    # Full statement audits pass
    assert res.audit.balance_sheet_balanced is True


def test_phase4_st_debt_interest_coupling_on_repayment():
    res = run_full_model(ModelAssumptions())
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet

    # F26A:
    assert debt_df.loc[0, 'Beginning_Short_Term_Debt_INR'] == 80_000_000.0
    assert debt_df.loc[0, 'Ending_Short_Term_Debt_INR'] == 0.0
    assert bs_df.loc[0, 'Short_Term_Debt_INR'] == 0.0
    assert abs(debt_df.loc[0, 'ST_Interest_Expense_INR'] - (80_000_000.0 * 0.0975)) < 0.01

    # F27E through F32P:
    for i in range(1, len(debt_df)):
        assert debt_df.loc[i, 'Beginning_Short_Term_Debt_INR'] == 0.0
        assert debt_df.loc[i, 'Ending_Short_Term_Debt_INR'] == 0.0
        assert bs_df.loc[i, 'Short_Term_Debt_INR'] == 0.0
        assert debt_df.loc[i, 'ST_Interest_Expense_INR'] == 0.0

    # Balance sheet balances and cash flow reconciles across all seven periods
    assert res.audit.balance_sheet_balanced is True
    assert res.audit.cash_reconciled is True


def test_phase4_st_debt_interest_coupling_on_drawdown():
    # Set high annual capex to force a deficit and ST debt draw
    m = ModelAssumptions(
        annual_capex_inr=150_000_000.0,
        minimum_cash_inr=50_000_000.0,
        short_term_debt=DebtFacilityInput(facility_type='Working Capital / CC / OD', opening_balance_inr=80_000_000.0, annual_interest_rate=0.10)
    )
    res = run_full_model(m)
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet

    # Look for the first period where ending ST debt is positive
    draw_periods = debt_df[debt_df['Ending_Short_Term_Debt_INR'] > 0.0].index.tolist()
    assert len(draw_periods) > 0, 'High capex should trigger ST debt draw'
    first_draw_idx = draw_periods[0]
    assert first_draw_idx < len(debt_df) - 1, 'Should have subsequent period to test interest'

    next_idx = first_draw_idx + 1
    end_debt = debt_df.loc[first_draw_idx, 'Ending_Short_Term_Debt_INR']
    assert bs_df.loc[first_draw_idx, 'Short_Term_Debt_INR'] == end_debt

    # Next period: Beginning ST debt must equal prior Ending ST debt
    assert debt_df.loc[next_idx, 'Beginning_Short_Term_Debt_INR'] == end_debt
    expected_interest = end_debt * 0.10
    assert abs(debt_df.loc[next_idx, 'ST_Interest_Expense_INR'] - expected_interest) < 0.01

    # Full statement audits pass
    assert res.audit.balance_sheet_balanced is True


def test_phase4_st_debt_interest_coupling_on_repayment():
    res = run_full_model(ModelAssumptions())
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet

    # F26A:
    assert debt_df.loc[0, 'Beginning_Short_Term_Debt_INR'] == 80_000_000.0
    assert debt_df.loc[0, 'Ending_Short_Term_Debt_INR'] == 0.0
    assert bs_df.loc[0, 'Short_Term_Debt_INR'] == 0.0
    assert abs(debt_df.loc[0, 'ST_Interest_Expense_INR'] - (80_000_000.0 * 0.0975)) < 0.01

    # F27E through F32P:
    for i in range(1, len(debt_df)):
        assert debt_df.loc[i, 'Beginning_Short_Term_Debt_INR'] == 0.0
        assert debt_df.loc[i, 'Ending_Short_Term_Debt_INR'] == 0.0
        assert bs_df.loc[i, 'Short_Term_Debt_INR'] == 0.0
        assert debt_df.loc[i, 'ST_Interest_Expense_INR'] == 0.0

    # Balance sheet balances and cash flow reconciles across all seven periods
    assert res.audit.balance_sheet_balanced is True
    assert res.audit.cash_reconciled is True


def test_phase4_st_debt_interest_coupling_on_drawdown():
    # Set high annual capex (70 Cr / year) to force a deficit and ST debt draw
    m = ModelAssumptions(
        annual_capex_inr=700_000_000.0,
        minimum_cash_inr=50_000_000.0,
        short_term_debt=DebtFacilityInput(facility_type='Working Capital / CC / OD', opening_balance_inr=80_000_000.0, annual_interest_rate=0.10)
    )
    res = run_full_model(m)
    debt_df = res.debt_schedule
    is_df = res.income_statement
    bs_df = res.balance_sheet

    # Look for the first period where ending ST debt is positive
    draw_periods = debt_df[debt_df['Ending_Short_Term_Debt_INR'] > 0.0].index.tolist()
    assert len(draw_periods) > 0, 'High capex should trigger ST debt draw'
    first_draw_idx = draw_periods[0]
    assert first_draw_idx < len(debt_df) - 1, 'Should have subsequent period to test interest'

    next_idx = first_draw_idx + 1
    end_debt = debt_df.loc[first_draw_idx, 'Ending_Short_Term_Debt_INR']
    assert bs_df.loc[first_draw_idx, 'Short_Term_Debt_INR'] == end_debt

    # Next period: Beginning ST debt must equal prior Ending ST debt
    assert debt_df.loc[next_idx, 'Beginning_Short_Term_Debt_INR'] == end_debt
    expected_interest = end_debt * 0.10
    assert abs(debt_df.loc[next_idx, 'ST_Interest_Expense_INR'] - expected_interest) < 0.01

    # Full statement audits pass
    assert res.audit.balance_sheet_balanced is True
    assert res.audit.cash_reconciled is True
    assert res.audit.retained_earnings_reconciled is True


def test_phase4_st_debt_interest_rate_propagation():
    rate_1 = 0.08
    rate_2 = 0.12
    m1 = ModelAssumptions(short_term_debt=DebtFacilityInput(facility_type='Working Capital / CC / OD', opening_balance_inr=80_000_000.0, annual_interest_rate=rate_1))
    m2 = ModelAssumptions(short_term_debt=DebtFacilityInput(facility_type='Working Capital / CC / OD', opening_balance_inr=80_000_000.0, annual_interest_rate=rate_2))

    res1 = run_full_model(m1)
    res2 = run_full_model(m2)

    # In F26A (opening balance = 80m):
    assert abs(res1.debt_schedule.loc[0, 'ST_Interest_Expense_INR'] - 80_000_000.0 * rate_1) < 0.01
    assert abs(res2.debt_schedule.loc[0, 'ST_Interest_Expense_INR'] - 80_000_000.0 * rate_2) < 0.01

    assert res1.audit.balance_sheet_balanced is True
    assert res2.audit.balance_sheet_balanced is True
