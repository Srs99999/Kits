# ────────────────────────────────────────────
#   Kits Inventory  –  Flask + SQLite
#   Works locally *and* on Render with a disk
# ────────────────────────────────────────────
import os, pathlib, sqlite3
from io import BytesIO

import pandas as pd
from flask import (
    Flask, render_template, request, jsonify,
    send_file, abort
)
from flask_sqlalchemy import SQLAlchemy

# ───────────── Persistent-disk location ─────────────
# on Render we mount a disk at /data.  Locally we fall
# back to a file alongside this script.
DISK_PATH  = os.environ.get("DB_DIR", "/data")
LOCAL_PATH = pathlib.Path(__file__).with_name("kits_inventory.db")
DB_FILE    = pathlib.Path(DISK_PATH) / "kits_inventory.db" \
             if os.path.isdir(DISK_PATH) else LOCAL_PATH

DB_URI = f"sqlite:///{DB_FILE}"

# ───────────── Flask / SQLAlchemy setup ─────────────
app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI            = DB_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS     = False,
    JSON_SORT_KEYS                     = False,
)
db = SQLAlchemy(app)

# ───────────── Model ─────────────
class KitsInventory(db.Model):
    __tablename__ = "kits_inventory"
    s_no  = db.Column(db.Integer, primary_key=True)

    kit_no            = db.Column(db.String)
    station_id        = db.Column(db.String)
    laptop_sn         = db.Column(db.String)
    machine_id        = db.Column(db.String)
    printer           = db.Column(db.String)
    fingerprint       = db.Column(db.String)
    iris              = db.Column(db.String)
    camera            = db.Column(db.String)
    usb_hub           = db.Column(db.String)
    spike             = db.Column(db.String)
    gps_device        = db.Column(db.String)
    white_background  = db.Column(db.String)
    lamp_bulb         = db.Column(db.String)
    operator_name     = db.Column(db.String)
    user_code         = db.Column(db.String)
    aadhaar_number    = db.Column(db.String)
    mobile_number     = db.Column(db.String)
    cheque            = db.Column(db.String)
    nseit_certificate = db.Column(db.String)
    pvc               = db.Column(db.String)
    aadhaar           = db.Column(db.String)
    pan               = db.Column(db.String)
    declaration       = db.Column(db.String)
    education_certificate = db.Column(db.String)
    agreements        = db.Column(db.String)
    district          = db.Column(db.String)
    appointment_date  = db.Column(db.String)
    zonal_coordinator = db.Column(db.String)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# ───────────── one-time bootstrap:  table + data ─────────────
EXCEL_FILE = pathlib.Path(__file__).with_name("kits_data_virinchi.xlsx")

def bootstrap():
    "Create the DB file / table and import Excel if table is empty"
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)  # /data on first run
    db.create_all()

    # Anything in the table already? if not, seed from Excel
    if not KitsInventory.query.first():
        if not EXCEL_FILE.exists():
            print("Excel sheet not found; skipping import")
            return
        df = pd.read_excel(EXCEL_FILE)
        df.columns = [c.name for c in KitsInventory.__table__.columns]
        df.to_sql("kits_inventory", db.engine, if_exists="append", index=False)
        print(f"Imported {len(df)} rows from {EXCEL_FILE}")

with app.app_context():
    bootstrap()

# ───────────── Helpers ─────────────
def update_from_dict(row, data):
    for col in row.__table__.columns.keys():
        if col != "s_no" and col in data:
            setattr(row, col, data[col])

# ───────────── API routes ─────────────
@app.route("/api/kits_inventory")
def api_get():
    rows = KitsInventory.query.order_by(KitsInventory.s_no).all()
    return jsonify({
        "columns": [c.name for c in KitsInventory.__table__.columns],
        "data"   : [r.to_dict() for r in rows]
    })

@app.route("/api/kits", methods=["POST"])
def api_create():
    data = request.get_json() or {}
    if not data.get("kit_no"):
        abort(400, "kit_no required")
    if KitsInventory.query.filter_by(kit_no=data["kit_no"]).first():
        abort(400, "kit_no already exists")

    row = KitsInventory()
    update_from_dict(row, data)
    db.session.add(row); db.session.commit()
    return jsonify(row.to_dict()), 201

@app.route("/api/kits/<kit_no>", methods=["PUT"])
def api_update(kit_no):
    row = KitsInventory.query.filter_by(kit_no=kit_no).first_or_404()
    update_from_dict(row, request.get_json() or {})
    db.session.commit()
    return jsonify(row.to_dict())

# bulk delete omitted for brevity – add back if you need it

# ───────────── Excel export ─────────────
@app.route("/export/excel")
def export_excel():
    rows = KitsInventory.query.order_by(KitsInventory.s_no).all()
    buf  = BytesIO()
    pd.DataFrame([r.to_dict() for r in rows]).to_excel(buf, index=False)
    buf.seek(0)
    return send_file(buf, as_attachment=True,
                     download_name="kits_inventory.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ───────────── Front end (static html/js) ─────────────
@app.route("/")
def index():
    return render_template("kits_inventory.html")

# ───────────── Local run ─────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
