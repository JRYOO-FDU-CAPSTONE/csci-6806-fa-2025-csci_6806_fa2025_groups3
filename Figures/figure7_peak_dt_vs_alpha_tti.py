import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import defaultdict
import re

def parse_trace_file(file_path):
    """Parse a trace file and extract relevant information."""
    print(f"Parsing trace file: {file_path}")

    data = []
    skipped_lines = 0

    with open(file_path, 'r') as f:
        for line in tqdm(f, desc=f"Reading {os.path.basename(file_path)}"):
            line = line.strip()
            if line.startswith('#') or not line:
                skipped_lines += 1
                continue

            try:
                values = line.split()
                if len(values) >= 8:  # Minimum required fields
                    entry = {
                        'block_id': int(values[0]),
                        'offset': int(values[1]),
                        'size': int(values[2]),
                        'time': float(values[3]),
                        'op': int(values[4]),
                        'pipeline': int(values[5]),
                        'namespace': int(values[6]),
                        'user': int(values[7])
                    }

                    # Add additional fields if present
                    if len(values) > 8:
                        entry['rs_shard_id'] = int(values[8])
                        if len(values) > 9:
                            entry['op_count'] = int(values[9])

                    data.append(entry)
            except Exception as e:
                print(f"Error parsing line: {line[:50]}... Error: {e}")
                skipped_lines += 1

    print(f"Loaded {len(data)} entries, skipped {skipped_lines} lines")
    return data


def calculate_metrics(trace_data, num_bins=15):
    """Calculate α_tti and peak_dt metrics from trace data."""
    print("Calculating metrics from trace data...")

    # Group requests by block_id
    block_requests = defaultdict(list)
    for entry in trace_data:
        block_id = entry['block_id']
        block_requests[block_id].append(entry)

    # Calculate metrics for each block
    alpha_tti_values = []
    peak_dt_values = []

    for block_id, requests in block_requests.items():
        if len(requests) < 2:
            continue

        # Sort requests by time
        requests.sort(key=lambda x: x['time'])

        # Calculate inter-arrival times in milliseconds for better scale
        inter_arrival_times = []
        for i in range(1, len(requests)):
            inter_arrival_times.append((requests[i]['time'] - requests[i-1]['time']) * 1000)  # Convert to ms

        if not inter_arrival_times:
            continue

        # Calculate α_tti as inverse of average inter-arrival time (normalized)
        avg_inter_arrival = np.mean(inter_arrival_times)
        alpha_tti = 1000.0 / avg_inter_arrival if avg_inter_arrival > 0 else 0  # Normalized value

        # Calculate peak_dt as 95th percentile of inter-arrival times (more robust than max)
        peak_dt = np.percentile(inter_arrival_times, 95)  # Using 95th percentile instead of max

        # Apply reasonable limits to filter outliers
        if 0 < alpha_tti < 20 and 0 < peak_dt < 10000:  # Filter extreme outliers
            alpha_tti_values.append(alpha_tti)
            peak_dt_values.append(peak_dt)

    print(f"Calculated metrics for {len(alpha_tti_values)} blocks (after filtering outliers)")

    # Bin the data for cleaner visualization
    if len(alpha_tti_values) > num_bins:
        # Create bins
        min_alpha = min(alpha_tti_values)
        max_alpha = max(alpha_tti_values)
        alpha_bins = np.linspace(min_alpha, max_alpha, num_bins)

        # Bin the data
        binned_alpha = []
        binned_peak_dt = []
        bin_counts = []

        for i in range(len(alpha_bins)-1):
            bin_start = alpha_bins[i]
            bin_end = alpha_bins[i+1]
            bin_center = (bin_start + bin_end) / 2

            # Get indices of values in this bin
            indices = np.where((np.array(alpha_tti_values) >= bin_start) &
                              (np.array(alpha_tti_values) < bin_end))[0]

            if len(indices) > 0:
                # Calculate median values for this bin (more robust than mean)
                median_peak_dt = np.median(np.array(peak_dt_values)[indices])
                binned_alpha.append(bin_center)
                binned_peak_dt.append(median_peak_dt)
                bin_counts.append(len(indices))

        print(f"Binned data into {len(binned_alpha)} bins")
        return np.array(binned_alpha), np.array(binned_peak_dt), np.array(bin_counts)
    else:
        return np.array(alpha_tti_values), np.array(peak_dt_values), np.ones(len(alpha_tti_values))


def main():
    # Define directories
    data_dir = '/home/ubuntu/Baleen-FAST24/data/storage/20230325/Region7'
    output_dir = 'runs/example/dt-slru/rejectx-1_lru_366.475GB'
    os.makedirs(output_dir, exist_ok=True)

    try:
        print("Starting data processing...")

        # Find trace files
        trace_files = glob.glob(os.path.join(data_dir, '*.trace'))

        if not trace_files:
            raise FileNotFoundError(f"No trace files found in {data_dir}")

        print(f"Found {len(trace_files)} trace files")

        # Process the first trace file
        trace_data = parse_trace_file(trace_files[0])

        # Calculate metrics from trace data
        alpha_tti_values, peak_dt_values, bin_counts = calculate_metrics(trace_data)

        # Plot the PDF graph
        plot_pdf_graph(alpha_tti_values, peak_dt_values, bin_counts, output_dir)

        print(f"PDF Figure 7 generated successfully and saved to {output_dir}")

    except Exception as e:
        print(f"Error generating Figure 7: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
