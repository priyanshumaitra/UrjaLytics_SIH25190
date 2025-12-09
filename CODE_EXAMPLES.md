# Code Examples & API Usage

## Frontend Examples

### Example 1: Using useCSVUpload Hook

```javascript
import { useCSVUpload } from "../hooks/useCSVUpload";

function MyComponent() {
  const {
    csvFiles, // Array of File objects
    csvData, // Array of {frequency, magnitude, source}
    statistics, // Array of stat objects from backend
    isAnalyzing, // Boolean loading state
    analysisError, // Error message if any
    handleCSVUpload, // Function to handle file input change
    removeCSVFile, // Function to remove file by index
    sendToBackend, // Function to send files to API
  } = useCSVUpload();

  return (
    <div>
      <input type="file" multiple onChange={handleCSVUpload} accept=".csv" />

      {isAnalyzing && <p>Analyzing files...</p>}
      {analysisError && <p style={{ color: "red" }}>{analysisError}</p>}

      {csvFiles.map((file, idx) => (
        <div key={idx}>
          <span>{file.name}</span>
          <button onClick={() => removeCSVFile(idx)}>Remove</button>
        </div>
      ))}

      {statistics.map((stat) => (
        <div key={stat.name}>
          <h3>{stat.name}</h3>
          <p>Data Points: {stat.data_points}</p>
          <p>Avg Magnitude: {stat.avg_mag} dB</p>
        </div>
      ))}
    </div>
  );
}
```

### Example 2: Direct Backend API Call

```javascript
// Manual API call (if not using hook)
async function analyzeFiles(file1, file2) {
  const formData = new FormData();
  formData.append("file1", file1);
  if (file2) formData.append("file2", file2);

  try {
    const response = await fetch("/api/fra/analyze", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (result.success) {
      console.log("Chart data:", result.chart_data);
      console.log("Stats:", result.statistics);
      return result;
    } else {
      console.error("Error:", result.error);
    }
  } catch (error) {
    console.error("Network error:", error);
  }
}
```

## Backend Examples

### Example 1: Using FRAAnalyzer Class

```python
from graph import FRAAnalyzer
import pandas as pd

# Single file analysis
csv_content = open('Normal.csv').read()
result = FRAAnalyzer.analyze_single_csv(
    csv_content=csv_content,
    is_fault_format=False,
    file_name="Normal.csv"
)

if result['success']:
    print(f"Data points: {len(result['chart_data'])}")
    print(f"Statistics: {result['statistics']}")
    # Use chart_data for visualization
else:
    print(f"Error: {result['error']}")
```

### Example 2: Two File Comparison

```python
from graph import FRAAnalyzer

# Read files
with open('Normal.csv', 'r') as f:
    normal_csv = f.read()

with open('Fault.csv', 'r') as f:
    fault_csv = f.read()

# Analyze
result = FRAAnalyzer.analyze_two_csvs(
    csv_content_1=normal_csv,
    csv_content_2=fault_csv,
    is_fault_format_1=False,
    is_fault_format_2=False,
    file_name_1="Normal.csv",
    file_name_2="Fault.csv"
)

if result['success']:
    # Access results
    print("Chart points:", len(result['chart_data']))
    print("Difference array:", result['difference'])
    print("Statistics:")
    for stat in result['statistics']:
        print(f"  {stat['name']}: avg={stat['avg_mag']} dB")
```

### Example 3: Custom Vector Comparison

```python
from graph import FRAAnalyzer
import numpy as np

# Pre-computed vectors
freq = np.array([10, 20, 30, 40, 50])
mag1 = np.array([50.2, 48.5, 45.8, 43.2, 40.5])
mag2 = np.array([48.5, 46.2, 43.8, 41.5, 38.9])

# Calculate statistics
stats1 = FRAAnalyzer.calculate_statistics(freq, mag1)
stats2 = FRAAnalyzer.calculate_statistics(freq, mag2)
diff = FRAAnalyzer.calculate_difference(freq, mag1, mag2)

print("File 1 avg magnitude:", stats1['avg_mag'], "dB")
print("File 2 avg magnitude:", stats2['avg_mag'], "dB")
print("Difference:", diff)  # [mag2[i] - mag1[i] for i in range(len(freq))]
```

### Example 4: API Endpoint Usage

```python
# In main.py - example of how it's used

@app.route('/api/fra/analyze', methods=['POST'])
def analyze_fra():
    file1 = request.files.get('file1')
    file2 = request.files.get('file2')

    csv_content_1 = file1.read().decode('utf-8')
    csv_content_2 = file2.read().decode('utf-8') if file2 else None

    if csv_content_2:
        result = FRAAnalyzer.analyze_two_csvs(
            csv_content_1,
            csv_content_2,
            file_name_1=file1.filename,
            file_name_2=file2.filename
        )
    else:
        result = FRAAnalyzer.analyze_single_csv(
            csv_content_1,
            file_name=file1.filename
        )

    return jsonify(result)
```

## CSV Format Examples

### Example 1: Standard Normal File

```csv
freq,RMS,Peaks,Phase
10.0,50.2,55.1,45.5
20.0,48.5,52.3,46.2
30.0,45.8,49.7,47.1
40.0,43.2,46.8,48.3
50.0,40.5,43.5,49.1
```

### Example 2: European Decimal Format

```csv
freq,RMS,Peaks,Phase
10,50,2,55,1,45,5
20,48,5,52,3,46,2
30,45,8,49,7,47,1
```

(Note: Backend converts these automatically)

### Example 3: Fault Format (Semicolon-separated)

```
Frequency;H1 x1 (Magnitude (dB));Phase;Coherence
10;48,5;45,5;0,95
20;46,2;46,2;0,92
30;43,8;47,1;0,88
```

### Example 4: Different Column Names

```csv
frequency,magnitude
10.0,-50.2
20.0,-48.5
30.0,-45.8
```

Backend handles these automatically!

## Testing Examples

### Example 1: Test with cURL

```bash
# Single file
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Normal.csv"

# Two files
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Normal.csv" \
  -F "file2=@Fault.csv"

# With fault format flag
curl -X POST http://localhost:5000/api/fra/analyze \
  -F "file1=@Normal.csv" \
  -F "file2=@Failed.csv" \
  -F "is_fault_format_2=true"
```

### Example 2: Test with Python

```python
import requests
import json

# Prepare files
files = {
    'file1': open('Normal.csv', 'rb'),
    'file2': open('Fault.csv', 'rb')
}

# Send request
response = requests.post(
    'http://localhost:5000/api/fra/analyze',
    files=files
)

# Parse response
result = response.json()

# Print results
if result['success']:
    print(json.dumps(result, indent=2))
else:
    print(f"Error: {result['error']}")

# Close files
files['file1'].close()
files['file2'].close()
```

### Example 3: Test with JavaScript/Node.js

```javascript
const FormData = require("form-data");
const fs = require("fs");
const axios = require("axios");

async function testFRA() {
  const form = new FormData();
  form.append("file1", fs.createReadStream("Normal.csv"));
  form.append("file2", fs.createReadStream("Fault.csv"));

  try {
    const response = await axios.post(
      "http://localhost:5000/api/fra/analyze",
      form,
      { headers: form.getHeaders() }
    );

    console.log("Success:", response.data);
  } catch (error) {
    console.error("Error:", error.message);
  }
}

testFRA();
```

## Response Examples

### Example 1: Single File Response

```json
{
  "success": true,
  "chart_data": [
    {
      "index": 0,
      "frequency": 10.0,
      "magnitude": 50.2
    },
    {
      "index": 1,
      "frequency": 20.0,
      "magnitude": 48.5
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
  "file_name": "Normal.csv"
}
```

### Example 2: Two File Comparison Response

```json
{
  "success": true,
  "chart_data": [
    {
      "index": 0,
      "frequency": 10.0,
      "magnitude": 50.2,
      "magnitude2": 48.5
    },
    {
      "index": 1,
      "frequency": 20.0,
      "magnitude": 48.5,
      "magnitude2": 46.2
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
    },
    {
      "name": "Fault.csv",
      "data_points": 150,
      "min_freq": 10.0,
      "max_freq": 1000.0,
      "min_mag": -82.1,
      "max_mag": -22.5,
      "avg_mag": -47.8,
      "std_mag": 16.1
    },
    {
      "name": "Difference (Fault.csv - Normal.csv)",
      "min_diff": -5.2,
      "max_diff": 3.8,
      "avg_diff": -2.5,
      "std_diff": 1.8
    }
  ],
  "frequencies": [10.0, 20.0, ...],
  "difference": [-1.7, -2.3, -2.0, ...],
  "file1_name": "Normal.csv",
  "file2_name": "Fault.csv"
}
```

### Example 3: Error Response

```json
{
  "success": false,
  "error": "CSV must contain columns for frequency and magnitude. Found columns: ['time', 'voltage', 'current']"
}
```

## Advanced Usage

### Example 1: Batch Processing

```python
import os
from graph import FRAAnalyzer

# Process all CSV files in a directory
csv_dir = 'data/fra_files'
results = {}

for filename in os.listdir(csv_dir):
    if filename.endswith('.csv'):
        filepath = os.path.join(csv_dir, filename)
        with open(filepath, 'r') as f:
            csv_content = f.read()

        result = FRAAnalyzer.analyze_single_csv(
            csv_content,
            file_name=filename
        )

        if result['success']:
            results[filename] = {
                'data_points': len(result['chart_data']),
                'avg_mag': result['statistics'][0]['avg_mag']
            }

print("Batch processing complete:")
for filename, stats in results.items():
    print(f"{filename}: {stats}")
```

### Example 2: Statistical Comparison

```python
from graph import FRAAnalyzer
import numpy as np

# Analyze multiple files
files = ['Normal1.csv', 'Normal2.csv', 'Fault1.csv']
all_stats = []

for filename in files:
    with open(filename, 'r') as f:
        result = FRAAnalyzer.analyze_single_csv(f.read(), file_name=filename)
    all_stats.append(result['statistics'][0])

# Compare statistics
print("Comparison across files:")
print("File | Avg Mag | Std Dev")
for stat in all_stats:
    print(f"{stat['name']} | {stat['avg_mag']} | {stat['std_mag']}")

# Find outliers (high std dev = anomaly)
std_devs = [s['std_mag'] for s in all_stats]
threshold = np.mean(std_devs) + np.std(std_devs)
print(f"\nOutliers (std_mag > {threshold}):")
for stat in all_stats:
    if stat['std_mag'] > threshold:
        print(f"  {stat['name']}: {stat['std_mag']}")
```

## Debugging Tips

### Enable Debug Logging

```python
# In main.py
app.config['DEBUG'] = True
app.logger.setLevel(logging.DEBUG)

import logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/api/fra/analyze', methods=['POST'])
def analyze_fra():
    app.logger.debug(f"Received files: {request.files.keys()}")
    # ... rest of function
    app.logger.debug(f"Result: {result}")
    return jsonify(result)
```

### Check File Content Before Upload

```javascript
// Frontend debugging
const handleCSVUpload = (e) => {
  const files = Array.from(e.target.files);
  files.forEach((file) => {
    console.log(`File: ${file.name}, Size: ${file.size} bytes`);

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target.result;
      console.log(`First 200 chars: ${content.substring(0, 200)}`);
    };
    reader.readAsText(file);
  });
};
```

### Verify Backend Response

```python
# Print full response before returning
result = FRAAnalyzer.analyze_two_csvs(...)
print(f"Response: {json.dumps(result, indent=2)}")
return jsonify(result)
```
