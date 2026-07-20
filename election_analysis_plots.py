from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

CSV_PATH = Path(r"C:\Users\Sobiya Anjum\Downloads\archive (6)\GE_2024_Results.csv")
OUT_DIR = Path('.')
OUT_DIR.mkdir(exist_ok=True)

def load_clean():
    df = pd.read_csv(CSV_PATH, na_values=['-'])
    df.columns = [c.strip() for c in df.columns]
    if '% of Votes' in df.columns:
        df.rename(columns={'% of Votes': 'Pct Votes'}, inplace=True)
    for col in ['EVM Votes', 'Postal Votes', 'Total Votes', 'Pct Votes']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def seats_by_party(df, out):
    winners = df[df['Result'].astype(str).str.lower() == 'won']
    seats = winners['Party'].value_counts().head(30)
    plt.figure(figsize=(10,6))
    sns.barplot(x=seats.values, y=seats.index, palette='tab20')
    plt.xlabel('Seats')
    plt.title('Top parties by seats won')
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

def votes_by_party(df, out):
    votes = df.groupby('Party')['Total Votes'].sum().sort_values(ascending=False).head(30)
    plt.figure(figsize=(10,6))
    sns.barplot(x=votes.values, y=votes.index, palette='mako')
    plt.xlabel('Total votes (sum across candidates)')
    plt.title('Top parties by total votes received')
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

def margins_hist(df, out):
    # compute margin between top2
    top2 = df.sort_values(['Constituency', 'Total Votes'], ascending=[True, False]).groupby('Constituency').head(2)
    margins = top2.groupby('Constituency')['Total Votes'].apply(lambda x: float(x.iloc[0] - (x.iloc[1] if len(x) > 1 else 0)))
    plt.figure(figsize=(8,5))
    sns.histplot(margins[margins>=0], bins=100)
    plt.xlabel('Winning margin (votes)')
    plt.title('Distribution of winning margins')
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

def evm_vs_postal_scatter(df, out):
    # aggregate by constituency
    agg = df.groupby('Constituency')[['EVM Votes','Postal Votes']].sum().dropna()
    plt.figure(figsize=(7,7))
    plt.scatter(agg['EVM Votes'], agg['Postal Votes'], alpha=0.6)
    maxv = max(agg['EVM Votes'].max(), agg['Postal Votes'].max())
    plt.plot([0, maxv], [0, maxv], color='red', linestyle='--')
    plt.xlabel('EVM Votes (sum per constituency)')
    plt.ylabel('Postal Votes (sum per constituency)')
    plt.title('EVM vs Postal Votes by Constituency')
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

def evm_postal_by_party(df, out):
    agg = df.groupby('Party')[['EVM Votes','Postal Votes']].sum().fillna(0)
    top = agg.sum(axis=1).sort_values(ascending=False).head(20).index
    agg_top = agg.loc[top]
    agg_top = agg_top.sort_values('EVM Votes', ascending=True)
    plt.figure(figsize=(10,8))
    agg_top.plot(kind='barh')
    plt.xlabel('Votes (sum)')
    plt.title('EVM vs Postal Votes by Party (top 20)')
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

def turnout_top20(df, out):
    turnout = df.groupby('Constituency')['Total Votes'].sum().sort_values(ascending=False).head(20)
    plt.figure(figsize=(10,8))
    sns.barplot(x=turnout.values, y=turnout.index, palette='viridis')
    plt.xlabel('Total votes cast (sum of candidate totals)')
    plt.title('Top 20 constituencies by summed total votes')
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

def main():
    df = load_clean()
    seats_by_party(df, OUT_DIR / 'seats_by_party.png')
    votes_by_party(df, OUT_DIR / 'votes_by_party.png')
    margins_hist(df, OUT_DIR / 'margins_hist.png')
    evm_vs_postal_scatter(df, OUT_DIR / 'evm_vs_postal_scatter.png')
    evm_postal_by_party(df, OUT_DIR / 'evm_postal_by_party.png')
    turnout_top20(df, OUT_DIR / 'turnout_top20.png')
    print('Plots written:', ', '.join([str(p) for p in [OUT_DIR/'seats_by_party.png', OUT_DIR/'votes_by_party.png', OUT_DIR/'margins_hist.png', OUT_DIR/'evm_vs_postal_scatter.png', OUT_DIR/'evm_postal_by_party.png', OUT_DIR/'turnout_top20.png']]))

if __name__ == '__main__':
    main()
