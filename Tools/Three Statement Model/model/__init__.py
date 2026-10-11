"""
model package
=============
Manufacturing FP&A 3-Statement Financial Model.
Exposes ModelAssumptions, central periods, Schedule III presentations, and run_full_model.
"""

from model.assumptions import (
    ModelAssumptions,
    ProductAssumption,
    VariableCostAssumption,
    InflationAssumption,
    FixedAssetInput,
    DebtFacilityInput,
    WorkingCapitalAssumption,
)
from model.periods import (
    STANDARD_PERIODS,
    PeriodInfo,
    get_period_by_id,
    get_period_ids,
    get_display_labels,
)
from model.operating_forecast import build_operating_forecast
from model.depreciation_and_debt import build_depreciation_schedule, build_debt_schedule
from model.income_statement import build_income_statement
from model.working_capital import build_working_capital_schedule
from model.balance_sheet_and_cfs import build_cfs_and_balance_sheet
from model.schedule_iii import (
    build_schedule_iii_balance_sheet,
    build_schedule_iii_profit_and_loss,
    build_schedule_iii_cash_flow,
)
from model.engine import run_full_model, FullModelResult, AuditReport

__all__ = [
    "ModelAssumptions",
    "ProductAssumption",
    "VariableCostAssumption",
    "InflationAssumption",
    "FixedAssetInput",
    "DebtFacilityInput",
    "WorkingCapitalAssumption",
    "STANDARD_PERIODS",
    "PeriodInfo",
    "get_period_by_id",
    "get_period_ids",
    "get_display_labels",
    "build_operating_forecast",
    "build_depreciation_schedule",
    "build_debt_schedule",
    "build_income_statement",
    "build_working_capital_schedule",
    "build_cfs_and_balance_sheet",
    "build_schedule_iii_balance_sheet",
    "build_schedule_iii_profit_and_loss",
    "build_schedule_iii_cash_flow",
    "run_full_model",
    "FullModelResult",
    "AuditReport",
]