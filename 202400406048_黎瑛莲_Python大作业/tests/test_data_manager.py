import sys
import os

def _add_src_to_path():
    # Ensure src/ is on sys.path so tests can import the package
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src = os.path.join(root, "src")
    if src not in sys.path:
        sys.path.insert(0, src)


def test_data_manager_crud(tmp_path):
    _add_src_to_path()
    from accounting_202400406048.data_manager import DataManager

    test_file = tmp_path / "test_records.csv"
    dm = DataManager(filepath=str(test_file))
    # Initially empty
    assert dm.get_all_records().empty

    # Add record
    rec_id = dm.add_record("2026-06-24", "支出", "测试", 10.5, "note")
    df = dm.get_all_records()
    assert len(df) == 1
    assert float(df.loc[df['id'] == rec_id, 'amount'].iloc[0]) == 10.5

    # Update record
    dm.update_record(rec_id, {"amount": 20.0, "note": "updated"})
    df2 = dm.get_all_records()
    assert float(df2.loc[df2['id'] == rec_id, 'amount'].iloc[0]) == 20.0
    assert df2.loc[df2['id'] == rec_id, 'note'].iloc[0] == "updated"

    # Summary
    income, expense = dm.get_summary()
    assert expense == 20.0

    # Delete
    dm.delete_record(rec_id)
    assert dm.get_all_records().empty


def test_export_csv(tmp_path):
    _add_src_to_path()
    from accounting_202400406048.data_manager import DataManager

    test_file = tmp_path / "test_records2.csv"
    dm = DataManager(filepath=str(test_file))
    dm.add_record("2026-06-24", "收入", "工资", 1000.0, "salary")
    out_path = tmp_path / "out.csv"
    dm.export_csv(str(out_path))
    assert out_path.exists()
