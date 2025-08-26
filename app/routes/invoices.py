from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db

bp = Blueprint("invoices", __name__, url_prefix="/invoices")

@bp.route("/")
def list_invoices():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT i.id, i.invoice_number, i.invoice_date, i.status,
               v.name AS vendor_name,
               SUM(ii.quantity * ii.unit_price) AS total
        FROM invoices i
        JOIN vendors v ON i.vendor_id = v.id
        JOIN invoice_items ii ON i.id = ii.invoice_id
        GROUP BY i.id
        ORDER BY i.invoice_date DESC
    """)
    invoices = cursor.fetchall()
    return render_template("invoices.html", invoices=invoices)

@bp.route("/add", methods=["POST"])
def add_invoice():
    data = request.form
    vendor_id = data.get("vendor_id")
    invoice_date = data.get("invoice_date")
    status = data.get("status")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*)+1 FROM invoices")
    next_id = cursor.fetchone()[0]
    invoice_number = f"INV-{next_id:03d}"

    cursor.execute("INSERT INTO invoices (invoice_number, vendor_id, invoice_date, status) VALUES (%s,%s,%s,%s)",
                   (invoice_number, vendor_id, invoice_date, status))
    invoice_id = cursor.lastrowid

    product_ids = request.form.getlist("product_id")
    quantities = request.form.getlist("quantity")
    prices = request.form.getlist("unit_price")

    for pid, qty, price in zip(product_ids, quantities, prices):
        cursor.execute("INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s)",
                       (invoice_id, pid, qty, price))

    db.commit()
    return redirect(url_for("invoices.list_invoices"))
