from typing import Dict, List, Tuple
import pandas as pd

def build_schedule_iii_balance_sheet(bs_df: pd.DataFrame) -> pd.DataFrame:
    col_labels = bs_df['Display_Label'].tolist()

    lines = {
        "I. ASSETS": [""] * len(col_labels),
        "(1) Non-Current Assets": [""] * len(col_labels),
        "    (a) Property, Plant and Equipment": bs_df['Net_Fixed_Assets_Cr'].values,
        "    Total Non-Current Assets": bs_df['Net_Fixed_Assets_Cr'].values,
        "(2) Current Assets": [""] * len(col_labels),
        "    (a) Inventories": bs_df['Inventory_Cr'].values,
        "    (b) Financial Assets": [""] * len(col_labels),
        "        (i) Investments (Short-Term Liquid Investments)": bs_df['Liquid_Investments_Cr'].values,
        "        (ii) Trade Receivables": bs_df['Trade_Receivables_Cr'].values,
        "        (iii) Cash and Cash Equivalents": bs_df['Cash_and_Equivalents_Cr'].values,
        "    Total Current Assets": bs_df['Total_Current_Assets_Cr'].values,
        "TOTAL ASSETS": bs_df['Total_Assets_Cr'].values,
        "II. EQUITY AND LIABILITIES": [""] * len(col_labels),
        "(1) Equity": [""] * len(col_labels),
        "    (a) Equity Share Capital": bs_df['Share_Capital_Cr'].values,
        "    (b) Other Equity (Retained Earnings)": bs_df['Retained_Earnings_Cr'].values,
        "    Total Equity": bs_df['Total_Shareholders_Equity_Cr'].values,
        "(2) Non-Current Liabilities": [""] * len(col_labels),
        "    (a) Financial Liabilities": [""] * len(col_labels),
        "        (i) Borrowings (Long-Term Term Loans)": bs_df['Long_Term_Debt_Cr'].values,
        "    Total Non-Current Liabilities": bs_df['Long_Term_Debt_Cr'].values,
        "(3) Current Liabilities": [""] * len(col_labels),
        "    (a) Financial Liabilities": [""] * len(col_labels),
        "        (i) Borrowings (Short-Term Credit Facilities)": bs_df['Short_Term_Debt_Cr'].values,
        "        (ii) Borrowings (Current Maturities of Long-Term Debt)": bs_df['CMLTD_Cr'].values,
        "        (iii) Trade Payables": bs_df['Trade_Payables_Cr'].values,
        "    Total Current Liabilities": bs_df['Total_Current_Liabilities_Cr'].values,
        "TOTAL LIABILITIES": bs_df['Total_Liabilities_Cr'].values,
        "TOTAL EQUITY AND LIABILITIES": bs_df['Total_Liabilities_and_Equity_Cr'].values,
        "BALANCE VERIFICATION (Variance)": bs_df['Balance_Check_Cr'].values,
    }

    return pd.DataFrame(lines, index=col_labels).T


def build_schedule_iii_profit_and_loss(is_df: pd.DataFrame) -> pd.DataFrame:
    col_labels = is_df['Display_Label'].tolist()

    lines = {
        "I. Revenue from Operations": is_df['Revenue_Cr'].values,
        "II. Other Income": [0.0] * len(col_labels),
        "III. Total Income (I + II)": is_df['Revenue_Cr'].values,
        "IV. Expenses:": [""] * len(col_labels),
        "    Cost of Materials Consumed (Raw Materials)": is_df['RM_Cost_Cr'].values,
        "    Other Direct Manufacturing & Variable Conversion Expenses": is_df['OVC_Cost_Cr'].values,
        "    Other Operating Overheads (Factory & Administrative)": is_df['Fixed_Operating_Costs_Cr'].values,
        "    Finance Costs (Interest Expense on Borrowings)": is_df['Interest_Expense_Cr'].values,
        "    Depreciation and Amortisation Expense": is_df['Depreciation_Cr'].values,
        "    Total Expenses (IV)": (
            is_df['RM_Cost_Cr'] + is_df['OVC_Cost_Cr'] + is_df['Fixed_Operating_Costs_Cr']
            + is_df['Interest_Expense_Cr'] + is_df['Depreciation_Cr']
        ).values,
        "V. Profit Before Tax (III - IV)": is_df['PBT_Cr'].values,
        "VI. Tax Expense:": [""] * len(col_labels),
        "    Current Tax": is_df['Tax_Expense_Cr'].values,
        "VII. Profit for the Period (PAT) (V - VI)": is_df['Net_Profit_Cr'].values,
    }

    return pd.DataFrame(lines, index=col_labels).T


def build_schedule_iii_cash_flow(cfs_df: pd.DataFrame) -> pd.DataFrame:
    col_labels = cfs_df['Display_Label'].tolist()

    op_profit_before_wc = (cfs_df['Net_Profit_Cr'] + cfs_df['Depreciation_Cr'] + cfs_df['Interest_Expense_Addback_Cr']).values

    lines = {
        "A. CASH FLOWS FROM OPERATING ACTIVITIES": [""] * len(col_labels),
        "   Profit for the Period (PAT)": cfs_df['Net_Profit_Cr'].values,
        "   Adjustments for: Depreciation & Amortisation Expense": cfs_df['Depreciation_Cr'].values,
        "   Adjustments for: Finance Costs (Interest Expense)": cfs_df['Interest_Expense_Addback_Cr'].values,
        "   Operating Profit before Working Capital Changes": op_profit_before_wc,
        "   Working Capital Adjustments: Change in Working Capital": cfs_df['Change_in_NWC_Cr'].values,
        "   Net Cash Generated from Operating Activities (A)": cfs_df['CFO_Cr'].values,
        "B. CASH FLOWS FROM INVESTING ACTIVITIES": [""] * len(col_labels),
        "   Payment for Property, Plant and Equipment (Capex)": cfs_df['Capex_Cr'].values,
        "   Net Cash Used in Investing Activities (B)": cfs_df['CFI_Cr'].values,
        "C. CASH FLOWS FROM FINANCING ACTIVITIES": [""] * len(col_labels),
        "   Repayment of Long-Term Borrowings": cfs_df['LT_Debt_Repayment_Cr'].values,
        "   Net Proceeds / (Repayment) of Short-Term Borrowings": cfs_df['ST_Debt_Net_Draw_Cr'].values,
        "   Finance Costs Paid (Interest Paid)": cfs_df['Interest_Paid_Cr'].values,
        "   Dividends Paid": cfs_df['Dividends_Paid_Cr'].values,
        "   Net Cash Flows from Financing Activities (C)": cfs_df['CFF_Cr'].values,
        "Net Increase / (Decrease) in Cash & Cash Equivalents (A + B + C)": cfs_df['Net_Change_in_Cash_Cr'].values,
        "Cash and Liquid Investments at Beginning of the Period": cfs_df['Beginning_Cash_Cr'].values,
        "Cash and Liquid Investments at End of the Period": cfs_df['Ending_Cash_Cr'].values,
    }


    return pd.DataFrame(lines, index=col_labels).T
