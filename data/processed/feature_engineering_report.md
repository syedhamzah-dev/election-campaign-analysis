git tg

# Feature Engineering Report: Module 2 Pipeline

> [!NOTE]
> This report documents the engineered features created during **Module 2 (Feature Engineering Pipeline)** for the Election Campaign Analysis (2004–2024) project.

---

## 1. Summary of Engineered Features

### A. Constituency-Level Features (`constituency_engineered.csv`)

- **`Margin_Percentage`** (`float64`): Normalized victory margin relative to top-2 total polled valid votes.
  - *Utility*: Eliminates turnout magnitude bias; supports EDA margin analysis, dashboard filtering, and ML inputs.
- **`Victory_Category`** (`object`): Categorical tier (`Landslide` >15%, `Comfortable` 5-15%, `Tight / Close Contest` <5%).
  - *Utility*: Enables rapid competitive intensity filtering in Streamlit dashboard views.
- **`Seat_Flip_Status`** (`float64`): Binary flag (`1.0` if winning party changed from election $T-1$, `0.0` if retained, `NaN` for base 2004).
  - *Utility*: Key target variable for Machine Learning classification model and seat volatility tracking.
- **`Coalition_Block`** (`object`): Categorical alliance tag (`NDA`, `UPA / I.N.D.I.A.`, `Left Front`, `Others / Regional`).
  - *Utility*: Tracks macro-alliance consolidation and power shifts across two decades.
- **`Runner_Up_Ratio`** (`float64`): Ratio of runner-up votes to winner votes (`Runner_up_Votes / Winner_Votes`).
  - *Utility*: Quantifies challenge intensity (closer to 1.0 indicates fierce contest).
- **`Incumbent_Hold_Count`** (`int64`): Count of consecutive elections the incumbent party has retained the seat.
  - *Utility*: Identifies party strongholds versus vulnerable seats.

### B. Party-Level Features (`party_summary_engineered.csv`)

- **`Seat_Conversion_Efficiency`** (`float64`): Ratio of national seats won to national vote percentage share (`Seats / Percentage`).
  - *Utility*: Quantifies First-Past-The-Post vote conversion efficiency for national vs regional parties.
- **`Coalition_Block`** (`object`): National alliance mapping per political party.

### C. State-Level Features (`state_summary_engineered.csv`)

- **`State_Total_Seats`** (`int64`): Total Lok Sabha seats in the state.
- **`State_Seat_Share`** (`float64`): Percentage share of state seats won by a party/alliance (`Seats_Won / State_Total_Seats * 100`).
- **`State_Volatility_Rate`** (`float64`): Historical percentage of seat flips in the state.
  - *Utility*: Ranks battleground swing states for campaign strategy.

---

## 2. Feature Distribution Highlights

- **Total Constituency Records**: 2715
- **Victory Category Breakdown**:
  - Landslide (>15% margin): 1229 seats
  - Comfortable (5-15% margin): 940 seats
  - Tight / Close Contest (<5% margin): 546 seats
- **Coalition Block Distribution**:
  - NDA Seats: 1346
  - UPA / I.N.D.I.A. Seats: 1053
  - Left Front Seats: 5
  - Regional / Others Seats: 311
- **Seat Flip Totals (2009–2024 Transitions)**:
  - Total Seat Flips Recorded: 1060 seats
  - Total Incumbent Retentions: 1092 seats
