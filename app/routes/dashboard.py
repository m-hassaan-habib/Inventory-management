from datetime import date

from flask import Blueprint, render_template
from db import get_db

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


def month_start(d: date) -> date:
    return date(d.year, d.month, 1)


def add_months(d: date, delta: int) -> date:
    y = d.year
    m = d.month + delta
    while m > 12:
        m -= 12
        y += 1
    while m < 1:
        m += 12
        y -= 1
    return date(y, m, 1)


@bp.route("/")
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    today = date.today()
    m0_start = month_start(today)
    m1_start = add_months(m0_start, -1)

    cursor.execute("SELECT COUNT(*) AS c FROM invoices")
    total_invoices = int(cursor.fetchone()["c"] or 0)

    cursor.execute("SELECT COUNT(*) AS c FROM vendors")
    total_vendors = int(cursor.fetchone()["c"] or 0)

    cursor.execute("SELECT COUNT(*) AS c FROM products")
    total_products = int(cursor.fetchone()["c"] or 0)

    cursor.execute(
        """
        SELECT COALESCE(SUM(ii.quantity * ii.unit_price), 0) AS total_amount
        FROM invoice_items ii
        """
    )
    total_expenses = float(cursor.fetchone()["total_amount"] or 0)

    cursor.execute(
        """
        SELECT COALESCE(SUM(ii.quantity * ii.unit_price), 0) AS total_amount
        FROM invoices i
        LEFT JOIN invoice_items ii ON ii.invoice_id = i.id
        WHERE i.invoice_date >= %s
        """,
        (m0_start,),
    )
    rev_curr = float(cursor.fetchone()["total_amount"] or 0)

    cursor.execute(
        """
        SELECT COALESCE(SUM(ii.quantity * ii.unit_price), 0) AS total_amount
        FROM invoices i
        LEFT JOIN invoice_items ii ON ii.invoice_id = i.id
        WHERE i.invoice_date >= %s AND i.invoice_date < %s
        """,
        (m1_start, m0_start),
    )
    rev_prev = float(cursor.fetchone()["total_amount"] or 0)

    revenue_mom_pct = None
    if rev_prev > 0:
        revenue_mom_pct = round(((rev_curr - rev_prev) / rev_prev) * 100, 1)

    cursor.execute("SELECT COUNT(*) AS c FROM invoices WHERE invoice_date >= %s", (m0_start,))
    inv_curr = int(cursor.fetchone()["c"] or 0)

    cursor.execute(
        "SELECT COUNT(*) AS c FROM invoices WHERE invoice_date >= %s AND invoice_date < %s",
        (m1_start, m0_start),
    )
    inv_prev = int(cursor.fetchone()["c"] or 0)

    invoices_mom_pct = None
    if inv_prev > 0:
        invoices_mom_pct = round(((inv_curr - inv_prev) / inv_prev) * 100, 1)

    cursor.execute(
        """
        SELECT i.id, i.invoice_number, v.name AS vendor_name,
               COALESCE(SUM(ii.quantity * ii.unit_price), 0) AS total,
               i.status
        FROM invoices i
        JOIN vendors v ON i.vendor_id = v.id
        LEFT JOIN invoice_items ii ON ii.invoice_id = i.id
        GROUP BY i.id
        ORDER BY i.invoice_date DESC
        LIMIT 5
        """
    )
    recent_invoices = cursor.fetchall()
    for r in recent_invoices:
        r["total"] = float(r["total"] or 0)

    cursor.execute(
        """
        SELECT LOWER(COALESCE(status, 'pending')) AS st, COUNT(*) AS c
        FROM invoices
        GROUP BY st
        """
    )
    status_rows = cursor.fetchall()
    status_map = {row["st"]: int(row["c"] or 0) for row in status_rows}
    status_labels = ["Paid", "Pending", "Overdue"]
    status_values = [
        status_map.get("paid", 0),
        status_map.get("pending", 0),
        status_map.get("overdue", 0),
    ]

    start_7m = add_months(m0_start, -6)
    end_next = add_months(m0_start, 1)

    cursor.execute(
        """
        SELECT DATE_FORMAT(i.invoice_date, '%Y-%m') AS ym,
               COALESCE(SUM(ii.quantity * ii.unit_price), 0) AS total
        FROM invoices i
        LEFT JOIN invoice_items ii ON ii.invoice_id = i.id
        WHERE i.invoice_date >= %s AND i.invoice_date < %s
        GROUP BY ym
        ORDER BY ym
        """,
        (start_7m, end_next),
    )
    monthly_rows = cursor.fetchall()
    monthly_map = {row["ym"]: float(row["total"] or 0) for row in monthly_rows}

    revenue_labels = []
    revenue_values = []
    for k in range(7):
        ms = add_months(start_7m, k)
        ym = f"{ms.year:04d}-{ms.month:02d}"
        revenue_labels.append(ms.strftime("%b"))
        revenue_values.append(float(monthly_map.get(ym, 0)))

    return render_template(
        "dashboard.html",
        total_expenses=total_expenses,
        total_invoices=total_invoices,
        total_vendors=total_vendors,
        total_products=total_products,
        recent_invoices=recent_invoices,
        revenue_mom_pct=revenue_mom_pct,
        invoices_mom_pct=invoices_mom_pct,
        revenue_labels=revenue_labels,
        revenue_values=revenue_values,
        status_labels=status_labels,
        status_values=status_values,
    )
