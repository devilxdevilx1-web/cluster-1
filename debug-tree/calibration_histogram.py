"""
calibration_histogram.py
Visualizes the confidence distribution of the Debug Tree engine.
"""
import numpy as np

def print_histogram(confidences):
    print("\n--- CONFIDENCE DISTRIBUTION ---")
    bins = [0, 20, 40, 60, 80, 100]
    labels = ["Weak (0-20)", "Low (20-40)", "Partial (40-60)", "Success (60-80)", "Absolute (80+)"]
    
    counts = np.histogram(confidences, bins=bins)[0]
    for i in range(len(labels)):
        bar = "#" * int(counts[i] * 5)
        print(f"{labels[i]:<20} | {bar} ({counts[i]})")

if __name__ == "__main__":
    # Sample distribution based on target calibration
    # Structural Success: 60-80%
    # Partial: 30-60%
    # Weak Signals: 10-30%
    sample = [75, 78, 62, 65, 45, 50, 55, 35, 25, 15]
    print_histogram(sample)
