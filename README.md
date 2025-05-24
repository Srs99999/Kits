# Kits Inventory Dashboard

Flask-based CRUD dashboard for managing Aadhaar kit assets, with:

- Inline Add / Edit / Bulk-Delete
- Excel export
- Printable **Handover** & **Kit Form** sheets
- SQLite backend via SQLAlchemy

## Quick-start (local)

```bash
# 1  Clone + create venv
git clone https://github.com/<your-org>/kits-inventory.git
cd kits-inventory
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate

# 2  Install deps
pip install -r requirements.txt

# 3  Run
python app.py
# → http://127.0.0.1:5000
