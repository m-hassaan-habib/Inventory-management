from flask import Blueprint, render_template, request
from db import get_db
from datetime import date, timedelta

bp = Blueprint("reports", __name__, url_prefix="/reports")

@bp.route("/", methods=["GET"])
def reports():
    vendor_id = request.args.get("vendor_id")
    range_param = request.args.get("range")
    from_date = request.args.get("from")
    to_date = request.args.get("to")

    today = date.today()

    # if no manual dates, apply quick range
    if not from_date or not to_date:
        if range_param == "today":
            from_date = to_date = today.isoformat()
        elif range_param == "7":
            from_date = (today - timedelta(days=7)).isoformat()
            to_date = today.isoformat()
        elif range_param == "15":
            from_date = (today - timedelta(days=15)).isoformat()
            to_date = today.isoformat()
        elif range_param == "30":
            from_date = (today - timedelta(days=30)).isoformat()
            to_date = today.isoformat()
        elif range_param == "month":
            from_date = today.replace(day=1).isoformat()
            to_date = today.isoformat()
        elif range_param == "year":
            from_date = today.replace(month=1, day=1).isoformat()
            to_date = today.isoformat()

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT i.id, i.invoice_number, i.invoice_date, i.status,
               v.id AS vendor_id, v.name AS vendor_name,
               SUM(ii.quantity * ii.unit_price) AS total,
               SUM(ii.quantity) AS total_items
        FROM invoices i
        JOIN vendors v ON i.vendor_id = v.id
        JOIN invoice_items ii ON i.id = ii.invoice_id
        WHERE 1=1
    """
    params = []
    if vendor_id:
        query += " AND v.id=%s"
        params.append(vendor_id)
    if from_date and to_date:
        query += " AND i.invoice_date BETWEEN %s AND %s"
        params.extend([from_date, to_date])
    query += " GROUP BY i.id ORDER BY i.invoice_date DESC"

    cursor.execute(query, params)
    invoices = cursor.fetchall()

    summary = {
        "total_invoices": len(invoices),
        "total_revenue": sum(x["total"] for x in invoices),
        "total_items": sum(x["total_items"] for x in invoices)
    }

    cursor.execute("SELECT id, name FROM vendors ORDER BY name")
    vendors = cursor.fetchall()

    return render_template(
        "reports.html",
        invoices=invoices,
        summary=summary,
        vendors=vendors,
        from_date=from_date,
        to_date=to_date,
        vendor_id=vendor_id,
        range_param=range_param
    )
