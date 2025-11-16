import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import defaultdict
import resource

def limit_memory():
    """Limit memory usage to prevent crashes"""
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (min(2*1024*1024*1024, soft), hard))  # Limit to 2GB
    except:
        print("Could not set memory limits")

def parse_trace_file(file_path, max_entries=50000):
    """Parse a trace file with memory efficiency."""
    print(f"Parsing trace file: {file_path}")

    data = []
    skipped_lines = 0
    entry_count = 0

    with open(file_path, 'r') as f:
        for line in tqdm(f, desc=f"Reading {os.path.basename(file_path)}"):
            if entry_count >= max_entries:
                break

            line = line.strip()
            if line.startswith('#') or not line:
                skipped_lines += 1
                continue

            try:
                values = line.split()
                if len(values) >= 8:
                    entry = {
                        'block_id': int(values[0]),
                        'size': int(values[2]),
                        'time': float(values[3]),
                        'op': int(values[4])
                    }
                    data.append(entry)
                    entry_count += 1
            except Exception as e:
                print(f"Error parsing line: {line[:50]}... Error: {e}")
                skipped_lines += 1

    print(f"Loaded {len(data)} entries, skipped {skipped_lines} lines")
    return data

def analyze_cache_sizes(trace_data):
    """Analyze available cache sizes in the data."""
    print("Analyzing cache sizes in data...")

    # Group requests by block size
    block_size_requests = defaultdict(list)
    for entry in trace_data:
        block_size = entry['size'] / (1024 * 1024)  # Convert to MB
        block_size_requests[block_size].append(entry)

    # Get all unique cache sizes and sort them
    unique_sizes = sorted(block_size_requests.keys())
    print(f"Found {len(unique_sizes)} unique cache sizes in data")

    # Select the most common cache sizes (top 8 by number of requests)
    size_counts = []
    for size in unique_sizes:
        size_counts.append((size, len(block_size_requests[size])))

    # Sort by count of requests (descending)
    size_counts.sort(key=lambda x: x[1], reverse=True)

    # Select top 8 cache sizes
    selected_sizes = [size for size, count in size_counts[:8]]
    print(f"Selected top 8 cache sizes: {selected_sizes}")

    return selected_sizes, block_size_requests


def main():
    # Limit memory usage
    limit_memory()

    # Define directories for Figure 4
    data_dir = '/home/ubuntu/Baleen-FAST24/data/storage/202110/Region4'
    output_dir = 'runs/example/dt-slru/rejectx-1_lru_366.475GB'
    os.makedirs(output_dir, exist_ok=True)

    try:
        print("Starting data processing for Figure 4...")

        # Find trace files
        trace_files = glob.glob(os.path.join(data_dir, '*.trace'))

        if not trace_files:
            raise FileNotFoundError(f"No trace files found in {data_dir}")

        print(f"Found {len(trace_files)} trace files")

        # Process the first trace file
        trace_data = parse_trace_file(trace_files[0])

        # Analyze cache sizes and select top 8
        selected_sizes, block_size_requests = analyze_cache_sizes(trace_data)

        # Calculate metrics for selected cache sizes
        cache_sizes, peak_values = calculate_metrics(block_size_requests, selected_sizes)

        if cache_sizes is None:
            raise ValueError("No valid metrics could be calculated")

        # Plot Figure 4 with proper value labels
        plot_figure4(cache_sizes, peak_values, output_dir)

        print(f"Figure 4 PDF generated successfully")

    except Exception as e:
        print(f"Error generating Figure 4: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
