"""
Data manager module for the accounting package.

Contains DataManager class with strongly named methods and docstrings.
"""

import os
import uuid
import pandas as pd

DATA_FILE = "records.csv"


class DataManager:
    """Manage accounting records and persist them to CSV.

    Usage:
        dm = DataManager()
        rec_id = dm.add_record(...)
    """

    def __init__(self, filepath=DATA_FILE):
        self.filepath = filepath
        self.columns = ["id", "date", "type", "category", "amount", "note"]
        self.table = pd.DataFrame(columns=self.columns)
        self.load_data()

    def load_data(self):
        """Load data from CSV file. If the file does not exist, start with an empty table."""
        if os.path.exists(self.filepath):
            try:
                df = pd.read_csv(self.filepath, dtype={"id": str})
                for col in self.columns:
                    if col not in df.columns:
                        df[col] = ""
                df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
                self.table = df[self.columns].copy()
            except Exception as e:
                # If loading fails, reset to empty and propagate an error
                self.table = pd.DataFrame(columns=self.columns)
                raise RuntimeError(f"Failed to load data: {e}") from e
        else:
            self.table = pd.DataFrame(columns=self.columns)

    def save_data(self):
        """Save current table to CSV. Raises RuntimeError on failure."""
        try:
            self.table.to_csv(self.filepath, index=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save data: {e}") from e

    def add_record(self, date, record_type, category, amount, note):
        """Add a record and persist it. Returns the new record id."""
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
        """Update the record identified by record_id using keys in new_values."""
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
        """Delete a record by id and persist changes."""
        if record_id not in self.table["id"].values:
            raise KeyError("Record to delete does not exist")
        self.table = self.table[self.table["id"] != record_id].reset_index(drop=True)
        self.save_data()

    def get_all_records(self):
        """Return a copy of the internal DataFrame for safe reading."""
        return self.table.copy()

    def get_summary(self):
        """Return (income, expense) totals as floats."""
        df = self.table.copy()
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        income = df[df["type"] == "收入"]["amount"].sum()
        expense = df[df["type"] == "支出"]["amount"].sum()
        return float(income), float(expense)

    def export_csv(self, path):
        """Export current table to CSV path."""
        try:
            self.table.to_csv(path, index=False)
        except Exception as e:
            raise RuntimeError(f"Export CSV failed: {e}") from e

    def export_excel(self, path):
        """Export current table to Excel xlsx. Requires openpyxl or xlsxwriter."""
        try:
            self.table.to_excel(path, index=False)
        except Exception as e:
            raise RuntimeError(f"Export Excel failed: {e}") from e
