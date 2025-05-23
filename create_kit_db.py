import sqlite3
import os

# Path for the database
db_path = os.path.join(os.path.dirname(__file__), 'kits_inventory.db')

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table with appropriate column names
cursor.execute('''
CREATE TABLE IF NOT EXISTS kits (
    s_no INTEGER,
    kit_no TEXT,
    station_id TEXT,
    laptop_sn TEXT,
    machine_id TEXT,
    printer TEXT,
    fingerprint TEXT,
    iris TEXT,
    camera TEXT,
    usb_hub TEXT,
    spike TEXT,
    gps_device TEXT,
    white_background TEXT,
    lamp_bulb TEXT,
    operator_name TEXT,
    user_code TEXT,
    aadhaar_number TEXT,
    mobile_number TEXT,
    cheque TEXT,
    nseit_certificate TEXT,
    pvc TEXT,
    aadhaar TEXT,
    pan TEXT,
    declaration TEXT,
    education_certificate TEXT,
    agreements TEXT,
    district TEXT,
    appointment_date TEXT,
    zonal_coordinator TEXT
)
''')

conn.commit()
conn.close()

print(f"Database created at {db_path}")
