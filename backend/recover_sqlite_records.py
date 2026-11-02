import csv
import sqlite3
import struct
from pathlib import Path

SOURCE = Path(r"C:\Users\Xufruz\OneDrive\Documents\Locked In\Forcasting Keuangan\backend\recovery_2026-11-02_2230\finance-before-recovery.db")
OUTPUT = SOURCE.parent / "carved-transactions.csv"
PLANS_OUTPUT = SOURCE.parent / "carved-planned-expenses.csv"


def read_varint(data, pos):
    value = 0
    for index in range(9):
        if pos >= len(data):
            raise ValueError("varint extends beyond input")
        byte = data[pos]
        pos += 1
        if index == 8:
            value = (value << 8) | byte
            return value, pos
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, pos
    raise ValueError("invalid varint")


def serial_size(serial_type):
    if serial_type == 0:
        return 0
    if serial_type == 1:
        return 1
    if serial_type == 2:
        return 2
    if serial_type == 3:
        return 3
    if serial_type == 4:
        return 4
    if serial_type == 5:
        return 6
    if serial_type in (6, 7):
        return 8
    if serial_type in (8, 9):
        return 0
    if serial_type in (10, 11):
        raise ValueError("reserved serial type")
    return (serial_type - 12) // 2


def decode_value(data, serial_type):
    if serial_type == 0:
        return None
    if serial_type == 1:
        return int.from_bytes(data, "big", signed=True)
    if serial_type == 2:
        return int.from_bytes(data, "big", signed=True)
    if serial_type == 3:
        return int.from_bytes(data, "big", signed=True)
    if serial_type == 4:
        return int.from_bytes(data, "big", signed=True)
    if serial_type == 5:
        return int.from_bytes(data, "big", signed=True)
    if serial_type == 6:
        return int.from_bytes(data, "big", signed=True)
    if serial_type == 7:
        return struct.unpack(">d", data)[0]
    if serial_type == 8:
        return 0
    if serial_type == 9:
        return 1
    if serial_type >= 13 and serial_type % 2 == 1:
        return data.decode("utf-8", "replace")
    if serial_type >= 12 and serial_type % 2 == 0:
        return data.hex()
    raise ValueError("unknown serial type")


def parse_cell(data, start):
    payload_size, pos = read_varint(data, start)
    _, pos = read_varint(data, pos)  # Row ID
    payload_start = pos
    payload_end = payload_start + payload_size
    if payload_size <= 0 or payload_end > len(data):
        raise ValueError("invalid payload size")

    header_size, header_pos = read_varint(data, payload_start)
    header_end = payload_start + header_size
    if header_end > payload_end or header_size < 2:
        raise ValueError("invalid record header")

    serial_types = []
    while header_pos < header_end:
        serial_type, header_pos = read_varint(data, header_pos)
        serial_types.append(serial_type)
    if header_pos != header_end:
        raise ValueError("misaligned record header")

    values = []
    value_pos = header_end
    for serial_type in serial_types:
        size = serial_size(serial_type)
        value_end = value_pos + size
        if value_end > payload_end:
            raise ValueError("record value extends beyond payload")
        values.append(decode_value(data[value_pos:value_end], serial_type))
        value_pos = value_end
    if value_pos != payload_end:
        raise ValueError("record payload not fully consumed")
    return values


def is_iso_date(value):
    return (
        isinstance(value, str)
        and len(value) >= 10
        and value[4:5] == "-"
        and value[7:8] == "-"
    )


def is_transaction(values):
    # The transaction schema evolved over time. Older SQLite records may retain
    # only the original seven fields even though the current table has ten.
    if not 7 <= len(values) <= 10:
        return False
    tx_id, tx_date, description, amount, tx_type, category = values[:6]
    return (
        isinstance(tx_id, str)
        and tx_id.startswith("tx-")
        and is_iso_date(tx_date)
        and isinstance(description, str)
        and isinstance(amount, (int, float))
        and tx_type in {"income", "expense", "transfer", "transfer_in"}
        and isinstance(category, str)
        and any(is_iso_date(value) for value in values[6:] if isinstance(value, str))
    )


def normalized_transaction(values):
    tx_id, tx_date, description, amount, tx_type, category = values[:6]
    trailing = list(values[6:])
    created_at_index = next(
        (index for index, value in enumerate(trailing) if is_iso_date(value)),
        None,
    )
    if created_at_index is None:
        raise ValueError("transaction has no created_at value")
    created_at = trailing[created_at_index]
    account_values = trailing[created_at_index + 1:]
    wallet = account_values[0] if len(account_values) >= 1 else ""
    transfer_to = account_values[1] if len(account_values) >= 2 else ""
    savings_status = account_values[2] if len(account_values) >= 3 else "non_savings"
    return [
        tx_id, tx_date, description, amount, tx_type, category,
        wallet or "", transfer_to or "", savings_status or "non_savings", created_at
    ]


def is_plan(values):
    if not 8 <= len(values) <= 9:
        return False
    plan_id, title, amount, category, probability, plan_date, notes = values[:7]
    return (
        isinstance(plan_id, str)
        and plan_id.startswith("plan-")
        and isinstance(title, str)
        and isinstance(amount, (int, float))
        and isinstance(category, str)
        and isinstance(probability, int)
        and 0 <= probability <= 100
        and is_iso_date(plan_date)
        and any(is_iso_date(value) for value in values[7:] if isinstance(value, str))
    )


def main():
    data = SOURCE.read_bytes()
    candidates = {}
    plan_candidates = {}
    for start in range(len(data)):
        try:
            values = parse_cell(data, start)
        except (ValueError, IndexError, OverflowError, UnicodeDecodeError, struct.error):
            continue
        if is_transaction(values):
            candidates[values[0]] = normalized_transaction(values)
        elif is_plan(values):
            plan_candidates[values[0]] = values

    rows = sorted(candidates.values(), key=lambda row: (row[1], row[0]))
    plans = []
    for values in plan_candidates.values():
        plan_id, title, amount, category, probability, plan_date, notes = values[:7]
        trailing = list(values[7:])
        created_at = next(value for value in trailing if is_iso_date(value))
        if len(created_at) > 26:
            continue
        plans.append([plan_id, title, amount, category, probability, plan_date, notes or "", created_at])
    plans.sort(key=lambda row: (row[5], row[0]))
    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "id", "date", "description", "amount", "type", "category",
            "wallet", "transfer_to", "savings_status", "created_at"
        ])
        writer.writerows(rows)

    with PLANS_OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "title", "amount", "category", "probability", "date", "notes", "created_at"])
        writer.writerows(plans)

    print(f"Recovered {len(rows)} transaction candidates")
    print(f"Saved candidate CSV: {OUTPUT}")
    print(f"Recovered {len(plans)} planned-expense candidates")
    print(f"Saved planned-expense CSV: {PLANS_OUTPUT}")


if __name__ == "__main__":
    main()
