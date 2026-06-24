"""
Data manager module for the accounting package.
"""

import os
import uuid
import pandas as pd

DATA_FILE = "records.csv"


class DataManager:
    """Manage accounting records and persist them to CSV."""

    def __init__(self, filepath=DATA_FILE):
        self.filepath = filepath
        self.columns = ["id", "date", "type", "category", "amount", "note"]
        self.table = pd.DataFrame(columns=self.columns)
        self.load_data()

    def load_data(self):
        if os.path.exists(self.filepath):
            try:
                df = pd.read_csv(self.filepath, dtype={"id": str})
                for col in self.columns:
                    if col not in df.columns:
                        df[col] = ""
                df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
                self.table = df[self.columns].copy()
            except Exception as e:
                self.table = pd.DataFrame(columns=self.columns)
                raise RuntimeError(f"Failed to load data: {e}") from e
        else:
            self.table = pd.DataFrame(columns=self.columns)

    def save_data(self):
        try:
            self.table.to_csv(self.filepath, index=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save data: {e}") from e

    def add_record(self, date, record_type, category, amount, note):
        rec_id = str(uuid.uuid4())
        record = {
            "id": rec_id,
            "date": date,
            "type": record_type,
            "category": category or "其他",
            "amount": float(amount),
            "note": note or ""
        }
        self.table = pd.concat([self.table, pd.DataFrame([record])], ignore_index=True)
        self.save_data()
        return rec_id

    def update_record(self, record_id, new_values: dict):
        idxs = self.table.index[self.table["id"] == record_id].tolist()
        if not idxs:
            raise KeyError("Record not found")
        idx = idxs[0]
        for key, val in new_values.items():
            if key in self.columns:
                self.table.at[idx, key] = val
        self.table["amount"] = pd.to_numeric(self.table["amount"], errors="coerce").fillna(0.0)
        self.save_data()

    def delete_record(self, record_id):
        if record_id not in self.table["id"].values:
            raise KeyError("Record to delete does not exist")
        self.table = self.table[self.table["id"] != record_id].reset_index(drop=True)
        self.save_data()

    def get_all_records(self):
        return self.table.copy()

    def get_summary(self):
        df = self.table.copy()
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        income = df[df["type"] == "收入"]["amount"].sum()
        expense = df[df["type"] == "支出"]["amount"].sum()
        return float(income), float(expense)

    def export_csv(self, path):
        try:
            self.table.to_csv(path, index=False)
        except Exception as e:
            raise RuntimeError(f"Export CSV failed: {e}") from e

    def export_excel(self, path):
        try:
            self.table.to_excel(path, index=False)
        except Exception as e:
            raise RuntimeError(f"Export Excel failed: {e}") from e
