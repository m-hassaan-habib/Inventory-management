from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from db import get_db

bp = Blueprint("products", __name__, url_prefix="/products")


@bp.route("/")
def list_products():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            p.id,
            p.name,
            p.type,
            p.variants,
            p.default_price,
            COUNT(DISTINCT ii.invoice_id) AS usage_count
        FROM products p
        LEFT JOIN invoice_items ii ON p.id = ii.product_id
        GROUP BY p.id
        ORDER BY p.name
    """)
    products = cursor.fetchall()
    return render_template("products.html", products=products)



@bp.route("/add", methods=["POST"])
def add_product():
    data = request.form
    name = data.get("name")
    type_ = data.get("type")
    variants = data.get("variants")
    price = data.get("default_price")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO products (name, type, variants, default_price) VALUES (%s,%s,%s,%s)",
        (name, type_, variants, price),
    )
    db.commit()
    return redirect(url_for("products.list_products"))


@bp.route("/edit/<int:product_id>", methods=["POST"])
def edit_product(product_id):
    data = request.form
    name = data.get("name")
    type_ = data.get("type")
    variants = data.get("variants")
    price = data.get("default_price")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """UPDATE products
           SET name=%s, type=%s, variants=%s, default_price=%s
           WHERE id=%s""",
        (name, type_, variants, price, product_id),
    )
    db.commit()
    return redirect(url_for("products.list_products"))


@bp.route("/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    db.commit()
    return redirect(url_for("products.list_products"))


@bp.route("/<int:product_id>/invoices")
def product_invoices(product_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, name, type, variants, default_price FROM products WHERE id=%s",
        (product_id,),
    )
    product = cursor.fetchone()
    if not product:
        return jsonify({"product": None, "invoices": []}), 404

    cursor.execute("""
        SELECT i.id, i.invoice_number,
               DATE_FORMAT(i.invoice_date, '%Y-%m-%d') AS invoice_date,
               i.status,
               v.name AS vendor_name,
               COALESCE(SUM(ii.quantity * ii.unit_price), 0) AS total
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.id
        JOIN vendors v ON i.vendor_id = v.id
        WHERE ii.product_id = %s
        GROUP BY i.id
        ORDER BY i.invoice_date DESC
    """, (product_id,))
    invoices = cursor.fetchall()

    return jsonify({"product": product, "invoices": invoices})
