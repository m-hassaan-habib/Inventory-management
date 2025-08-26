from flask import Blueprint, render_template, request
from db import get_db

bp = Blueprint("reports", __name__, url_prefix="/reports")

@bp.route("/")
def reports():
    vendor_id = request.args.get("vendor_id")
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT i.id, i.invoice_number, i.invoice_date, i.status,
               v.id AS vendor_id, v.name AS vendor_name,
               SUM(ii.quantity * ii.unit_price) AS total,
               SUM(ii.quantity) AS items
        FROM invoices i
        JOIN vendors v ON i.vendor_id = v.id
        JOIN invoice_items ii ON i.id = ii.invoice_id
        WHERE 1=1
    """
    params = []
    if vendor_id:
        query += " AND v.id=%s"
        params.append(vendor_id)
    if date_from and date_to:
        query += " AND i.invoice_date BETWEEN %s AND %s"
        params.extend([date_from, date_to])
    query += " GROUP BY i.id"

    cursor.execute(query, params)
    invoices = cursor.fetchall()

    # summary
    summary = {
        "total_invoices": len(invoices),
        "total_revenue": sum(x["total"] for x in invoices),
        "total_items": sum(x["items"] for x in invoices)
    }

    # fetch vendors for dropdown
    cursor.execute("SELECT id, name FROM vendors ORDER BY name")
    vendors = cursor.fetchall()

    return render_template("reports.html", invoices=invoices, summary=summary, vendors=vendors)
