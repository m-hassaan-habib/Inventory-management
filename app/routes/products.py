from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db

bp = Blueprint("products", __name__, url_prefix="/products")

@bp.route("/")
def list_products():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.name, p.type, p.variants, p.default_price,
               COUNT(ii.id) AS usage_count
        FROM products p
        LEFT JOIN invoice_items ii ON p.id = ii.product_id
        GROUP BY p.id
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
    cursor.execute("INSERT INTO products (name, type, variants, default_price) VALUES (%s,%s,%s,%s)",
                   (name, type_, variants, price))
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
    cursor.execute("""UPDATE products 
                      SET name=%s, type=%s, variants=%s, default_price=%s 
                      WHERE id=%s""",
                   (name, type_, variants, price, product_id))
    db.commit()
    return redirect(url_for("products.list_products"))
