from flask import Flask, render_template, request, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///f:/Sai_Python/test_pd/kits_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Kit(db.Model):
    __tablename__ = 'kits'
    id = db.Column(db.Integer, primary_key=True)
    kit_no = db.Column(db.String(100), unique=True, nullable=False)
    station_id = db.Column(db.String(100))
    laptop_sno = db.Column(db.String(100))
    machine_id = db.Column(db.String(100))
    printer = db.Column(db.String(100))
    fingerprint = db.Column(db.String(100))
    iris = db.Column(db.String(100))
    camera = db.Column(db.String(100))
    usb_hub = db.Column(db.String(100))
    spike = db.Column(db.String(100))
    gps_device = db.Column(db.String(100))
    white_background = db.Column(db.String(100))
    lamp_bulb = db.Column(db.String(100))
    operator_name = db.Column(db.String(100))
    user_code = db.Column(db.String(100))
    aadhaar_number = db.Column(db.String(100))
    mobile_number = db.Column(db.String(100))
    cheque = db.Column(db.String(100))
    nseit_certificate = db.Column(db.String(100))
    pvc = db.Column(db.String(100))
    aadhaar = db.Column(db.String(100))
    pan = db.Column(db.String(100))
    declaration = db.Column(db.String(100))
    education_certificate = db.Column(db.String(100))
    agreements = db.Column(db.String(100))
    district = db.Column(db.String(100))
    date = db.Column(db.String(100))
    zonal_coordinator = db.Column(db.String(100))

@app.route('/api/kits', methods=['GET'])
def get_all_kits():
    kits = Kit.query.all()
    data = []
    for kit in kits:
        data.append({
            'kitNo': kit.kit_no,
            'stationId': kit.station_id,
            'laptopSNo': kit.laptop_sno,
            'machineId': kit.machine_id,
            'printer': kit.printer,
            'fingerprint': kit.fingerprint,
            'iris': kit.iris,
            'camera': kit.camera,
            'usbHub': kit.usb_hub,
            'spike': kit.spike,
            'gpsDevice': kit.gps_device,
            'whiteBackground': kit.white_background,
            'lampBulb': kit.lamp_bulb,
            'operatorName': kit.operator_name,
            'userCode': kit.user_code,
            'aadhaarNumber': kit.aadhaar_number,
            'mobileNumber': kit.mobile_number,
            'cheque': kit.cheque,
            'nseitCertificate': kit.nseit_certificate,
            'pvc': kit.pvc,
            'aadhaar': kit.aadhaar,
            'pan': kit.pan,
            'declaration': kit.declaration,
            'educationCertificate': kit.education_certificate,
            'agreements': kit.agreements,
            'district': kit.district,
            'date': kit.date,
            'zonalCoordinator': kit.zonal_coordinator
        })
    return jsonify({'status': 'success', 'data': data})

@app.route('/api/kits', methods=['POST'])
def save_kit():
    data = request.get_json()
    if not data.get('kitNo'):
        return jsonify({'status': 'error', 'message': 'Kit Number is required'}), 400
    if Kit.query.filter_by(kit_no=data['kitNo']).first():
        return jsonify({'status': 'error', 'message': 'Kit Number already exists'}), 400
    kit = Kit(
        kit_no=data['kitNo'],
        station_id=data.get('stationId', ''),
        laptop_sno=data.get('laptopSNo', ''),
        machine_id=data.get('machineId', ''),
        printer=data.get('printer', ''),
        fingerprint=data.get('fingerprint', ''),
        iris=data.get('iris', ''),
        camera=data.get('camera', ''),
        usb_hub=data.get('usbHub', ''),
        spike=data.get('spike', ''),
        gps_device=data.get('gpsDevice', ''),
        white_background=data.get('whiteBackground', ''),
        lamp_bulb=data.get('lampBulb', ''),
        operator_name=data.get('operatorName', ''),
        user_code=data.get('userCode', ''),
        aadhaar_number=data.get('aadhaarNumber', ''),
        mobile_number=data.get('mobileNumber', ''),
        cheque=data.get('cheque', ''),
        nseit_certificate=data.get('nseitCertificate', ''),
        pvc=data.get('pvc', ''),
        aadhaar=data.get('aadhaar', ''),
        pan=data.get('pan', ''),
        declaration=data.get('declaration', ''),
        education_certificate=data.get('educationCertificate', ''),
        agreements=data.get('agreements', ''),
        district=data.get('district', ''),
        date=data.get('date', ''),
        zonal_coordinator=data.get('zonalCoordinator', '')
    )
    db.session.add(kit)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Kit saved successfully'})

@app.route('/', methods=['GET'])
def index():
    kits = Kit.query.all()
    kits_data = []
    for idx, kit in enumerate(kits, start=1):
        kits_data.append({
            'sNo': idx,
            'kitNo': kit.kit_no,
            'stationId': kit.station_id,
            'laptopSNo': kit.laptop_sno,
            'machineId': kit.machine_id,
            'printer': kit.printer,
            'fingerprint': kit.fingerprint,
            'iris': kit.iris,
            'camera': kit.camera,
            'usbHub': kit.usb_hub,
            'spike': kit.spike,
            'gpsDevice': kit.gps_device,
            'whiteBackground': kit.white_background,
            'lampBulb': kit.lamp_bulb,
            'operatorName': kit.operator_name,
            'userCode': kit.user_code,
            'aadhaarNumber': kit.aadhaar_number,
            'mobileNumber': kit.mobile_number,
            'cheque': kit.cheque,
            'nseitCertificate': kit.nseit_certificate,
            'pvc': kit.pvc,
            'aadhaar': kit.aadhaar,
            'pan': kit.pan,
            'declaration': kit.declaration,
            'educationCertificate': kit.education_certificate,
            'agreements': kit.agreements,
            'district': kit.district,
            'date': kit.date,
            'zonalCoordinator': kit.zonal_coordinator
        })
    return render_template('kits_inventory.html', kitsData=kits_data)

@app.route('/api/kits/bulk-delete', methods=['POST'])
def bulk_delete_kits():
    data = request.get_json()
    kit_nos = data.get('kitNos', [])
    if not kit_nos:
        return jsonify({'status': 'error', 'message': 'No kit numbers provided'}), 400
    deleted = 0
    for kit_no in kit_nos:
        kit = Kit.query.filter_by(kit_no=kit_no).first()
        if kit:
            db.session.delete(kit)
            deleted += 1
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'{deleted} kits deleted successfully'})

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/debug/print_kits')
def debug_print_kits():
    kits = Kit.query.all()
    if not kits:
        return "No kits found in the database."
    for kit in kits:
        print(vars(kit))
    return "Kits printed to console."

def migrate_kits_excel_to_db(excel_path):
    df = pd.read_excel(excel_path, engine="openpyxl")
    for _, row in df.iterrows():
        if not Kit.query.filter_by(kit_no=str(row.get('Kit No', '')).strip()).first():
            kit = Kit(
                kit_no=str(row.get('Kit No', '')),
                station_id=str(row.get('Station ID', '')),
                laptop_sno=str(row.get('Laptop S/No', '')),
                machine_id=str(row.get('Machine ID', '')),
                printer=str(row.get('Printer', '')),
                fingerprint=str(row.get('Fingerprint', '')),
                iris=str(row.get('Iris', '')),
                camera=str(row.get('Camera', '')),
                usb_hub=str(row.get('USB Hub', '')),
                spike=str(row.get('Spike', '')),
                gps_device=str(row.get('GPS device', '')),
                white_background=str(row.get('White Background', '')),
                lamp_bulb=str(row.get('Lamp & Bulb', '')),
                operator_name=str(row.get('Operator Name', '')),
                user_code=str(row.get('User Code As Per Credentials', '')),
                aadhaar_number=str(row.get('Aadhaar Number', '')),
                mobile_number=str(row.get('Mobile Number', '')),
                cheque=str(row.get('Cheque', '')),
                nseit_certificate=str(row.get('Nseit Certificate', '')),
                pvc=str(row.get('PVC', '')),
                aadhaar=str(row.get('Aadhaar', '')),
                pan=str(row.get('Pan', '')),
                declaration=str(row.get('Declaration', '')),
                education_certificate=str(row.get('Education Certificate', '')),
                agreements=str(row.get('Agreements', '')),
                district=str(row.get('District', '')),
                date=str(row.get('Date', '')),
                zonal_coordinator=str(row.get('Zonal coordinator', ''))
            )
            db.session.add(kit)
    db.session.commit()
    print("Excel data migrated to kits_inventory.db")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
