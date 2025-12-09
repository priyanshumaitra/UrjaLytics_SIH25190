# UrjaLytics FRA Analysis - Complete Implementation Guide

## 🎯 Project Overview

UrjaLytics is a transformer health monitoring system with **Frequency Response Analysis (FRA)** capabilities. This implementation provides a complete backend system for analyzing FRA CSV files and comparing transformer baseline vs fault conditions.

### What's New

- ✅ Backend FRA analysis engine (`graph.py`)
- ✅ RESTful API endpoints for CSV analysis
- ✅ Automatic frequency/magnitude column detection
- ✅ Support for multiple CSV formats (normal and fault)
- ✅ Two-file comparison with difference calculation
- ✅ Comprehensive statistics generation
- ✅ Frontend integration via React hook

---

## 📁 Project Structure

```
UrjaLytics_SIH25190/
├── backend/
│   ├── main.py                 # Flask server + API endpoints
│   ├── graph.py               # FRA Analysis Engine (NEW)
│   ├── requirements.txt        # Python dependencies
│   └── test.py               # Testing file
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AnalysisTab.jsx       # Chart visualization (UPDATED)
│   │   │   ├── Uploads.jsx           # Upload component (UPDATED)
│   │   │   └── ...
│   │   ├── hooks/
│   │   │   └── useCSVUpload.js      # API integration hook (REWRITTEN)
│   │   └── ...
│   └── ...
│
├── FRA_IMPLEMENTATION_SUMMARY.md      # Detailed changes
├── QUICK_START.md                     # Setup instructions
├── ARCHITECTURE.md                    # System design & data flow
├── CODE_EXAMPLES.md                   # Usage examples
└── README.md                          # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ with pip
- Node.js 14+ with npm
- Git

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Start Flask server
python main.py
```

Expected output:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 3. Verify Installation

```bash
# Test API health
curl http://localhost:5000/api/health
# Expected: {"status": "ok", "service": "UrjaLytics FRA Analysis"}
```

---

## 📊 How It Works

### 1. CSV File Upload

User selects 1-2 CSV files with frequency and magnitude data

### 2. Backend Processing

- Parse CSV with automatic column detection
- Handle various formats (normal, fault, European decimals)
- Align frequency grids (interpolation for 2 files)
- Calculate statistics (min, max, avg, std dev)
- Compute difference (File2 - File1)

### 3. Data Visualization

- Display dual-axis graph (one per file)
- Show statistics in side panel
- Export options (chart, report)

---

## 📝 Supported CSV Formats

### Format 1: Standard FRA (Comma-separated)

```csv
freq,RMS,Peaks,Phase
10.0,50.2,55.1,45.5
20.0,48.5,52.3,46.2
```

### Format 2: Fault/European (Semicolon-separated)

```csv
Frequency;H1 x1 (Magnitude (dB));Phase
10;48,5;45,5
20;46,2;46,2
```

### Format 3: Flexible Headers

Backend automatically detects:

- Frequency columns: `freq`, `frequency`, `hz`
- Magnitude columns: `mag`, `magnitude`, `db`
- First 2 numeric columns used if no match

---

## 🔌 API Endpoints

### POST /api/fra/analyze

Main endpoint for FRA analysis

- **Request**: FormData with file1, optional file2
- **Response**: chart_data, statistics, frequencies
- **Example**:

```bash
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Normal.csv" \
  -F "file2=@Fault.csv"
```

### GET /api/health

Health check endpoint

- **Response**: `{"status": "ok", "service": "UrjaLytics FRA Analysis"}`

---

## 📈 Response Structure

```json
{
  "success": true,
  "chart_data": [
    {
      "index": 0,
      "frequency": 10.0,
      "magnitude": 50.2,
      "magnitude2": 48.5  // Only if 2 files
    }
  ],
  "statistics": [
    {
      "name": "Normal.csv",
      "data_points": 150,
      "min_freq": 10.0,
      "max_freq": 1000.0,
      "min_mag": -80.5,
      "max_mag": -20.0,
      "avg_mag": -45.3,
      "std_mag": 15.2
    }
  ],
  "frequencies": [10.0, 20.0, ...],
  "file1_name": "Normal.csv",
  "file2_name": "Fault.csv"
}
```

---

## 🛠 Features

### Backend (graph.py)

- ✅ Multiple CSV format support
- ✅ Automatic column detection
- ✅ European decimal handling (1,234 → 1.234)
- ✅ Frequency grid alignment & interpolation
- ✅ Robust error handling
- ✅ Statistical analysis
- ✅ Difference calculation

### Frontend (React)

- ✅ File upload UI (drag & drop)
- ✅ Recharts visualization
- ✅ Dual-axis comparison
- ✅ Statistics sidebar
- ✅ Export chart as SVG
- ✅ Generate text reports
- ✅ Error state handling
- ✅ Loading indicators

---

## 📚 Documentation Files

| File                            | Purpose                            |
| ------------------------------- | ---------------------------------- |
| `FRA_IMPLEMENTATION_SUMMARY.md` | Detailed technical changes         |
| `QUICK_START.md`                | Step-by-step setup guide           |
| `ARCHITECTURE.md`               | System design & data flow diagrams |
| `CODE_EXAMPLES.md`              | Code snippets & API examples       |
| `README.md`                     | This file                          |

---

## 🔄 Workflow Example

### Scenario: Compare Normal vs Fault Measurements

1. **Upload Files**

   - User uploads `Normal.csv` (baseline measurement)
   - User uploads `Failed_ICT-II.csv` (fault measurement)

2. **Frontend Processing**

   - `handleCSVUpload()` receives both files
   - `useCSVUpload` hook sends to backend via `POST /api/fra/analyze`

3. **Backend Processing**

   - Parse both CSVs
   - Extract frequency and RMS (magnitude) columns
   - Align frequency grids (interpolate if needed)
   - Calculate:
     - Normal: avg_mag=-45.3 dB, std_mag=15.2
     - Fault: avg_mag=-47.8 dB, std_mag=16.1
     - Difference: avg_diff=-2.5 dB

4. **Frontend Display**

   - Recharts shows two curves (blue=Normal, red=Fault)
   - Statistics panel shows all metrics
   - User can export graph or generate report

5. **Analysis**
   - 2.5 dB average difference detected
   - Fault has higher standard deviation (16.1 vs 15.2)
   - Indicates potential transformer degradation

---

## 🐛 Troubleshooting

### Issue: "CSV must contain columns for frequency and magnitude"

**Solution**: Ensure CSV has at least 2 numeric columns with frequency and magnitude data

### Issue: Port 5000 already in use

**Solution**:

```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: CORS errors

**Solution**:

- Ensure Flask-CORS is installed: `pip install Flask-CORS`
- Backend must be running at `http://localhost:5000`
- Frontend must make requests to correct URL

### Issue: CSV parsing fails with European decimals

**Solution**: Backend automatically converts `1,234` → `1.234`. If still failing, check file encoding (use UTF-8)

---

## 🧪 Testing

### Unit Testing

```bash
# Backend test file
python backend/test.py
```

### Manual API Testing

```bash
# Test single file
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@sample.csv"

# Test comparison
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Normal.csv" \
  -F "file2=@Fault.csv"
```

### Frontend Testing

1. Navigate to Uploads tab
2. Upload test CSV files
3. View Analysis tab
4. Verify chart and statistics display

---

## 📦 Dependencies

### Backend

- **Flask 2.3.3**: Web framework
- **Flask-CORS 4.0.0**: Cross-origin requests
- **pandas 2.0.3**: Data processing
- **numpy 1.24.3**: Numerical computing
- **scikit-learn 1.3.0**: Machine learning (future use)
- **pymongo 4.5.0**: MongoDB integration

### Frontend

- **React**: UI framework
- **recharts**: Chart visualization
- **lucide-react**: Icons
- **tailwindcss**: Styling

---

## 🔐 Security Considerations

- ✅ File size validation
- ✅ CSV format validation
- ✅ Server-side data processing
- ✅ Error messages don't expose system paths
- ✅ CORS properly configured
- ✅ Input sanitization

---

## 🚀 Future Enhancements

### Phase 2

- [ ] Machine learning fault detection
- [ ] Database persistence
- [ ] Historical trend analysis
- [ ] Automated reporting

### Phase 3

- [ ] Advanced statistics (percentiles, peaks)
- [ ] Multi-file comparison
- [ ] Batch processing
- [ ] Web socket real-time updates

### Phase 4

- [ ] Mobile app support
- [ ] Cloud deployment
- [ ] API authentication
- [ ] Usage analytics

---

## 👥 Contributing

To contribute:

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

---

## 📞 Support

### Common Issues

See `QUICK_START.md` troubleshooting section

### Technical Details

See `ARCHITECTURE.md` for system design

### Code Examples

See `CODE_EXAMPLES.md` for usage patterns

### API Documentation

See `FRA_IMPLEMENTATION_SUMMARY.md` for endpoint details

---

## 📄 License

UrjaLytics - Transformer Health Monitoring System

---

## ✅ Implementation Checklist

- [x] Create backend/graph.py with FRAAnalyzer class
- [x] Add /api/fra/analyze endpoint to main.py
- [x] Update requirements.txt with dependencies
- [x] Rewrite useCSVUpload hook for API integration
- [x] Simplify AnalysisTab component
- [x] Update Uploads component props
- [x] Create comprehensive documentation
- [x] Add code examples
- [x] Document API responses
- [x] Test end-to-end flow

---

## 📊 Statistics Summary

After implementation:

- **Backend Files**: 1 new (graph.py), 1 modified (main.py), 1 modified (requirements.txt)
- **Frontend Files**: 3 modified (useCSVUpload.js, AnalysisTab.jsx, Uploads.jsx)
- **Documentation**: 4 new files (guides + examples)
- **API Endpoints**: 2 new endpoints
- **Lines of Code**:
  - Backend: ~400 lines (graph.py)
  - Frontend Hook: ~150 lines (simplified from 200+)

---

## 🎓 Learning Resources

### Understanding FRA

- Frequency Response Analysis measures transformer impedance vs frequency
- Helps detect winding deformation, core issues, insulation degradation
- Baseline comparison with fault conditions reveals damage patterns

### Data Processing

- Backend handles parsing, normalization, interpolation
- Frontend focuses on visualization and user interaction
- Separation of concerns improves maintainability

### REST API Design

- Clear endpoint naming (/api/fra/analyze)
- Consistent response format
- Proper error handling
- CORS enabled for cross-domain requests

---

## 🎉 Success Criteria Met

✅ Deleted local CSV parsing logic from frontend
✅ Implemented robust backend FRA analysis engine
✅ Created separate graph.py module
✅ Integrated with existing Flask server
✅ Properly connected via API endpoints
✅ Handles 2 CSV file uploads
✅ Shows frequency/magnitude comparison
✅ Calculates and displays differences
✅ Generates comprehensive statistics
✅ Maintains clean separation of concerns

---

## 📞 Getting Help

1. **Check Documentation**: Start with QUICK_START.md
2. **Review Examples**: See CODE_EXAMPLES.md
3. **Understand Architecture**: Read ARCHITECTURE.md
4. **Check Logs**: Review browser console and terminal output
5. **Test API**: Use cURL to test endpoints directly

---

**Last Updated**: December 9, 2025
**Status**: ✅ Complete and Ready for Testing
