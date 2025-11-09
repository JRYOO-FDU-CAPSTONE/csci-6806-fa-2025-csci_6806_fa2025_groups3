import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import defaultdict
from scipy.ndimage import gaussian_filter1d

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
                        'op': int(values[4]),
                        'pipeline': int(values[5]),
                        'namespace': int(values[6]),
                        'user': int(values[7])
                    }
                    data.append(entry)
                    entry_count += 1
            except Exception as e:
                print(f"Error parsing line: {line[:50]}... Error: {e}")
                skipped_lines += 1

    print(f"Loaded {len(data)} entries, skipped {skipped_lines} lines")
    return data

def calculate_median_dt_metrics(trace_data, time_window=300):
    """Calculate median disk-head time metrics from trace data."""
    print("Calculating median DT metrics...")

    # Sort all requests by time
    all_requests = sorted(trace_data, key=lambda x: x['time'])
    if not all_requests:
        return [], [], []

    # Determine time range
    min_time = all_requests[0]['time']
    max_time = all_requests[-1]['time']

    # Create time bins
    time_bins = np.arange(min_time, max_time + time_window, time_window)

    # Calculate metrics for each time window
    timestamps = []
    median_disk_head_times = []
    request_counts = []

    for i in range(len(time_bins)-1):
        start_time = time_bins[i]
        end_time = time_bins[i+1]

        # Get requests in this time window
        window_requests = [r for r in all_requests if start_time <= r['time'] < end_time]
        if not window_requests:
            continue

        # Group by block_id to calculate inter-arrival times
        block_requests = defaultdict(list)
        for req in window_requests:
            block_requests[req['block_id']].append(req)

        # Calculate median disk-head time for this window
        inter_arrival_times = []
        for block_id, requests in block_requests.items():
            if len(requests) < 2:
                continue

            # Sort requests by time
            requests.sort(key=lambda x: x['time'])

            # Calculate inter-arrival times
            for j in range(1, len(requests)):
                inter_arrival_times.append((requests[j]['time'] - requests[j-1]['time']) * 1000)  # Convert to ms

        if inter_arrival_times:
            # Use median as representative disk-head time
            median_dt = np.median(inter_arrival_times)
            timestamps.append((start_time + end_time) / 2)
            median_disk_head_times.append(median_dt)
            request_counts.append(len(window_requests))

    print(f"Calculated {len(timestamps)} time windows")

    # Apply smoothing to reduce noise
    if len(median_disk_head_times) > 10:
        median_disk_head_times = gaussian_filter1d(median_disk_head_times, sigma=2)
        request_counts = gaussian_filter1d(request_counts, sigma=2)

    return timestamps, median_disk_head_times, request_counts

def plot_clean_line_graph(timestamps, median_disk_head_times, request_counts, output_dir):
    """Plot a clean line graph for Figure 2: Median DT across eviction schemes."""
    print("Plotting clean line graph...")

    # Create figure with improved layout
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Convert timestamps to minutes since start for better x-axis
    start_time = timestamps[0]
    relative_times = [(t - start_time)/60 for t in timestamps]  # Convert to minutes

    # Plot median disk-head time
    line1 = ax1.plot(relative_times, median_disk_head_times,
                    color='#1f77b4', linewidth=2, alpha=0.8,
                    label='Median Disk-head Time')

    # Highlight the minimum point
    min_index = np.argmin(median_disk_head_times)
    min_time = relative_times[min_index]
    min_value = median_disk_head_times[min_index]

    ax1.scatter([min_time], [min_value], color='#d62728', s=80,
               edgecolor='black', linewidth=1, zorder=5,
               label=f'Minimum: {min_value:.1f}ms')

    # Add a vertical line at the minimum point
    ax1.axvline(x=min_time, color='#d62728', linestyle='--', linewidth=1, alpha=0.5)

    # Set labels and title with improved formatting
    ax1.set_title('Median DT across Eviction Schemes (E0-E2)', fontsize=14, pad=20, weight='bold')
    ax1.set_xlabel('Time (minutes)', fontsize=12, labelpad=10)
    ax1.set_ylabel('Median Disk-head Time (ms)', fontsize=12, labelpad=10, color='#1f77b4')

    # Set axis limits with some padding
    ax1.set_xlim(0, max(relative_times) * 1.01)
    ax1.set_ylim(0, max(median_disk_head_times) * 1.1)

    # Add grid with improved styling
    ax1.grid(True, linestyle='--', alpha=0.3)

    # Create secondary axis for request count
    ax2 = ax1.twinx()
    line2 = ax2.plot(relative_times, request_counts, color='#ff7f0e',
                    linestyle='-', linewidth=1.5, alpha=0.7,
                    label='Request Count')

    ax2.set_ylabel('Request Count', fontsize=12, labelpad=10, color='#ff7f0e')

    # Adjust y-axis limits for secondary axis
    ax2.set_ylim(0, max(request_counts) * 1.1)

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper right', framealpha=1, fontsize=10)

    # Add annotation for the minimum point
    ax1.text(min_time, min_value + max(median_disk_head_times)*0.05,
            f'Min: {min_value:.1f}ms',
            ha='center', va='bottom', fontsize=10, weight='bold',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=3))

    # Add a subtle background to highlight the minimum region
    min_region_width = 10  # minutes
    ax1.axvspan(min_time - min_region_width/2, min_time + min_region_width/2,
               color='#e6f3ff', alpha=0.3)

    # Add statistics box
    stats_text = (f"Time Windows: {len(timestamps):,}\n"
                  f"Avg Median DT: {np.mean(median_disk_head_times):.1f}ms\n"
                  f"Min Median DT: {min_value:.1f}ms")

    ax1.text(0.98, 0.95, stats_text, transform=ax1.transAxes,
            fontsize=10, ha='right', va='top',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=3))

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save as PDF with high quality
    output_path = os.path.join(output_dir, 'Figure2_Median_DT_across_Eviction_Schemes.pdf')
    plt.savefig(output_path, bbox_inches='tight', format='pdf', dpi=300)
    plt.close()

    print(f"Clean line graph saved to {output_path}")
    return output_path

def main():
    # Define directories for Figure 2
    data_dir = '/home/ubuntu/Baleen-FAST24/data/storage/201910/Region2'
    output_dir = 'runs/example/dt-slru/rejectx-1_lru_366.475GB'
    os.makedirs(output_dir, exist_ok=True)

    try:
        print("Starting data processing for Figure 2...")

        # Find trace files
        trace_files = glob.glob(os.path.join(data_dir, '*.trace'))

        if not trace_files:
            raise FileNotFoundError(f"No trace files found in {data_dir}")

        print(f"Found {len(trace_files)} trace files")

        # Process the first trace file
        trace_data = parse_trace_file(trace_files[0])

        # Calculate median DT metrics
        timestamps, median_disk_head_times, request_counts = calculate_median_dt_metrics(trace_data)

        if not timestamps:
            raise ValueError("No valid time windows found in the data")

        # Plot clean line graph
        plot_clean_line_graph(timestamps, median_disk_head_times, request_counts, output_dir)

        print(f"Figure 2 PDF generated successfully")

    except Exception as e:
        print(f"Error generating Figure 2: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
