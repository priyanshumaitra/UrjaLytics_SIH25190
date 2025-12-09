# FRA Analysis Backend Implementation - Summary

## Overview

Successfully implemented a complete FRA (Frequency Response Analysis) backend system for UrjaLytics that properly handles CSV file parsing, frequency/magnitude data extraction, and comparison visualization.

## Changes Made

### 1. **Backend - New File: `backend/graph.py`**

- **FRAAnalyzer class** with static methods for:

  - `parse_normal_fra_csv()`: Parses standard FRA format (freq, RMS, Peaks, Phase)
  - `parse_fault_fra_csv()`: Parses fault format (semicolon-separated)
  - `normalize_vector_length()`: Aligns vectors to same length
  - `calculate_difference()`: Computes magnitude difference between two files
  - `prepare_chart_data()`: Converts data to Recharts-compatible format
  - `calculate_statistics()`: Generates statistics (min, max, avg, std dev)
  - `analyze_two_csvs()`: Main method for comparing two FRA files
  - `analyze_single_csv()`: Analyzes single FRA file

- **Features**:
  - Handles European decimal formats (commas → dots)
  - Robust error handling with meaningful messages
  - Frequency interpolation when grids don't match
  - Automatic column detection (frequency vs magnitude)

### 2. **Backend - Updated: `backend/main.py`**

- **New API Endpoints**:

  - `POST /api/fra/analyze`: Main endpoint for CSV file analysis
    - Accepts file uploads (up to 2 files)
    - Optional: `is_fault_format_1`, `is_fault_format_2` parameters
    - Returns: chart_data, statistics, difference array
  - `POST /api/fra/compare-vectors`: Advanced endpoint for pre-parsed vectors
  - `GET /api/health`: Health check endpoint

- **Imports**: Added Flask-CORS, graph module, numpy
- **CORS enabled** for frontend requests

### 3. **Backend - Updated: `backend/requirements.txt`**

```
Flask==2.3.3
Flask-CORS==4.0.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
pymongo==4.5.0
```

### 4. **Frontend - Updated: `frontend/src/hooks/useCSVUpload.js`**

- **Removed**: Local CSV parsing logic
- **Added**: API integration with `/api/fra/analyze`
- **New functionality**:

  - `sendToBackend()`: Sends files to backend via FormData
  - Error handling with user-friendly messages
  - Loading state (`isAnalyzing`)
  - Error state (`analysisError`)
  - Statistics tracking from backend response

- **Backwards compatible**: Still supports max 2 files
- **File removal**: Re-analyzes remaining files automatically

### 5. **Frontend - Completely Rewritten: `frontend/src/components/AnalysisTab.jsx`**

- **Removed**: All local parsing and downsampling logic
- **Simplified**: Now purely a visualization component
- **Added**:

  - Error display with AlertCircle icon
  - Loading indicator (`isAnalyzing`)
  - Statistics passed from hook instead of computed locally
  - Proper display of backend-computed statistics:
    - data_points, min_freq, max_freq, min_mag, max_mag, avg_mag, std_mag

- **Kept**: All visualization features (Recharts, export, report generation)

### 6. **Frontend - Updated: `frontend/src/components/Uploads.jsx`**

- Updated hook destructuring to include `statistics`, `isAnalyzing`, `analysisError`
- Removed `zoomRange` (not used in new implementation)
- Pass all new props to AnalysisTab component

## How It Works

### Upload Flow:

1. User uploads 1-2 CSV files via Uploads component
2. `handleCSVUpload()` in hook receives files
3. Files sent to backend `/api/fra/analyze` endpoint
4. Backend parses files and returns:
   - `chart_data`: Points with frequency/magnitude for visualization
   - `statistics`: Computed stats for each file + difference
   - `frequencies`: Frequency array
   - Other metadata (file names, etc.)
5. Frontend stores data in state and displays in AnalysisTab

### CSV Format Support:

- **Normal files**: `freq, RMS, Peaks, Phase` (comma-separated)
- **Fault files**: Semicolon-separated with flexible column names
- **Auto-detection**: Finds first two numeric columns
- **European format**: Handles comma decimals (1,234.5 → 1.2345)

## API Response Example

```json
{
  "success": true,
  "chart_data": [
    {
      "index": 0,
      "frequency": 10.0,
      "magnitude": -50.25,
      "magnitude2": -48.75
    },
    ...
  ],
  "statistics": [
    {
      "name": "File 1",
      "data_points": 150,
      "min_freq": 10.0,
      "max_freq": 10000.0,
      "min_mag": -80.5,
      "max_mag": -20.0,
      "avg_mag": -45.3,
      "std_mag": 15.2
    },
    ...
  ],
  "frequencies": [10.0, 20.0, ...],
  "file1_name": "Normal.csv",
  "file2_name": "Fault.csv"
}
```

## Testing Steps

### 1. **Install Dependencies**:

```bash
cd backend
pip install -r requirements.txt
```

### 2. **Start Flask Server**:

```bash
python main.py
# Server runs on http://localhost:5000
```

### 3. **Test API Directly**:

```bash
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Normal.csv" \
  -F "file2=@Fault.csv"
```

### 4. **Test in Frontend**:

- Ensure backend is running at `http://localhost:5000`
- Navigate to Uploads tab
- Select "Upload CSV Files"
- Upload 1-2 CSV files with freq/magnitude columns
- Click "Analyze" or let it auto-analyze
- View results in Analysis tab with side-by-side comparison

## CSV File Format Requirements

### Minimum Required:

- **Column 1**: Frequency values (numeric)
- **Column 2**: Magnitude values (numeric, typically in dB)
- **Header row**: First row with column names

### Example Normal File:

```
freq,RMS,Peaks,Phase
10,50.2,55.1,45.5
20,48.5,52.3,46.2
30,45.8,49.7,47.1
...
```

### Example Fault File:

```
Frequency;H1 x1 (Magnitude (dB))
10;48.5
20;46.2
30;43.8
...
```

## Benefits of Backend Implementation

✅ **Separation of Concerns**: Logic in backend, visualization in frontend
✅ **Reusability**: Backend API can be used by other clients
✅ **Scalability**: Can add ML models, advanced analysis later
✅ **Robustness**: Centralized error handling
✅ **Consistency**: Single source of truth for data processing
✅ **Security**: File validation on server-side
✅ **Performance**: Backend can optimize parsing for large files

## Future Enhancements

1. **ML Integration**: Add fault detection model using parsed vectors
2. **Caching**: Store analysis results for repeated requests
3. **Batch Processing**: Handle multiple file pairs at once
4. **Advanced Statistics**: Add percentiles, peaks, trends
5. **Export Options**: CSV export of analysis results
6. **Database**: Store historical analysis results
7. **Comparison Reports**: Generate PDF reports with graphs

## File Changes Summary

| File                                      | Change Type   | Purpose                             |
| ----------------------------------------- | ------------- | ----------------------------------- |
| `backend/graph.py`                        | **NEW**       | FRA analysis engine                 |
| `backend/main.py`                         | **MODIFIED**  | Added 2 new API endpoints           |
| `backend/requirements.txt`                | **MODIFIED**  | Added pandas, numpy, Flask-CORS     |
| `frontend/src/hooks/useCSVUpload.js`      | **REWRITTEN** | Backend API integration             |
| `frontend/src/components/AnalysisTab.jsx` | **REWRITTEN** | Removed parsing, added error states |
| `frontend/src/components/Uploads.jsx`     | **MODIFIED**  | Updated hook props                  |

## Notes

- The frontend still supports downsampling through the backend's intelligent data management
- All data transformations happen server-side for consistency
- Error messages are user-friendly and helpful
- The system gracefully handles missing or malformed data
- Statistics include standard deviation for fault detection capabilities
