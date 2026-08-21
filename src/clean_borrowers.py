import pandas as pd

raw_path = "data/raw/borrowers.csv"
clean_path = "data/cleaned/borrowers.csv"

df = pd.read_csv(raw_path)

before = len(df)

df = df.drop_duplicates()

after = len(df)

df.to_csv(
    clean_path,
    index=False
)

print("Raw rows:", before)
print("Clean rows:", after)
print("Rows removed:", before - after)
print("Unique borrower IDs:", df["borrower_id"].nunique())
print("Output:", clean_path)
