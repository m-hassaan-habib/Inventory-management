from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db

bp = Blueprint("vendors", __name__, url_prefix="/vendors")

@bp.route("/")
def list_vendors():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT v.id, v.name, v.address, v.email,
               GROUP_CONCAT(p.phone_number) AS phones,
               COUNT(DISTINCT i.id) AS invoice_count,
               COALESCE(SUM(ii.quantity * ii.unit_price), 0) AS total_amount
        FROM vendors v
        LEFT JOIN vendor_phones p ON v.id = p.vendor_id
        LEFT JOIN invoices i ON v.id = i.vendor_id
        LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
        GROUP BY v.id
    """)
    vendors = cursor.fetchall()
    return render_template("vendors.html", vendors=vendors)

@bp.route("/add", methods=["POST"])
def add_vendor():
    data = request.form
    name = data.get("name")
    address = data.get("address")
    email = data.get("email")
    phones = request.form.getlist("phones")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO vendors (name, address, email) VALUES (%s,%s,%s)",
                   (name, address, email))
    vendor_id = cursor.lastrowid
    for phone in phones:
        cursor.execute("INSERT INTO vendor_phones (vendor_id, phone_number) VALUES (%s, %s)",
                       (vendor_id, phone))
    db.commit()
    return redirect(url_for("vendors.list_vendors"))


@bp.route("/edit/<int:vendor_id>", methods=["POST"])
def edit_vendor(vendor_id):
    data = request.form
    name = data.get("name")
    address = data.get("address")
    email = data.get("email")
    phones = request.form.getlist("phones")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE vendors SET name=%s, address=%s, email=%s WHERE id=%s",
                   (name, address, email, vendor_id))

    cursor.execute("DELETE FROM vendor_phones WHERE vendor_id=%s", (vendor_id,))
    for phone in phones:
        if phone.strip():
            cursor.execute("INSERT INTO vendor_phones (vendor_id, phone_number) VALUES (%s,%s)",
                           (vendor_id, phone))

    db.commit()
    return redirect(url_for("vendors.list_vendors"))
