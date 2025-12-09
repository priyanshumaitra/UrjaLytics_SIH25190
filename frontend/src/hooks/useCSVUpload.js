import { useState } from "react";

/**
 * Custom hook for handling CSV file uploads
 * Integrates with backend FRA analysis API at /api/fra/analyze
 * Supports up to 2 CSV files
 * Backend handles parsing, frequency/magnitude detection, and comparison
 */
export const useCSVUpload = () => {
  const [csvFiles, setCsvFiles] = useState([]);
  const [csvData, setCsvData] = useState([]);
  const [statistics, setStatistics] = useState([]);
  const [zoomRange, setZoomRange] = useState([null, null]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);

  /**
   * Send CSV files to backend for FRA analysis
   * Backend returns chart-ready data with frequency/magnitude pairs
   */
  const sendToBackend = async (files) => {
    setIsAnalyzing(true);
    setAnalysisError(null);

    try {
      const formData = new FormData();

      // Add files to form data
      files.forEach((file, index) => {
        formData.append(`file${index + 1}`, file);
      });

      // Detect if files are fault format (optional enhancement)
      // For now, assume normal CSV format
      // In future: can detect by filename patterns like "Failed", "Fault", etc.

      // Call backend API
      const response = await fetch("/api/fra/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(
          `Backend error: ${response.status} ${response.statusText}`
        );
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || "Unknown error from backend");
      }

      // Transform backend response to frontend format
      // Backend returns chart_data with: index, frequency, magnitude, [magnitude2]
      const transformedData = result.chart_data.map((point) => ({
        frequency: point.frequency,
        magnitude: point.magnitude,
        source: result.file1_name || "File 1",
        ...(point.magnitude2 && { magnitude2: point.magnitude2 }),
      }));

      // Add data from second file if available
      if (result.chart_data[0].magnitude2) {
        transformedData.forEach((point, idx) => {
          if (result.chart_data[idx].magnitude2) {
            // Create entries for the second file
            transformedData.push({
              frequency: point.frequency,
              magnitude: result.chart_data[idx].magnitude2,
              source: result.file2_name || "File 2",
            });
          }
        });
      }

      setCsvData(transformedData);
      setStatistics(result.statistics || []);

      return result;
    } catch (error) {
      console.error("Error analyzing CSV files:", error);
      setAnalysisError(error.message);
      setCsvData([]);
      setStatistics([]);
      alert(`Error analyzing CSV files: ${error.message}`);
      throw error;
    } finally {
      setIsAnalyzing(false);
    }
  };

  /**
   * Handle multiple CSV file uploads
   * Validates max 2 files, then sends to backend for analysis
   */
  const handleCSVUpload = async (e) => {
    const files = Array.from(e.target.files || []);

    if (files.length === 0) return;

    const totalFiles = csvFiles.length + files.length;
    if (totalFiles > 2) {
      alert(
        "Maximum 2 CSV files allowed. Please remove one before adding another."
      );
      return;
    }

    try {
      // Add to file list
      const newCsvFiles = [...csvFiles, ...files];
      setCsvFiles(newCsvFiles);

      // Send to backend for analysis
      await sendToBackend(newCsvFiles);
    } catch (error) {
      // Revert file list on error
      setCsvFiles(csvFiles);
    }
  };

  /**
   * Remove a CSV file by index
   * Re-analyze remaining files
   */
  const removeCSVFile = (index) => {
    const newFiles = csvFiles.filter((_, i) => i !== index);
    setCsvFiles(newFiles);

    if (newFiles.length > 0) {
      // Re-analyze with remaining files
      sendToBackend(newFiles);
    } else {
      // Clear all data
      setCsvData([]);
      setStatistics([]);
      setZoomRange([null, null]);
    }
  };

  /**
   * Reset zoom to show full data range
   */
  const resetZoom = () => {
    setZoomRange([null, null]);
  };

  return {
    csvFiles,
    csvData,
    statistics,
    zoomRange,
    isAnalyzing,
    analysisError,
    handleCSVUpload,
    removeCSVFile,
    resetZoom,
    sendToBackend,
  };
};
