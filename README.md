Invoice Management System

A modern web-based **Invoice Management System** built with **Flask**, **MySQL**, **TailwindCSS**, and **Chart.js**.  
The app provides vendors, products, invoices, reporting, and a dashboard with live analytics.

---

## Features

- **Dashboard**  
  - Overview cards (Revenue, Invoices, Vendors, Products)  
  - Animated charts (Revenue trend, Invoice status distribution)  
  - Quick actions via modals  

- **Invoices**  
  - Create, edit, and delete invoices  
  - Add multiple items (products, quantity, price) dynamically  
  - Auto-calculated totals  
  - Edit with pre-filled modal form  

- **Vendors**  
  - Manage vendor details, addresses, and multiple phone numbers  
  - View invoice history and total spend per vendor  

- **Products**  
  - Manage products with type, variants, and default price  
  - Track usage in invoices  

- **Reports**  
  - Quick filters (Today, 7/15/30 days, This Month, This Year)  
  - Vendor/date-based filtering  
  - Summary cards (total revenue, invoices, items sold)  
  - Invoice details table with pagination  

---

## Tech Stack

- **Backend:** Python 3.11+, Flask  
- **Database:** MySQL / MariaDB  
- **Frontend:** TailwindCSS, FontAwesome, Chart.js  
- **Templates:** Jinja2 (Flask templating)  

---

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/your-username/invoiceflow.git
cd invoiceflow
````

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy `.env.example` -> `.env` and set your values:

```ini
FLASK_ENV=development
DATABASE_URL=mysql+mysqlconnector://user:password@localhost/invoiceflow
SECRET_KEY=your-secret-key
```

### 5. Initialize database

```bash
mysql -u root -p < schema.sql
```

### 6. Run the app

```bash
flask run
```
OR

```bash
Python3 app/app.py
```

App will be available at:
 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Database Schema

**Vendors**

* `id`, `name`, `address`, `email`

**Vendor Phones**

* `id`, `vendor_id`, `phone_number`

**Products**

* `id`, `name`, `type`, `variants`, `default_price`

**Invoices**

* `id`, `invoice_number`, `vendor_id`, `invoice_date`, `status`

**Invoice Items**

* `id`, `invoice_id`, `product_id`, `quantity`, `unit_price`

---

## Dashboard

* **Revenue Overview:** Line/Bar chart
* **Invoice Status Distribution:** Pie/Donut chart
* **Recent Invoices:** Quick glance of latest invoices
* **Quick Actions:** Create invoice, vendor, product via modals

---

## Development Notes

* All add/edit actions open in **modals**.
* Edit invoice uses **AJAX fetch (`/invoices/<id>`)** to pre-fill modal


---
