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

def calculate_metrics(block_size_requests, selected_sizes):
    """Calculate metrics for selected cache sizes."""
    print("Calculating metrics for selected cache sizes...")

    cache_sizes = []
    peak_dt_values = []

    for size in selected_sizes:
        requests = block_size_requests[size]
        if len(requests) < 2:
            print(f"Not enough requests for cache size {size} MB")
            continue

        try:
            # Sort requests by time
            requests.sort(key=lambda x: x['time'])

            # Calculate inter-arrival times
            inter_arrival_times = []
            for i in range(1, len(requests)):
                delta = (requests[i]['time'] - requests[i-1]['time']) * 1000  # Convert to ms
                if 0 < delta < 20000:
                    inter_arrival_times.append(delta)

            if not inter_arrival_times:
                print(f"No valid inter-arrival times for cache size {size} MB")
                continue

            # Calculate peak DT as the 95th percentile
            peak_dt = np.percentile(inter_arrival_times, 95)
            cache_sizes.append(size)
            peak_dt_values.append(peak_dt)
            print(f"Cache size {size} MB: Peak DT = {peak_dt:.1f}ms")

        except Exception as e:
            print(f"Error processing cache size {size} MB: {e}")
            continue

    if not cache_sizes:
        print("No valid metrics calculated")
        return None, None

    return cache_sizes, peak_dt_values

def plot_figure4(cache_sizes, peak_values, output_dir):
    """Plot a clean bar graph for Figure 4 with proper value label positioning."""
    print("Plotting Figure 4 with proper value labels...")

    # Create figure with improved layout
    fig, ax = plt.subplots(figsize=(14, 8))
    plt.subplots_adjust(right=0.85, top=0.9, bottom=0.2, left=0.1)

    # Create positions for bars with proper spacing
    x_pos = np.arange(len(cache_sizes))

    # Create bars with a clean color
    bars = ax.bar(x_pos, peak_values,
                color='#2c7fb8', width=0.7, alpha=0.9)

    # Simple labels with larger font
    ax.set_title('Peak DT vs. Cache Size (LRU vs. best scheme)', fontsize=16, pad=20, weight='bold')
    ax.set_xlabel('Cache Size (MB)', fontsize=14, labelpad=10)
    ax.set_ylabel('Peak DT (milliseconds)', fontsize=14, labelpad=10)

    # Set reasonable axis limits with extra padding
    if peak_values:
        ax.set_ylim(0, max(peak_values) * 1.4)  # Increased padding for labels

    # Simple grid
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # Add value labels ABOVE the bars with proper spacing
    if peak_values:
        max_peak = max(peak_values)
        for i, (x, value) in enumerate(zip(x_pos, peak_values)):
            # Position the label above the bar with extra padding
            label_y = value + max_peak * 0.15  # Increased padding
            ax.text(x, label_y,
                   f'{value:.0f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add statistics box with improved formatting
    if peak_values:
        stats_text = (f"Cache Sizes: {len(cache_sizes):,}\n"
                     f"Avg Peak DT: {np.mean(peak_values):.1f}ms\n"
                     f"Max Peak DT: {max(peak_values):.1f}ms")

        ax.text(0.98, 0.95, stats_text, transform=ax.transAxes,
               fontsize=12, ha='right', va='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9))

    # Format x-axis labels with proper spacing
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f"{x:.1f}" for x in cache_sizes], rotation=45, ha='right')

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save as PDF with high quality
    output_path = os.path.join(output_dir, 'Figure4_PeakDT_vs_CacheSize.pdf')
    plt.savefig(output_path, bbox_inches='tight', format='pdf', dpi=300)
    plt.close()

    print(f"Figure 4 saved to {output_path}")
    return output_path

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
