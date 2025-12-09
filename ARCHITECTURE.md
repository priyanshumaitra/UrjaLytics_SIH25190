# FRA Analysis Architecture & Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Uploads Component                  AnalysisTab Component        │
│  ┌──────────────────────┐           ┌──────────────────────┐    │
│  │ - File Upload UI     │           │ - Recharts Graph     │    │
│  │ - File Selection     │──────────>│ - Statistics Panel   │    │
│  │ - Drag & Drop        │           │ - Export Features    │    │
│  └──────────────────────┘           └──────────────────────┘    │
│           │                                      ▲                │
│           │ handleCSVUpload()                   │                │
│           │                                      │                │
│           ▼                                      │                │
│  ┌──────────────────────┐                      │                │
│  │ useCSVUpload Hook    │                      │                │
│  │ - sendToBackend()    │──────API Call────────┘                │
│  │ - Error Handling     │   (FormData)                           │
│  │ - State Management   │                                        │
│  └──────────────────────┘                                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                           │ HTTP POST
                           │ /api/fra/analyze
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Backend (Flask)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  main.py - Flask Server                                          │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ POST /api/fra/analyze                                │       │
│  │ - Receives file uploads (file1, file2)               │       │
│  │ - Calls FRAAnalyzer.analyze_two_csvs()               │       │
│  │ - Returns JSON response                              │       │
│  └──────────────────────────────────────────────────────┘       │
│                   │                                              │
│                   ▼                                              │
│  graph.py - FRA Analysis Engine                                 │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ FRAAnalyzer Class                                    │       │
│  │ ┌────────────────────────────────────────────────┐  │       │
│  │ │ parse_normal_fra_csv()  ──┐                   │  │       │
│  │ │ parse_fault_fra_csv()    ──┤──> normalize()  │  │       │
│  │ │ calculate_difference()    ──┘                  │  │       │
│  │ │ calculate_statistics()                         │  │       │
│  │ │ prepare_chart_data()                           │  │       │
│  │ └────────────────────────────────────────────────┘  │       │
│  └──────────────────────────────────────────────────────┘       │
│           ▲                                       │              │
│           │                                       │              │
│           └───────────────────────────────────────┘              │
│                 JSON Response                                    │
│            (chart_data, statistics)                              │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow: Two File Comparison

```
INPUT: Two CSV Files
    ↓
    ├─ File 1: Normal.csv      File 2: Fault.csv
    │   (150 data points)       (180 data points)
    │
    ▼
PARSE & CLEAN
    ├─ Extract: freq, magnitude columns
    ├─ Handle European decimals: 1,234 → 1.234
    ├─ Remove NaN values
    │
    ▼
    File1_freq: [10, 20, 30, ...]        File2_freq: [10, 15, 20, 25, 30, ...]
    File1_mag:  [50.2, 48.5, 45.8, ...]  File2_mag:  [48.5, 47.1, 46.2, 44.8, 43.8, ...]

    ▼
NORMALIZE FREQUENCY GRID
    ├─ Use File1 frequency as base: [10, 20, 30, ...]
    ├─ Interpolate File2 magnitude to match: [48.5, 46.2, 43.8, ...]
    │
    ▼
    File1_freq: [10, 20, 30, ...]
    File1_mag:  [50.2, 48.5, 45.8, ...]
    File2_mag:  [48.5, 46.2, 43.8, ...]

    ▼
CALCULATE STATISTICS
    │
    ├─ File 1:
    │   ├─ data_points: 150
    │   ├─ min_freq: 10.0, max_freq: 1000.0 Hz
    │   ├─ min_mag: -80.5 dB, max_mag: -20.0 dB
    │   ├─ avg_mag: -45.3 dB
    │   └─ std_mag: 15.2 dB
    │
    ├─ File 2:
    │   ├─ data_points: 150
    │   ├─ min_freq: 10.0, max_freq: 1000.0 Hz
    │   ├─ min_mag: -82.1 dB, max_mag: -22.5 dB
    │   ├─ avg_mag: -47.8 dB
    │   └─ std_mag: 16.1 dB
    │
    └─ Difference:
        ├─ min_diff: -5.2 dB
        ├─ max_diff: 3.8 dB
        ├─ avg_diff: -2.5 dB
        └─ std_diff: 1.8 dB

    ▼
FORMAT FOR VISUALIZATION
    │
    [
      {index: 0, frequency: 10.0,  magnitude: 50.2,  magnitude2: 48.5},
      {index: 1, frequency: 20.0,  magnitude: 48.5,  magnitude2: 46.2},
      {index: 2, frequency: 30.0,  magnitude: 45.8,  magnitude2: 43.8},
      ...
    ]

    ▼
OUTPUT: JSON Response
{
  "success": true,
  "chart_data": [...],
  "statistics": [
    {name: "Normal.csv", data_points: 150, ...},
    {name: "Fault.csv", data_points: 150, ...},
    {name: "Difference", min_diff: -5.2, ...}
  ],
  "frequencies": [10.0, 20.0, 30.0, ...],
  "file1_name": "Normal.csv",
  "file2_name": "Fault.csv"
}
```

## Component Interaction Sequence

```
User Actions                  Frontend Components              Backend API
     │                              │                             │
     ├─────────────────────>│ Upload Component                    │
     │  Select CSV Files    │       │                             │
     │                      ├──────────────────────────────────>│ /api/fra/analyze
     │                      │ handleCSVUpload(files)            │   (POST FormData)
     │                      │       │                             │
     │                      │       ├──> useCSVUpload Hook       │
     │                      │       │    sendToBackend()         │
     │                      │       │         │                   │
     │                      │       │         └─────────────────>│ Flask Server
     │                      │       │              HTTP POST      │
     │                      │       │<─────────────────────────── │ JSON Response
     │                      │       │      (chart_data, stats)   │
     │                      │       │                             │
     │                      │       └─> State Update:            │
     │                      │           csvData                  │
     │                      │           statistics               │
     │                      │           isAnalyzing: false       │
     │                      │       │                             │
     │                      ├──────────────────────────────────>│
     │  Click "Analysis"    │ Switch Tab                         │
     │<─────────────────────│ Render AnalysisTab                │
     │  View Chart          │    - Read csvData                 │
     │  View Stats          │    - Read statistics              │
     │  Export/Report       │    - Display Recharts             │
     │                      │    - Show Statistics Panel        │
```

## Single File Analysis Flow

```
User uploads: Normal.csv (single file)
      │
      ▼
handleCSVUpload(file1)
      │
      ├─ sendToBackend([file1])
      │     │
      │     └─> POST /api/fra/analyze
      │         - file1: Normal.csv
      │         - no file2
      │
      ▼
Backend: analyze_single_csv()
      │
      ├─ Parse Normal.csv
      ├─ Calculate statistics
      ├─ Prepare chart data
      │
      ▼
Response:
{
  "chart_data": [{index, frequency, magnitude}, ...],
  "statistics": [{name: "Normal.csv", data_points, ...}],
  "file_name": "Normal.csv"
}
      │
      ▼
Frontend displays:
- Single curve on graph
- Statistics for one file
```

## Error Handling Flow

```
User Action
    │
    ├─ File selection → File too large/invalid format?
    │       ├─ Yes → Show error in UI
    │       └─ No → Continue
    │
    ├─ Send to backend → Network error?
    │       ├─ Yes → Show error message + retry
    │       └─ No → Continue
    │
    ├─ Backend processes → CSV parsing error?
    │       ├─ Yes → Return error JSON
    │       │         └─ Frontend shows: "Error parsing CSV: ..."
    │       └─ No → Return success response
    │
    └─ Display results → Empty data?
            ├─ Yes → Show "No data to display"
            └─ No → Display charts and stats
```

## Key Features

### 1. Intelligent Column Detection

```
CSV Headers → Backend analyzes → Finds columns
"freq" "frequency" "hz" → Frequency column
"mag" "magnitude" "db" → Magnitude column
Auto-selects first 2 numeric columns if headers unclear
```

### 2. Format Support

```
Normal Format:   freq,RMS,Peaks,Phase
Fault Format:    Frequency;H1 x1 (Magnitude);Phase
European:        1,234 (comma decimals)
All handled automatically
```

### 3. Frequency Grid Alignment

```
File1: [10, 20, 30, 40, 50] Hz
File2: [15, 25, 35, 45]     Hz
                    ↓
            Interpolate File2
                    ↓
File1: [10, 20, 30, 40, 50] Hz
File2: [?, 20, 30, 40, ?]   Hz (interpolated)
```

### 4. Statistics Generation

```
From data arrays → Calculate:
- Min, Max (frequency & magnitude)
- Average magnitude
- Standard deviation
- Data point count
Used for quality assessment
```

## Next: Machine Learning Integration

```
Enhanced Backend:
    │
    ├─ FRA Analysis (current)
    │
    ├─ + Fault Detection Model
    │   └─ RandomForestClassifier
    │       ├─ Input: FRA magnitude vector
    │       ├─ Output: Normal/Fault classification
    │       └─ Confidence: probability score
    │
    ├─ + Anomaly Detection
    │   └─ Statistical analysis
    │       ├─ Deviation from baseline
    │       ├─ Peak detection
    │       └─ Trend analysis
    │
    └─ Results displayed in UI
        ├─ Fault probability: X%
        ├─ Anomaly score: Y
        └─ Recommendations
```
