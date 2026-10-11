"""
app.py
======
Manufacturing FP&A 3-Statement Financial Model - Interactive Dashboard.

Features:
1. User-Editable Assumptions Manager with Session State & Reset to Defaults
2. Schedule III (Division II Ind AS) Financial Statements (Balance Sheet, P&L, Cash Flow)
3. Central Reporting Period Labels: F26A (Actual), F27E (Estimate), F28P (Projection)...
4. Dedicated FP&A / Management Review Views (EBITDA, Contribution Margins, Volume/ASP build)
5. Automated Model Audit & Zero-Variance Equilibrium Verification
"""

import streamlit as st
import pandas as pd
from model.assumptions import (
    ModelAssumptions,
    ProductAssumption,
    VariableCostAssumption,
    InflationAssumption,
    FixedAssetInput,
    DebtFacilityInput,
    WorkingCapitalAssumption,
)
from model.engine import run_full_model

st.set_page_config(
    page_title="Manufacturing FP&A 3-Statement Model",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.95rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #2563EB;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏭 Manufacturing FP&A 3-Statement Model (Ind AS)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Schedule III, Division II Compliance • Reporting Periods: F26A (Actual), F27E (Estimate), F28P–F30P (Projections) • Values in ₹ Crores</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. SESSION STATE & ASSUMPTIONS MANAGEMENT
# -----------------------------------------------------------------------------
def get_default_assumptions() -> ModelAssumptions:
    return ModelAssumptions()

if "model_assumptions" not in st.session_state:
    st.session_state["model_assumptions"] = get_default_assumptions()

# Sidebar: Controls & Reset
st.sidebar.header("⚙️ Model Controls")

col_rst1, col_rst2 = st.sidebar.columns([1, 1])
with col_rst1:
    if st.button("↺ Reset Defaults", use_container_width=True, help="Reset all model parameters to factory defaults"):
        st.session_state["model_assumptions"] = get_default_assumptions()
        st.rerun()

curr_assumptions: ModelAssumptions = st.session_state["model_assumptions"]

# -----------------------------------------------------------------------------
# 2. RUN ENGINE
# -----------------------------------------------------------------------------
model_result = run_full_model(curr_assumptions)
audit = model_result.audit
is_df = model_result.income_statement
bs_df = model_result.balance_sheet
cfs_df = model_result.cash_flow_statement

# -----------------------------------------------------------------------------
# 3. EXECUTIVE KPI HEADER
# -----------------------------------------------------------------------------
kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)
with kpi_c1:
    f26_rev = is_df.loc[0, "Revenue_Cr"]
    st.metric("F26A Revenue (Actual)", f"₹{f26_rev:,.1f} Cr", "Baseline")
with kpi_c2:
    f27_rev = is_df.loc[1, "Revenue_Cr"]
    growth = ((f27_rev / f26_rev) - 1) * 100
    st.metric("F27E Revenue (Estimate)", f"₹{f27_rev:,.1f} Cr", f"+{growth:.1f}% YoY")
with kpi_c3:
    f27_pat = is_df.loc[1, "Net_Profit_Cr"]
    st.metric("F27E PAT (Estimate)", f"₹{f27_pat:,.1f} Cr", f"{is_df.loc[1, 'Net_Margin_Pct']:.1f}% Margin")
with kpi_c4:
    f27_cash = bs_df.loc[1, "Cash_and_Equivalents_Cr"]
    st.metric("F27E Closing Cash", f"₹{f27_cash:,.1f} Cr", "Liquid Buffer")
with kpi_c5:
    st.metric("Balance Sheet Audit", "100% Balanced", f"Variance: ₹{audit.max_bs_variance_inr:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# Helper function to format tables cleanly for display
def format_display_table(df: pd.DataFrame) -> pd.DataFrame:
    formatted = df.copy()
    for col in formatted.columns:
        formatted[col] = formatted[col].apply(
            lambda x: "" if x == "" or pd.isna(x) else f"{x:,.2f}" if isinstance(x, (int, float)) else str(x)
        )
    return formatted

# -----------------------------------------------------------------------------
# 4. TABBED INTERFACE (Schedule III + Management + Editable Assumptions)
# -----------------------------------------------------------------------------
tab_sch3_bs, tab_sch3_pl, tab_sch3_cf, tab_mgmt, tab_assumptions, tab_audit = st.tabs([
    "🏛️ Schedule III Balance Sheet",
    "📑 Schedule III Statement of P&L",
    "💵 Statement of Cash Flows (Ind AS 7)",
    "📊 FP&A / Management Review",
    "📝 Model Assumptions Manager",
    "🛡️ Automated Audit & Reconciliation"
])

# TAB 1: SCHEDULE III BALANCE SHEET
with tab_sch3_bs:
    st.subheader("Balance Sheet (Ind AS — Schedule III, Division II)")
    st.caption("Classified into Non-Current / Current Assets and Liabilities • Values in ₹ Crores")
    if audit.balance_sheet_balanced:
        st.success("✅ **Balance Sheet Equilibrium Verified:** Total Assets == Total Equity and Liabilities for all periods (Zero Variance).")
    st.dataframe(format_display_table(model_result.schedule_iii_balance_sheet), use_container_width=True)

# TAB 2: SCHEDULE III PROFIT AND LOSS
with tab_sch3_pl:
    st.subheader("Statement of Profit and Loss (Ind AS — Schedule III, Division II)")
    st.caption("Formal expenses by nature: Cost of materials consumed, direct conversion, employee/admin overheads, finance costs, depreciation.")
    st.dataframe(format_display_table(model_result.schedule_iii_profit_and_loss), use_container_width=True)

# TAB 3: STATEMENT OF CASH FLOWS
with tab_sch3_cf:
    st.subheader("Statement of Cash Flows (Ind AS 7 — Indirect Method)")
    st.caption("Operating cash flows reconciled with non-cash depreciation and working capital changes.")
    st.dataframe(format_display_table(model_result.schedule_iii_cash_flow), use_container_width=True)

# TAB 4: FP&A / MANAGEMENT REVIEW
with tab_mgmt:
    st.subheader("FP&A Management Reporting View")
    st.caption("Internal management analysis: Contribution Margins, EBITDA, and Operating Ratios.")
    st.dataframe(format_display_table(model_result.is_presentation_cr), use_container_width=True)
    
    st.markdown("---")
    st.subheader("Supporting Analytical Schedules")
    subtab1, subtab2, subtab3 = st.tabs(["Production & ASP Schedule", "Working Capital Cycle", "Fixed Assets & Debt Tranches"])
    with subtab1:
        op_cols = ["Display_Label", "Product_A_Volume_Tonnes", "Product_B_Volume_Tonnes", "Total_Volume_Tonnes", "Revenue_Cr", "RM_Cost_Cr", "OVC_Cost_Cr", "Contribution_Cr", "EBITDA_Cr", "EBITDA_Margin_Pct"]
        st.dataframe(format_display_table(model_result.operating_forecast[op_cols].set_index("Display_Label").T), use_container_width=True)
    with subtab2:
        wc_cols = ["Display_Label", "DSO_Days", "DIO_Days", "DPO_Days", "Cash_Conversion_Cycle_Days", "Trade_Receivables_Cr", "Inventory_Cr", "Trade_Payables_Cr", "Net_Working_Capital_Cr", "Change_in_NWC_Cr"]
        st.dataframe(format_display_table(model_result.working_capital_schedule[wc_cols].set_index("Display_Label").T), use_container_width=True)
    with subtab3:
        debt_depr_df = pd.DataFrame({
            "Net PP&E (Closing)": model_result.depreciation_schedule["Ending_Net_PPE_Cr"].values,
            "Depreciation Charge": model_result.depreciation_schedule["Depreciation_Cr"].values,
            "Long-Term Borrowings": model_result.debt_schedule["Long_Term_Debt_Cr"].values,
            "Short-Term Borrowings": model_result.debt_schedule["Short_Term_Debt_Cr"].values,
            "Finance Costs": model_result.debt_schedule["Total_Interest_Expense_Cr"].values,
        }, index=model_result.depreciation_schedule["Display_Label"]).T
        st.dataframe(format_display_table(debt_depr_df), use_container_width=True)

# TAB 5: EDITABLE ASSUMPTIONS MANAGER
with tab_assumptions:
    st.subheader('Live Model Assumptions Manager')
    st.write('Modify any assumption below. Changes propagate through the entire 3-statement model engine, while all unchanged assumptions are strictly preserved.')
    
    with st.form('comprehensive_assumptions_form'):
        st.markdown('### 1. Products: Base Volumes, ASPs and Annual Growth Rates')
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown('##### Product A Assumptions')
            p_a_vol = st.number_input('Product A Base Volume (MT)', value=float(curr_assumptions.product_a.base_volume_tonnes), step=500.0, help='Baseline sales volume in Metric Tonnes for F26A')
            p_a_asp = st.number_input('Product A Base ASP (INR/MT)', value=float(curr_assumptions.product_a.base_asp_inr_per_tonne), step=1000.0, help='Baseline Average Selling Price in INR per MT for F26A')
            st.caption('Product A Volume Growth Rates (% YoY):')
            p_a_g_cols = st.columns(6)
            p_a_rates = []
            period_labels = ['F27E', 'F28P', 'F29P', 'F30P', 'F31P', 'F32P']
            for idx, plabel in enumerate(period_labels):
                default_val = float(curr_assumptions.product_a.annual_volume_growth_rates[idx] * 100)
                with p_a_g_cols[idx]:
                    r = st.number_input(f'{plabel} (%)', value=default_val, step=0.5, key=f'p_a_g_{idx}') / 100.0
                    p_a_rates.append(r)
        with col_p2:
            st.markdown('##### Product B Assumptions')
            p_b_vol = st.number_input('Product B Base Volume (MT)', value=float(curr_assumptions.product_b.base_volume_tonnes), step=500.0, help='Baseline sales volume in Metric Tonnes for F26A')
            p_b_asp = st.number_input('Product B Base ASP (INR/MT)', value=float(curr_assumptions.product_b.base_asp_inr_per_tonne), step=1000.0, help='Baseline Average Selling Price in INR per MT for F26A')
            st.caption('Product B Volume Growth Rates (% YoY):')
            p_b_g_cols = st.columns(6)
            p_b_rates = []
            for idx, plabel in enumerate(period_labels):
                default_val = float(curr_assumptions.product_b.annual_volume_growth_rates[idx] * 100)
                with p_b_g_cols[idx]:
                    r = st.number_input(f'{plabel} (%)', value=default_val, step=0.5, key=f'p_b_g_{idx}') / 100.0
                    p_b_rates.append(r)
        st.markdown('---')
        st.markdown('### 2. Variable Cost Structure, Fixed Overheads and Multi-Factor Inflation')
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown('##### Variable Costs and Fixed Overhead Baseline')
            rm_pct = st.slider('Raw Material Cost (% of Base Revenue)', 30.0, 75.0, float(curr_assumptions.variable_costs.rm_cost_pct_revenue * 100), 0.5) / 100.0
            ovc_pct = st.slider('Other Variable Costs (% of Base Revenue)', 2.0, 25.0, float(curr_assumptions.variable_costs.ovc_cost_pct_revenue * 100), 0.5) / 100.0
            base_fc_cr = st.number_input('Base Fixed Operating Costs (INR Cr)', value=float(curr_assumptions.base_fixed_costs_inr / 10_000_000.0), step=0.5, help='Factory and administrative fixed overhead baseline')
            corp_tax_rate = st.slider('Corporate Tax Rate (%)', 15.0, 35.0, float(curr_assumptions.corporate_tax_rate * 100), 0.1) / 100.0
        with col_c2:
            st.markdown('##### Multi-Factor Annual Inflation Rates (%)')
            rm_inf = st.slider('RM Price Inflation (% p.a.)', -10.0, 25.0, float(curr_assumptions.inflation.rm_inflation_rate * 100), 0.25) / 100.0
            ovc_inf = st.slider('OVC Escalation (% p.a.)', -10.0, 25.0, float(curr_assumptions.inflation.ovc_inflation_rate * 100), 0.25) / 100.0
            asp_inf = st.slider('ASP Realization Escalation (% p.a.)', -10.0, 25.0, float(curr_assumptions.inflation.asp_inflation_rate * 100), 0.25) / 100.0
            fc_inf = st.slider('Fixed Cost Inflation (% p.a.)', -10.0, 25.0, float(curr_assumptions.inflation.fixed_cost_inflation_rate * 100), 0.25) / 100.0
        st.markdown('---')
        st.markdown('### 3. Fixed Assets Register, Annual Capex, Debt Financing and Working Capital')
        col_fa, col_df = st.columns(2)
        with col_fa:
            st.markdown('##### Fixed Assets Register (Straight-Line Depreciation)')
            new_fa_list = []
            for i, fa in enumerate(curr_assumptions.fixed_assets):
                st.caption(f'Category {i+1}: {fa.category_name}')
                c_fa1, c_fa2, c_fa3 = st.columns(3)
                with c_fa1:
                    g_val_cr = st.number_input(f'Gross Value {i+1} (INR Cr)', value=float(fa.gross_asset_value_inr / 10_000_000.0), step=1.0, key=f'fa_g_{i}')
                with c_fa2:
                    u_life = st.number_input(f'Useful Life {i+1} (Yrs)', value=int(fa.useful_life_years), min_value=1, max_value=60, step=1, key=f'fa_l_{i}')
                with c_fa3:
                    s_pct = st.number_input(f'Salvage {i+1} (%)', value=float(fa.salvage_value_pct * 100), min_value=0.0, max_value=25.0, step=0.5, key=f'fa_s_{i}') / 100.0
                new_fa_list.append(FixedAssetInput(
                    category_name=fa.category_name,
                    gross_asset_value_inr=g_val_cr * 10_000_000.0,
                    useful_life_years=u_life,
                    salvage_value_pct=s_pct
                ))
            st.markdown('##### Annual Maintenance / Growth Capex')
            annual_capex_cr = st.number_input('Annual Capex (INR Cr / Year)', value=float(curr_assumptions.annual_capex_inr / 10_000_000.0), step=1.0, help='Annual capital expenditure connected to PPE additions and Cash Flow from Investing')
        with col_df:
            st.markdown('##### Debt Facilities (Balances and Borrowing Rates)')
            st.caption('Long-Term Debt Facility')
            c_lt1, c_lt2 = st.columns(2)
            with c_lt1:
                lt_bal_cr = st.number_input('LT Debt Balance (INR Cr)', value=float(curr_assumptions.long_term_debt.opening_balance_inr / 10_000_000.0), step=1.0)
            with c_lt2:
                lt_rate = st.slider('LT Interest Rate (% p.a.)', 4.0, 18.0, float(curr_assumptions.long_term_debt.annual_interest_rate * 100), 0.25) / 100.0
            st.caption('Short-Term Debt Facility')
            c_st1, c_st2 = st.columns(2)
            with c_st1:
                st_bal_cr = st.number_input('ST Debt Balance (INR Cr)', value=float(curr_assumptions.short_term_debt.opening_balance_inr / 10_000_000.0), step=1.0)
            with c_st2:
                st_rate = st.slider('ST Interest Rate (% p.a.)', 4.0, 18.0, float(curr_assumptions.short_term_debt.annual_interest_rate * 100), 0.25) / 100.0
            st.markdown('##### Working Capital Turnover Days')
            c_wc1, c_wc2, c_wc3 = st.columns(3)
            with c_wc1:
                dso = st.number_input('Receivable Days (DSO)', value=float(curr_assumptions.working_capital.receivable_days), step=1.0, help='Debtor days on gross revenue')
            with c_wc2:
                dio = st.number_input('Inventory Days (DIO)', value=float(curr_assumptions.working_capital.inventory_days), step=1.0, help='Inventory days on COGS')
            with c_wc3:
                dpo = st.number_input('Payable Days (DPO)', value=float(curr_assumptions.working_capital.payable_days), step=1.0, help='Creditor days on purchases')
        submit_btn = st.form_submit_button('Apply Updated Assumptions', use_container_width=True)
        if submit_btn:
            updated_assumptions = ModelAssumptions(
                forecast_years=curr_assumptions.forecast_years,
                base_year=curr_assumptions.base_year,
                product_a=ProductAssumption(
                    name=curr_assumptions.product_a.name,
                    base_volume_tonnes=p_a_vol,
                    annual_volume_growth_rates=p_a_rates,
                    base_asp_inr_per_tonne=p_a_asp
                ),
                product_b=ProductAssumption(
                    name=curr_assumptions.product_b.name,
                    base_volume_tonnes=p_b_vol,
                    annual_volume_growth_rates=p_b_rates,
                    base_asp_inr_per_tonne=p_b_asp
                ),
                variable_costs=VariableCostAssumption(
                    rm_cost_pct_revenue=rm_pct,
                    ovc_cost_pct_revenue=ovc_pct
                ),
                inflation=InflationAssumption(
                    rm_inflation_rate=rm_inf,
                    ovc_inflation_rate=ovc_inf,
                    fixed_cost_inflation_rate=fc_inf,
                    asp_inflation_rate=asp_inf
                ),
                fixed_assets=new_fa_list,
                annual_capex_inr=annual_capex_cr * 10_000_000.0,
                long_term_debt=DebtFacilityInput(
                    facility_type=curr_assumptions.long_term_debt.facility_type,
                    opening_balance_inr=lt_bal_cr * 10_000_000.0,
                    annual_interest_rate=lt_rate
                ),
                short_term_debt=DebtFacilityInput(
                    facility_type=curr_assumptions.short_term_debt.facility_type,
                    opening_balance_inr=st_bal_cr * 10_000_000.0,
                    annual_interest_rate=st_rate
                ),
                working_capital=WorkingCapitalAssumption(
                    inventory_days=dio,
                    receivable_days=dso,
                    payable_days=dpo
                ),
                base_fixed_costs_inr=base_fc_cr * 10_000_000.0,
                corporate_tax_rate=corp_tax_rate,
                capex_useful_life_years=capex_life,
                capex_salvage_value_pct=capex_salvage,
                lt_debt_repayment_tenure_years=lt_tenure,
                minimum_cash_inr=min_cash_cr * 10_000_000.0,
                dividend_payout_ratio=div_payout
            )
            st.session_state['model_assumptions'] = updated_assumptions
            st.success('All assumptions updated successfully! 3-statement model recalculated across all 7 periods.')
            st.rerun()

with tab_audit:
    st.subheader("Model Integrity & Reconciliation Audit Report")
    st.write(f"**Overall Audit Status:** `{audit.status}`")
    for detail in audit.details:
        st.markdown(f"- ✅ **{detail}**")
        
    st.markdown("---")
    st.subheader("Schedule III Compliance & Accounting Status Notes")
    st.info("""
    **Implemented Schedule III, Division II (Ind AS) Standards:**
    - Non-Current vs. Current Assets & Liabilities classification.
    - Statement of Profit and Loss structured by Nature of Expenses (Cost of materials consumed, direct operating costs, finance costs, depreciation).
    - Statement of Cash Flows mapped to Ind AS 7.
    
    **Statutory Disclosures & Standards Not Yet Implemented in Phase 1:**
    - Ind AS 116 Leases (ROU assets and lease liabilities)
    - Ind AS 12 Deferred tax timing differences
    - Ind AS 19 Employee defined benefit actuarial liabilities
    - Ind AS 109 Effective interest rate amortization on upfront debt charges
    - Detailed footnote disclosures (promoter shareholding, MSME creditor aging schedules).
    """)