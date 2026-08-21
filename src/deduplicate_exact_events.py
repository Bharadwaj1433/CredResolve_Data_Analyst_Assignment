import pandas as pd
from pathlib import Path

clean_path = Path("data/cleaned")

tables = {
    "payments": "payment_id",
    "whatsapp_events": "whatsapp_event_id"
}

for table, key in tables.items():
    path = clean_path / f"{table}.csv"
    df = pd.read_csv(path)

    before = len(df)
    df = df.drop_duplicates()
    after = len(df)

    df.to_csv(
        path,
        index=False
    )

    print(table)
    print("Rows before:", before)
    print("Rows after:", after)
    print("Rows removed:", before - after)

print("Exact duplicate removal completed")
