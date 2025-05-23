from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import os
import io
from datetime import datetime
import json

app = Flask(__name__)

# File paths
DATA_FILES = {
    "VIRINCHI": os.path.join(os.path.dirname(__file__), "virinchi.xlsx"),
    "SNR": os.path.join(os.path.dirname(__file__), "snr.xlsx")
}

OVERALL_PENALTY_FILE = os.path.join(os.path.dirname(__file__), "virinchi overall penalty.xlsx")
KITS_DATA_FILE = os.path.join(os.path.dirname(__file__), "kits_data_virinchi.xlsx") #

def load_data(company):
    """Load Excel data for the specified company"""
    file_path = DATA_FILES.get(company.upper())
    if not file_path or not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        df = pd.read_excel(file_path, engine="openpyxl")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()
    df.columns = [str(col).strip() for col in df.columns] #
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    for col in df.select_dtypes(include=['float', 'int']).columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df.fillna('', inplace=True) #
    return df

def filter_data(df, operator_id, operator_name):
    """Filter DataFrame based on operator ID and name"""
    if operator_id:
        operator_id = operator_id.lower()
        df = df[df.astype(str).apply(lambda row: operator_id in " ".join(row).lower(), axis=1)]
    if operator_name:
        operator_name = operator_name.lower()
        df = df[df.astype(str).apply(lambda row: operator_name in " ".join(row).lower(), axis=1)]
    return df

def load_kits_data():
    """Load kits data from Excel file"""
    columns = [
        'S No', 'Kit No', 'Station ID', 'Laptop S/No', 'Machine ID', 'Printer', 
        'Fingerprint', 'Iris', 'Camera', 'USB Hub', 'Spike', 'GPS device', 
        'White Background', 'Lamp & Bulb', 'Operator Name', 
        'User Code As Per Credentials', 'Aadhaar Number', 'Mobile Number', 
        'Cheque', 'Nseit Certificate', 'PVC', 'Aadhaar', 'Pan', 'Declaration', 
        'Education Certificate', 'Agreements', 'District', 'Date', 
        'Zonal coordinator'
    ]
    
    if not os.path.exists(KITS_DATA_FILE):
        df = pd.DataFrame(columns=columns)
        save_kits_data(df)
        return df
        
    try:
        df = pd.read_excel(KITS_DATA_FILE, engine="openpyxl")
        df.columns = [str(col).strip() for col in df.columns]
        
        # Handle numeric and non-numeric columns separately
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in df.columns:
            if col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = df[col].astype(str).fillna('')
                
        # Ensure S No is integer
        if 'S No' in df.columns:
            df['S No'] = pd.to_numeric(df['S No'], errors='coerce').fillna(0).astype(int)
            
        return df
        
    except Exception as e:
        print(f"Error loading kits data: {e}")
        return pd.DataFrame(columns=columns)

def save_kits_data(df):
    """Save kits data to Excel file"""
    try:
        # Ensure S No column is properly ordered
        if not df.empty:
            df = df.copy()  # Create a copy to avoid SettingWithCopyWarning
            if 'S No' in df.columns:
                df = df.sort_values('S No').reset_index(drop=True)
                df['S No'] = range(1, len(df) + 1)
            
            # Convert numeric columns to appropriate types
            numeric_cols = ['S No']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            # Convert string columns to string type
            string_cols = [col for col in df.columns if col not in numeric_cols]
            for col in string_cols:
                df[col] = df[col].astype(str)
        
        df.to_excel(KITS_DATA_FILE, index=False, engine='openpyxl')
        return True
        
    except Exception as e:
        print(f"Error saving kits data: {e}")
        return False

def validate_kit_data(kit_data):
    """Validate kit data before saving"""
    errors = []
    
    if not kit_data.get('kitNo', '').strip(): #
        errors.append("Kit Number is required")
    
    # Validate Aadhaar format if provided
    aadhaar = kit_data.get('aadhaarNumber', '').strip() #
    if aadhaar and not (len(aadhaar) == 14 and aadhaar[4] == '-' and aadhaar[9] == '-'): #
        errors.append("Aadhaar Number format should be XXXX-XXXX-XXXX")
    
    # Validate mobile number if provided
    mobile = kit_data.get('mobileNumber', '').strip() #
    if mobile and (not mobile.isdigit() or len(mobile) != 10): #
        errors.append("Mobile Number should be 10 digits")
    
    return errors

# Main routes
@app.route('/', methods=['GET', 'POST'])
def index():
    """Main index route for operator data"""
    operator_id = request.form.get('operator_id', '').strip()
    operator_name = request.form.get('operator_name', '').strip()
    company = request.form.get('company', 'VIRINCHI')

    data = load_data(company)
    filtered_data = filter_data(data.copy(), operator_id, operator_name)

    numeric_cols = ['be 1', 'be 2', 'be 3', 'de', 'doe 1', 'doe 2', 'total errors', 'actual penalty', 'Final Penalty']
    totals = {}
    for col in numeric_cols:
        if col in filtered_data.columns:
            totals[col] = filtered_data[col].sum()

    return render_template("index.html",
                           tables=filtered_data.to_dict(orient='records'),
                           column_names=filtered_data.columns,
                           totals=totals,
                           operator_id=operator_id,
                           operator_name=operator_name,
                           company=company,
                           companies=list(DATA_FILES.keys()))

@app.route('/export/excel', methods=['GET'])
def export_excel():
    """Export filtered data to Excel"""
    operator_id = request.args.get('operator_id', '').strip()
    operator_name = request.args.get('operator_name', '').strip()
    company = request.args.get('company', 'VIRINCHI')

    data = load_data(company)
    filtered_data = filter_data(data.copy(), operator_id, operator_name)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_data.to_excel(writer, index=False, sheet_name='Filtered Data')
    output.seek(0)
    return send_file(output,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     download_name=f'{company}_Filtered_Operator_Data.xlsx')

@app.route('/overall-penalty', methods=['GET', 'POST'])
def overall_penalty():
    """Overall penalty route"""
    operator_id = request.values.get('operator_id', '').strip().lower()
    operator_name = request.values.get('operator_name', '').strip().lower()

    if not os.path.exists(OVERALL_PENALTY_FILE):
        combined_df = pd.DataFrame()
    else:
        df = pd.read_excel(OVERALL_PENALTY_FILE, engine='openpyxl')
        df.columns = [str(col).strip() for col in df.columns]
        df.dropna(how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)

        if operator_id:
            combined_mask = df['operator id'].astype(str).str.lower().str.contains(operator_id)
            df = df[combined_mask]
        if operator_name:
            combined_mask = df['operator name'].astype(str).str.lower().str.contains(operator_name)
            df = df[combined_mask]

        for col in df.select_dtypes(include=['float', 'int']).columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        combined_df = df.fillna('')

    totals = {}
    for col in combined_df.columns:
        if pd.api.types.is_numeric_dtype(combined_df[col]):
            totals[col] = combined_df[col].sum()
        else:
            totals[col] = 'Total' if col.lower() in ['operator id', 'operator name'] else ''

    tables = combined_df.to_dict(orient='records')
    column_names = combined_df.columns.tolist()

    return render_template("overall_penalty.html",
                           tables=tables,
                           column_names=column_names,
                           totals=totals,
                           operator_id=operator_id,
                           operator_name=operator_name)

# Kits Management Routes
@app.route('/kits', methods=['GET'])
def kits():
    """Main kits inventory page"""
    return render_template("kits_inventory.html") #

# This is the active GET route for /api/kits
@app.route('/api/kits', methods=['GET'])
def get_all_kits():
    try:
        df = load_kits_data()
        kits_data = df.to_dict(orient='records')
        formatted_kits = []
        for i, kit in enumerate(kits_data):
            formatted_kit = {
                'sNo': i + 1,
                'kitNo': str(kit.get('Kit No', '')),
                'stationId': str(kit.get('Station ID', '')),
                'laptopSNo': str(kit.get('Laptop S/No', '')),
                'machineId': str(kit.get('Machine ID', '')),
                'printer': str(kit.get('Printer', '')),
                'fingerprint': str(kit.get('Fingerprint', '')),
                'iris': str(kit.get('Iris', '')),
                'camera': str(kit.get('Camera', '')),
                'usbHub': str(kit.get('USB Hub', '')),
                'spike': str(kit.get('Spike', '')),
                'gpsDevice': str(kit.get('GPS device', '')),
                'whiteBackground': str(kit.get('White Background', '')),
                'lampBulb': str(kit.get('Lamp & Bulb', '')),
                'operatorName': str(kit.get('Operator Name', '')),
                'userCode': str(kit.get('User Code As Per Credentials', '')),
                'aadhaarNumber': str(kit.get('Aadhaar Number', '')),
                'mobileNumber': str(kit.get('Mobile Number', '')),
                'cheque': str(kit.get('Cheque', '')),
                'nseitCertificate': str(kit.get('Nseit Certificate', '')),
                'pvc': str(kit.get('PVC', '')),
                'aadhaar': str(kit.get('Aadhaar', '')),
                'pan': str(kit.get('Pan', '')),
                'declaration': str(kit.get('Declaration', '')),
                'educationCertificate': str(kit.get('Education Certificate', '')),
                'agreements': str(kit.get('Agreements', '')),
                'district': str(kit.get('District', '')),
                'date': str(kit.get('Date', '')),
                'zonalCoordinator': str(kit.get('Zonal coordinator', ''))
            }
            formatted_kits.append(formatted_kit)
        return jsonify({'status': 'success', 'data': formatted_kits})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# This is the active POST route for /api/kits
@app.route('/api/kits', methods=['POST'])
def save_kit():
    try:
        kit_data = request.get_json()
        
        # Validate required fields
        if not kit_data.get('kitNo'):
            return jsonify({'status': 'error', 'message': 'Kit Number is required'}), 400

        df = load_kits_data()
        
        # Debug logging
        print("Received kit data:", kit_data)

        # Check for duplicate kit number (unless updating)
        if not kit_data.get('isUpdate'):
            if not df.empty and kit_data['kitNo'] in df['Kit No'].values:
                return jsonify({'status': 'error', 'message': 'Kit Number already exists'}), 400

        # Handle edit case
        if kit_data.get('isUpdate'):
            original_kit_no = kit_data.get('originalKitNo')
            df = df[df['Kit No'] != original_kit_no]

        # Prepare new row with exact field matching
        new_row = {
            'Kit No': kit_data.get('kitNo', ''),
            'Station ID': kit_data.get('stationId', ''),
            'Laptop S/No': kit_data.get('laptopSNo', ''),
            'Machine ID': kit_data.get('machineId', ''),
            'Printer': kit_data.get('printer', ''),
            'Fingerprint': kit_data.get('fingerprint', ''),  # Changed from fingerPrint
            'Iris': kit_data.get('iris', ''),
            'Camera': kit_data.get('camera', ''),
            'USB Hub': kit_data.get('usbHub', ''),
            'Spike': kit_data.get('spike', ''),
            'GPS device': kit_data.get('gpsDevice', ''),
            'White Background': kit_data.get('whiteBackground', ''),
            'Lamp & Bulb': kit_data.get('lampBulb', ''),
            'Operator Name': kit_data.get('operatorName', ''),
            'User Code As Per Credentials': kit_data.get('userCode', ''),
            'Aadhaar Number': kit_data.get('aadhaarNumber', ''),
            'Mobile Number': kit_data.get('mobileNumber', ''),
            'Cheque': kit_data.get('cheque', ''),
            'Nseit Certificate': kit_data.get('nseitCertificate', ''),
            'PVC': kit_data.get('pvc', ''),
            'Aadhaar': kit_data.get('aadhaar', ''),
            'Pan': kit_data.get('pan', ''),
            'Declaration': kit_data.get('declaration', ''),
            'Education Certificate': kit_data.get('educationCertificate', ''),
            'Agreements': kit_data.get('agreements', ''),
            'District': kit_data.get('district', ''),
            'Date': kit_data.get('date', ''),
            'Zonal coordinator': kit_data.get('zonalCoordinator', '')
        }

        # Add new row and reindex
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df['S No'] = range(1, len(df) + 1)

        # Save to Excel
        if save_kits_data(df):
            return jsonify({
                'status': 'success',
                'message': 'Kit saved successfully',
                'data': new_row
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to save kit'}), 500

    except Exception as e:
        print("Error saving kit:", str(e))  # Debug log
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/kits/<kit_no>', methods=['DELETE'])
def delete_kit(kit_no): #
    """Delete a specific kit"""
    try:
        df = load_kits_data() #
        
        if df.empty or kit_no not in df['Kit No'].values: #
            return jsonify({'status': 'error', 'message': 'Kit not found'}), 404 #
        
        df = df[df['Kit No'] != kit_no] #
        
        if save_kits_data(df): #
            return jsonify({'status': 'success', 'message': 'Kit deleted successfully'}) #
        else:
            return jsonify({'status': 'error', 'message': 'Failed to delete kit'}), 500 #
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 #

@app.route('/api/kits/bulk-delete', methods=['POST'])
def bulk_delete_kits(): #
    """Delete multiple kits"""
    try:
        data = request.get_json() #
        kit_nos = data.get('kitNos', []) #
        
        if not kit_nos: #
            return jsonify({'status': 'error', 'message': 'No kit numbers provided'}), 400 #
        
        df = load_kits_data() #
        
        df = df[~df['Kit No'].isin(kit_nos)] #
        
        if save_kits_data(df): #
            return jsonify({'status': 'success', 'message': f'{len(kit_nos)} kits deleted successfully'}) #
        else:
            return jsonify({'status': 'error', 'message': 'Failed to delete kits'}), 500 #
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 #

@app.route('/api/kits/search', methods=['GET'])
def search_kits(): #
    """Search kits by various criteria"""
    try:
        kit_no = request.args.get('kitNo', '').strip().lower() #
        station_id = request.args.get('stationId', '').strip().lower() #
        operator_name = request.args.get('operatorName', '').strip().lower() #
        
        df = load_kits_data() #
        
        if df.empty: #
            return jsonify({'status': 'success', 'data': []}) #
        
        if kit_no: #
            df = df[df['Kit No'].astype(str).str.lower().str.contains(kit_no, na=False)] #
        
        if station_id: #
            df = df[df['Station ID'].astype(str).str.lower().str.contains(station_id, na=False)] #
        
        if operator_name: #
            df = df[df['Operator Name'].astype(str).str.lower().str.contains(operator_name, na=False)] #
        
        kits_data = df.to_dict(orient='records') #
        formatted_kits = []
        for i, kit in enumerate(kits_data): # Format data similar to get_all_kits for consistency
            formatted_kit = {
                'sNo': i + 1,
                'kitNo': str(kit.get('Kit No', '')),
                'stationId': str(kit.get('Station ID', '')),
                'laptopSNo': str(kit.get('Laptop S/No', '')),
                'machineId': str(kit.get('Machine ID', '')),
                'printer': str(kit.get('Printer', '')),
                'fingerPrint': str(kit.get('Finger Print', '')),
                'iris': str(kit.get('Iris', '')),
                'camera': str(kit.get('Camera', '')),
                'usbHub': str(kit.get('USB Hub', '')),
                'spike': str(kit.get('Spike', '')),
                'gpsDevice': str(kit.get('GPS Device', '')),
                'whiteBackground': str(kit.get('White Background', '')),
                'lampBulb': str(kit.get('Lamp & Bulb', '')),
                'operatorName': str(kit.get('Operator Name', '')),
                'userCode': str(kit.get('User Code', '')),
                'aadhaarNumber': str(kit.get('Aadhaar Number', '')),
                'mobileNumber': str(kit.get('Mobile Number', ''))
            }
            formatted_kits.append(formatted_kit)
        
        return jsonify({'status': 'success', 'data': formatted_kits}) #
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 #

@app.route('/api/kits/export/excel', methods=['GET'])
def export_kits_excel(): #
    """Export kits data to Excel"""
    try:
        df = load_kits_data() #
        
        output = io.BytesIO() #
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer: #
            df.to_excel(writer, index=False, sheet_name='Kits Inventory') #
            
            workbook = writer.book #
            worksheet = writer.sheets['Kits Inventory'] #
            
            header_format = workbook.add_format({ #
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns.values): #
                worksheet.write(0, col_num, value, header_format) #
            
            worksheet.autofit() #
        
        output.seek(0) #
        
        filename = f'kits_inventory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx' #
        
        return send_file( #
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 #

@app.route('/api/kits/backup', methods=['GET'])
def backup_kits_data(): #
    """Create a backup of kits data"""
    try:
        df = load_kits_data() #
        backup_data = {
            'timestamp': datetime.now().isoformat(), #
            'data': df.to_dict(orient='records') #
        }
        
        output = io.BytesIO() #
        output.write(json.dumps(backup_data, indent=2).encode()) #
        output.seek(0) #
        
        filename = f'kits_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json' #
        
        return send_file( #
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 #

@app.route('/api/kits/restore', methods=['POST'])
def restore_kits_data(): #
    """Restore kits data from backup"""
    try:
        if 'file' not in request.files: #
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400 #
        
        file = request.files['file'] #
        if file.filename == '': #
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400 #
        
        backup_content = file.read().decode('utf-8') #
        backup_data = json.loads(backup_content) #
        
        if 'data' not in backup_data: #
            return jsonify({'status': 'error', 'message': 'Invalid backup file format'}), 400 #
        
        df = pd.DataFrame(backup_data['data']) #
        
        if save_kits_data(df): #
            return jsonify({'status': 'success', 'message': 'Data restored successfully'}) #
        else:
            return jsonify({'status': 'error', 'message': 'Failed to restore data'}), 500 #
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 #

# Error handlers
@app.errorhandler(404)
def not_found_error(error): #
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404 #

@app.errorhandler(500)
def internal_error(error): #
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500 #

if __name__ == '__main__':
    template_dir = os.path.join(os.path.dirname(__file__), 'templates') #
    if not os.path.exists(template_dir): #
        os.makedirs(template_dir) #
    
    # Ensure data directory (which is the script's directory for these files) exists
    # This is implicitly handled as files are expected in os.path.dirname(__file__)
    # data_dir = os.path.dirname(__file__)
    # if not os.path.exists(data_dir):
    #     os.makedirs(data_dir) # This usually isn't necessary for __file__ dirname
    
    app.run(debug=True, host='0.0.0.0', port=5000) #