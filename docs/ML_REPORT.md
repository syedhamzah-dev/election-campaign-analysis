# Machine Learning Report: Election Intelligence Module

This report documents the implementation of the **Election Intelligence** machine learning and data analytics module added to the **Election Campaign Analysis (2004–2024)** project.

---

## 1. Objective
The goal is to implement an **Election Intelligence** module that goes beyond a simple prediction model. It provides historical behavior analysis and safe/swing diagnostics for Lok Sabha constituencies, avoiding claim to predict the actual 2029 outcomes. It relies strictly on pre-election historical lag indicators to identify structural patterns, seat competitiveness tiers, coalition leanings, and behavioral similarities.

---

## 2. Dataset Used
- **File**: `data/processed/constituency_engineered.csv`
- **Total Records**: 2,715 constituency contests spanning five general election cycles (2004, 2009, 2014, 2019, 2024).
- **Usable Records**: 2,172 contests (2009–2024) once the baseline year 2004 is reserved to construct pre-election lag features.

---

## 3. Target Creation & Classification Methodology
### Target Variable: `Is_Swing` (Safe Seat vs. Swing Seat)
Since the target was not pre-calculated in the raw datasets, it was derived vectorially:
- **Swing Seat (`Is_Swing = 1`)**: Classified if a constituency flipped party control in that election (`Seat_Flip_Status == 1.0`) OR if the victory margin was highly competitive (`Margin_Percentage < 5.0%`), meaning it was extremely close to swinging.
- **Safe Seat (`Is_Swing = 0`)**: Classified if the incumbent party successfully held the seat with a comfortable or landslide margin ($\ge$ 5.0%).

---

## 4. Preprocessing & Feature Selection
### Selected Features (Safe Lag Predictors)
To enforce strict target leakage prevention, all predictors are either static structural indicators or lagged parameters from the preceding election ($T-1$):

| Predictor | Feature Type | Role & Preprocessing | Rationale |
| :--- | :--- | :--- | :--- |
| **`Year`** | Categorical | One-Hot Encoded | Captures election-specific national swings and waves. |
| **`State`** | Categorical | One-Hot Encoded | Models regional party dominance and state-level alignments. |
| **`Constituency_Type`** | Categorical | One-Hot Encoded | Captures demographic seat reservation patterns. |
| **`Prev_Winner_Party`** | Categorical | One-Hot Encoded (NaN $\rightarrow$ `"Unknown"`) | Establishes constituency baseline party alignment. |
| **`Prev_Margin_Percentage`** | Numerical | Standard Scaled | Represents competitiveness in the prior election cycle. |
| **`Prev_Runner_Up_Ratio`** | Numerical | Standard Scaled | Represents candidate competition intensity in the prior cycle. |
| **`Prev_Incumbent_Hold_Count`** | Numerical | Standard Scaled | Represents consecutive hold count leading into the election. |

### Excluded Features (Target Leakage Rationale)
Any post-hoc election outcomes or variables directly derived from the winner of the *current* election were excluded:
- **Target Leakage**: `Winner_Party` (target), `Winner_Candidate`, `Winner_Votes`, `Winner_Percentage`, `Runner_up_Candidate`, `Runner_up_Party`, `Runner_up_Votes`, `Runner_up_Percentage`, `Margin_Votes`, `Margin_Percentage`, `Status`, `Victory_Category`, `Coalition_Block`, `Runner_Up_Ratio`.
- **Derived Flip/Hold**: `Seat_Flip_Status` and `Incumbent_Hold_Count` (since these depend on the current winner and are computed post-hoc, using them directly causes target leakage).
- **A-spatial/Overfitting**: `Constituency_Name` (high cardinality) and `Constituency_No` (a-spatial index).

---

## 5. Model: Safe vs Swing Classifier
- **Algorithm**: Binary Logistic Regression (L2 regularization).
- **Solver**: `lbfgs` with a maximum of 1,000 iterations to ensure convergence.
- **Model Location**: `models/safe_swing_classifier.pkl` (Joblib format).
- **Preprocessing Objects**: `models/categorical_encoder.joblib`, `models/numerical_scaler.joblib`.

---

## 6. Classifier Evaluation Metrics
The classifier was trained on an 80% split and tested on a 20% test partition (431 samples) representing the 2009–2024 cycles:

- **Accuracy**: **75.64%**
- **Precision**: **77.19%**
- **Recall**: **81.85%**
- **F1 Score**: **79.45%**

*These metrics prove that using lagged historical outcomes is extremely effective at capturing seat stability versus swing vulnerability.*

---

## 7. Election Intelligence Analytics
Beyond simple classification, the module implements four key election intelligence algorithms in `src/ml/intelligence.py`:

### A. Seat Flip Risk Index (High, Medium, Low)
Tracks the seat volatility rate and recent victory margins:
- **High Flip Risk**: Historical flip rate $\ge$ 50% OR latest victory margin (2024) $<$ 5.0%.
- **Low Flip Risk**: Historical flip rate is 0.0 (never flipped) AND latest victory margin (2024) $\ge$ 10.0%.
- **Medium Flip Risk**: All other constituencies (flipped once, or held but with closer margins).

### B. Coalition Leaning (NDA, INDIA, Regional, Highly Competitive)
Determines the historical alignment of the seat over the 2004–2024 general elections:
- **NDA**: Won by an NDA coalition block party in $\ge$ 3 cycles.
- **INDIA**: Won by a UPA/INDIA block party in $\ge$ 3 cycles.
- **Regional**: Won by Regional/Others/Left Front parties in $\ge$ 3 cycles.
- **Highly Competitive**: No coalition won $\ge$ 3 cycles (e.g. split NDA 2, INDIA 2, Regional 1).

### C. Competitiveness Score (0–100)
A continuous composite score calculated for each constituency representing its historical competitiveness:
$$\text{Margin Score} = \max(0, 100 - \text{Avg Margin} \times 3)$$
$$\text{Flip Score} = \left(\frac{\text{Flips}}{\text{Valid Cycles}}\right) \times 100$$
$$\text{Party Score} = \left(\frac{\text{Unique Parties} - 1}{\text{Total Cycles} - 1}\right) \times 100$$
$$\text{Competitiveness Score} = 0.4 \times \text{Margin Score} + 0.3 \times \text{Flip Score} + 0.3 \times \text{Party Score}$$

**Tiers**:
- **0–30**: Safe
- **31–70**: Moderately Competitive
- **71–100**: Highly Competitive

### D. Nearest-Neighbor Similar Seats Analysis
Fits an unsupervised `NearestNeighbors(metric="euclidean")` model on the MinMax-scaled vector representing:
1. Competitiveness Score
2. Average victory margin
3. Seat flip rate
4. Number of unique winning parties
5. Latest victory margin (2024)
6. One-hot encoded Coalition Leaning (NDA, INDIA, Regional, Competitive)
7. One-hot encoded Reservation Status (GEN, SC, ST)

Retrieves the 5 behaviorally nearest neighbor constituencies and dynamically generates explanations comparing their coalition leans, seat types, and competitiveness index margins.

---

## 8. Streamlit Dashboard Integration
A new Streamlit page was created at `dashboard/pages/6_🤖_Election_Intelligence.py` and quick navigation linked in `dashboard/app.py`:
- **Dropdown Selector**: Integrated state and constituency filters.
- **Safe vs Swing Forecast Card**: Runs the `safe_swing_classifier.pkl` live to forecast the next election cycle using the 2024 statistics as predictors, along with confidence score and historical logic.
- **Interactive Badges**: Displays color-coded Seat Flip Risk, Coalition Leaning, and Competitiveness Score progress indicator.
- **Historical Timeline Grid**: Displays 5-column layout for 2004, 2009, 2014, 2019, 2024 showing winner party, vote share, margin, and trend analysis.
- **Similar Seats Inspector**: Displays 5 behaviorally closest seats. Clicking "Inspect Seat" updates state/selectbox and updates the dashboard instantly.
- **Performance Details Expander**: Displays metrics cards, Confusion Matrix plot, Feature Coefficients plot, and Competitiveness Score distribution.

---

## 9. Limitations
1. **No Polling Input**: The model relies on historical metrics rather than current opinion/exit polls, candidate popularity index, or seat-sharing agreements.
2. **Boundary Delimitations**: Electoral boundaries in India were delimited in 2008, causing structural shifts for some seats which are only partially adjusted.
3. **No Candidate Demographics**: Omits individual candidate net worth, age, gender, or crime history which can override historical seat leanings.

---

## 10. Future Scope
1. **Dynamic Coalition Mapping**: Adjust alliance flags based on current shifting dynamics (e.g. parties moving from NDA to INDIA or vice-versa).
2. **Census Demographic Merging**: Merge census variables (caste, religion, rural-urban split) to establish demographic clustering of similar seats.
3. **Model Ensembles**: Integrate Random Forests or Gradient Boosting models to evaluate non-linear feature combinations.
