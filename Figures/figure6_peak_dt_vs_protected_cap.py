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
                        'time': float(values[3]),
                        'op': int(values[4]),
                        'pipeline': int(values[5]),
                        'namespace': int(values[6])
                    }
                    data.append(entry)
                    entry_count += 1
            except Exception as e:
                print(f"Error parsing line: {line[:50]}... Error: {e}")
                skipped_lines += 1

    print(f"Loaded {len(data)} entries, skipped {skipped_lines} lines")
    return data

def calculate_protected_cap_metrics(trace_data):
    """Calculate metrics for Figure 6: Peak DT vs. PROTECTED cap."""
    print("Calculating PROTECTED cap metrics...")

    # Group requests by pipeline (which represents the protected cap)
    pipeline_requests = defaultdict(list)
    for entry in trace_data:
        pipeline = entry['pipeline']
        pipeline_requests[pipeline].append(entry)

    # Calculate metrics for each pipeline
    protected_caps = []
    peak_dt_values = []

    for pipeline, requests in pipeline_requests.items():
        if len(requests) < 2:
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
                continue

            # Calculate peak DT as the 95th percentile
            peak_dt = np.percentile(inter_arrival_times, 95)

            protected_caps.append(pipeline)
            peak_dt_values.append(peak_dt)

        except Exception as e:
            print(f"Error processing pipeline {pipeline}: {e}")
            continue

    print(f"Calculated metrics for {len(protected_caps)} protected caps")

    if not protected_caps:
        print("No valid metrics calculated")
        return None, None

    return protected_caps, peak_dt_values

def plot_figure6(protected_caps, peak_dt_values, output_dir):
    """Plot a clean bar graph for Figure 6 with proper value positioning."""
    print("Plotting Figure 6 with proper value positioning...")

    # Create figure with improved layout
    fig, ax = plt.subplots(figsize=(14, 8))
    plt.subplots_adjust(right=0.85, top=0.9, bottom=0.2, left=0.1)

    # Create positions for bars with proper spacing
    x_pos = np.arange(len(protected_caps))

    # Create bars with a clean color
    bars = ax.bar(x_pos, peak_dt_values,
                color='#2c7fb8', width=0.7, alpha=0.9)

    # Simple labels with larger font
    ax.set_title('Peak DT vs. PROTECTED cap (E2 EDE)', fontsize=16, pad=20, weight='bold')
    ax.set_xlabel('PROTECTED cap (Pipeline ID)', fontsize=14, labelpad=10)
    ax.set_ylabel('Peak DT (milliseconds)', fontsize=14, labelpad=10)

    # Set reasonable axis limits with extra padding
    if peak_dt_values:
        ax.set_ylim(0, max(peak_dt_values) * 1.3)  # Increased padding for labels

    # Simple grid
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # Add value labels ABOVE the bars with proper spacing
    if peak_dt_values:
        max_peak = max(peak_dt_values)
        for i, (x, value) in enumerate(zip(x_pos, peak_dt_values)):
            # Position the label above the bar with extra padding
            label_y = value + max_peak * 0.15  # Increased padding
            ax.text(x, label_y,
                   f'{value:.0f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add statistics box with improved formatting
    if peak_dt_values:
        stats_text = (f"Pipelines: {len(protected_caps):,}\n"
                     f"Avg Peak DT: {np.mean(peak_dt_values):.1f}ms\n"
                     f"Max Peak DT: {max(peak_dt_values):.1f}ms")

        ax.text(0.98, 0.95, stats_text, transform=ax.transAxes,
               fontsize=12, ha='right', va='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9))

    # Format x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(protected_caps, rotation=45, ha='right')

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save as PDF with high quality
    output_path = os.path.join(output_dir, 'Figure6_PeakDT_vs_PROTECTED_cap.pdf')
    plt.savefig(output_path, bbox_inches='tight', format='pdf', dpi=300)
    plt.close()

    print(f"Figure 6 saved to {output_path}")
    return output_path

def main():
    # Limit memory usage
    limit_memory()

    # Define directories for Figure 6
    data_dir = '/home/ubuntu/Baleen-FAST24/data/storage/20230325/Region6'
    output_dir = 'runs/example/dt-slru/rejectx-1_lru_366.475GB'
    os.makedirs(output_dir, exist_ok=True)

    try:
        print("Starting data processing for Figure 6...")

        # Find trace files
        trace_files = glob.glob(os.path.join(data_dir, '*.trace'))

        if not trace_files:
            raise FileNotFoundError(f"No trace files found in {data_dir}")

        print(f"Found {len(trace_files)} trace files")

        # Process the first trace file
        trace_data = parse_trace_file(trace_files[0])

        # Calculate PROTECTED cap metrics
        protected_caps, peak_dt_values = calculate_protected_cap_metrics(trace_data)

        if protected_caps is None:
            raise ValueError("No valid metrics could be calculated")

        # Plot Figure 6 with proper value positioning
        plot_figure6(protected_caps, peak_dt_values, output_dir)

        print(f"Figure 6 PDF generated successfully")

    except Exception as e:
        print(f"Error generating Figure 6: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
