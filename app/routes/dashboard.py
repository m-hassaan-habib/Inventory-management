from flask import Blueprint, render_template, jsonify
from db import get_db

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@bp.route("/")
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_invoices FROM invoices")
    total_invoices = cursor.fetchone()["total_invoices"]

    cursor.execute("SELECT COUNT(*) AS total_vendors FROM vendors")
    total_vendors = cursor.fetchone()["total_vendors"]

    cursor.execute("SELECT COUNT(*) AS total_products FROM products")
    total_products = cursor.fetchone()["total_products"]

    cursor.execute("""
        SELECT SUM(ii.quantity * ii.unit_price) AS total_revenue
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.id
    """)
    total_revenue = cursor.fetchone()["total_revenue"] or 0

    cursor.execute("""
        SELECT i.invoice_number, v.name AS vendor_name,
               SUM(ii.quantity * ii.unit_price) AS total,
               i.status
        FROM invoices i
        JOIN vendors v ON i.vendor_id = v.id
        JOIN invoice_items ii ON i.id = ii.invoice_id
        GROUP BY i.id
        ORDER BY i.invoice_date DESC
        LIMIT 5
    """)
    recent_invoices = cursor.fetchall()

    return render_template("dashboard.html",
                           total_revenue=total_revenue,
                           total_invoices=total_invoices,
                           total_vendors=total_vendors,
                           total_products=total_products,
                           recent_invoices=recent_invoices)
