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
                        'namespace': int(values[6]),
                        'hit': int(values[7]) if len(values) > 7 else 0
                    }
                    data.append(entry)
                    entry_count += 1
            except Exception as e:
                print(f"Error parsing line: {line[:50]}... Error: {e}")
                skipped_lines += 1

    print(f"Loaded {len(data)} entries, skipped {skipped_lines} lines")
    return data

def calculate_hit_rates(trace_data):
    """Calculate cache hit rates for different eviction schemes."""
    print("Calculating cache hit rates...")

    # Group requests by pipeline (which represents the eviction scheme)
    pipeline_requests = defaultdict(list)
    for entry in trace_data:
        pipeline = entry['pipeline']
        pipeline_requests[pipeline].append(entry)

    # Calculate hit rates for each scheme (E0, E1, E2)
    schemes = {
        0: {'name': 'E0', 'hits': 0, 'total': 0},
        1: {'name': 'E1', 'hits': 0, 'total': 0},
        2: {'name': 'E2', 'hits': 0, 'total': 0}
    }

    for pipeline, requests in pipeline_requests.items():
        scheme_id = pipeline % 3  # Distribute pipelines across 3 schemes
        for req in requests:
            schemes[scheme_id]['total'] += 1
            if req.get('hit', 0) == 1:
                schemes[scheme_id]['hits'] += 1

    # Calculate hit rates
    hit_rates = []
    scheme_names = []
    for scheme_id, data in schemes.items():
        if data['total'] > 0:
            hit_rate = data['hits'] / data['total']
            hit_rates.append(hit_rate)
            scheme_names.append(data['name'])
            print(f"Scheme {data['name']}: {data['hits']} hits / {data['total']} requests = {hit_rate:.2f}")

    if not hit_rates:
        print("No valid hit rate data calculated")
        return None, None

    return scheme_names, hit_rates

def plot_figure3(scheme_names, hit_rates, output_dir):
    """Plot a clean bar graph for Figure 3: Cache Hit Rate Across Eviction Schemes."""
    print("Plotting Figure 3...")

    # Create figure with improved layout
    fig, ax = plt.subplots(figsize=(10, 8))
    plt.subplots_adjust(right=0.85, top=0.9, bottom=0.2, left=0.1)

    # Create positions for bars with proper spacing
    x_pos = np.arange(len(scheme_names))

    # Use a professional color scheme
    colors = ['#4c72b0', '#dd8452', '#55a868']  # Blue, Orange, Green

    # Create bars with clean colors
    bars = ax.bar(x_pos, hit_rates,
                color=colors, width=0.6, alpha=0.9)

    # Add value labels ON the bars
    for i, (x, value) in enumerate(zip(x_pos, hit_rates)):
        ax.text(x, value + 0.01,
               f'{value:.2f}',
               ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Simple labels with larger font
    ax.set_title('Cache Hit Rate Across Eviction Schemes (E0-E2)', fontsize=16, pad=20, weight='bold')
    ax.set_xlabel('Eviction Scheme', fontsize=14, labelpad=10)
    ax.set_ylabel('Cache Hit Rate (%)', fontsize=14, labelpad=10)

    # Set reasonable axis limits
    ax.set_ylim(0, 1.05)
    ax.set_yticks(np.arange(0, 1.1, 0.1))
    ax.set_yticklabels([f"{x:.0%}" for x in np.arange(0, 1.1, 0.1)])

    # Simple grid
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')

    # Format x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(scheme_names)

    # Add statistics box with improved formatting
    stats_text = (f"Schemes: {len(scheme_names):,}\n"
                 f"Avg Hit Rate: {np.mean(hit_rates):.2f}\n"
                 f"Max Hit Rate: {max(hit_rates):.2f}")

    ax.text(0.98, 0.95, stats_text, transform=ax.transAxes,
           fontsize=12, ha='right', va='top',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9))

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save as PDF with high quality
    output_path = os.path.join(output_dir, 'Figure3_Cache_Hit_Rate.pdf')
    plt.savefig(output_path, bbox_inches='tight', format='pdf', dpi=300)
    plt.close()

    print(f"Figure 3 saved to {output_path}")
    return output_path

def main():
    # Limit memory usage
    limit_memory()

    # Define directories for Figure 3
    data_dir = '/home/ubuntu/Baleen-FAST24/data/storage/201910/Region3'
    output_dir = 'runs/example/dt-slru/rejectx-1_lru_366.475GB'
    os.makedirs(output_dir, exist_ok=True)

    try:
        print("Starting data processing for Figure 3...")

        # Find trace files
        trace_files = glob.glob(os.path.join(data_dir, '*.trace'))

        if not trace_files:
            raise FileNotFoundError(f"No trace files found in {data_dir}")

        print(f"Found {len(trace_files)} trace files")

        # Process the first trace file
        trace_data = parse_trace_file(trace_files[0])

        # Calculate hit rates
        scheme_names, hit_rates = calculate_hit_rates(trace_data)

        if scheme_names is None:
            raise ValueError("No valid hit rate data could be calculated")

        # Plot Figure 3
        plot_figure3(scheme_names, hit_rates, output_dir)

        print(f"Figure 3 PDF generated successfully")

    except Exception as e:
        print(f"Error generating Figure 3: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
