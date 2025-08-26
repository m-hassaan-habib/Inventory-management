from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db

bp = Blueprint("invoices", __name__, url_prefix="/invoices")

@bp.route("/")
def list_invoices():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # fetch invoices
    cursor.execute("""
        SELECT i.id, i.invoice_number, i.invoice_date, i.status,
               v.name AS vendor_name, v.id AS vendor_id,
               SUM(ii.quantity * ii.unit_price) AS total
        FROM invoices i
        JOIN vendors v ON i.vendor_id = v.id
        JOIN invoice_items ii ON i.id = ii.invoice_id
        GROUP BY i.id
        ORDER BY i.invoice_date DESC
    """)
    invoices = cursor.fetchall()

    # attach items to each invoice
    for inv in invoices:
        cursor.execute("""
            SELECT p.name AS product_name, ii.product_id, ii.quantity, ii.unit_price
            FROM invoice_items ii
            JOIN products p ON ii.product_id=p.id
            WHERE ii.invoice_id=%s
        """, (inv["id"],))
        inv["items"] = cursor.fetchall()

    # fetch vendors for dropdown
    cursor.execute("SELECT id, name FROM vendors ORDER BY name")
    vendors = cursor.fetchall()

    # fetch products for dropdown (include price)
    cursor.execute("SELECT id, name, default_price FROM products ORDER BY name")
    products = cursor.fetchall()

    return render_template("invoices.html",
                           invoices=invoices,
                           vendors=vendors,
                           products=products)


@bp.route("/add", methods=["POST"])
def add_invoice():
    data = request.form
    vendor_id = data.get("vendor_id")
    invoice_date = data.get("invoice_date")
    status = data.get("status")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT IFNULL(MAX(id), 0) + 1 AS next_id FROM invoices")
    next_id = cursor.fetchone()["next_id"]
    invoice_number = f"INV-{next_id:03d}"

    cursor.execute(
        "INSERT INTO invoices (invoice_number, vendor_id, invoice_date, status) VALUES (%s,%s,%s,%s)",
        (invoice_number, vendor_id, invoice_date, status),
    )
    invoice_id = cursor.lastrowid

    product_ids = request.form.getlist("product_id")
    quantities = request.form.getlist("quantity")
    prices = request.form.getlist("unit_price")

    for pid, qty, price in zip(product_ids, quantities, prices):
        cursor.execute(
            "INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s)",
            (invoice_id, pid, qty, price),
        )

    db.commit()
    return redirect(url_for("invoices.list_invoices"))


@bp.route("/edit/<int:invoice_id>", methods=["POST"])
def edit_invoice(invoice_id):
    data = request.form
    vendor_id = data.get("vendor_id")
    invoice_date = data.get("invoice_date")
    status = data.get("status")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""UPDATE invoices 
                      SET vendor_id=%s, invoice_date=%s, status=%s 
                      WHERE id=%s""",
                   (vendor_id, invoice_date, status, invoice_id))

    # Clear old items
    cursor.execute("DELETE FROM invoice_items WHERE invoice_id=%s", (invoice_id,))

    # Insert new items
    product_ids = request.form.getlist("product_id")
    quantities = request.form.getlist("quantity")
    prices = request.form.getlist("unit_price")

    for pid, qty, price in zip(product_ids, quantities, prices):
        if pid and qty:
            cursor.execute("INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s)",
                           (invoice_id, pid, qty, price))

    db.commit()
    return redirect(url_for("invoices.list_invoices"))


@bp.route("/delete/<int:invoice_id>", methods=["POST"])
def delete_invoice(invoice_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM invoices WHERE id=%s", (invoice_id,))
    db.commit()
    return redirect(url_for("invoices.list_invoices"))


