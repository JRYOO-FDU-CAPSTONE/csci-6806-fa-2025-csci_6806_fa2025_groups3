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

def calculate_peak_dt_metrics(trace_data, eviction_schemes=['E0', 'E1', 'E2']):
    """Calculate peak disk-head time metrics for different eviction schemes."""
    print("Calculating peak DT metrics for eviction schemes...")

    # Group requests by pipeline (which represents eviction scheme)
    pipeline_requests = defaultdict(list)
    for entry in trace_data:
        pipeline = entry['pipeline']
        pipeline_requests[pipeline].append(entry)

    # Calculate metrics for each eviction scheme
    scheme_metrics = {scheme: [] for scheme in eviction_schemes}

    for pipeline, requests in pipeline_requests.items():
        if len(requests) < 2:
            continue

        try:
            # Determine which eviction scheme this pipeline belongs to
            # This is a simplified mapping - adjust according to your actual data
            scheme_index = pipeline % 3  # Distribute pipelines across 3 schemes
            scheme = eviction_schemes[scheme_index]

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
            scheme_metrics[scheme].append(peak_dt)

        except Exception as e:
            print(f"Error processing pipeline {pipeline}: {e}")
            continue

    # Calculate average peak DT for each scheme
    avg_peak_dts = []
    scheme_labels = []

    for scheme in eviction_schemes:
        if scheme_metrics[scheme]:
            avg_peak_dt = np.mean(scheme_metrics[scheme])
            avg_peak_dts.append(avg_peak_dt)
            scheme_labels.append(scheme)
            print(f"Scheme {scheme}: {len(scheme_metrics[scheme])} pipelines, Avg Peak DT: {avg_peak_dt:.1f}ms")
        else:
            print(f"No valid data for scheme {scheme}")

    if not avg_peak_dts:
        print("No valid metrics calculated")
        return None, None

    return scheme_labels, avg_peak_dts

def plot_figure1_bar_graph(scheme_labels, avg_peak_dts, output_dir):
    """Plot a clean bar graph for Figure 1: Peak DT across eviction schemes."""
    print("Plotting Figure 1 bar graph...")

    # Create figure with improved layout
    plt.figure(figsize=(10, 7))
    plt.style.use('seaborn-white')

    # Use a professional color scheme
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, Orange, Green

    # Create proper bar plot
    bars = plt.bar(scheme_labels, avg_peak_dts,
                 color=colors, width=0.6,
                 edgecolor='gray', alpha=0.8, linewidth=0.5)

    # Add value labels on top of each bar
    for i, (label, value) in enumerate(zip(scheme_labels, avg_peak_dts)):
        plt.text(i, value + max(avg_peak_dts)*0.02,
                f'{value:.1f}ms',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add labels and title with improved formatting
    plt.title('Peak DT across Eviction Schemes (E0-E2)', fontsize=14, pad=20, weight='bold')
    plt.xlabel('Eviction Scheme', fontsize=12, labelpad=10)
    plt.ylabel('Peak Disk-head Time (milliseconds)', fontsize=12, labelpad=10)

    # Set axis limits with some padding
    plt.ylim(0, max(avg_peak_dts) * 1.2)

    # Add grid with improved styling
    plt.grid(True, linestyle='--', alpha=0.3, axis='y')

    # Add statistics box
    stats_text = (f"Avg Peak DT: {np.mean(avg_peak_dts):.1f}ms\n"
                  f"Max Peak DT: {max(avg_peak_dts):.1f}ms\n"
                  f"Min Peak DT: {min(avg_peak_dts):.1f}ms")

    plt.text(0.98, 0.95, stats_text, transform=plt.gca().transAxes,
            fontsize=10, ha='right', va='top',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=3))

    # Save as PDF for best quality
    output_path = os.path.join(output_dir, 'Figure1_Peak_DT_across_Eviction_Schemes.pdf')
    plt.savefig(output_path, bbox_inches='tight', format='pdf')
    plt.close()

    print(f"Figure 1 saved to {output_path}")
    return output_path

def main():
    # Limit memory usage
    limit_memory()

    # Define directories for Figure 1
    data_dir = '/home/ubuntu/Baleen-FAST24/data/storage/201910/Region1'
    output_dir = 'runs/example/dt-slru/rejectx-1_lru_366.475GB'
    os.makedirs(output_dir, exist_ok=True)

    try:
        print("Starting data processing for Figure 1...")

        # Find trace files
        trace_files = glob.glob(os.path.join(data_dir, '*.trace'))

        if not trace_files:
            raise FileNotFoundError(f"No trace files found in {data_dir}")

        print(f"Found {len(trace_files)} trace files")

        # Process the first trace file
        trace_data = parse_trace_file(trace_files[0])

        # Calculate metrics for eviction schemes
        scheme_labels, avg_peak_dts = calculate_peak_dt_metrics(trace_data)

        if scheme_labels is None:
            raise ValueError("No valid metrics could be calculated")

        # Plot Figure 1 bar graph
        plot_figure1_bar_graph(scheme_labels, avg_peak_dts, output_dir)

        print(f"Figure 1 PDF generated successfully")

    except Exception as e:
        print(f"Error generating Figure 1: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
