import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("graphs", exist_ok=True)

print("="*80)
print("           EXPLORATORY DATA ANALYSIS (EDA)")
print("="*80)

df = pd.read_csv("result_by_state_cleaned.csv")

print("\n" + "="*80)
print("1. DATASET LOADED SUCCESSFULLY")
print("="*80)

print("\n" + "="*80)
print("2. FIRST FIVE ROWS")
print("="*80)
print(df.head())

print("\n" + "="*80)
print("3. LAST FIVE ROWS")
print("="*80)
print(df.tail())

print("\n" + "="*80)
print("4. DATASET INFORMATION")
print("="*80)
df.info()

print("\n" + "="*80)
print("5. DATASET SHAPE")
print("="*80)

print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\n" + "="*80)
print("6. COLUMN NAMES")
print("="*80)

print(df.columns.tolist())

print("\n" + "="*80)
print("7. DATA TYPES")
print("="*80)

print(df.dtypes)

print("\n" + "="*80)
print("8. MISSING VALUES")
print("="*80)

print(df.isnull().sum())

print("\n" + "="*80)
print("9. DUPLICATE RECORDS")
print("="*80)

duplicates = df.duplicated().sum()

print(f"Total Duplicate Rows : {duplicates}")

print("\n" + "="*80)
print("10. STATISTICAL SUMMARY (NUMERICAL)")
print("="*80)

print(df.describe())

print("\n" + "="*80)
print("12. UNIQUE VALUES IN EACH COLUMN")
print("="*80)

print(df.nunique())

print("\n" + "="*80)
print("13. VALUE COUNTS OF CATEGORICAL COLUMNS")
print("="*80)

for col in df.select_dtypes(include="object"):
    print(f"\nColumn : {col}")
    print(df[col].value_counts())

print("\n" + "="*80)
print("14. CORRELATION MATRIX")
print("="*80)

print(df.corr(numeric_only=True))

print("\n" + "="*80)
print("15. OUTLIER DETECTION USING IQR")
print("="*80)

numeric_cols = df.select_dtypes(include=np.number).columns

for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    outliers = ((df[col] < lower) | (df[col] > upper)).sum()

    print(f"{col:<25} Outliers : {outliers}")

print("\n" + "="*80)
print("16. DISTRIBUTION ANALYSIS")
print("="*80)    


print("\n" + "="*80)
print("16. HISTOGRAM")
print("="*80)

numeric_cols = df.select_dtypes(include='number').columns

for col in numeric_cols:
    plt.figure(figsize=(8,5))
    plt.hist(df[col], bins=20, edgecolor='black')
    plt.title(f"Histogram of {col}")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.grid(alpha=0.3)

    plt.savefig(f"graphs/histogram_{col}.png", dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()


  



print("\n" + "="*80)
print("18. BAR CHARTS")
print("="*80)

categorical_cols = df.select_dtypes(include='object').columns

for col in categorical_cols:
    plt.figure(figsize=(10,5))
    df[col].value_counts().plot(kind='bar')

    plt.title(f"Bar Chart of {col}")
    plt.xlabel(col)
    plt.ylabel("Count")
    plt.xticks(rotation=45)

    plt.savefig(f"graphs/bar_{col}.png", dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()


print("\n" + "="*80)
print("19. PIE CHARTS")
print("="*80)

for col in categorical_cols:
    plt.figure(figsize=(7,7))

    df[col].value_counts().plot(
        kind='pie',
        autopct='%1.1f%%'
    )

    plt.title(f"Pie Chart of {col}")
    plt.ylabel("")

    plt.savefig(f"graphs/pie_{col}.png", dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()

print("\n" + "="*80)
print("20. SCATTER PLOTS")
print("="*80)

if len(numeric_cols) >= 2:
    for i in range(len(numeric_cols)-1):

        x = numeric_cols[i]
        y = numeric_cols[i+1]

        plt.figure(figsize=(8,5))
        plt.scatter(df[x], df[y])

        plt.title(f"{x} vs {y}")
        plt.xlabel(x)
        plt.ylabel(y)

        plt.savefig(f"graphs/scatter_{x}_vs_{y}.png",
                    dpi=300,
                    bbox_inches="tight")

        plt.show()
        plt.close()

print("\n" + "="*80)
print("21. LINE PLOTS")
print("="*80)

for col in numeric_cols:

    plt.figure(figsize=(10,5))
    plt.plot(df[col])

    plt.title(f"Line Plot of {col}")
    plt.xlabel("Index")
    plt.ylabel(col)

    plt.savefig(f"graphs/line_{col}.png", dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()

print("\n" + "="*80)
print("22. CORRELATION HEATMAP")
print("="*80)

corr = df.corr(numeric_only=True)

plt.figure(figsize=(10,8))
plt.imshow(corr, cmap='coolwarm', interpolation='nearest')
plt.colorbar()

plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
plt.yticks(range(len(corr.columns)), corr.columns)

plt.title("Correlation Heatmap")

plt.savefig("graphs/correlation_heatmap.png",
            dpi=300,
            bbox_inches="tight")

plt.show()
plt.close()            

print("\n" + "="*80)
print("20. FINAL OBSERVATIONS")
print("="*80)

print("""
EDA Completed Successfully.

Summary Checklist
-----------------
✓ Dataset Loaded
✓ Shape Checked
✓ Data Types Verified
✓ Missing Values Checked
✓ Duplicate Rows Checked
✓ Statistical Summary Generated
✓ Unique Values Examined
✓ Correlation Analysed
✓ Outliers Detected
✓ Distributions Visualized
✓ Relationships Visualized

Proceed to Feature Engineering or Machine Learning.
""")