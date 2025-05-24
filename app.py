# app.py  ─────────────────────────────────────────────── Kits Inventory

import os
from io import BytesIO

import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy

# ────────────────────────────── persistent DB path
BASE_DIR  = os.path.abspath(os.path.dirname(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "data")          # lives on the Render disk
os.makedirs(DATA_DIR, exist_ok=True)                # make sure it exists

DEFAULT_SQLITE = os.path.join(DATA_DIR, "kits_inventory.db")
DB_URI = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE}")

# ────────────────────────────── Flask ⭑ SQLAlchemy
app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI          = DB_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS   = False,
)
db = SQLAlchemy(app)

# ────────────────────────────── Model
class KitsInventory(db.Model):
    __tablename__ = "kits_inventory"

    s_no              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kit_no            = db.Column(db.String(100), unique=True, nullable=False)
    station_id        = db.Column(db.String(100))
    laptop_sn         = db.Column(db.String(100))
    machine_id        = db.Column(db.String(100))
    printer           = db.Column(db.String(100))
    fingerprint       = db.Column(db.String(100))
    iris              = db.Column(db.String(100))
    camera            = db.Column(db.String(100))
    usb_hub           = db.Column(db.String(100))
    spike             = db.Column(db.String(100))
    gps_device        = db.Column(db.String(100))
    white_background  = db.Column(db.String(100))
    lamp_bulb         = db.Column(db.String(100))
    operator_name     = db.Column(db.String(100))
    user_code         = db.Column(db.String(100))
    aadhaar_number    = db.Column(db.String(100))
    mobile_number     = db.Column(db.String(100))
    cheque            = db.Column(db.String(100))
    nseit_certificate = db.Column(db.String(100))
    pvc               = db.Column(db.String(100))
    aadhaar           = db.Column(db.String(100))
    pan               = db.Column(db.String(100))
    declaration       = db.Column(db.String(100))
    education_certificate = db.Column(db.String(100))
    agreements        = db.Column(db.String(100))
    district          = db.Column(db.String(100))
    appointment_date  = db.Column(db.String(100))
    zonal_coordinator = db.Column(db.String(100))

# ────────────────────────────── helpers
def kit_to_dict(kit: KitsInventory) -> dict:
    return {c.name: getattr(kit, c.name) for c in KitsInventory.__table__.columns}

def update_from_dict(kit: KitsInventory, data: dict):
    for c in KitsInventory.__table__.columns:
        if c.name == "s_no":
            continue
        if c.name in data:
            setattr(kit, c.name, data[c.name])

# ────────────────────────────── API
@app.route("/api/kits_inventory")
def api_get():
    rows = KitsInventory.query.order_by(KitsInventory.s_no).all()
    return jsonify({
        "status":  "success",
        "columns": [c.name for c in KitsInventory.__table__.columns],
        "data":    [kit_to_dict(r) for r in rows],
    })

@app.route("/api/kits", methods=["POST"])
def api_create():
    data = request.get_json() or {}
    if not data.get("kit_no"):
        return jsonify({"status":"error","message":"kit_no required"}), 400
    if KitsInventory.query.filter_by(kit_no=data["kit_no"]).first():
        return jsonify({"status":"error","message":"kit_no already exists"}), 400

    kit = KitsInventory(kit_no=data["kit_no"])
    update_from_dict(kit, data)
    db.session.add(kit); db.session.commit()
    return jsonify({"status":"success","data":kit_to_dict(kit)}), 201

@app.route("/api/kits/<kit_no>", methods=["PUT"])
def api_update(kit_no):
    kit = KitsInventory.query.filter_by(kit_no=kit_no).first()
    if kit is None:
        return jsonify({"status":"error","message":"Kit not found"}), 404
    update_from_dict(kit, request.get_json() or {})
    db.session.commit()
    return jsonify({"status":"success","data":kit_to_dict(kit)})

@app.route("/api/kits/bulk-delete", methods=["POST"])
def api_bulk_delete():
    kit_nos = (request.get_json() or {}).get("kitNos", [])
    if not kit_nos:
        return jsonify({"status":"error","message":"No kit numbers supplied"}), 400
    deleted = KitsInventory.query.filter(KitsInventory.kit_no.in_(kit_nos))\
                                 .delete(synchronize_session=False)
    db.session.commit()
    return jsonify({"status":"success","message":f"{deleted} kits deleted"})

# ────────────────────────────── Excel export
@app.route("/export/excel")
def export_excel():
    rows = KitsInventory.query.order_by(KitsInventory.s_no).all()
    df   = pd.DataFrame([kit_to_dict(r) for r in rows])

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Kits Inventory")
    buf.seek(0)

    return send_file(
        buf,
        as_attachment=True,
        download_name="kits_inventory.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# ────────────────────────────── KIT FORM
@app.route("/kit-form/<kit_no>")
def kit_form(kit_no):
    kit = KitsInventory.query.filter_by(kit_no=kit_no).first_or_404()
    items = [
        ("Acer Laptop A315-41",           kit.laptop_sn),
        ("EPSON Printer L3110",           kit.printer or "NO"),
        ("Fingerprint Scanner",           kit.fingerprint),
        ("Iris Scanner",                  kit.iris),
        ("Logitech B525 Web Cam",         kit.camera),
        ("TARGUS USB 2.0 Hub",            kit.usb_hub),
        ("GPS Receiver TATVIK GNSS 100",  kit.gps_device),
        ("Spike Protector",               "Received"),
        ("Focus Lamp",                    "Received"),
        ("Acer Laptop Bag",               "Received"),
        ("Aadhaar Kit Bag",               "Received"),
    ]
    return render_template("kit_form.html", kit=kit, items=items)

# ────────────────────────────── HANDOVER
@app.route("/handover/<kit_no>")
def handover(kit_no):
    kit = KitsInventory.query.filter_by(kit_no=kit_no).first_or_404()
    return render_template(
        "kit_handover.html",
        kit    = kit,
        fields = kit_to_dict(kit)
    )

# ────────────────────────────── Front-end landing
@app.route("/")
def index():
    return render_template("kits_inventory.html")

# ────────────────────────────── bootstrap
if __name__ == "__main__":
    with app.app_context():
        db.create_all()                  # creates the table the first time
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
