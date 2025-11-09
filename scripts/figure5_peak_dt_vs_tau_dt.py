import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import resource
import gc

def limit_memory():
    """Limit memory usage to prevent crashes"""
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (min(1*1024*1024*1024, soft), hard))  # Limit to 1GB
    except:
        print("Could not set memory limits")

def parse_trace_file(file_path, max_entries=20000):
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
                        'op': int(values[4])
                    }
                    data.append(entry)
                    entry_count += 1
            except Exception as e:
                print(f"Error parsing line: {line[:50]}... Error: {e}")
                skipped_lines += 1

    print(f"Loaded {len(data)} entries, skipped {skipped_lines} lines")
    return data

def process_single_block(block_id, requests):
    """Process a single block to calculate metrics."""
    try:
        if len(requests) < 2:
            return None

        # Sort requests by time
        requests.sort(key=lambda x: x['time'])

        # Calculate inter-arrival times
        inter_arrival_times = []
        for i in range(1, min(20, len(requests))):  # Limit to first 20 requests
            delta = (requests[i]['time'] - requests[i-1]['time']) * 1000  # Convert to ms
            if 0 < delta < 20000:
                inter_arrival_times.append(delta)

        if not inter_arrival_times:
            return None

        # Calculate τ (tau) as the average inter-arrival time
        tau = np.mean(inter_arrival_times)

        # Calculate peak DT as the 95th percentile
        peak_dt = np.percentile(inter_arrival_times, 95)

        return (tau, peak_dt)

    except Exception as e:
        return None

def calculate_metrics(trace_data):
    """Calculate metrics with minimal memory usage."""
    print("Calculating metrics...")

    # Group requests by block_id using a dictionary
    block_requests = {}
    for entry in trace_data:
        block_id = entry['block_id']
        if block_id not in block_requests:
            block_requests[block_id] = []
        block_requests[block_id].append(entry)

    print(f"Found {len(block_requests)} unique blocks")

    # Process blocks one at a time
    tau_values = []
    peak_dt_values = []

    for i, (block_id, requests) in enumerate(tqdm(block_requests.items(), desc="Processing blocks")):
        result = process_single_block(block_id, requests)
        if result:
            tau, peak_dt = result
            tau_values.append(tau)
            peak_dt_values.append(peak_dt)

        # Free memory periodically
        if i % 1000 == 0:
            gc.collect()

    print(f"Calculated metrics for {len(tau_values)} blocks")

    if not tau_values:
        print("No valid metrics calculated")
        return None, None

    return tau_values, peak_dt_values

def calculate_binned_metrics(tau_values, peak_dt_values, num_bins=15):
    """Calculate binned metrics for line graph."""
    print("Calculating binned metrics...")

    # Convert to numpy arrays
    tau_values = np.array(tau_values)
    peak_dt_values = np.array(peak_dt_values)

    # Create bins
    min_tau = min(tau_values)
    max_tau = max(tau_values)
    bin_edges = np.linspace(min_tau, max_tau, num_bins+1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Bin the data
    binned_tau = []
    binned_peak = []

    for i in range(num_bins):
        mask = (tau_values >= bin_edges[i]) & (tau_values < bin_edges[i+1])
        if np.sum(mask) > 0:
            binned_tau.append(np.mean(tau_values[mask]))
            binned_peak.append(np.mean(peak_dt_values[mask]))
        else:
            binned_tau.append(0)
            binned_peak.append(0)

    return bin_centers, binned_peak

def plot_simple_line_graph(bin_centers, peak_binned, output_dir):
    """Plot a simple line graph for Figure 5."""
    print("Plotting simple line graph...")

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot the line with markers
    ax.plot(bin_centers, peak_binned, color='#1f77b4',
           linewidth=2, marker='o', markersize=6,
           label='Peak DT')

    # Simple labels
    ax.set_title('Peak DT vs. τ DT (E1 DT-SLRU)', fontsize=14, pad=20)
    ax.set_xlabel('τ DT (milliseconds)', fontsize=12)
    ax.set_ylabel('Peak DT (milliseconds)', fontsize=12)

    # Set reasonable axis limits
    valid_bins = [i for i, val in enumerate(peak_binned) if val > 0]
    if valid_bins:
        x_min = min(bin_centers[valid_bins])*0.95
        x_max = max(bin_centers[valid_bins])*1.05
        y_min = min([peak_binned[i] for i in valid_bins])*0.95
        y_max = max([peak_binned[i] for i in valid_bins])*1.05
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

    # Simple grid
    ax.grid(True, linestyle='--', alpha=0.3)

    # Simple legend
    ax.legend(loc='upper left', fontsize=10)

    # Add statistics box
    valid_peaks = [p for p in peak_binned if p > 0]
    if valid_peaks:
        stats_text = (f"Blocks: {len(valid_peaks):,}\n"
                     f"Avg τ DT: {np.mean(bin_centers[valid_bins]):.1f}ms\n"
                     f"Avg Peak DT: {np.mean(valid_peaks):.1f}ms")

        ax.text(0.98, 0.02, stats_text, transform=ax.transAxes,
               fontsize=10, ha='right', va='bottom',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

    # Save as PDF
    output_path = os.path.join(output_dir, 'Figure5_PeakDT_vs_TauDT_Simple.pdf')
    plt.savefig(output_path, bbox_inches='tight', format='pdf')
    plt.close()

    print(f"Simple line graph saved to {output_path}")
    return output_path

def main():
    # Limit memory usage
    limit_memory()

    # Define directories for Figure 5
    data_dir = '/home/ubuntu/Baleen-FAST24/data/storage/20230325/Region5'
    output_dir = 'runs/example/dt-slru/rejectx-1_lru_366.475GB'
    os.makedirs(output_dir, exist_ok=True)

    try:
        print("Starting data processing for Figure 5...")

        # Find trace files
        trace_files = glob.glob(os.path.join(data_dir, '*.trace'))

        if not trace_files:
            raise FileNotFoundError(f"No trace files found in {data_dir}")

        print(f"Found {len(trace_files)} trace files")

        # Process the first trace file with limited entries
        trace_data = parse_trace_file(trace_files[0])

        # Calculate metrics
        tau_values, peak_dt_values = calculate_metrics(trace_data)

        if tau_values is None:
            raise ValueError("No valid metrics could be calculated")

        # Calculate binned metrics
        bin_centers, peak_binned = calculate_binned_metrics(tau_values, peak_dt_values)

        # Plot simple line graph
        plot_simple_line_graph(bin_centers, peak_binned, output_dir)

        print(f"Figure 5 PDF generated successfully")

    except Exception as e:
        print(f"Error generating Figure 5: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
