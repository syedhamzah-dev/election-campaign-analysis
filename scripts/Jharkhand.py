import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.cluster import KMeans

# ── CONFIG ───────────────────────────────────────────────────────────────────
DATA_FILE   = "census_2011.csv"
OUTPUT_DIR  = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# ─────────────────────────────────────────────────────────────────────────────


# =============================================================================
# MODULE 1 — LOAD & CLEAN DATA
# =============================================================================
print("=" * 60)
print("MODULE 1 — Loading & Cleaning Data")
print("=" * 60)

df = pd.read_csv(DATA_FILE)

print(f"Shape          : {df.shape}")
print(f"Columns        : {list(df.columns)}")
print(f"\nMissing values :\n{df.isnull().sum()}")
print(f"\nLEVEL counts  :\n{df['LEVEL'].value_counts()}")

df = df[df["TOT_POP"] > 0].copy()
df.dropna(subset=["TOT_POP", "M_POP", "TOT_SC", "TOT_ST", "TOT_LIT"],
          inplace=True)

#Feature Engineering
df["F_POP"]         = df["TOT_POP"] - df["M_POP"]
df["LITERACY_RATE"] = df["TOT_LIT"] / df["TOT_POP"]
df["SC_RATIO"]      = df["TOT_SC"]  / df["TOT_POP"]
df["ST_RATIO"]      = df["TOT_ST"]  / df["TOT_POP"]
df["FEMALE_RATIO"]  = df["F_POP"]   / df["TOT_POP"]
df["GENDER_GAP"]    = df["M_POP"]   - df["F_POP"]

# Encode categoricals
df["LEVEL_ENC"]    = LabelEncoder().fit_transform(df["LEVEL"])
df["DISTRICT_ENC"] = LabelEncoder().fit_transform(df["DISTRICT"])

print(f"\nClean shape    : {df.shape}")
print(f"\nSample derived features:")
print(df[["NAME", "LITERACY_RATE", "SC_RATIO",
          "ST_RATIO", "FEMALE_RATIO"]].head())

#EXPLORATORY DATA ANALYSIS

#Literacy Rate by District

lit_by_dist = df.groupby("DISTRICT")["LITERACY_RATE"].mean().sort_values()

plt.figure(figsize=(10, 6))
lit_by_dist.plot(kind="barh", color="steelblue")
plt.title("Average Literacy Rate by District")
plt.xlabel("Literacy Rate")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/literacy_by_district.png", dpi=150)
plt.show()
print("Saved: literacy_by_district.png")

#Gender Gap by District

plt.figure(figsize=(10, 6))
df.groupby("DISTRICT")["FEMALE_RATIO"].mean().sort_values()\
  .plot(kind="barh", color="tomato",
        title="Female Population Ratio by District")
plt.axvline(0.5, color="black", linestyle="--", label="Equal (0.5)")
plt.xlabel("Female Ratio")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/gender_gap.png", dpi=150)
plt.show()
print("Saved: gender_gap.png")

#2D: Correlation Heatmap

corr_cols = ["TOT_POP", "LITERACY_RATE", "SC_RATIO",
             "ST_RATIO", "FEMALE_RATIO", "GENDER_GAP"]
plt.figure(figsize=(8, 6))
sns.heatmap(df[corr_cols].corr(), annot=True, fmt=".2f",
            cmap="coolwarm", center=0)
plt.title("Feature Correlation Heatmap")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/correlation_heatmap.png", dpi=150)
plt.show()
print("Saved: correlation_heatmap.png")

#Literacy Rate Distribution 

plt.figure(figsize=(8, 5))
df["LITERACY_RATE"].hist(bins=40, color="teal", edgecolor="white")
plt.title("Distribution of Literacy Rate Across All Areas")
plt.xlabel("Literacy Rate")
plt.ylabel("Count of Areas")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/literacy_distribution.png", dpi=150)
plt.show()
print("Saved: literacy_distribution.png")


#REGRESSION: PREDICT LITERACY RATE

features = ["TOT_POP", "SC_RATIO", "ST_RATIO",
            "FEMALE_RATIO", "LEVEL_ENC", "DISTRICT_ENC"]
target   = "LITERACY_RATE"

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

#Gradient Boosting

gb_model = GradientBoostingRegressor(n_estimators=200,
                                     learning_rate=0.05,
                                     max_depth=4,
                                     random_state=42)
gb_model.fit(X_train, y_train)
gb_preds = gb_model.predict(X_test)

print("\n--- Gradient Boosting ---")
print(f"R²  Score : {r2_score(y_test, gb_preds):.4f}")
print(f"MAE       : {mean_absolute_error(y_test, gb_preds):.4f}")

cv_gb = cross_val_score(gb_model, X, y, cv=5, scoring="r2")
print(f"CV R² Mean: {cv_gb.mean():.4f} ± {cv_gb.std():.4f}")

#Random Forest

rf_model = RandomForestRegressor(n_estimators=200, random_state=42)
rf_model.fit(X_train, y_train)
rf_preds = rf_model.predict(X_test)

print("\n--- Random Forest ---")
print(f"R²  Score : {r2_score(y_test, rf_preds):.4f}")
print(f"MAE       : {mean_absolute_error(y_test, rf_preds):.4f}")

cv_rf = cross_val_score(rf_model, X, y, cv=5, scoring="r2")
print(f"CV R² Mean: {cv_rf.mean():.4f} ± {cv_rf.std():.4f}")

#Feature Importance
importances = pd.Series(gb_model.feature_importances_,
                        index=features).sort_values()

plt.figure(figsize=(8, 5))
importances.plot(kind="barh", color="teal")
plt.title("Feature Importance — What Predicts Literacy Rate?")
plt.xlabel("Importance Score")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/feature_importance.png", dpi=150)
plt.show()
print("Saved: feature_importance.png")

# Actual vs Predicted Plot
plt.figure(figsize=(7, 7))
plt.scatter(y_test, gb_preds, alpha=0.3, color="steelblue", s=10)
plt.plot([0, 1], [0, 1], "r--", label="Perfect prediction")
plt.xlabel("Actual Literacy Rate")
plt.ylabel("Predicted Literacy Rate")
plt.title("Actual vs Predicted Literacy Rate")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/actual_vs_predicted.png", dpi=150)
plt.show()
print("Saved: actual_vs_predicted.png")

# MODULE 4 — CLUSTERING: AREA PROFILES
from sklearn.preprocessing import StandardScaler

cluster_features = ["LITERACY_RATE", "SC_RATIO",
                    "ST_RATIO", "FEMALE_RATIO", "TOT_POP"]
X_scaled = StandardScaler().fit_transform(df[cluster_features])

# Elbow method
inertias = []
for k in range(2, 10):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

plt.figure(figsize=(7, 4))
plt.plot(range(2, 10), inertias, marker="o", color="steelblue")
plt.title("Elbow Method — Optimal Number of Clusters")
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Inertia")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/elbow.png", dpi=150)
plt.show()
print("Saved: elbow.png")

# Apply k=4 (adjust after looking at elbow plot)
K = 4
df["CLUSTER"] = KMeans(n_clusters=K, random_state=42,
                       n_init=10).fit_predict(X_scaled)

print("\nCluster Profiles (mean values):")
profile = df.groupby("CLUSTER")[cluster_features].mean().round(3)
print(profile)

# Cluster distribution
plt.figure(figsize=(6, 4))
df["CLUSTER"].value_counts().sort_index()\
  .plot(kind="bar", color="mediumpurple", edgecolor="white")
plt.title("Number of Areas per Cluster")
plt.xlabel("Cluster")
plt.ylabel("Count")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/cluster_distribution.png", dpi=150)
plt.show()
print("Saved: cluster_distribution.png")

# Literacy rate per cluster
plt.figure(figsize=(7, 4))
df.groupby("CLUSTER")["LITERACY_RATE"].mean()\
  .plot(kind="bar", color="teal", edgecolor="white")
plt.title("Average Literacy Rate per Cluster")
plt.xlabel("Cluster")
plt.ylabel("Literacy Rate")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/cluster_literacy.png", dpi=150)
plt.show()
print("Saved: cluster_literacy.png")



#DEVELOPMENT SCORE (CUSTOM INEQUALITY INDEX)

scaler = MinMaxScaler()

df["DEV_SCORE_RAW"] = (
      0.50 * df["LITERACY_RATE"]
    + 0.25 * df["FEMALE_RATIO"]
    - 0.15 * df["SC_RATIO"]
    - 0.10 * df["ST_RATIO"]
)

df["DEV_SCORE"] = scaler.fit_transform(df[["DEV_SCORE_RAW"]]) * 100

print("\nTop 10 Most Developed Areas:")
print(df.nlargest(10, "DEV_SCORE")[
    ["NAME", "DISTRICT", "LITERACY_RATE", "DEV_SCORE"]].to_string())

print("\nTop 10 Least Developed Areas:")
print(df.nsmallest(10, "DEV_SCORE")[
    ["NAME", "DISTRICT", "LITERACY_RATE", "DEV_SCORE"]].to_string())

# Dev score by district
plt.figure(figsize=(10, 6))
df.groupby("DISTRICT")["DEV_SCORE"].mean().sort_values()\
  .plot(kind="barh", color="goldenrod")
plt.title("Average Development Score by District")
plt.xlabel("Development Score (0-100)")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/dev_score_by_district.png", dpi=150)
plt.show()
print("Saved: dev_score_by_district.png")
