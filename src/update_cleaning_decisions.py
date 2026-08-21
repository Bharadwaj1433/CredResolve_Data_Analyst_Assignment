from pathlib import Path

path = Path("reports/cleaning_decisions.md")

text = path.read_text()

text = text.replace(
    "## Data Integrity\n\nNo raw records were modified or deleted.\n\nCleaning transformations are reproducible through scripts stored under src.",
    "## Data Integrity\n\nThe raw data files remain unchanged. All cleaning transformations were applied to copies in the cleaned analytical layer.\n\nThe cleaning transformations used to produce the current cleaned layer are represented by scripts stored under src."
)

path.write_text(text)
print("Cleaning decisions updated")
