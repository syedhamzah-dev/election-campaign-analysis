# 🗳️ Election Campaign Analysis (Lok Sabha 2004–2024)

A comprehensive data analytics project that explores 20 years of Indian General Elections using Python, Pandas, NumPy, Streamlit, Matplotlib, and Seaborn.

The project transforms raw Election Commission of India datasets into meaningful analytical insights through data cleaning, feature engineering, exploratory data analysis, and an interactive dashboard.

---

## Project Overview

This project aims to answer important questions about Indian elections, including:

- How has the political landscape changed from 2004–2024?
- Which political alliances have gained or lost dominance?
- Which parties efficiently convert vote share into parliamentary seats?
- Which states are the most politically competitive?
- Which constituencies consistently change winners?
- Which parties retain constituencies most effectively?

---

## Objectives

- Perform end-to-end data analysis
- Build a modular analytics pipeline
- Generate publication-quality visualizations
- Develop an interactive Streamlit dashboard
- Demonstrate professional data analytics workflow

---

## Dataset

Source:

- Election Commission of India (ECI)
- Wikipedia (Election Summary Data)

Coverage:

- Lok Sabha Elections
- 2004
- 2009
- 2014
- 2019
- 2024

---

## Technology Stack

- Python
- NumPy
- Pandas
- Matplotlib
- Seaborn
- Streamlit
- pathlib.Path
- Jupyter Notebook

No external machine learning libraries were used.

---

## Project Workflow

Raw Data

↓

Data Cleaning

↓

Feature Engineering

↓

Exploratory Data Analysis

↓

Visualization

↓

Interactive Dashboard

↓

Insights & Reporting

---

## Repository Structure

```
Election-Campaign-Analysis/

│

├── app/
│ ├── pages/
│ ├── utils.py
│ └── main.py
│
├── src/
│ ├── cleaner.py
│ ├── feature_engineering.py
│ ├── visualization.py
│ ├── data_loader.py
│ └── eda_utils.py
│
├── data/
│ ├── raw/
│ └── processed/
│
├── outputs/
│ └── figures/
│
├── logs/
│
├── notebooks/
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Dashboard Modules

### Executive Overview

Provides high-level election KPIs and national trends.

---

### Party Analysis

- Party growth
- Seat retention
- Vote-to-seat conversion

---

### State Analysis

- State competitiveness
- Victory margins
- Historical seat volatility

---

### Constituency Analysis

- Reserved vs General seats
- Closest elections
- Largest victory margins

---

### Executive Insights

Summarizes major findings and campaign recommendations.

---

## Key Findings

- Indian elections have increasingly become bipolar after 2014.
- First-Past-The-Post rewards geographically concentrated vote share.
- Several states consistently exhibit high electoral volatility.
- Constituency-level analysis identifies both safe seats and highly competitive battlegrounds.
- Seat retention rates vary significantly across major political parties.

---

## Future Scope

- Incorporate voter turnout data
- Include campaign expenditure analysis
- Add demographic and census features
- Build constituency-level predictive models
- Develop interactive geospatial election maps

---

## Limitations

- Based only on publicly available election result datasets.
- No demographic or socio-economic variables.
- No campaign expenditure data.
- Constituency delimitation affects direct comparisons between 2004 and 2009.
- No voter turnout information for margin normalization.

---

## Team Members

| Name | Role |
|------|------|
| **Syed Mohammad Hamzah** | Project Lead, Data Cleaning, Feature Engineering, Project Architecture, Dashboard Integration, Final Review |
| **Member 2** | National Election Analysis |
| **Member 3** | Party Performance Analysis |
| **Member 4** | State-Level Analysis |
| **Member 5** | Constituency Analysis |
| **Member 6** | Visualization Development |
| **Member 7** | Dashboard Testing |
| **Member 8** | Documentation & Reports |
| **Member 9** | Quality Assurance |
| **Member 10** | Presentation & Repository Support |

*(Update member names before final submission.)*

---

## Contribution Workflow

Each team member worked on an independent feature branch.

Example:

```
main

↓

feature/data-cleaning

↓

feature/feature-engineering

↓

feature/national-analysis

↓

feature/party-analysis

↓

feature/state-analysis

↓

feature/constituency-analysis

↓

feature/dashboard

↓

main
```

All pull requests were reviewed by the Project Lead before merging.

---

## Installation

Clone the repository

```bash
git clone https://github.com/yourusername/Election-Campaign-Analysis.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run Streamlit

```bash
streamlit run app/main.py
```

---

## Acknowledgements

- Election Commission of India
- Wikipedia Election Data
---
