# Data Quality Report: Module 1 Cleaning Pipeline

> [!NOTE]
> This report documents the execution results of **Module 1 (Data Cleaning Pipeline)** for the Election Campaign Analysis (2004–2024) project.

---

## 1. Dataset Shape Transformation

| Dataset | Raw Rows | Raw Cols | Cleaned Rows | Cleaned Cols | Duplicates Removed |
|---|---|---|---|---|---|
| `constituency_master.csv` | 2715 | 14 | 2715 | 15 | 0 |
| `party_summary_master.csv` | 2468 | 5 | 2464 | 5 | 4 |
| `state_summary_master.csv` | 643 | 6 | 643 | 6 | 0 |

---

## 2. Post-Cleaning Null Value Verification

### `constituency_master.csv` Null Counts:
```
Year                    0
State                   0
Constituency_No         0
Constituency_Name       0
Constituency_Type       0
Winner_Candidate        0
Winner_Party            0
Winner_Votes            0
Winner_Percentage       0
Runner_up_Candidate     0
Runner_up_Party         0
Runner_up_Votes         0
Runner_up_Percentage    0
Margin_Votes            0
Status                  0
```

### `party_summary_master.csv` Null Counts:
```
Year          0
Party         0
Votes         0
Seats         0
Percentage    0
```

### `state_summary_master.csv` Null Counts:
```
Year                     0
State_UT                 0
Party_Alliance           0
Votes_Received           0
Vote_Share_Percentage    0
Seats_Won                0
```

---

## 3. Key Cleaning Actions Completed
1. **Surat 2024 Uncontested Seat Imputed**: Successfully populated missing runner-up fields with explicit `'None (Uncontested)'` tags and set `Status = 'Uncontested'`.
2. **Missing Percentage Shares Recomputed**: Recalculated `Winner_Percentage` and `Runner_up_Percentage` across 2,145 historical records (2004–2019).
3. **Party Name Standardization**: Normalized acronym variations (e.g. `BJP`, `INC`, `SP`, `TMC`, `SS(UBT)`, `NCP-SP`, `LJPRV`) across all tables.
4. **State/UT Name Harmonization**: Aligned historical state names (e.g. `Orissa` → `Odisha`, `Andaman & Nicobar` → `Andaman and Nicobar Islands`).
5. **Duplicate Party Aggregation**: Grouped and aggregated split `(Year, Party)` entries in party summaries.
