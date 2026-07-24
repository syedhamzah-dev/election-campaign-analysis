# 📄 Technical Project Report: Election Campaign Analysis (2004–2024)

> **Comprehensive Technical Architecture, Analytical Findings, Visualization Design Blueprint, and Streamlit Dashboard Intelligence System for Indian General Elections (Lok Sabha 2004–2024)**

---

## 1. Executive Summary & Introduction

### Executive Summary

The **Election Campaign Analysis** system provides an end-to-end analytical framework and interactive intelligence dashboard covering **20 years of Indian Lok Sabha General Elections (2004, 2009, 2014, 2019, 2024)**. The project ingests raw candidate and constituency tallies from the Election Commission of India (ECI), standardizes over 50 political party acronym variations and historical state name shifts, engineers domain-specific features (*State Seat Volatility Rate*, *First-Past-The-Post Vote Conversion Efficiency*, *Victory Margin Spreads*, *Coalition Blocks*), and exports **13 publication-quality 300 DPI figures**.

The dashboard is delivered via a multi-page **Streamlit** web application driven by a **single centralized sidebar filtering pipeline** (**Year**, **State**, **Alliance**, **Party**, **Constituency Type**). The system computes real-time dynamic text insights directly from active filters, offering actionable intelligence for election strategists, researchers, journalists, and policymakers.

---

## 2. Domain Motivation & Problem Formulation

### Motivation

Indian Lok Sabha General Elections constitute the largest democratic voting exercise on earth, encompassing over 900 million eligible voters across 543 parliamentary constituencies. Despite the wealth of election data published by the ECI, raw files exhibit significant technical challenges:

1. **Entity Inconsistency**: Party names vary wildly across cycles (e.g. `Bharatiya Janata Party` vs `BJP`, `Samajwadi Party` vs `SP`, `Shiv Sena (Uddhav Balasaheb Thackrey)` vs `SS(UBT)`).
2. **Missing Percentage Shares**: Historical ECI records (2004–2019) frequently omit percentage vote shares and victory margin percentages.
3. **Misleading Visualizations**: Comparing absolute EVM vote volumes with postal votes obscures relative postal reliance due to scale differences (postal votes average ~1–2% of totals).
4. **Lack of Centralized Filtering**: Standalone static plots do not react dynamically when analysts isolate specific states, alliances, or seat categories.

### System Formulation

The platform addresses these challenges through a 5-tier architecture:

- **Tier 1 (Ingestion)**: Safe CSV loading and structural validation (`src/data_loader.py`).
- **Tier 2 (Cleaning)**: Vectorized name standardization, missing value recomputation, and Surat 2024 uncontested seat edge-case handling (`src/cleaner.py`).
- **Tier 3 (Feature Engineering)**: Multi-year lag matching, seat flip tracking, conversion efficiency, and coalition mapping (`src/feature_engineering.py`).
- **Tier 4 (Visual Engine)**: Modular submodules (`src/visualizations/`) producing 300 DPI figures with strict party color rules and statistical benchmarks (`src/visualization.py` facade).
- **Tier 5 (Interactive Dashboard)**: Streamlit app (`app/`) with unified sidebar filtering and automated dynamic text insights (`app/utils.py`).

---

## 3. Datasets Description & Schema

The pipeline ingests four primary raw CSV datasets:

### 1. `constituency.csv` (Historical Master 2004–2024)

- **Rows**: 2,715 constituency records (543 seats × 5 election cycles).
- **Columns**: `Year`, `State`, `Constituency_No`, `Constituency_Name`, `Constituency_Type` (`GEN`, `SC`, `ST`), `Winner_Candidate`, `Winner_Party`, `Winner_Votes`, `Runner_up_Candidate`, `Runner_up_Party`, `Runner_up_Votes`, `Margin_Votes`.

### 2. `result_by_party_cleaned.csv` (Party Aggregates 2004–2024)

- **Rows**: National party-level aggregations per year.
- **Columns**: `Year`, `Party`, `Seats`, `Votes`, `Percentage`.

### 3. `result_by_state_cleaned.csv` (State Aggregates 2004–2024)

- **Rows**: State-level party seat and vote tallies.
- **Columns**: `Year`, `State_UT`, `Party_Alliance`, `Seats_Won`, `Votes_Received`, `Vote_Share_Percentage`.

### 4. `election_results_2024.csv` (Detailed Candidate Results 2024)

- **Rows**: 544 constituency rows (including Surat uncontested seat).
- **Columns**: `Constituency`, `Const. No.`, `Leading Candidate`, `Leading Party`, `Trailing Candidate`, `Trailing Party`, `Margin`, `Status`, `EVM Votes`, `Postal Votes`, `Total Votes`.

---

## 4. Data Cleaning Pipeline (`src/cleaner.py`)

The cleaning pipeline executes five vectorized transformations:

1. **Surat 2024 Uncontested Seat Imputation**:
   In the 2024 election, BJP candidate Mukesh Dalal won the Surat constituency uncontested. Raw data contained null values for runner-up fields. The cleaner explicitly imputes:

   - `Winner_Percentage = 100.0`
   - `Runner_up_Candidate = 'None (Uncontested)'`
   - `Runner_up_Party = 'None (Uncontested)'`
   - `Runner_up_Votes = 0.0`
   - `Status = 'Uncontested'`
2. **Vectorized Name Standardization**:
   Using `PARTY_STANDARDIZATION_MAP` and `STATE_STANDARDIZATION_MAP`, string expressions are normalized (e.g., `Orissa` → `Odisha`, `Bharatiya Janata Party` → `BJP`, `Indian National Congress` → `INC`, `All India Trinamool Congress` → `TMC`).
3. **Recomputation of Missing Vote Percentage Shares**:
   For 2,145 historical records lacking percentage vote shares:

   $$
   \text{Winner \%} = \text{round}\left(\frac{\text{Winner Votes}}{\text{Winner Votes} + \text{Runner-up Votes}} \times 100, 2\right)
   $$
4. **Duplicate Party Aggregation**:
   In national party summaries, split entries for parties like `CPI(ML)L` and `Jharkhand Party` are grouped by `(Year, Party)` and aggregated.
5. **State Summary Seat Reconstruction**:
   Missing `Seats_Won` tallies in state summaries are cross-verified and reconstructed directly from clean constituency-level winner tallies.

---

## 5. Feature Engineering (`src/feature_engineering.py`)

Feature engineering adds key quantitative metrics for exploratory analysis:

1. **Coalition Block Categorization**:
   Parties are mapped into four national electoral blocks:

   - **NDA**: BJP, TDP, JD(U), SHS, LJP, AD(S), AJSU, etc.
   - **UPA / I.N.D.I.A.**: INC, SP, TMC, DMK, SS(UBT), NCP-SP, CPI(M), IUML, RJD, AAP, etc.
   - **Left Front**: CPI(M), CPI, Forward Bloc, RSP.
   - **Others / Regional**: YSRCP, BRS, BJD, BSP, AIMIM, IND, etc.
2. **Constituency Seat Flip Tracking & State Volatility Rate**:
   By matching constituencies across consecutive election cycles (`Prev_Year = Year - 5`), the pipeline determines whether the incumbent party retained or lost the seat (`Seat_Flip_Status` = 1 if flipped, 0 if retained).
   The **State Volatility Rate (%)** is computed as:

   $$
   \text{State Volatility Rate (\%)} = \left(\frac{\text{Total Seat Flips in State}}{\text{Total Constituency Transitions}}\right) \times 100
   $$
3. **FPTP Seat Conversion Efficiency**:
   Measures how efficiently a party converts vote share into parliamentary seats:

   $$
   \text{Seat Conversion Efficiency} = \frac{\text{National Seats Won}}{\text{National Vote Share (\%)}} \quad (\text{seats per vote \%})
   $$
4. **Victory Margin Categorization**:
   Seats are classified into competitive intensity tiers:

   - **Tight / Close Contest**: Margin $< 5\%$
   - **Moderate Contest**: $5\% \le \text{Margin} < 15\%$
   - **Landslide / Safe Seat**: Margin $\ge 15\%$

---

## 6. Exploratory Data Analysis & Detailed Visualization Design

Every generated figure has been audited and designed according to publication standards:

### Viz 1: Coalition Seat Share Trajectory (2004–2024)

- **Primary Dashboard Module**: Overview Page (Tab 1)
- **Objective**: Track parliamentary majority control across 20 years.
- **Why Chosen**: Stacked bar chart visually emphasizes majority thresholds (272 seats).
- **Insight**: In 2024, NDA (292) and UPA/I.N.D.I.A. (235) captured 97.1% of seats, showing near-total collapse of unaligned regional seats.
- **Color Standard**: Official Coalition Colors (NDA Saffron `#FF9933`, UPA Blue `#19A0FF`).

### Viz 2: National Vote Share % vs Seats Won (FPTP Conversion)

- **Primary Dashboard Module**: Overview (Tab 2) & Party Analysis (Tab 5)
- **Objective**: Demonstrate First-Past-The-Post vote conversion distortion.
- **Why Chosen**: Dual-axis bar chart comparing national vote share % with seats won.
- **Insight**: BJP converted 36.6% vote share into 240 seats, showing how concentrated geographic support multiplies seat returns.
- **Color Standard**: Official Party Colors.

### Viz 3: Battleground State Seat Volatility Ranking

- **Primary Dashboard Module**: State Analysis (Tab 1)
- **Objective**: Rank Indian states by constituency seat flip frequency.
- **Why Chosen**: Horizontal bar chart sorted descending with percentage annotations.
- **Insight**: Tamil Nadu (65.0%), UP (58.3%), and Karnataka (57.1%) are top national campaign battlegrounds.
- **Color Standard**: Professional Seaborn palette (`mako_r`).

### Viz 4: Victory Margin Distribution Across Major States

- **Primary Dashboard Module**: State Analysis (Tab 2)
- **Objective**: Compare competitive spread and outliers across major states.
- **Why Chosen**: Side-by-side boxplots showing median, interquartile range, and outliers.
- **Insight**: Kerala and UP exhibit narrow median margins (<8%), while Gujarat displays wide margins (>25%).
- **Color Standard**: Professional Seaborn palette (`Blues_r`).

### Viz 5: Party Seat Breakdown Across Reserved & General Constituencies

- **Primary Dashboard Module**: Constituency Analysis (Tab 4)
- **Objective**: Evaluate party performance in General (`GEN`), Scheduled Castes (`SC`), and Scheduled Tribes (`ST`) seats.
- **Why Chosen**: Stacked bar chart showing party composition within reservation categories.
- **Insight**: BJP holds dominant majorities in ST/SC reserved seats (capturing >50% of ST seats in 2014–2019).
- **Color Standard**: Official Party Colors.

### Viz 6: Extreme Victory Margins (Tightest Wins vs Landslide Sweeps)

- **Primary Dashboard Module**: Constituency Analysis (Tab 5)
- **Objective**: Highlight razor-thin electoral wins vs massive sweeps.
- **Why Chosen**: Dual-panel horizontal bar chart comparing top 10 tightest vs top 10 largest margins.
- **Insight**: Tightest victory was 25 votes (Ladakh 2004) and 48 votes (Mumbai North West 2024); largest exceeded 1.17M votes (Indore 2024).
- **Color Standard**: Professional Seaborn palettes (`Reds_r` / `Greens_r`).

### Viz 7: Incumbent Party Seat Retention vs Seat Loss Breakdown

- **Primary Dashboard Module**: Party Analysis (Tab 4)
- **Objective**: Measure stronghold defensive stability across consecutive elections.
- **Why Chosen**: Stacked horizontal bar chart detailing retained vs lost seats per party.
- **Insight**: TMC & DMK maintain highest stronghold retention rates (>75%), whereas INC suffered heavy seat losses in 2014.
- **Color Standard**: Official Party Colors.

### Viz 8: Top Parties by Seats Won

- **Primary Dashboard Module**: Party Analysis (Tab 1)
- **Objective**: Compare total seats won by political parties.
- **Why Chosen**: Horizontal bar chart sorted descending with integer seat count labels.
- **Insight**: BJP and INC remain the primary national seat anchors across cycles.
- **Color Standard**: Official Party Colors.

### Viz 9: Top Parties by Total Votes Received

- **Primary Dashboard Module**: Party Analysis (Tab 2)
- **Objective**: Display absolute candidate vote volume tallies.
- **Why Chosen**: Horizontal bar chart with million vote (`M`) annotations and national average vote benchmark line.
- **Insight**: BJP received over 230M total votes in 2024, followed by INC with 135M+ votes.
- **Color Standard**: Official Party Colors.

### Viz 10: Postal Vote Share (%) Breakdown by Party

- **Primary Dashboard Module**: Party Analysis (Tab 3)
- **Objective**: Measure relative party reliance on postal ballots vs general EVM voting.
- **Why Chosen**: Replaced misleading absolute EVM vs Postal chart with relative percentage calculation:
  $$
  \text{Postal Vote Share (\%)} = \frac{\text{Postal Votes}}{\text{EVM Votes} + \text{Postal Votes}} \times 100
  $$
- **Insight**: Postal votes average ~1.2%–2.5% of party totals, with specific cadre and service-aligned parties showing higher relative dependence.
- **Color Standard**: Official Party Colors.

### Viz 11: Top 20 Constituencies by Total Votes Cast (Turnout)

- **Primary Dashboard Module**: Constituency Analysis (Tab 1)
- **Objective**: Identify constituencies with the highest electorate participation.
- **Why Chosen**: Horizontal bar chart sorted by total votes cast.
- **Insight**: Dhubri (Assam) recorded the highest total candidate votes cast exceeding 2.45M votes.
- **Color Standard**: Professional Seaborn palette (`mako_r`).

### Viz 12: Distribution of Winning Margins Across Seats

- **Primary Dashboard Module**: Constituency Analysis (Tab 2)
- **Objective**: Analyze competitive balance distribution across parliamentary seats.
- **Why Chosen**: Histogram with Kernel Density Estimate (KDE) and explicit **Median Margin Line** overlay.
- **Insight**: Median victory margin across seats is ~65,000 votes, with heavy right-skewed distribution.
- **Color Standard**: Professional Seaborn Histogram styling.

### Viz 13: EVM vs Postal Votes Scatter Plot by Constituency

- **Secondary / Advanced Module**: Constituency Analysis (Tab 3 - Advanced View)
- **Objective**: Scatter plot comparing absolute EVM and Postal vote volumes per constituency.
- **Why Chosen**: Enables detection of outlier constituencies deviating from the 5% postal ratio benchmark line.
- **Insight**: Postal votes scale linearly with EVM vote volumes across constituencies.
- **Color Standard**: Professional Seaborn Scatter styling.

---

## 7. Dashboard Architecture & Centralized Filtering Pipeline

### Architecture

The Streamlit app is structured cleanly:

- `app/main.py`: Entrypoint featuring custom CSS styling, landing header, macro KPI cards, and page navigation overview.
- `app/utils.py`: Contains cached data loader (`load_processed_data`), centralized sidebar filter handler (`render_sidebar_filters`), and automated dynamic insights engine (`compute_dynamic_insights`).
- `app/pages/`: Modular pages for Overview, Party Analysis, State Analysis, Constituency Analysis, and Executive Insights.

### Centralized Filtering Pipeline

All pages invoke `render_sidebar_filters(c_df, p_df, s_df)`, rendering controls for:

1. **Select Election Year(s)** (`multiselect`)
2. **Select State / UT** (`selectbox`)
3. **Select Alliance / Block** (`selectbox`)
4. **Select Party** (`multiselect`)
5. **Constituency Type** (`radio`)

The pipeline applies filters across all datasets simultaneously, returning synchronized DataFrames `(c_filt, p_filt, s_filt)`. Every metric, table, chart, and dynamic insight updates real-time with zero stale data.

---

## 8. Key Statistical Findings & Policy Recommendations

1. **Bipolar Coalition Dominance**: Pre-poll alliance formation is essential for election viability; unaligned regional parties face structural vote dilution under FPTP.
2. **Resource Allocation in Battleground States**: Campaign expenditure and leader rallies should concentrate on high-volatility states (**Tamil Nadu, UP, Karnataka, Maharashtra**).
3. **Micro-Targeting in Reserved Constituencies**: Scheduled Tribes (`ST`) and Scheduled Castes (`SC`) reserved seats respond strongly to targeted welfare outreach, providing high seat multipliers.
4. **Close Contest Preparedness**: With over 50 constituencies decided by narrow margins (<5%), legal and polling agent training in close-contest management is critical.

---

## 9. Visualization Audit & Categorization Matrix

| Figure File | Visualization Function             | Classification | Dashboard Location     | Rationale                                            |
| ----------- | ---------------------------------- | -------------- | ---------------------- | ---------------------------------------------------- |
| `fig_01`  | `plot_coalition_trajectory`      | Primary        | Overview Tab 1         | Essential macro coalition seat share trend           |
| `fig_02`  | `plot_vote_seat_conversion`      | Primary        | Party Tab 5 / Overview | Demonstrates FPTP vote-to-seat conversion distortion |
| `fig_03`  | `plot_state_volatility_ranking`  | Primary        | State Tab 1            | Ranks battleground states by flip rate               |
| `fig_04`  | `plot_state_margin_distribution` | Primary        | State Tab 2            | Highlights competitive intensity spread by state     |
| `fig_05`  | `plot_reserved_category_wins`    | Primary        | Constituency Tab 4     | Vital demographic SC/ST/GEN win breakdown            |
| `fig_06`  | `plot_extreme_margins`           | Primary        | Constituency Tab 5     | Compares razor-thin wins vs landslide sweeps         |
| `fig_07`  | `plot_party_retention_loss`      | Primary        | Party Tab 4            | Measures incumbent stronghold stability              |
| `fig_08`  | `plot_seats_by_party`            | Primary        | Party Tab 1            | Core party seat comparison                           |
| `fig_09`  | `plot_votes_by_party`            | Primary        | Party Tab 2            | Core party absolute vote tally comparison            |
| `fig_10`  | `plot_postal_vote_share`         | Primary        | Party Tab 3            | Replaces absolute chart with relative % dependence   |
| `fig_11`  | `plot_turnout_top20`             | Primary        | Constituency Tab 1     | Ranks highest participation constituencies           |
| `fig_12`  | `plot_margins_hist`              | Primary        | Constituency Tab 2     | Statistical distribution of winning margins          |
| `fig_13`  | `plot_evm_vs_postal_scatter`     | Advanced       | Constituency Tab 3     | Secondary scatter plot for outlier investigation     |
| Legacy      | `plot_evm_postal_by_party`       | Archived       | Code Archive           | Replaced by relative Postal Vote Share (%) chart     |

---

## 10. Conclusions & Future Work Roadmap

### Conclusions

The refactored **Election Campaign Analysis** platform succeeds in transforming raw ECI election data into a publication-ready analytics suite. By combining modular Python plot submodules, strict official party color standards, a single centralized sidebar filter pipeline, and real-time automated dynamic text insights, the application provides an authoritative intelligence tool for election strategy.

### Future Machine Learning Roadmap

1. **Constituency Seat Flip Binary Classifier**: Train Decision Tree and Logistic Regression models using historical victory margins, runner-up vote ratios, and incumbent hold counts to predict seat flip probability in upcoming elections.
2. **GIS Spatial Mapping**: Integrate Folium / Plotly interactive GIS choropleth maps for state and constituency boundaries.
3. **Sentiment & Social Media Integration**: Incorporate digital campaign ad spend and news sentiment data.
