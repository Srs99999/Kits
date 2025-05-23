import pandas as pd
import sqlite3
import os

# Define file paths
excel_file = os.path.join(os.path.dirname(__file__), 'kits_data_virinchi.xlsx')
db_path = os.path.join(os.path.dirname(__file__), 'kits_inventory.db')

# Read the Excel file
df = pd.read_excel(excel_file)

# Optional: Rename columns to match your SQLite table schema
df.columns = [
    "s_no", "kit_no", "station_id", "laptop_sn", "machine_id", "printer",
    "fingerprint", "iris", "camera", "usb_hub", "spike", "gps_device",
    "white_background", "lamp_bulb", "operator_name", "user_code",
    "aadhaar_number", "mobile_number", "cheque", "nseit_certificate",
    "pvc", "aadhaar", "pan", "declaration", "education_certificate",
    "agreements", "district", "appointment_date", "zonal_coordinator"
]

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Insert into the 'kits_inventory' table
df.to_sql('kits_inventory', conn, if_exists='append', index=False)

conn.close()

print("Data imported successfully into kits_inventory.db")
# Verify the data import
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM kits_inventory")
count = cursor.fetchone()[0]
conn.close()
print(f"Total records in 'kits_inventory' table: {count}")