# Testing Guide & Sample Data

## Quick Test Setup

### Generate Sample CSV Files

Create these files in your test directory:

#### File 1: Normal.csv (Baseline measurement)

```csv
freq,RMS,Peaks,Phase
10,50.2,55.1,45.5
20,48.5,52.3,46.2
30,45.8,49.7,47.1
40,43.2,46.8,48.3
50,40.5,43.5,49.1
60,38.1,41.2,49.8
70,35.8,39.0,50.2
80,33.6,37.1,50.5
90,31.5,35.3,50.7
100,29.5,33.6,50.8
```

#### File 2: Fault.csv (Fault measurement)

```csv
freq,RMS,Peaks,Phase
10,48.5,53.2,44.2
20,46.2,49.8,45.1
30,43.8,46.5,45.9
40,41.5,44.1,46.8
50,38.9,41.2,47.5
60,36.5,39.0,48.2
70,34.2,37.1,48.8
80,32.0,35.3,49.3
90,29.8,33.6,49.7
100,27.8,31.9,50.0
```

---

## Testing Scenarios

### Test 1: Single File Upload

**Expected Behavior**:

1. User uploads Normal.csv
2. Backend parses file
3. Displays single curve graph
4. Shows statistics for one file

**Test Steps**:

```bash
# Via API
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Normal.csv"

# Via Frontend
1. Go to Uploads tab
2. Click "Upload CSV Files"
3. Select Normal.csv
4. Click "Analyze"
5. View in Analysis tab
```

**Expected Result**:

```json
{
  "success": true,
  "chart_data": [
    {
      "index": 0,
      "frequency": 10.0,
      "magnitude": 50.2
    },
    ...
  ],
  "statistics": [
    {
      "name": "Normal.csv",
      "data_points": 10,
      "min_freq": 10.0,
      "max_freq": 100.0,
      "min_mag": 29.5,
      "max_mag": 50.2,
      "avg_mag": 40.67,
      "std_mag": 8.63
    }
  ]
}
```

---

### Test 2: Two File Comparison

**Expected Behavior**:

1. User uploads Normal.csv and Fault.csv
2. Backend aligns frequency grids
3. Displays dual-axis comparison
4. Shows statistics for both files + difference

**Test Steps**:

```bash
# Via API
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Normal.csv" \
  -F "file2=@Fault.csv"

# Via Frontend
1. Go to Uploads tab
2. Click "Upload CSV Files"
3. Select Normal.csv
4. Click again, select Fault.csv
5. Files auto-analyze
6. View in Analysis tab
```

**Expected Result**:

- Two curves overlaid (blue and red)
- Fault curve consistently lower than Normal
- Average difference: ~1.7-2.0 dB
- Statistics panel shows both files + difference

---

### Test 3: Format Handling - European Decimals

Create `European.csv`:

```csv
freq,RMS,Peaks,Phase
10,50,2,55,1,45,5
20,48,5,52,3,46,2
30,45,8,49,7,47,1
```

**Test**:

```bash
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@European.csv"
```

**Expected Result**: Successfully parsed (backend converts commas to dots)

---

### Test 4: Format Handling - Semicolon Separated

Create `Fault_Format.csv`:

```csv
Frequency;H1 x1 (Magnitude (dB));Phase;Coherence
10;48,5;45,5;0,95
20;46,2;46,2;0,92
30;43,8;47,1;0,88
```

**Test**:

```bash
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Fault_Format.csv" \
  -F "is_fault_format_1=true"
```

**Expected Result**: Successfully parsed despite semicolons and European format

---

### Test 5: Error Handling - Invalid CSV

Create `Invalid.csv`:

```csv
Date,Temperature,Humidity
2025-01-01,25.5,65
2025-01-02,26.1,62
```

**Test**:

```bash
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Invalid.csv"
```

**Expected Result**: Error message explaining no frequency/magnitude columns found

---

### Test 6: Edge Case - Large Frequency Range

Create `Large_Range.csv`:

```csv
freq,RMS
1,50.2
10,48.5
100,45.8
1000,43.2
10000,40.5
100000,38.1
1000000,35.8
```

**Test**:

```bash
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Large_Range.csv"
```

**Expected Result**: Chart displays with proper frequency axis scaling (1, 10, 100, 1k, 10k, 100k, 1M)

---

### Test 7: Edge Case - Missing Values

Create `Missing.csv`:

```csv
freq,RMS
10,50.2
20,
30,45.8
40,
50,40.5
```

**Test**:

```bash
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Missing.csv"
```

**Expected Result**: Successfully parses, skipping empty values (5 data points instead of 5)

---

## Frontend UI Testing

### Test: File Upload Flow

```
Step 1: Navigate to Uploads tab
Expected: See "Upload CSV Files" section

Step 2: Click file input or drag file
Expected: File browser opens / accepts drop

Step 3: Select file
Expected: File name appears, analysis starts automatically

Step 4: View results
Expected: AnalysisTab appears with chart

Step 5: Remove file button
Expected: Clears file and chart
```

### Test: Chart Interactions

```
1. Zoom with mouse wheel (if implemented)
2. Hover for tooltips (frequency/magnitude values)
3. Legend click to show/hide curves
4. Export button saves SVG
5. Report button generates text file
```

### Test: Error Display

```
1. Upload invalid file
Expected: Red error box appears with message

2. File with no frequency column
Expected: Clear error message about missing columns

3. Network error (backend offline)
Expected: Error message about connection

4. Large file (>10MB)
Expected: Either processes or shows size error
```

---

## Performance Testing

### Test: Large File Handling

Create `Large.csv` with 10,000 data points:

```python
import csv

with open('Large.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['freq', 'RMS'])
    for i in range(1, 10001):
        writer.writerow([i * 0.1, 50.0 - (i * 0.001)])
```

**Test**:

```bash
time curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Large.csv"
```

**Expected Result**:

- Processes in < 1 second
- Backend handles gracefully
- Frontend displays without lag

---

### Test: Two Large Files

```python
# Create two 10K point files
# Normal_Large.csv and Fault_Large.csv
```

**Test**:

```bash
time curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Normal_Large.csv" \
  -F "file2=@Fault_Large.csv"
```

**Expected Result**:

- Processes in < 2 seconds
- Interpolation works correctly
- Statistics accurate

---

## Integration Testing

### Test: End-to-End Flow

**Step 1**: Start backend

```bash
cd backend
python main.py
```

**Step 2**: Start frontend

```bash
cd frontend
npm run dev
```

**Step 3**: Open browser

```
http://localhost:5173
```

**Step 4**: Complete workflow

1. Navigate to Uploads
2. Upload Normal.csv
3. Upload Fault.csv
4. Wait for analysis
5. View Analysis tab
6. Check statistics
7. Export chart
8. Generate report
9. Remove files
10. Repeat

**Expected Result**: All operations work smoothly with no errors

---

## API Response Verification

### Verify Chart Data

```python
import json
import requests

response = requests.post(
    'http://localhost:5000/api/fra/analyze',
    files={'file1': open('Normal.csv'), 'file2': open('Fault.csv')}
)

data = response.json()

# Verify structure
assert data['success'] == True
assert 'chart_data' in data
assert 'statistics' in data
assert len(data['chart_data']) > 0
assert len(data['statistics']) >= 2

# Verify chart data has required fields
for point in data['chart_data']:
    assert 'index' in point
    assert 'frequency' in point
    assert 'magnitude' in point

print("✓ Chart data verified")
```

### Verify Statistics

```python
# Verify statistics structure
for stat in data['statistics']:
    assert 'name' in stat
    assert 'data_points' in stat
    assert 'min_mag' in stat
    assert 'max_mag' in stat
    assert 'avg_mag' in stat

    # Verify logical values
    assert stat['min_mag'] <= stat['max_mag']
    assert stat['min_mag'] <= stat['avg_mag'] <= stat['max_mag']

print("✓ Statistics verified")
```

---

## Load Testing

### Using Apache Bench

```bash
# Install Apache Bench (if not present)
# On Windows: Use WSL or download separately
# On Mac: brew install httpd
# On Linux: apt install apache2-utils

# Single file upload test
ab -n 100 -c 10 -p Normal.csv \
   -T "multipart/form-data; boundary=abcdef" \
   http://localhost:5000/api/fra/analyze
```

### Using Python

```python
import concurrent.futures
import requests
import time

def upload_file():
    with open('Normal.csv', 'rb') as f:
        files = {'file1': f}
        response = requests.post(
            'http://localhost:5000/api/fra/analyze',
            files=files
        )
    return response.status_code

# Load test: 10 concurrent uploads
start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(upload_file, range(10)))
elapsed = time.time() - start

print(f"10 uploads in {elapsed:.2f}s")
print(f"Success: {sum(1 for r in results if r == 200)}/10")
```

---

## Checklist for Testing

- [ ] Test 1: Single file upload (API)
- [ ] Test 2: Single file upload (Frontend)
- [ ] Test 3: Two file comparison (API)
- [ ] Test 4: Two file comparison (Frontend)
- [ ] Test 5: European decimal format
- [ ] Test 6: Semicolon-separated format
- [ ] Test 7: Invalid CSV error handling
- [ ] Test 8: Large frequency range
- [ ] Test 9: Missing values handling
- [ ] Test 10: File upload UI
- [ ] Test 11: Chart interactions
- [ ] Test 12: Error display
- [ ] Test 13: Large file (>1MB)
- [ ] Test 14: Two large files
- [ ] Test 15: End-to-end flow
- [ ] Test 16: API response structure
- [ ] Test 17: Statistics accuracy
- [ ] Test 18: Load testing

---

## Debugging Commands

### Check Backend Health

```bash
curl http://localhost:5000/api/health
```

### Debug CSV Parsing (Python)

```python
from graph import FRAAnalyzer

with open('Normal.csv', 'r') as f:
    content = f.read()

result = FRAAnalyzer.analyze_single_csv(content)

if result['success']:
    print(f"✓ Parsed {len(result['chart_data'])} points")
    print(f"  Min mag: {result['statistics'][0]['min_mag']} dB")
    print(f"  Max mag: {result['statistics'][0]['max_mag']} dB")
else:
    print(f"✗ Error: {result['error']}")
```

### Frontend Console Debugging

```javascript
// In browser console
// Check if API call succeeded
fetch("/api/fra/analyze", {
  method: "POST",
  body: formData,
})
  .then((r) => r.json())
  .then((d) => console.log(d))
  .catch((e) => console.error(e));
```

---

## Known Limitations & Workarounds

| Issue                   | Cause                            | Workaround                         |
| ----------------------- | -------------------------------- | ---------------------------------- |
| Frequency grid mismatch | Files have different freq points | Backend interpolates automatically |
| European decimals       | CSV uses commas                  | Backend converts automatically     |
| Missing values          | NaN in data                      | Backend skips empty rows           |
| Large files slow        | File I/O overhead                | Consider batch processing          |
| CORS errors             | Frontend/Backend mismatch        | Ensure CORS enabled in Flask       |

---

## Test Reports

After running tests, record results:

```markdown
## Test Report - [Date]

### Backend Tests

- [ ] Health check: ✓ PASS
- [ ] Single file: ✓ PASS
- [ ] Two files: ✓ PASS
- [ ] Error handling: ✓ PASS
- [ ] Performance: ✓ PASS (< 2s)

### Frontend Tests

- [ ] File upload: ✓ PASS
- [ ] Chart display: ✓ PASS
- [ ] Statistics: ✓ PASS
- [ ] Error messages: ✓ PASS
- [ ] Export features: ✓ PASS

### Integration Tests

- [ ] End-to-end flow: ✓ PASS
- [ ] API response format: ✓ PASS
- [ ] Data accuracy: ✓ PASS

### Summary

All tests passed. System ready for production.
```
