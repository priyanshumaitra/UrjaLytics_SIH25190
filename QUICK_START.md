# Quick Start Guide - FRA Analysis Backend

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Backend server running
- Frontend React app

## Setup Instructions

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Dependencies installed**:

- Flask 2.3.3 - Web framework
- Flask-CORS 4.0.0 - Enable cross-origin requests
- pandas 2.0.3 - Data processing
- numpy 1.24.3 - Numerical operations
- scikit-learn 1.3.0 - Machine learning (for future enhancements)
- pymongo 4.5.0 - MongoDB connection

### Step 2: Start the Flask Server

```bash
# In backend directory
python main.py
```

Expected output:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 3: Verify Backend is Running

```bash
# In another terminal
curl http://localhost:5000/api/health
```

Expected response:

```json
{ "status": "ok", "service": "UrjaLytics FRA Analysis" }
```

### Step 4: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## Testing the FRA Analysis

### Option A: Via Frontend UI

1. Navigate to http://localhost:5173 (or your frontend URL)
2. Go to "Uploads" tab
3. Click "Upload CSV Files"
4. Select 1-2 CSV files with frequency/magnitude data
5. View analysis in "Analysis" tab

### Option B: Direct API Testing

```bash
# With curl
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@path/to/Normal.csv" \
  -F "file2=@path/to/Fault.csv"

# With Python requests
python
>>> import requests
>>> files = {'file1': open('Normal.csv'), 'file2': open('Fault.csv')}
>>> r = requests.post('http://localhost:5000/api/fra/analyze', files=files)
>>> r.json()
```

## Expected CSV File Format

### Standard FRA Format:

```csv
freq,RMS,Peaks,Phase
10.0,50.2,55.1,45.5
20.0,48.5,52.3,46.2
30.0,45.8,49.7,47.1
```

### Fault/European Format:

```csv
Frequency;H1 x1 (Magnitude (dB));Phase;Other
10;48.5;45.5;0
20;46.2;46.2;0
30;43.8;47.1;0
```

## API Endpoints

### 1. POST /api/fra/analyze

Analyze 1-2 CSV files

- **Parameters**:
  - `file1` (required): First CSV file
  - `file2` (optional): Second CSV file
  - `is_fault_format_1` (optional): Boolean for fault format
  - `is_fault_format_2` (optional): Boolean for fault format
- **Returns**: chart_data, statistics, frequencies

### 2. GET /api/health

Health check

- **Returns**: status and service name

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 5000
# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On Mac/Linux:
lsof -i :5000
kill -9 <PID>
```

### Module Not Found

```bash
# Ensure you're in backend directory
pip install -r requirements.txt

# Or install individually
pip install Flask Flask-CORS pandas numpy
```

### CORS Errors

- Ensure Flask-CORS is installed
- Backend is running at http://localhost:5000
- Frontend makes requests to correct URL

### CSV Parsing Errors

- Check CSV format (first row is header)
- Ensure at least 2 numeric columns
- Check for encoding issues (use UTF-8)
- Commas in numbers should be cleaned (1.234 not 1,234)

## File Structure

```
backend/
├── main.py           # Flask server with API endpoints
├── graph.py          # FRA analysis engine (NEW)
├── requirements.txt  # Python dependencies
└── test.py          # Testing file

frontend/
├── src/
│   ├── components/
│   │   ├── AnalysisTab.jsx          # Chart visualization (UPDATED)
│   │   ├── Uploads.jsx              # Main upload component (UPDATED)
│   │   └── ...
│   ├── hooks/
│   │   └── useCSVUpload.js          # API integration (REWRITTEN)
│   └── ...
└── ...
```

## Example Analysis Session

### Step 1: Upload Files

```
User uploads: Normal.csv and Fault.csv
```

### Step 2: Backend Processing

```
1. Receives files
2. Parses frequency/magnitude columns
3. Aligns frequency grids
4. Calculates statistics
5. Computes difference (Fault - Normal)
6. Returns formatted chart data
```

### Step 3: Frontend Display

```
1. Receives data from backend
2. Renders dual-axis chart
3. Shows statistics side panel
4. Allows export and report generation
```

## Next Steps

1. Test with sample CSV files
2. Deploy to production server
3. Add database persistence
4. Integrate ML fault detection
5. Create automated reports

## Support

For issues or questions:

1. Check browser console for frontend errors
2. Check terminal for backend errors
3. Verify all dependencies are installed
4. Ensure CSV format matches requirements
5. Test API directly with curl
