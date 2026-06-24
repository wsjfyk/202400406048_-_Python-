"""
charts module: plotting utilities for the accounting package.
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox


def show_monthly_chart(parent_window, data_frame):
    if data_frame.empty:
        messagebox.showinfo("No data", "No records available for plotting.")
        return
    df = data_frame.copy()
    df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date_parsed"])
    if df.empty:
        messagebox.showinfo("No valid dates", "No parsable dates in data.")
        return
    df["month"] = df["date_parsed"].dt.to_period("M").astype(str)
    df["signed"] = df.apply(lambda r: float(r["amount"]) if r["type"] == "收入" else -float(r["amount"]), axis=1)
    monthly = df.groupby("month")["signed"].sum().sort_index()
    if monthly.empty:
        messagebox.showinfo("No data", "No amounts available for aggregation.")
        return
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["green" if v >= 0 else "red" for v in monthly.values]
    monthly.plot(kind="bar", color=colors, ax=ax)
    ax.set_title("Monthly Net Income (positive=income)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    plt.tight_layout()
    _show_figure_in_tk(parent_window, fig, title="Monthly Chart")


def show_category_pie(parent_window, data_frame):
    if data_frame.empty:
        messagebox.showinfo("No data", "No records available for plotting.")
        return
    df = data_frame.copy()
    df_exp = df[df["type"] == "支出"].copy()
    if df_exp.empty:
        messagebox.showinfo("No expenses", "No expense records for pie chart.")
        return
    df_exp["amount"] = pd.to_numeric(df_exp["amount"], errors="coerce").fillna(0.0)
    group = df_exp.groupby("category")["amount"].sum().sort_values(ascending=False)
    if group.empty:
        messagebox.showinfo("No data", "No expense amounts.")
        return
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(group, labels=group.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Expense Category Ratio")
    plt.tight_layout()
    _show_figure_in_tk(parent_window, fig, title="Category Pie")


def _show_figure_in_tk(parent_window, fig, title="Figure"):
    win = tk.Toplevel(parent_window)
    win.title(title)
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def save_image():
        try:
            path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
            if not path:
                return
            fig.savefig(path)
            messagebox.showinfo("Saved", f"Chart saved to {path}")
        except Exception as e:
            messagebox.showerror("Save failed", f"Saving image failed: {e}")

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill=tk.X, pady=6)
    tk.Button(btn_frame, text="Save Image", command=save_image).pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.RIGHT, padx=8)
