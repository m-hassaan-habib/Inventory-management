from flask import Flask, render_template
from db import close_db
from routes.dashboard import bp as dashboard_bp
from routes.vendors import bp as vendors_bp
from routes.products import bp as products_bp
from routes.invoices import bp as invoices_bp
from routes.reports import bp as reports_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(reports_bp)

    @app.teardown_appcontext
    def teardown(exception):
        close_db()

    # Default route
    @app.route("/")
    def home():
        return render_template("dashboard.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5002)
