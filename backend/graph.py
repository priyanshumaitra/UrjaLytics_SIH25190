"""
FRA (Frequency Response Analysis) Graph Analysis Module

This module handles:
1. Parsing FRA CSV files with various formats (normal and fault files)
2. Extracting frequency and magnitude data
3. Comparing two FRA vectors (Normal vs Fault / Baseline vs Test)
4. Generating visualization data for the frontend
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import io


class FRAAnalyzer:
    """
    FRA (Frequency Response Analysis) Analyzer
    
    Handles parsing and comparison of FRA CSV files
    """
    
    @staticmethod
    def parse_normal_fra_csv(csv_content: str) -> np.ndarray:
        """
        Parse normal FRA CSV file format.
        Expected format: freq, RMS, Peaks, Phase (with header row)
        
        Args:
            csv_content: String content of the CSV file
            
        Returns:
            np.ndarray: Sorted magnitude values by frequency
        """
        try:
            # Read CSV from string content
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Convert all columns to numeric, replacing commas with dots for European format
            df = df.replace(',', '.', regex=True)
            df = df.apply(pd.to_numeric, errors='coerce')
            
            # Remove rows where all values are NaN
            df = df.dropna(how='all')
            
            # Identify columns - typically first is frequency, second is RMS (magnitude)
            numeric_cols = [c for c in df.columns if df[c].notna().sum() > 0]
            
            if len(numeric_cols) < 2:
                raise ValueError(
                    f"CSV must have at least 2 numeric columns (frequency and magnitude). Found: {numeric_cols}"
                )
            
            # Extract frequency and magnitude
            freq = df[numeric_cols[0]].values  # First column is frequency
            mag = df[numeric_cols[1]].values   # Second column is RMS/Magnitude
            
            # Remove NaN values
            mask = ~np.isnan(freq) & ~np.isnan(mag)
            freq = freq[mask]
            mag = mag[mask]
            
            if len(mag) == 0:
                raise ValueError("No valid data points found in CSV file")
            
            # Sort by frequency
            idx = np.argsort(freq)
            mag_sorted = mag[idx]
            
            return freq[idx], mag_sorted
            
        except Exception as e:
            raise ValueError(f"Error parsing FRA CSV: {str(e)}")
    
    @staticmethod
    def parse_fault_fra_csv(csv_content: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Parse fault FRA CSV file (semicolon-separated format).
        Expected format: Frequency, Magnitude columns
        
        Args:
            csv_content: String content of the CSV file
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (frequency, magnitude) arrays sorted by frequency
        """
        try:
            # Try semicolon separator first (European format)
            try:
                df = pd.read_csv(io.StringIO(csv_content), sep=';')
            except:
                # Fall back to comma separator
                df = pd.read_csv(io.StringIO(csv_content), sep=',')
            
            # Clean up: replace European decimal commas with dots
            df = df.replace(',', '.', regex=True)
            
            # Convert to numeric
            df_num = df.apply(pd.to_numeric, errors='coerce')
            
            # Find valid columns (at least some non-NaN values)
            valid_cols = [c for c in df_num.columns if df_num[c].notna().sum() > 10]
            
            if len(valid_cols) < 2:
                raise ValueError("Could not find sufficient numeric columns")
            
            # Heuristic: first numeric column = frequency, second = magnitude
            freq_col = valid_cols[0]
            mag_col = valid_cols[1]
            
            freq = df_num[freq_col].values
            mag = df_num[mag_col].values
            
            # Remove NaNs
            mask = ~np.isnan(freq) & ~np.isnan(mag)
            freq = freq[mask]
            mag = mag[mask]
            
            if len(mag) == 0:
                raise ValueError("No valid data points found")
            
            # Sort by frequency
            idx = np.argsort(freq)
            
            return freq[idx], mag[idx]
            
        except Exception as e:
            raise ValueError(f"Error parsing fault FRA CSV: {str(e)}")
    
    @staticmethod
    def normalize_vector_length(vectors: List[np.ndarray]) -> List[np.ndarray]:
        """
        Normalize all vectors to the same length by truncating to minimum length.
        
        Args:
            vectors: List of numpy arrays
            
        Returns:
            List of arrays all with same length
        """
        if not vectors:
            return []
        
        min_len = min(len(v) for v in vectors)
        return [v[:min_len] for v in vectors]
    
    @staticmethod
    def calculate_difference(freq: np.ndarray, mag1: np.ndarray, mag2: np.ndarray) -> np.ndarray:
        """
        Calculate the difference between two magnitude vectors.
        
        Args:
            freq: Frequency array
            mag1: First magnitude array (baseline/normal)
            mag2: Second magnitude array (test/fault)
            
        Returns:
            np.ndarray: Difference array (mag2 - mag1)
        """
        return mag2 - mag1
    
    @staticmethod
    def prepare_chart_data(
        freq: np.ndarray,
        mag1: np.ndarray,
        mag1_label: str = "File 1",
        mag2: Optional[np.ndarray] = None,
        mag2_label: str = "File 2"
    ) -> List[Dict]:
        """
        Prepare data for Recharts visualization.
        
        Args:
            freq: Frequency array
            mag1: First magnitude array
            mag1_label: Label for first magnitude
            mag2: Optional second magnitude array
            mag2_label: Label for second magnitude
            
        Returns:
            List of dictionaries with keys: frequency, magnitude, [magnitude2], index
        """
        data = []
        
        for idx, f in enumerate(freq):
            point = {
                'index': idx,
                'frequency': round(float(f), 2),
                'magnitude': round(float(mag1[idx]), 2),
            }
            
            if mag2 is not None:
                point['magnitude2'] = round(float(mag2[idx]), 2)
            
            data.append(point)
        
        return data
    
    @staticmethod
    def calculate_statistics(freq: np.ndarray, mag: np.ndarray) -> Dict:
        """
        Calculate statistics for a FRA vector.
        
        Args:
            freq: Frequency array
            mag: Magnitude array
            
        Returns:
            Dictionary with statistics
        """
        return {
            'data_points': len(mag),
            'min_freq': round(float(np.min(freq)), 2),
            'max_freq': round(float(np.max(freq)), 2),
            'min_mag': round(float(np.min(mag)), 2),
            'max_mag': round(float(np.max(mag)), 2),
            'avg_mag': round(float(np.mean(mag)), 2),
            'std_mag': round(float(np.std(mag)), 2),
        }
    
    @staticmethod
    def analyze_two_csvs(
        csv_content_1: str,
        csv_content_2: str,
        is_fault_format_1: bool = False,
        is_fault_format_2: bool = False,
        file_name_1: str = "File 1",
        file_name_2: str = "File 2"
    ) -> Dict:
        """
        Analyze two FRA CSV files and return comparison data.
        
        Args:
            csv_content_1: Content of first CSV file
            csv_content_2: Content of second CSV file
            is_fault_format_1: Whether first file is fault format (semicolon-separated)
            is_fault_format_2: Whether second file is fault format (semicolon-separated)
            file_name_1: Label for first file
            file_name_2: Label for second file
            
        Returns:
            Dictionary with:
            - chart_data: List of points for visualization
            - statistics: Stats for both files
            - difference: Difference array
            - success: True if successful
        """
        try:
            # Parse both files
            if is_fault_format_1:
                freq1, mag1 = FRAAnalyzer.parse_fault_fra_csv(csv_content_1)
            else:
                freq1, mag1 = FRAAnalyzer.parse_normal_fra_csv(csv_content_1)
            
            if is_fault_format_2:
                freq2, mag2 = FRAAnalyzer.parse_fault_fra_csv(csv_content_2)
            else:
                freq2, mag2 = FRAAnalyzer.parse_normal_fra_csv(csv_content_2)
            
            # Normalize to same frequency grid (use first file's frequency)
            # Interpolate second file's magnitude to first file's frequency grid
            if len(freq1) != len(freq2):
                mag2_interp = np.interp(freq1, freq2, mag2)
                mag2 = mag2_interp
                freq2 = freq1
            
            # Normalize vector lengths
            freq1, mag1, mag2 = FRAAnalyzer.normalize_vector_length([freq1, mag1, mag2])
            
            # Calculate difference
            difference = FRAAnalyzer.calculate_difference(freq1, mag1, mag2)
            
            # Prepare chart data
            chart_data = FRAAnalyzer.prepare_chart_data(
                freq1, mag1, file_name_1, mag2, file_name_2
            )
            
            # Calculate statistics
            stats_1 = FRAAnalyzer.calculate_statistics(freq1, mag1)
            stats_1['name'] = file_name_1
            
            stats_2 = FRAAnalyzer.calculate_statistics(freq1, mag2)
            stats_2['name'] = file_name_2
            
            diff_stats = {
                'name': f'Difference ({file_name_2} - {file_name_1})',
                'min_diff': round(float(np.min(difference)), 2),
                'max_diff': round(float(np.max(difference)), 2),
                'avg_diff': round(float(np.mean(difference)), 2),
                'std_diff': round(float(np.std(difference)), 2),
            }
            
            return {
                'success': True,
                'chart_data': chart_data,
                'statistics': [stats_1, stats_2, diff_stats],
                'difference': difference.tolist(),
                'frequencies': freq1.tolist(),
                'file1_name': file_name_1,
                'file2_name': file_name_2,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'chart_data': [],
                'statistics': [],
            }
    
    @staticmethod
    def analyze_single_csv(
        csv_content: str,
        is_fault_format: bool = False,
        file_name: str = "File 1"
    ) -> Dict:
        """
        Analyze a single FRA CSV file.
        
        Args:
            csv_content: Content of CSV file
            is_fault_format: Whether file is fault format
            file_name: Label for file
            
        Returns:
            Dictionary with chart data and statistics
        """
        try:
            # Parse file
            if is_fault_format:
                freq, mag = FRAAnalyzer.parse_fault_fra_csv(csv_content)
            else:
                freq, mag = FRAAnalyzer.parse_normal_fra_csv(csv_content)
            
            # Prepare chart data
            chart_data = FRAAnalyzer.prepare_chart_data(freq, mag, file_name)
            
            # Calculate statistics
            stats = FRAAnalyzer.calculate_statistics(freq, mag)
            stats['name'] = file_name
            
            return {
                'success': True,
                'chart_data': chart_data,
                'statistics': [stats],
                'frequencies': freq.tolist(),
                'magnitudes': mag.tolist(),
                'file_name': file_name,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'chart_data': [],
                'statistics': [],
            }
