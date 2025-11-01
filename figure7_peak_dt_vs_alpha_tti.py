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
