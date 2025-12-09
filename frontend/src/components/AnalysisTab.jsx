import React from "react";
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Download, BarChart3, TrendingUp, AlertCircle } from "lucide-react";

/**
 * AnalysisTab Component
 * Displays FRA (Frequency Response Analysis) data visualization
 * Data comes from backend API at /api/fra/analyze
 * Shows comparison of up to 2 CSV files with statistics
 */
const AnalysisTab = ({
  csvFiles = [],
  csvData = [],
  statistics = [],
  chartHeight,
  setChartHeight,
  analysisError = null,
  isAnalyzing = false,
}) => {
  const color = ["#3B82F6", "#EF4444", "#10B981"];

  // Prepare chart data from backend response
  const processChartData = () => {
    if (!csvData || csvData.length === 0) return [];

    // Backend already returns chart-ready data
    // Just need to map it to recharts format with index
    const freqMap = new Map();

    csvData.forEach((d) => {
      if (!d || typeof d.frequency !== "number") return;

      const freq = parseFloat(d.frequency.toFixed(2));

      if (!freqMap.has(freq)) {
        freqMap.set(freq, { frequency: freq });
      }

      const entry = freqMap.get(freq);
      const source = d.source || "Unknown";

      // Store magnitude by source
      if (source === csvFiles[0]?.name || source === "File 1") {
        entry.magnitude = parseFloat(d.magnitude.toFixed(2));
      } else if (source === csvFiles[1]?.name || source === "File 2") {
        entry.magnitude2 = parseFloat(d.magnitude.toFixed(2));
      }
    });

    // Convert to array and add index for X-axis
    return Array.from(freqMap.values())
      .sort((a, b) => a.frequency - b.frequency)
      .map((entry, index) => ({
        ...entry,
        index: index,
      }));
  };

  const chartData = processChartData();
  const hasValidData = chartData && chartData.length > 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Main Chart */}
      <div className="lg:col-span-3">
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-800">FRA Analysis</h2>
            </div>
            {hasValidData && (
              <button
                onClick={() => {
                  // Export chart as image
                  const svg = document.querySelector("svg");
                  if (svg) {
                    const url = URL.createObjectURL(
                      new Blob([new XMLSerializer().serializeToString(svg)], {
                        type: "image/svg+xml",
                      })
                    );
                    const link = document.createElement("a");
                    link.href = url;
                    link.download = "fra-analysis.svg";
                    link.click();
                  }
                }}
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
                title="Export chart"
              >
                <Download className="w-5 h-5 text-gray-600" />
              </button>
            )}
          </div>

          {analysisError && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-700">{analysisError}</p>
            </div>
          )}

          {isAnalyzing && (
            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-700">
                Analyzing CSV files... Please wait
              </p>
            </div>
          )}

          {hasValidData && chartData.length > 0 ? (
            <>
              {/* Height Control */}
              <div className="mb-4 flex items-center gap-3">
                <label className="text-sm font-medium text-gray-700">
                  Chart Height:
                </label>
                <input
                  type="range"
                  min="300"
                  max="700"
                  step="50"
                  value={chartHeight || 420}
                  onChange={(e) => setChartHeight(Number(e.target.value))}
                  className="flex-1"
                />
                <span className="text-sm text-gray-600">
                  {chartHeight || 420}px
                </span>
              </div>

              {/* Chart */}
              <div className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
                <ResponsiveContainer width="100%" height={chartHeight || 420}>
                  <ComposedChart
                    data={chartData}
                    margin={{ top: 10, right: 80, left: 50, bottom: 60 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis
                      dataKey="index"
                      type="number"
                      label={{
                        value: "Frequency (Hz)",
                        position: "insideBottomRight",
                        offset: -5,
                      }}
                      stroke="#6B7280"
                      style={{ fontSize: "12px" }}
                      tickFormatter={(index) => {
                        if (chartData && chartData[index]) {
                          const freq = chartData[index].frequency;
                          return freq >= 1000000
                            ? `${(freq / 1000000).toFixed(1)}M`
                            : freq >= 1000
                            ? `${(freq / 1000).toFixed(0)}k`
                            : Math.floor(freq).toString();
                        }
                        return index.toString();
                      }}
                    />
                    {/* Left Y-axis for first file */}
                    <YAxis
                      yAxisId="left"
                      label={{
                        value:
                          csvFiles.length > 0
                            ? csvFiles[0].name?.replace(".csv", "")
                            : "File 1 (dB)",
                        angle: -90,
                        position: "insideLeft",
                      }}
                      stroke="#3B82F6"
                      style={{ fontSize: "12px" }}
                    />
                    {/* Right Y-axis for second file (if available) */}
                    {csvFiles.length > 1 && (
                      <YAxis
                        yAxisId="right"
                        orientation="right"
                        label={{
                          value: csvFiles[1].name?.replace(".csv", ""),
                          angle: 90,
                          position: "insideRight",
                        }}
                        stroke="#EF4444"
                        style={{ fontSize: "12px" }}
                      />
                    )}
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#FFFFFF",
                        border: "1px solid #E5E7EB",
                        borderRadius: "8px",
                      }}
                      formatter={(value) => [
                        typeof value === "number" ? value.toFixed(2) : value,
                        "",
                      ]}
                      labelFormatter={(index) => {
                        if (chartData && chartData[index]) {
                          return `Frequency: ${chartData[index].frequency} Hz`;
                        }
                        return `Point ${index}`;
                      }}
                    />
                    <Legend
                      wrapperStyle={{ paddingTop: "20px" }}
                      iconType="line"
                    />

                    {/* Render line for first file */}
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="magnitude"
                      data={chartData}
                      stroke="#3B82F6"
                      strokeWidth={2}
                      name={
                        csvFiles.length > 0
                          ? csvFiles[0].name?.replace(".csv", "")
                          : "File 1"
                      }
                      isAnimationActive={false}
                      dot={false}
                    />

                    {/* Second file if available */}
                    {csvFiles.length > 1 && (
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="magnitude2"
                        data={chartData}
                        stroke="#EF4444"
                        strokeWidth={2}
                        name={
                          csvFiles[1]?.name?.replace(".csv", "") || "File 2"
                        }
                        isAnimationActive={false}
                        dot={false}
                      />
                    )}
                  </ComposedChart>
                </ResponsiveContainer>
              </div>

              {/* Action Buttons */}
              <div className="mt-4 flex gap-3">
                <button
                  onClick={() => {
                    // Generate report
                    const reportText = `
FRA Analysis Report
===================
Generated: ${new Date().toLocaleString()}

Files Analyzed: ${csvFiles.map((f) => f.name).join(", ")}

Statistics:
${statistics
  .map(
    (s) => `
${s.name}:
  - Data Points: ${s.data_points}
  - Frequency Range: ${s.min_freq} - ${s.max_freq} Hz
  - Magnitude Range: ${s.min_mag} - ${s.max_mag} dB
  - Avg Magnitude: ${s.avg_mag} dB
  - Std Deviation: ${s.std_mag || "N/A"} dB
`
  )
  .join("\n")}
                    `;
                    const blob = new Blob([reportText], { type: "text/plain" });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement("a");
                    link.href = url;
                    link.download = "fra-report.txt";
                    link.click();
                  }}
                  className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-all text-sm"
                >
                  📄 Generate Report
                </button>
              </div>
            </>
          ) : (
            <div className="h-96 flex items-center justify-center text-center">
              <div>
                <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 font-medium">No data to display</p>
                <p className="text-sm text-gray-400">
                  Upload CSV files with frequency and magnitude columns to see
                  analysis
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right Sidebar: Statistics */}
      <aside className="lg:col-span-1">
        <div className="bg-white rounded-2xl shadow-md p-4 border border-gray-100 h-fit sticky top-4">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-800">Statistics</h3>
          </div>

          {statistics.length > 0 ? (
            <div className="space-y-4">
              {statistics.map((stat, idx) => (
                <div
                  key={stat.name || idx}
                  className="p-3 rounded-lg border-l-4"
                  style={{
                    borderLeftColor: color[idx % color.length],
                    backgroundColor: color[idx % color.length] + "15",
                  }}
                >
                  <div className="font-semibold text-sm text-gray-800 truncate mb-2">
                    {stat.name?.replace(".csv", "")}
                  </div>

                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Points:</span>
                      <span className="font-medium text-gray-800">
                        {stat.data_points}
                      </span>
                    </div>
                    {stat.min_freq !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Freq Range:</span>
                        <span className="font-medium text-gray-800">
                          {stat.min_freq} - {stat.max_freq} Hz
                        </span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-gray-600">Mag Range:</span>
                      <span className="font-medium text-gray-800">
                        {stat.min_mag} - {stat.max_mag} dB
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Avg Mag:</span>
                      <span className="font-medium text-gray-800">
                        {stat.avg_mag} dB
                      </span>
                    </div>
                    {stat.std_mag !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Std Dev:</span>
                        <span className="font-medium text-gray-800">
                          {stat.std_mag} dB
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-sm text-gray-500 mb-2">No data loaded</div>
              <div className="text-xs text-gray-400">
                Statistics will appear after analysis
              </div>
            </div>
          )}
        </div>
      </aside>
    </div>
  );
};

export default AnalysisTab;
