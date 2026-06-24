import os
import sys
from pathlib import Path

# Ensure src is on path when running tests from this tests/ directory
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_data_manager_add_update_delete(tmp_path):
    """Test DataManager add, update, delete and persistence."""
    from accounting_202400406048.data_manager import DataManager

    csv_path = tmp_path / "records.csv"

    dm = DataManager(filepath=str(csv_path))
    # initially empty
    df0 = dm.get_all_records()
    assert df0.empty

    # add record
    rec_id = dm.add_record("2026-06-24", "支出", "餐饮", 50.0, "午餐")
    df1 = dm.get_all_records()
    assert len(df1) == 1
    income, expense = dm.get_summary()
    assert income == 0.0 and expense == 50.0

    # update record
    dm.update_record(rec_id, {"amount": 60.0, "note": "晚餐"})
    df2 = dm.get_all_records()
    assert float(df2.loc[df2["id"] == rec_id, "amount"].iloc[0]) == 60.0

    # persistence: create new manager to read same file
    dm2 = DataManager(filepath=str(csv_path))
    df_new = dm2.get_all_records()
    assert len(df_new) == 1

    # delete
    dm.delete_record(rec_id)
    assert dm.get_all_records().empty


def test_export_csv(tmp_path):
    from accounting_202400406048.data_manager import DataManager

    csv_path = tmp_path / "records.csv"
    out_path = tmp_path / "export.csv"
    dm = DataManager(filepath=str(csv_path))
    dm.add_record("2026-06-24", "收入", "工资", 1000.0, "工资入账")
    dm.export_csv(str(out_path))
    assert out_path.exists()
