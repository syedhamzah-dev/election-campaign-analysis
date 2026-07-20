from pathlib import Path
import pandas as pd

CSV_PATH = Path(r"C:\Users\Sobiya Anjum\Downloads\archive (6)\GE_2024_Results.csv")

def main():
    df = pd.read_csv(CSV_PATH, na_values=['-'])
    df.columns = [c.strip() for c in df.columns]
    # normalize column names
    if '% of Votes' in df.columns:
        df.rename(columns={'% of Votes': 'Pct Votes'}, inplace=True)

    # numeric conversions
    for col in ['EVM Votes', 'Postal Votes', 'Total Votes', 'Pct Votes']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    out_lines = []
    out_lines.append(f"File: {CSV_PATH}\nRows: {len(df)} Columns: {len(df.columns)}\n")
    out_lines.append("Columns and dtypes:\n" + df.dtypes.to_string() + "\n")
    out_lines.append("Missing values per column:\n" + df.isnull().sum().to_string() + "\n")
    if df.select_dtypes(include='number').shape[1] > 0:
        out_lines.append("Numeric summary (describe):\n" + df.describe().to_string() + "\n")

    if 'Party' in df.columns:
        out_lines.append("Top 10 parties by candidate count:\n" + df['Party'].value_counts().head(10).to_string() + "\n")

    if 'Result' in df.columns:
        winners = df[df['Result'].astype(str).str.lower() == 'won']
        out_lines.append("Top 10 parties by seats won:\n" + winners['Party'].value_counts().head(10).to_string() + "\n")

    # compute winning margins per constituency
    if 'Constituency' in df.columns and 'Total Votes' in df.columns:
        top2 = df.sort_values(['Constituency', 'Total Votes'], ascending=[True, False]).groupby('Constituency').head(2)
        margins = top2.groupby('Constituency')['Total Votes'].apply(lambda x: int(x.iloc[0] - (x.iloc[1] if len(x) > 1 else 0)))
        closest = margins.sort_values().head(10)
        out_lines.append("Top 10 closest margins (votes):\n" + closest.to_string() + "\n")

        turnout = df.groupby('Constituency')['Total Votes'].sum().sort_values(ascending=False).head(10)
        out_lines.append("Top 10 constituencies by total votes cast (sum of candidate totals):\n" + turnout.to_string() + "\n")

    report = "\n".join(out_lines)
    print(report)
    Path('analysis_report.txt').write_text(report)
    print("Report written to analysis_report.txt")

if __name__ == '__main__':
    main()
