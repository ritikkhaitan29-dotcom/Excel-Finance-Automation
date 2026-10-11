"""
model/periods.py
================
Central Reporting-Period and Data Classification Configuration.

Standard 7-Period Structure:
- FY2025-26: F26A  (Synthetic / Illustrative Actual baseline)
- FY2026-27: F27E  (Illustrative Estimate - current financial year)
- FY2027-28: F28P  (Projection)
- FY2028-29: F29P  (Projection)
- FY2029-30: F30P  (Projection)
- FY2030-31: F31P  (Projection)
- FY2031-32: F32P  (Projection)

Data Classification:
--------------------
- F26A: "Synthetic / Illustrative Actual" (Identified as synthetic data; not verified historical audited actuals)
- F27E: "Illustrative Estimate" (Conceptually YTD actuals + remaining estimate, currently synthetic)
- F28P to F32P: "Projection" (Forward 3-statement forecast)
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class PeriodInfo:
    """Metadata for a single financial reporting period."""
    period_id: str          # e.g., 'F26A', 'F27E', 'F28P', ..., 'F32P'
    fiscal_year: str        # e.g., 'FY2025-26', 'FY2026-27'
    classification: str     # 'Synthetic / Illustrative Actual', 'Illustrative Estimate', 'Projection'
    short_classification: str # 'Actual (Synthetic)', 'Estimate', 'Projection'
    description: str        # Context and source methodology

    @property
    def display_label(self) -> str:
        """Standard presentation column header, e.g. 'F26A [Synthetic Actual]'."""
        return f"{self.period_id} [{self.short_classification}]"


# Central definition of standard model reporting periods (exactly 7 periods)
STANDARD_PERIODS: List[PeriodInfo] = [
    PeriodInfo(
        period_id="F26A",
        fiscal_year="FY2025-26",
        classification="Synthetic / Illustrative Actual",
        short_classification="Synthetic Actual",
        description="Base-year synthetic / illustrative actuals. Not verified historical actuals."
    ),
    PeriodInfo(
        period_id="F27E",
        fiscal_year="FY2026-27",
        classification="Illustrative Estimate",
        short_classification="Illustrative Estimate",
        description="Current financial year estimate (Conceptually YTD actuals + remaining period estimate, currently synthetic)."
    ),
    PeriodInfo(
        period_id="F28P",
        fiscal_year="FY2027-28",
        classification="Projection",
        short_classification="Projection",
        description="Forward 3-statement projection"
    ),
    PeriodInfo(
        period_id="F29P",
        fiscal_year="FY2028-29",
        classification="Projection",
        short_classification="Projection",
        description="Forward 3-statement projection"
    ),
    PeriodInfo(
        period_id="F30P",
        fiscal_year="FY2029-30",
        classification="Projection",
        short_classification="Projection",
        description="Forward 3-statement projection"
    ),
    PeriodInfo(
        period_id="F31P",
        fiscal_year="FY2030-31",
        classification="Projection",
        short_classification="Projection",
        description="Forward 3-statement projection"
    ),
    PeriodInfo(
        period_id="F32P",
        fiscal_year="FY2031-32",
        classification="Projection",
        short_classification="Projection",
        description="Forward 3-statement projection"
    ),
]


def get_period_by_id(period_id: str) -> PeriodInfo:
    """Retrieve period info by ID."""
    for p in STANDARD_PERIODS:
        if p.period_id == period_id:
            return p
    raise ValueError(f"Unknown period_id: {period_id}")


def get_period_ids() -> List[str]:
    """Returns list of all 7 period IDs: ['F26A', 'F27E', 'F28P', 'F29P', 'F30P', 'F31P', 'F32P']."""
    return [p.period_id for p in STANDARD_PERIODS]


def get_display_labels() -> List[str]:
    """Returns standard display headers for all 7 periods."""
    return [p.display_label for p in STANDARD_PERIODS]