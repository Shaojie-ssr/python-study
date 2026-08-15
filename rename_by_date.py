from pathlib import Path
from datetime import date

folder = Path("messy_folder/文档")
today = date.today().isoformat()      # "2026-07-31"

for f in folder.iterdir():
    if f.suffix == ".txt":
        new_name = f"{today}_{f.name}"
        f.rename(folder / new_name)
        print(f"{f.name} → {new_name}")
