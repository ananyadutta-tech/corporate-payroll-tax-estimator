"""Corporate Payroll Tax Estimator — Version 2 (Tkinter GUI).

Educational illustration: India new income-tax regime, financial year 2026-27.
Assumes an Indian resident salaried individual with only ordinary salary income.
Does NOT calculate PF, professional tax, employer benefits, other income,
actual payroll TDS, tax rounding or special-rate income. Not a substitute
for validated payroll/tax software.

Run: python corporate_payroll_tax_estimator_v2.py
Only Python's standard library is required.
"""

import math
import tkinter as tk
from tkinter import messagebox, ttk

# Theme colours
NAVY = "#142841"
BLUE = "#1967D2"
BACKGROUND = "#F2F5FA"
WHITE = "#FFFFFF"
TEXT = "#23354A"
MUTED = "#60748B"
GREEN = "#167A5A"
BORDER = "#DBE4EE"

# Educational scope: above this gross salary, surcharge rules may apply.
MAX_GROSS_SALARY = 5_075_000
STANDARD_DEDUCTION = 75_000

# All seven slabs under the new regime.
# Each tuple: (lower limit, upper limit, rate, readable label).
SLABS = [
    (0, 400_000, 0.00, "Up to ₹4,00,000"),
    (400_000, 800_000, 0.05, "₹4L – ₹8L"),
    (800_000, 1_200_000, 0.10, "₹8L – ₹12L"),
    (1_200_000, 1_600_000, 0.15, "₹12L – ₹16L"),
    (1_600_000, 2_000_000, 0.20, "₹16L – ₹20L"),
    (2_000_000, 2_400_000, 0.25, "₹20L – ₹24L"),
    (2_400_000, None, 0.30, "Above ₹24L"),
]


def rupees(amount):
    """Display a number as a currency amount."""
    return f"₹{amount:,.2f}"


def calculate_tax(gross_salary):
    """Return an educational tax calculation for one annual gross salary."""
    deduction = min(gross_salary, STANDARD_DEDUCTION)
    taxable = gross_salary - deduction

    # These if / elif statements are the MAIN part of your assignment.
    if taxable <= 400_000:
        slab_tax = 0
    elif taxable <= 800_000:
        slab_tax = (taxable - 400_000) * 0.05
    elif taxable <= 1_200_000:
        slab_tax = 20_000 + (taxable - 800_000) * 0.10
    elif taxable <= 1_600_000:
        slab_tax = 60_000 + (taxable - 1_200_000) * 0.15
    elif taxable <= 2_000_000:
        slab_tax = 120_000 + (taxable - 1_600_000) * 0.20
    elif taxable <= 2_400_000:
        slab_tax = 200_000 + (taxable - 2_000_000) * 0.25
    else:
        slab_tax = 300_000 + (taxable - 2_400_000) * 0.30

    # Section 87A: rebate for eligible resident individuals, plus marginal relief.
    if taxable <= 1_200_000:
        relief = min(slab_tax, 60_000)
    elif slab_tax > taxable - 1_200_000:
        relief = slab_tax - (taxable - 1_200_000)
    else:
        relief = 0

    tax_after_relief = slab_tax - relief
    cess = tax_after_relief * 0.04
    total_tax = tax_after_relief + cess

    return {
        "gross": gross_salary,
        "deduction": deduction,
        "taxable": taxable,
        "slab_tax": slab_tax,
        "relief": relief,
        "cess": cess,
        "total_tax": total_tax,
        "net_annual": gross_salary - total_tax,
        "net_monthly": (gross_salary - total_tax) / 12,
    }


def tax_breakdown(taxable):
    """Produce each slab's taxable part and tax for the breakdown table."""
    rows = []
    for lower, upper, rate, label in SLABS:
        applicable_upper = taxable if upper is None else min(taxable, upper)
        amount_in_band = max(0, applicable_upper - lower)
        rows.append((label, f"{rate:.0%}", amount_in_band, amount_in_band * rate))
    return rows


def add_field(parent, label, row):
    """Create one labelled input box."""
    tk.Label(parent, text=label, font=("Segoe UI", 10, "bold"),
             bg=WHITE, fg=TEXT).grid(row=row * 2, column=0, sticky="w", pady=(12, 5))
    entry = tk.Entry(parent, font=("Segoe UI", 12), bg=WHITE, fg=TEXT,
                     relief="solid", bd=1, highlightthickness=1,
                     highlightcolor=BLUE, highlightbackground=BORDER)
    entry.grid(row=row * 2 + 1, column=0, sticky="ew", ipady=8)
    return entry


def make_card(parent, label, initial, accent):
    """Create a metric card, such as Annual Tax or Net Monthly Salary."""
    card = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
    card.pack(side="left", fill="both", expand=True, padx=(0, 10))
    tk.Label(card, text=label, bg=WHITE, fg=MUTED,
             font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(13, 4))
    value = tk.StringVar(value=initial)
    tk.Label(card, textvariable=value, bg=WHITE, fg=accent,
             font=("Segoe UI", 21, "bold")).pack(anchor="w", padx=16, pady=(0, 12))
    return value


def calculate_payroll():
    """Read employee fields, validate input and refresh the dashboard."""
    name = name_entry.get().strip()
    employee_id = id_entry.get().strip()
    department = department_entry.get().strip()
    salary_text = salary_entry.get().strip().replace(",", "")

    if not name or not employee_id or not department or not salary_text:
        messagebox.showerror("Missing information", "Please fill in all four fields.")
        return
    try:
        gross = float(salary_text)
    except ValueError:
        messagebox.showerror("Invalid salary", "Salary must be a number, e.g. 1500000.")
        return

    if not math.isfinite(gross) or gross < 0:
        messagebox.showerror("Invalid salary", "Please enter a non-negative, finite salary.")
        return
    if gross > MAX_GROSS_SALARY:
        messagebox.showerror("Outside this demo's range",
                             "This version supports gross salary up to ₹50,75,000 "
                             "to avoid surcharge calculations.")
        return

    figures = calculate_tax(gross)
    annual_tax_var.set(rupees(figures["total_tax"]))
    net_monthly_var.set(rupees(figures["net_monthly"]))
    employee_var.set(f"{name}  •  {employee_id}  •  {department}")

    # Replace old values in the summary.
    for key, var in detail_vars.items():
        var.set(rupees(figures[key]))

    # Replace old rows in the slab table.
    for old_row in slab_table.get_children():
        slab_table.delete(old_row)
    for label, rate, amount, tax in tax_breakdown(figures["taxable"]):
        slab_table.insert("", "end", values=(label, rate, rupees(amount), rupees(tax)))

    status_var.set("Calculation complete. This is an estimate, not a payroll payslip.")


def clear_fields():
    """Clear input fields and reset the output area."""
    for entry in (name_entry, id_entry, department_entry, salary_entry):
        entry.delete(0, tk.END)
    annual_tax_var.set("—")
    net_monthly_var.set("—")
    employee_var.set("No employee selected")
    for var in detail_vars.values():
        var.set("—")
    for old_row in slab_table.get_children():
        slab_table.delete(old_row)
    status_var.set("Enter employee details to calculate a payroll estimate.")
    name_entry.focus_set()


def build_window():
    """Construct the main Tkinter window and all its widgets."""
    global window, name_entry, id_entry, department_entry, salary_entry
    global annual_tax_var, net_monthly_var, employee_var, detail_vars
    global slab_table, status_var

    window = tk.Tk()
    window.title("Corporate Payroll Tax Estimator | HR Dashboard")
    window.geometry("1080x725")
    window.minsize(930, 650)
    window.configure(bg=BACKGROUND)

    # Blue top bar.
    header = tk.Frame(window, bg=NAVY, height=96)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="CORPORATE PAYROLL TAX ESTIMATOR", bg=NAVY, fg=WHITE,
             font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=26, pady=(17, 2))
    tk.Label(header, text="HR Dashboard  •  India new tax regime  •  FY 2026–27",
             bg=NAVY, fg="#CDDFF4", font=("Segoe UI", 10)).pack(anchor="w", padx=27)

    body = tk.Frame(window, bg=BACKGROUND)
    body.pack(fill="both", expand=True, padx=18, pady=15)

    # Left card: employee form.
    left_card = tk.Frame(body, bg=WHITE, width=330, highlightbackground=BORDER,
                         highlightthickness=1)
    left_card.pack(side="left", fill="y", padx=(0, 15))
    left_card.pack_propagate(False)
    tk.Label(left_card, text="Employee details", bg=WHITE, fg=NAVY,
             font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(20, 5))
    tk.Label(left_card, text="Fill in the details below.", bg=WHITE, fg=MUTED,
             font=("Segoe UI", 10)).pack(anchor="w", padx=18)

    form = tk.Frame(left_card, bg=WHITE)
    form.pack(fill="x", padx=18, pady=(7, 20))
    form.columnconfigure(0, weight=1)
    name_entry = add_field(form, "Employee name", 0)
    id_entry = add_field(form, "Employee ID", 1)
    department_entry = add_field(form, "Department", 2)
    salary_entry = add_field(form, "Gross annual salary (₹)", 3)

    tk.Button(form, text="CALCULATE PAYROLL", command=calculate_payroll,
              font=("Segoe UI", 11, "bold"), bg=BLUE, fg=WHITE,
              activebackground="#104CA5", activeforeground=WHITE,
              relief="flat", cursor="hand2", pady=11).grid(
                  row=8, column=0, sticky="ew", pady=(20, 8))
    tk.Button(form, text="CLEAR ALL", command=clear_fields,
              font=("Segoe UI", 11, "bold"), bg="#E8EEF6", fg=NAVY,
              relief="flat", cursor="hand2", pady=10).grid(
                  row=9, column=0, sticky="ew")

    tk.Label(left_card, text="Example: 1500000 = ₹15 lakh/year",
             bg=WHITE, fg=MUTED, font=("Segoe UI", 9)).pack(
                 anchor="w", padx=18, pady=(0, 15))

    # Right area: summary + itemised report.
    right = tk.Frame(body, bg=BACKGROUND)
    right.pack(side="left", fill="both", expand=True)

    employee_var = tk.StringVar(value="No employee selected")
    tk.Label(right, textvariable=employee_var, bg=BACKGROUND, fg=TEXT,
             font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

    metrics = tk.Frame(right, bg=BACKGROUND)
    metrics.pack(fill="x")
    annual_tax_var = make_card(metrics, "Estimated annual income tax", "—", BLUE)
    net_monthly_var = make_card(metrics, "Estimated monthly net pay*", "—", GREEN)

    detail_box = tk.Frame(right, bg=WHITE, highlightbackground=BORDER,
                          highlightthickness=1)
    detail_box.pack(fill="x", pady=(12, 11))
    tk.Label(detail_box, text="Salary summary", bg=WHITE, fg=NAVY,
             font=("Segoe UI", 13, "bold")).grid(
                 row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(10, 6))

    # Label and internal dictionary key for each amount.
    fields = [
        ("Gross annual salary", "gross"),
        ("Standard deduction", "deduction"),
        ("Taxable income", "taxable"),
        ("Tax before rebate", "slab_tax"),
        ("87A rebate / relief", "relief"),
        ("4% health & education cess", "cess"),
        ("Net annual salary*", "net_annual"),
    ]
    detail_vars = {}
    for index, (label, key) in enumerate(fields):
        row = 1 + index // 2
        pair_column = (index % 2) * 2
        detail_vars[key] = tk.StringVar(value="—")
        tk.Label(detail_box, text=label, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9)).grid(
                     row=row * 2, column=pair_column, sticky="w",
                     padx=(14, 8), pady=(7, 0))
        tk.Label(detail_box, textvariable=detail_vars[key], bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).grid(
                     row=row * 2 + 1, column=pair_column, sticky="w",
                     padx=(14, 8), pady=(0, 6))
    detail_box.columnconfigure(0, weight=1)
    detail_box.columnconfigure(2, weight=1)

    table_card = tk.Frame(right, bg=WHITE, highlightbackground=BORDER,
                          highlightthickness=1)
    table_card.pack(fill="both", expand=True)
    tk.Label(table_card, text="Progressive tax-bracket breakdown", bg=WHITE, fg=NAVY,
             font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=14, pady=(10, 8))

    style = ttk.Style(window)
    style.theme_use("clam")
    style.configure("Payroll.Treeview", font=("Segoe UI", 9), rowheight=24,
                    background=WHITE, fieldbackground=WHITE, foreground=TEXT)
    style.configure("Payroll.Treeview.Heading", font=("Segoe UI", 9, "bold"),
                    background="#E8EFF8", foreground=NAVY)
    style.map("Payroll.Treeview", background=[("selected", "#D6E8FF")],
              foreground=[("selected", TEXT)])

    columns = ("band", "rate", "income", "tax")
    slab_table = ttk.Treeview(table_card, columns=columns, show="headings",
                              style="Payroll.Treeview", height=7)
    for name, heading, width, anchor in [
        ("band", "Income band", 135, "w"),
        ("rate", "Rate", 52, "center"),
        ("income", "Income in band", 145, "e"),
        ("tax", "Tax", 120, "e"),
    ]:
        slab_table.heading(name, text=heading)
        slab_table.column(name, width=width, minwidth=50, anchor=anchor, stretch=True)
    slab_table.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    status_var = tk.StringVar(value="Enter employee details to calculate a payroll estimate.")
    tk.Label(window, textvariable=status_var, bg=BACKGROUND, fg=MUTED,
             font=("Segoe UI", 9)).pack(anchor="w", padx=22)
    tk.Label(window,
             text="*Net amounts subtract income tax only, not PF/other payroll deductions. Educational demo, not a payslip.",
             bg=BACKGROUND, fg=MUTED, font=("Segoe UI", 8)).pack(
                 anchor="w", padx=22, pady=(0, 10))

    name_entry.focus_set()
    window.bind("<Return>", lambda event: calculate_payroll())
    window.mainloop()


if __name__ == "__main__":
    build_window()
