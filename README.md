1. ## A7: Artifact Evaluation

   This artifact includes **seven analysis scripts** that comprehensively evaluate the performance of the Baleen flash caching system under various configurations. The evaluation focuses on **disk-head time (DT)**, **cache hit rate**, and the impact of key tuning parameters such as cache size, protected capacity, τ<sub>DT</sub>, and α<sub>TTI</sub>. All scripts are designed to be memory-efficient, reproducible, and produce publication-quality PDF figures suitable for validation of results presented in the paper.

   ### System Requirements

   - **OS**: Ubuntu 22.04  
   - **CPU**: x86_64 architecture with AVX2 support  
   - **Memory**: ≥ 8 GB (≥16 GB recommended for large traces)  
   - **GPU**: Optional (all scripts run on CPU)  
   - **Python**: 3.10.6  
   - **Dependencies**:
     ```text
     anaconda
     numpy==1.23.5
     matplotlib==3.7.1
     torch==2.1.0
     scipy
     tqdm
     ```

   To set up the environment:
   ```bash
   chmod +x ./getting-started.sh
   ./getting-started.sh  # Creates a Conda environment and installs dependencies
   ```

   ---

   ### Reproducing Results

   All scripts are located in the `scripts/` directory and follow a consistent naming convention (`figureX_*.py`). By default, output PDFs are saved to:  
   `runs/example/dt-slru/rejectx-1_lru_366.475GB/`

   | Figure       | Script                                | Description                                                  | Input Data Path                                              | Output File                                     |
   | ------------ | ------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ----------------------------------------------- |
   | **Figure 1** | `figure1_peak_dt.py`                  | Compares **peak DT** (95th percentile inter-arrival time) across eviction schemes E0, E1, and E2 | `/home/ubuntu/Baleen-FAST24/data/storage/201910/Region1/*.trace` | `Figure1_Peak_DT_across_Eviction_Schemes.pdf`   |
   | **Figure 2** | `figure2_median_dt.py`                | Plots **median DT over time** with dual-axis request volume; highlights global minimum | `/home/ubuntu/Baleen-FAST24/data/storage/201910/Region2/*.trace` | `Figure2_Median_DT_across_Eviction_Schemes.pdf` |
   | **Figure 3** | `figure3_cache_hit_rate.py`           | Analyzes **cache hit rate** as a function of cache size      | Varies by experiment (typically same as Fig 1)               | `Figure3_Cache_Hit_Rate_vs_Cache_Size.pdf`      |
   | **Figure 4** | `figure4_peak_dt_vs_cache_size.py`    | Shows how **peak DT changes with increasing cache capacity** | Trace directories organized by cache size (e.g., `cache_64GB/`, `cache_128GB/`) | `Figure4_Peak_DT_vs_Cache_Size.pdf`             |
   | **Figure 5** | `figure5_peak_dt_vs_tau_dt.py`        | Evaluates the effect of **τ<sub>DT</sub> (DT threshold)** on peak DT | Directories labeled by τ<sub>DT</sub> values (e.g., `tau_0.5/`, `tau_1.0/`) | `Figure5_Peak_DT_vs_tau_DT.pdf`                 |
   | **Figure 6** | `figure6_peak_dt_vs_protected_cap.py` | Studies **protected capacity** impact on peak DT             | Subdirectories named by protected capacity (e.g., `prot_10GB/`, `prot_20GB/`) | `Figure6_Peak_DT_vs_Protected_Cap.pdf`          |
   | **Figure 7** | `figure7_peak_dt_vs_alpha_tti.py`     | Investigates influence of **α<sub>TTI</sub> (temporal locality weight)** on peak DT | Directories varying α<sub>TTI</sub> (e.g., `alpha_0.2/`, `alpha_0.8/`) | `Figure7_Peak_DT_vs_alpha_TTI.pdf`              |

   #### How to Run
   Each figure can be regenerated independently:
   ```bash
   python scripts/figureX_*.py
   ```
   Example:
   ```bash
   python scripts/figure5_peak_dt_vs_tau_dt.py
   ```

   > **Note**: Data paths are hardcoded in each script (typically under `/home/ubuntu/Baleen-FAST24/data/...`). To run in other environments, modify the `data_dir` variable inside the script. Scripts for Figures 4–7 expect a specific directory structure where subdirectories encode parameter values (e.g., `cache_128GB/`). Ensure your trace data matches this layout.

   **Typical runtime**: 2–8 minutes per figure (depending on trace size)  
   **Memory usage**: Most scripts cap input at ~50,000 entries or enforce memory limits (2–4 GB) to prevent OOM errors.

   ---

   ### Verification Checklist

   To validate the correctness of this artifact, perform the following tests:

   | Test ID    | Description                      | Command                                                    | Success Criteria                                             |
   | ---------- | -------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------ |
   | **Test 1** | Basic peak DT bar chart (Fig 1)  | `python scripts/figure1_peak_dt.py`                        | Generates a 3-bar PDF (E0/E1/E2), values in ms (e.g., 50–200 ms) |
   | **Test 2** | Time-series median DT (Fig 2)    | `python scripts/figure2_median_dt.py`                      | Produces a dual-axis smoothed line plot with min-DT marker   |
   | **Test 3** | Cache hit rate trend (Fig 3)     | `python scripts/figure3_cache_hit_rate.py`                 | Curve increases with cache size, no anomalies                |
   | **Test 4** | Parameter sweep plots (Figs 4–7) | Run `figure4.py` through `figure7.py`                      | Each generates a valid multi-series or parametric plot with labeled axes |
   | **Test 5** | Robustness to malformed input    | Insert `# comment` or invalid lines into any `.trace` file | Script skips bad lines with warnings; continues processing   |
   | **Test 6** | Memory safety under load         | Run any script on a trace >100k lines                      | No crash; memory usage stays ≤4 GB                           |
   | **Test 7** | Output completeness              | Check output directory after running all scripts           | All 7 PDFs exist and are non-empty                           |

   ---

   ### Limitations

   While this artifact supports full reproducibility of the paper’s key figures, the following limitations should be noted:

   1. **Hardcoded paths**: Input/output directories are embedded in the code; no CLI argument support.
   2. **Single-file processing**: Most scripts process only the **first `.trace` file** found per directory, ignoring potential replicates.
   3. **Input truncation**: To control memory, scripts often limit parsing to 50,000 entries—this may reduce statistical robustness on sparse or bursty workloads.
   4. **Time unit assumption**: Scripts assume timestamps in traces are in **seconds**; if original data uses microseconds, DT values will be off by 1000×.
   5. **Simplified scheme mapping**: Figure 1 assigns E0/E1/E2 via `pipeline % 3`, which may not reflect actual experimental policy assignment.
   6. **Strict directory structure**: Figures 4–7 require trace data to be organized in parameter-specific subdirectories (e.g., `alpha_0.5/`). Deviations cause silent failures or missing data.
   7. **No automatic data provisioning**: Users must supply or mount the original Baleen-FAST24 I/O traces; the artifact does not include or download datasets.
   8. **Fixed visualization style**: Colors, fonts, and layout are preset; customization requires code modification.

