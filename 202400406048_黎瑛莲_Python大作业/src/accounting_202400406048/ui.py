"""
UI module: attempt to use icons from assets when available.
Buttons will show icon+text when icon exists, otherwise fall back to text only.
"""

# ... (Keep the previously committed ExpenseTrackerUI implementation but update button creation to use icons)

import traceback
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import pandas as pd
from PIL import Image, ImageTk
from pathlib import Path

try:
    from ttkbootstrap import Style
except Exception:
    Style = None

try:
    from tkcalendar import DateEntry
except Exception:
    DateEntry = None

from .data_manager import DataManager
from .charts import show_monthly_chart, show_category_pie
from .utils import make_logo_image, load_icon_image


def _load_icon_photo(name: str, prefer_size: int = 24):
    """Return a PhotoImage if an icon file exists, otherwise None."""
    p = load_icon_image(name, prefer_size=prefer_size)
    if not p:
        return None
    try:
        img = Image.open(p)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


class ExpenseTrackerUI:
    def __init__(self, root, data_manager: DataManager, theme: str = "litera"):
        self.root = root
        self.data_manager = data_manager
        self.root.title("记账本 - 美化版")

        self._icons = {}

        # Apply ttkbootstrap style if available
        self.style = None
        if Style is not None:
            try:
                self.style = Style(theme=theme)
            except Exception:
                try:
                    self.style = Style()
                except Exception:
                    self.style = None

        default_font = (None, 10)
        try:
            s = ttk.Style() if Style is None else self.style
            s.configure("TLabel", font=default_font)
            s.configure("TButton", padding=6)
            s.configure("Treeview", font=(None, 10), rowheight=26)
        except Exception:
            pass

        header = ttk.Frame(self.root, padding=(10, 8))
        header.pack(fill=tk.X)
        try:
            logo_img = make_logo_image("记账", size=(48, 48))
            self.logo_tk = ImageTk.PhotoImage(logo_img)
            ttk.Label(header, image=self.logo_tk).pack(side=tk.LEFT, padx=(0, 8))
        except Exception:
            ttk.Label(header, text="记账本", font=(None, 14, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(header, text="个人记账本", font=(None, 14, "bold")).pack(side=tk.LEFT)

        main_pane = ttk.Frame(self.root, padding=(10, 6))
        main_pane.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_pane)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(main_pane, width=280)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(toolbar, text="日期:").pack(side=tk.LEFT, padx=(4, 2))
        self.var_date = tk.StringVar(value=datetime.date.today().isoformat())
        if DateEntry is not None:
            self.date_entry = DateEntry(toolbar, textvariable=self.var_date, date_pattern='yyyy-mm-dd', width=12)
            self.date_entry.pack(side=tk.LEFT)
        else:
            ttk.Entry(toolbar, textvariable=self.var_date, width=12).pack(side=tk.LEFT)

        ttk.Label(toolbar, text="类型:").pack(side=tk.LEFT, padx=(8, 2))
        self.var_type = tk.StringVar(value="支出")
        ttk.Combobox(toolbar, textvariable=self.var_type, values=["支出", "收入"], width=8, state="readonly").pack(side=tk.LEFT)

        ttk.Label(toolbar, text="类别:").pack(side=tk.LEFT, padx=(8, 2))
        self.var_category = tk.StringVar(value="其他")
        ttk.Entry(toolbar, textvariable=self.var_category, width=12).pack(side=tk.LEFT)

        ttk.Label(toolbar, text="金额:").pack(side=tk.LEFT, padx=(8, 2))
        self.var_amount = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.var_amount, width=10).pack(side=tk.LEFT)

        # load optional icons
        self._icons['add'] = _load_icon_photo('icon_add')
        self._icons['edit'] = _load_icon_photo('icon_edit')
        self._icons['delete'] = _load_icon_photo('icon_delete')

        # use image+text if icon available, otherwise text-only button
        if self._icons.get('add'):
            ttk.Button(toolbar, text="添加", image=self._icons['add'], compound='left', command=self.on_add).pack(side=tk.LEFT, padx=6)
        else:
            ttk.Button(toolbar, text="添加", command=self.on_add).pack(side=tk.LEFT, padx=6)
        if self._icons.get('edit'):
            ttk.Button(toolbar, text="编辑", image=self._icons['edit'], compound='left', command=self.on_edit).pack(side=tk.LEFT, padx=6)
        else:
            ttk.Button(toolbar, text="编辑", command=self.on_edit).pack(side=tk.LEFT, padx=6)
        if self._icons.get('delete'):
            ttk.Button(toolbar, text="删除", image=self._icons['delete'], compound='left', command=self.on_delete).pack(side=tk.LEFT, padx=6)
        else:
            ttk.Button(toolbar, text="删除", command=self.on_delete).pack(side=tk.LEFT, padx=6)

        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(filter_frame, text="搜索:").pack(side=tk.LEFT, padx=(2, 4))
        self.var_search = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.var_search, width=24)
        search_entry.pack(side=tk.LEFT)
        # optional search icon
        self._icons['search'] = _load_icon_photo('icon_search')
        if self._icons.get('search'):
            ttk.Button(filter_frame, text="应用", image=self._icons['search'], compound='left', command=self.on_search).pack(side=tk.LEFT, padx=6)
        else:
            ttk.Button(filter_frame, text="应用", command=self.on_search).pack(side=tk.LEFT, padx=6)
        ttk.Button(filter_frame, text="重置", command=self.on_reset_search).pack(side=tk.LEFT)

        table_frame = ttk.Frame(left_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("date", "type", "category", "amount", "note")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {"date": "日期", "type": "类型", "category": "类别", "amount": "金额", "note": "备注"}
        for col in columns:
            self.tree.heading(col, text=headings[col])
        self.tree.column("note", width=220)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        try:
            self.tree.tag_configure("oddrow", background="#f9f9f9")
            self.tree.tag_configure("evenrow", background="#ffffff")
        except Exception:
            pass

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="编辑", command=self.on_edit)
        self.context_menu.add_command(label="删除", command=self.on_delete)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.on_edit())

        summary_frame = ttk.LabelFrame(right_frame, text="汇总")
        summary_frame.pack(fill=tk.X, pady=(0, 6), padx=6)

        self.lbl_total_count = ttk.Label(summary_frame, text="记录数: 0", font=(None, 12))
        self.lbl_total_count.pack(anchor=tk.W, padx=8, pady=4)
        self.lbl_income = ttk.Label(summary_frame, text="收入总计: 0.00", foreground="green")
        self.lbl_income.pack(anchor=tk.W, padx=8, pady=2)
        self.lbl_expense = ttk.Label(summary_frame, text="支出总计: 0.00", foreground="red")
        self.lbl_expense.pack(anchor=tk.W, padx=8, pady=2)
        self.lbl_net = ttk.Label(summary_frame, text="净额: 0.00", font=(None, 11, "bold"))
        self.lbl_net.pack(anchor=tk.W, padx=8, pady=6)

        charts_frame = ttk.LabelFrame(right_frame, text="图表")
        charts_frame.pack(fill=tk.X, pady=(6, 6), padx=6)
        # chart icons
        self._icons['chart'] = _load_icon_photo('icon_chart')
        if self._icons.get('chart'):
            ttk.Button(charts_frame, text="月度柱状图", image=self._icons['chart'], compound='left', command=self.on_show_monthly).pack(fill=tk.X, padx=8, pady=4)
            ttk.Button(charts_frame, text="类别饼图", image=self._icons['chart'], compound='left', command=self.on_show_category).pack(fill=tk.X, padx=8, pady=4)
        else:
            ttk.Button(charts_frame, text="月度柱状图", command=self.on_show_monthly).pack(fill=tk.X, padx=8, pady=4)
            ttk.Button(charts_frame, text="类别饼图", command=self.on_show_category).pack(fill=tk.X, padx=8, pady=4)

        export_frame = ttk.LabelFrame(right_frame, text="导出")
        export_frame.pack(fill=tk.X, pady=(6, 6), padx=6)
        self._icons['export'] = _load_icon_photo('icon_export')
        if self._icons.get('export'):
            ttk.Button(export_frame, text="导出 CSV", image=self._icons['export'], compound='left', command=self.on_export_csv).pack(fill=tk.X, padx=8, pady=4)
            ttk.Button(export_frame, text="导出 Excel", image=self._icons['export'], compound='left', command=self.on_export_excel).pack(fill=tk.X, padx=8, pady=4)
        else:
            ttk.Button(export_frame, text="导出 CSV", command=self.on_export_csv).pack(fill=tk.X, padx=8, pady=4)
            ttk.Button(export_frame, text="导出 Excel", command=self.on_export_excel).pack(fill=tk.X, padx=8, pady=4)

        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.refresh_table()
        self.update_summary()

    # actions (same as before)
    def on_add(self):
        try:
            date_str = self.var_date.get().strip()
            if not date_str:
                messagebox.showwarning("输入错误", "请填写日期（YYYY-MM-DD）。")
                return
            datetime.date.fromisoformat(date_str)
            amount = float(self.var_amount.get().strip())
            rec_id = self.data_manager.add_record(date_str, self.var_type.get(), self.var_category.get(), amount, "")
            self.status_var.set("已添加记录")
            self.refresh_table()
            self.update_summary()
            self.var_amount.set("")
        except ValueError as ve:
            messagebox.showwarning("输入错误", f"无效输入：{ve}")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("添加失败", str(e))

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
            messagebox.showerror("错误", "未找到所选记录。")
            return
        EditRecordDialog(self.root, self.data_manager, record_id, row, on_saved=self._on_edit_saved)

    def _on_edit_saved(self):
        self.refresh_table()
        self.update_summary()

    def on_delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("删除", "请先选中一行。")
            return
        record_id = sel[0]
        if not messagebox.askyesno("确认删除", "确定删除所选记录？"):
            return
        try:
            self.data_manager.delete_record(record_id)
            self.status_var.set("已删除记录")
            self.refresh_table()
            self.update_summary()
        except Exception as e:
            messagebox.showerror("删除失败", str(e))

    def on_search(self):
        keyword = self.var_search.get().strip()
        self.refresh_table(filter_keyword=keyword)

    def on_reset_search(self):
        self.var_search.set("")
        self.refresh_table()

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

    def on_export_csv(self):
        try:
            path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
            if not path:
                return
            self.data_manager.export_csv(path)
            messagebox.showinfo("导出成功", f"已导出到 {path}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def on_export_excel(self):
        try:
            path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel', '*.xlsx')])
            if not path:
                return
            self.data_manager.export_excel(path)
            messagebox.showinfo("导出成功", f"已导出到 {path}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def refresh_table(self, filter_keyword: str = None):
        for r in self.tree.get_children():
            self.tree.delete(r)
        df = self.data_manager.get_all_records().copy()
        if filter_keyword:
            mask = (
                df["date"].astype(str).str.contains(filter_keyword, na=False)
                | df["category"].astype(str).str.contains(filter_keyword, na=False)
                | df["note"].astype(str).str.contains(filter_keyword, na=False)
            )
            df = df[mask]
        try:
            df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.sort_values(by="date_parsed", ascending=False).drop(columns="date_parsed")
        except Exception:
            pass
        for i, (_, row) in enumerate(df.iterrows()):
            iid = row["id"]
            display_amount = f"{float(row['amount']):.2f}"
            tag = "evenrow" if (i % 2 == 0) else "oddrow"
            self.tree.insert("", tk.END, iid=iid, values=(row["date"], row["type"], row["category"], display_amount, row["note"]), tags=(tag,))

    def update_summary(self):
        try:
            total = len(self.data_manager.get_all_records())
            income, expense = self.data_manager.get_summary()
            net = income - expense
            self.lbl_total_count.config(text=f"记录数: {total}")
            self.lbl_income.config(text=f"收入总计: {income:.2f}")
            self.lbl_expense.config(text=f"支出总计: {expense:.2f}")
            self.lbl_net.config(text=f"净额: {net:.2f}")
        except Exception:
            pass

    def _show_context_menu(self, event):
        try:
            iid = self.tree.identify_row(event.y)
            if iid:
                self.tree.selection_set(iid)
                self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()


class EditRecordDialog:
    def __init__(self, master, data_manager: DataManager, record_id: str, row, on_saved=None):
        self.data_manager = data_manager
        self.record_id = record_id
        self.on_saved = on_saved
        self.win = tk.Toplevel(master)
        self.win.title("编辑记录")
        self.win.transient(master)
        self.win.grab_set()

        self.var_date = tk.StringVar(value=row["date"])
        self.var_type = tk.StringVar(value=row["type"])
        self.var_category = tk.StringVar(value=row["category"])
        self.var_amount = tk.StringVar(value=str(row["amount"]))
        self.var_note = tk.StringVar(value=row["note"])

        frm = ttk.Frame(self.win, padding=8)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="日期(YYYY-MM-DD)：").grid(row=0, column=0, sticky=tk.W, padx=6, pady=6)
        if DateEntry is not None:
            DateEntry(frm, textvariable=self.var_date, date_pattern='yyyy-mm-dd').grid(row=0, column=1, padx=6, pady=6)
        else:
            ttk.Entry(frm, textvariable=self.var_date).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(frm, text="类型：").grid(row=1, column=0, sticky=tk.W, padx=6)
        ttk.Combobox(frm, textvariable=self.var_type, values=["支出", "收入"], state="readonly").grid(row=1, column=1, padx=6, pady=6)

        ttk.Label(frm, text="类别：").grid(row=2, column=0, sticky=tk.W, padx=6)
        ttk.Entry(frm, textvariable=self.var_category).grid(row=2, column=1, padx=6, pady=6)

        ttk.Label(frm, text="金额：").grid(row=3, column=0, sticky=tk.W, padx=6)
        ttk.Entry(frm, textvariable=self.var_amount).grid(row=3, column=1, padx=6, pady=6)

        ttk.Label(frm, text="备注：").grid(row=4, column=0, sticky=tk.W, padx=6)
        ttk.Entry(frm, textvariable=self.var_note, width=40).grid(row=4, column=1, padx=6, pady=6)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(8, 0))
        ttk.Button(btn_frame, text="保存", command=self.on_save).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="取消", command=self.win.destroy).pack(side=tk.LEFT)

    def on_save(self):
        try:
            datetime.date.fromisoformat(self.var_date.get().strip())
            amount = float(self.var_amount.get().strip())
            new_values = {
                "date": self.var_date.get().strip(),
                "type": self.var_type.get(),
                "category": self.var_category.get().strip() or "其他",
                "amount": amount,
                "note": self.var_note.get().strip(),
            }
            self.data_manager.update_record(self.record_id, new_values)
            if callable(self.on_saved):
                self.on_saved()
            self.win.destroy()
        except Exception as e:
            messagebox.showerror("保存失败", str(e))


# entry point used by __main__.py

def run_app():
    root = tk.Tk()
    dm = DataManager()
    root.geometry("980x640")
    app = ExpenseTrackerUI(root, dm)
    root.mainloop()
