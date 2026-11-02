import csv
from pathlib import Path

recovery_dir = Path(__file__).parent
source = recovery_dir / "carved-transactions.csv"
target = recovery_dir / "recovered-original-transactions.csv"

known_ai_test_ids = {
    "tx-c864b390", "tx-da6bcbf7", "tx-5f20bd18",
    "tx-770f11bc", "tx-2e45e1c8", "tx-96121d9",
    "tx-ef50b403", "tx-d9b06d0b", "tx-3df73ad9",
    "tx-d35508ab", "tx-01ba9dca", "tx-8041df50",
    "tx-44ea3b37", "tx-db36a1d2", "tx-b2402787",
    "tx-6947ac97", "tx-df744eff", "tx-780aa4a7",
    "tx-17a05889", "tx-4034967e", "tx-1a1a2d2c",
    "tx-cc7f54a2", "tx-8e4bb1cb", "tx-c4e3ff65",
    "tx-5bfa2da5", "tx-228c085b", "tx-cb9b70c2",
    "tx-1b701ed6", "tx-19cb15e9", "tx-84f9be41",
    "tx-b73dbedb", "tx-85183ff3", "tx-0058b42f",
    "tx-16552884",
}

with source.open(encoding="utf-8", newline="") as file:
    reader = csv.DictReader(file)
    rows = list(reader)
    fieldnames = reader.fieldnames

original_rows = [
    row for row in rows
    if row["id"] not in known_ai_test_ids
    and not (
        row["description"] == "Transaksi Baru"
        and row["created_at"].startswith("2026-11-02")
    )
]
suspicious_rows = [
    row for row in original_rows
    if row["description"] == "Transaksi Baru" and row["created_at"].startswith("2026-11-02")
]

with target.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(original_rows)

print(f"Recovered candidates: {len(rows)}")
print(f"Excluded known AI test records: {len(rows) - len(original_rows)}")
print(f"Original transaction candidates: {len(original_rows)}")
print(f"Suspicious candidates remaining: {len(suspicious_rows)}")
print(f"Saved: {target}")
