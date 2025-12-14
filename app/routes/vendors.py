from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db

bp = Blueprint("vendors", __name__, url_prefix="/vendors")

@bp.route("/")
def list_vendors():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            v.id,
            v.name,
            v.address,
            v.email,
            ph.phones,
            COALESCE(inv.invoice_count, 0) AS invoice_count,
            COALESCE(inv.total_amount, 0) AS total_amount
        FROM vendors v
        LEFT JOIN (
            SELECT vendor_id, GROUP_CONCAT(DISTINCT phone_number) AS phones
            FROM vendor_phones
            GROUP BY vendor_id
        ) ph ON ph.vendor_id = v.id
        LEFT JOIN (
            SELECT
                i.vendor_id,
                COUNT(DISTINCT i.id) AS invoice_count,
                COALESCE(SUM(ii.quantity * ii.unit_price), 0) AS total_amount
            FROM invoices i
            LEFT JOIN invoice_items ii ON ii.invoice_id = i.id
            GROUP BY i.vendor_id
        ) inv ON inv.vendor_id = v.id
        ORDER BY v.name
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
    name = (data.get("name") or "").strip()
    address = (data.get("address") or "").strip()
    email = (data.get("email") or "").strip()

    raw_phones = request.form.getlist("phones")

    cleaned = []
    seen = set()
    for p in raw_phones:
        p = (p or "").strip()
        if not p:
            continue
        if p in seen:
            continue
        seen.add(p)
        cleaned.append(p)

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE vendors SET name=%s, address=%s, email=%s WHERE id=%s",
        (name, address, email, vendor_id),
    )

    cursor.execute("DELETE FROM vendor_phones WHERE vendor_id=%s", (vendor_id,))
    for phone in cleaned:
        cursor.execute(
            "INSERT INTO vendor_phones (vendor_id, phone_number) VALUES (%s,%s)",
            (vendor_id, phone),
        )

    db.commit()
    return redirect(url_for("vendors.list_vendors"))



@bp.route("/delete/<int:vendor_id>", methods=["POST"])
def delete_vendor(vendor_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM vendors WHERE id=%s", (vendor_id,))
    db.commit()
    return redirect(url_for("vendors.list_vendors"))
