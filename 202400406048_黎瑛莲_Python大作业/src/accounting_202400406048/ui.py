"""
UI module for the accounting package.
Provides ExpenseTrackerUI class and run_app convenience function.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import traceback
import pandas as pd
from PIL import ImageTk

from .data_manager import DataManager
from .charts import show_monthly_chart, show_category_pie
from .utils import make_logo_image


class ExpenseTrackerUI:
    """Graphical user interface for the expense tracker application."""

    def __init__(self, root, data_manager: DataManager):
        self.root = root
        self.data_manager = data_manager
        self.root.title("记账本 - 重构与风格统一")
        try:
            logo = make_logo_image("记账")
            self.tk_logo = ImageTk.PhotoImage(logo)
            self.root.iconphoto(False, self.tk_logo)
        except Exception:
            pass

        # Input variables (snake_case naming)
        self.var_date = tk.StringVar(value="")
        self.var_type = tk.StringVar(value="支出")
        self.var_category = tk.StringVar(value="其他")
        self.var_amount = tk.StringVar(value="")
        self.var_note = tk.StringVar(value="")

        self.build_gui()
        self.refresh_table()
        self.update_status()

    def build_gui(self):
        """Construct GUI layout and widgets."""
        top_frame = ttk.Frame(self.root, padding=8)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="日期(YYYY-MM-DD)：").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(top_frame, textvariable=self.var_date, width=12).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(top_frame, text="类型：").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        ttk.Combobox(top_frame, textvariable=self.var_type, values=["支出", "收入"], width=8, state="readonly").grid(row=0, column=3, sticky=tk.W)

        ttk.Label(top_frame, text="类别：").grid(row=0, column=4, sticky=tk.W, padx=(10, 0))
        ttk.Entry(top_frame, textvariable=self.var_category, width=12).grid(row=0, column=5, sticky=tk.W)

        ttk.Label(top_frame, text="金额：").grid(row=0, column=6, sticky=tk.W, padx=(10, 0))
        ttk.Entry(top_frame, textvariable=self.var_amount, width=10).grid(row=0, column=7, sticky=tk.W)

        ttk.Label(top_frame, text="备注：").grid(row=1, column=0, sticky=tk.W, pady=(6, 0))
        ttk.Entry(top_frame, textvariable=self.var_note, width=60).grid(row=1, column=1, columnspan=6, sticky=tk.W, pady=(6, 0))

        btn_frame = ttk.Frame(self.root, padding=8)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="添加记录", command=self.on_add).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="编辑选中", command=self.on_edit).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="删除选中", command=self.on_delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="导出 CSV", command=self.on_export_csv).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="导出 Excel", command=self.on_export_excel).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="月度柱状图", command=self.on_show_monthly).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_frame, text="类别饼图", command=self.on_show_category).pack(side=tk.LEFT, padx=4)

        # Table
        table_frame = ttk.Frame(self.root, padding=8)
        table_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("date", "type", "category", "amount", "note")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("note", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-1>", lambda e: self.on_edit())

        # Status bar
        self.status_var = tk.StringVar()
        status_label = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, side=tk.BOTTOM)

    # Event handlers (snake_case)
    def on_add(self):
        date = self.var_date.get().strip()
        if not date:
            messagebox.showwarning("输入错误", "请填写日期（YYYY-MM-DD）。")
            return
        try:
            amount = float(self.var_amount.get().strip())
        except Exception:
            messagebox.showwarning("输入错误", "金额请输入数字。")
            return
        try:
            self.data_manager.add_record(date, self.var_type.get(), self.var_category.get(), amount, self.var_note.get())
            self.refresh_table()
            self.clear_inputs()
            self.update_status()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("保存失败", f"添加记录失败：{e}")

    def on_edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("编辑", "请先选中一行。")
            return
        record_id = sel[0]
        try:
            df = self.data_manager.get_all_records()
            row = df.loc[df["id"] == record_id].iloc[0]
        except Exception:
            messagebox.showerror("查找失败", "未能找到所选记录。")
            return
        EditRecordWindow(self.root, self.data_manager, record_id, row, on_saved=lambda: (self.refresh_table(), self.update_status()))

    def on_delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("删除", "请先选中一行。")
            return
        record_id = sel[0]
        if not messagebox.askyesno("确认删除", "确定要删除选中的记录吗？"):
            return
        try:
            self.data_manager.delete_record(record_id)
            self.refresh_table()
            self.update_status()
        except Exception as e:
            messagebox.showerror("删除失败", f"删除记录失败：{e}")

    def on_export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV 文件", "*.csv")])
        if not path:
            return
        try:
            self.data_manager.export_csv(path)
            messagebox.showinfo("导出成功", f"已导出到 {path}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def on_export_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel 文件", "*.xlsx")])
        if not path:
            return
        try:
            self.data_manager.export_excel(path)
            messagebox.showinfo("导出成功", f"已导出到 {path}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def on_show_monthly(self):
        try:
            df = self.data_manager.get_all_records()
            show_monthly_chart(self.root, df)
        except Exception as e:
            messagebox.showerror("绘图失败", str(e))

    def on_show_category(self):
        try:
            df = self.data_manager.get_all_records()
            show_category_pie(self.root, df)
        except Exception as e:
            messagebox.showerror("绘图失败", str(e))

    def refresh_table(self):
        """Refresh treeview contents from data manager."""
        for r in self.tree.get_children():
            self.tree.delete(r)
        df = self.data_manager.get_all_records().copy()
        try:
            df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.sort_values(by="date_parsed", ascending=False).drop(columns="date_parsed")
        except Exception:
            pass
        for _, row in df.iterrows():
            iid = row["id"]
            self.tree.insert("", tk.END, iid=iid, values=(row["date"], row["type"], row["category"], row["amount"], row["note"]))

    def clear_inputs(self):
        self.var_date.set("")
        self.var_amount.set("")
        self.var_note.set("")

    def update_status(self):
        try:
            total = len(self.data_manager.get_all_records())
            income, expense = self.data_manager.get_summary()
            self.status_var.set(f"记录数：{total}    收入总计：{income:.2f}    支出总计：{expense:.2f}")
        except Exception:
            self.status_var.set(f"记录数：{len(self.data_manager.get_all_records())}")


class EditRecordWindow:
    """Popup window for editing a single record."""

    def __init__(self, master, data_manager, record_id, row_series, on_saved=None):
        self.data_manager = data_manager
        self.record_id = record_id
        self.on_saved = on_saved
        self.win = tk.Toplevel(master)
        self.win.title("编辑记录")
        self.var_date = tk.StringVar(value=row_series["date"])
        self.var_type = tk.StringVar(value=row_series["type"])
        self.var_category = tk.StringVar(value=row_series["category"])
        self.var_amount = tk.StringVar(value=str(row_series["amount"]))
        self.var_note = tk.StringVar(value=row_series["note"])
        self.build()

    def build(self):
        ttk.Label(self.win, text="日期(YYYY-MM-DD)：").grid(row=0, column=0, sticky=tk.W, padx=6, pady=6)
        ttk.Entry(self.win, textvariable=self.var_date).grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(self.win, text="类型：").grid(row=1, column=0, sticky=tk.W, padx=6)
        ttk.Combobox(self.win, textvariable=self.var_type, values=["支出", "收入"], state="readonly").grid(row=1, column=1, padx=6, pady=6)
        ttk.Label(self.win, text="类别：").grid(row=2, column=0, sticky=tk.W, padx=6)
        ttk.Entry(self.win, textvariable=self.var_category).grid(row=2, column=1, padx=6, pady=6)
        ttk.Label(self.win, text="金额：").grid(row=3, column=0, sticky=tk.W, padx=6)
        ttk.Entry(self.win, textvariable=self.var_amount).grid(row=3, column=1, padx=6, pady=6)
        ttk.Label(self.win, text="备注：").grid(row=4, column=0, sticky=tk.W, padx=6)
        ttk.Entry(self.win, textvariable=self.var_note, width=40).grid(row=4, column=1, padx=6, pady=6)
        ttk.Button(self.win, text="保存", command=self.on_save).grid(row=5, column=0, padx=6, pady=8)
        ttk.Button(self.win, text="取消", command=self.win.destroy).grid(row=5, column=1, padx=6, pady=8)

    def on_save(self):
        try:
            amount = float(self.var_amount.get().strip())
            new_values = {
                "date": self.var_date.get().strip(),
                "type": self.var_type.get(),
                "category": self.var_category.get().strip() or "其他",
                "amount": amount,
                "note": self.var_note.get().strip()
            }
            self.data_manager.update_record(self.record_id, new_values)
            if callable(self.on_saved):
                self.on_saved()
            self.win.destroy()
        except Exception as e:
            messagebox.showerror("保存失败", f"保存失败：{e}")


def run_app():
    """Convenience function to start the Tk application."""
    root = tk.Tk()
    root.geometry("900x600")
    dm = DataManager()
    app = ExpenseTrackerUI(root, dm)
    # prefill today's date for convenience
    import datetime
    app.var_date.set(datetime.date.today().isoformat())
    root.mainloop()
