from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from graph import FRAAnalyzer
import os
import traceback

app = Flask(__name__)

# Enable CORS for frontend requests
CORS(app)

# Connect to MongoDB - optional, only if needed
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    db = client['mydatabase']  # Replace 'mydatabase' with your DB name
    collection = db['mycollection']  # Replace 'mycollection' with your collection name
    # Test connection
    client.admin.command('ping')
    print("MongoDB connected successfully")
except Exception as e:
    print(f"Warning: MongoDB connection failed: {e}")
    print("Backend will run without MongoDB")
    client = None
    db = None
    collection = None


# ==================== FRA ANALYSIS ENDPOINTS ====================

@app.route('/api/fra/analyze', methods=['POST'])
def analyze_fra():
    """
    Analyze FRA CSV files for frequency response analysis.
    
    Expects:
    - form data with file uploads
    - Optional: is_fault_format_1, is_fault_format_2 (boolean indicators)
    
    Returns:
    - JSON with chart_data, statistics, and comparison results
    """
    try:
        # Get uploaded files
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')
        
        if not file1:
            return jsonify({'success': False, 'error': 'file1 is required'}), 400
        
        # Read file contents
        csv_content_1 = file1.read().decode('utf-8')
        file_name_1 = file1.filename or 'File 1'
        
        # Check if fault format indicator is provided
        is_fault_format_1 = request.form.get('is_fault_format_1', 'false').lower() == 'true'
        
        # If only one file, analyze it
        if not file2:
            result = FRAAnalyzer.analyze_single_csv(
                csv_content_1,
                is_fault_format=is_fault_format_1,
                file_name=file_name_1
            )
            return jsonify(result)
        
        # Analyze two files
        csv_content_2 = file2.read().decode('utf-8')
        file_name_2 = file2.filename or 'File 2'
        is_fault_format_2 = request.form.get('is_fault_format_2', 'false').lower() == 'true'
        
        result = FRAAnalyzer.analyze_two_csvs(
            csv_content_1,
            csv_content_2,
            is_fault_format_1=is_fault_format_1,
            is_fault_format_2=is_fault_format_2,
            file_name_1=file_name_1,
            file_name_2=file_name_2
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in /api/fra/analyze: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fra/compare-vectors', methods=['POST'])
def compare_vectors():
    """
    Compare pre-parsed FRA vectors (for advanced use cases).
    
    Expects JSON:
    {
        "freq": [array of frequencies],
        "mag1": [array of magnitudes for file 1],
        "mag2": [array of magnitudes for file 2],
        "file1_name": "Name of File 1",
        "file2_name": "Name of File 2"
    }
    """
    try:
        data = request.get_json()
        
        freq = data.get('freq', [])
        mag1 = data.get('mag1', [])
        mag2 = data.get('mag2', [])
        file1_name = data.get('file1_name', 'File 1')
        file2_name = data.get('file2_name', 'File 2')
        
        if not freq or not mag1 or not mag2:
            return jsonify({'success': False, 'error': 'freq, mag1, and mag2 arrays are required'}), 400
        
        # Calculate difference
        import numpy as np
        mag1_arr = np.array(mag1)
        mag2_arr = np.array(mag2)
        difference = FRAAnalyzer.calculate_difference(
            np.array(freq), mag1_arr, mag2_arr
        )
        
        # Prepare chart data
        chart_data = FRAAnalyzer.prepare_chart_data(
            np.array(freq), mag1_arr, file1_name, mag2_arr, file2_name
        )
        
        # Calculate statistics
        stats_1 = FRAAnalyzer.calculate_statistics(np.array(freq), mag1_arr)
        stats_1['name'] = file1_name
        
        stats_2 = FRAAnalyzer.calculate_statistics(np.array(freq), mag2_arr)
        stats_2['name'] = file2_name
        
        diff_stats = {
            'name': f'Difference ({file2_name} - {file1_name})',
            'min_diff': round(float(np.min(difference)), 2),
            'max_diff': round(float(np.max(difference)), 2),
            'avg_diff': round(float(np.mean(difference)), 2),
            'std_diff': round(float(np.std(difference)), 2),
        }
        
        return jsonify({
            'success': True,
            'chart_data': chart_data,
            'statistics': [stats_1, stats_2, diff_stats],
            'difference': difference.tolist(),
        })
        
    except Exception as e:
        print(f"Error in /api/fra/compare-vectors: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'UrjaLytics FRA Analysis'})


# ==================== EXISTING ENDPOINTS ====================

if __name__ == '__main__':
    print("Starting UrjaLytics FRA Analysis Backend...")
    print("Server running at http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)