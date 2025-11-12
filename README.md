# **A7: Artifact Evaluation**

This artifact provides seven analysis scripts that evaluate the **Baleen flash caching system** under diverse configurations.  
It measures key performance metrics like **Disk-head Time (DT)** and **Cache Hit Rate**, while exploring tuning parameters such as **Cache Size**, **Protected Capacity**, **τDT**, and **αTTI**.

All scripts are lightweight, reproducible, and produce publication-quality figures.

---

## **System Requirements**
 **OS**  Ubuntu 22.04 
 **CPU**  x86_64 
 **Memory**  ≥ 8 GB (16 GB recommended) |
 **GPU**  Optional (CPU-only supported) |
 **Python**  3.10.6 |
 **Dependencies** | anaconda, numpy==1.23.5, matplotlib==3.7.1, torch==2.1.0, scipy, tqdm |

### **Setup**

```bash
chmod +x ./getting-started.sh
./getting-started.sh   # creates Conda environment & installs dependencies
```

---

## **Reproducing Results**

All scripts are stored under the `scripts/` directory and follow the naming pattern:

```
figureX_*.py
```

**Output directory example:**
```
runs/example/dt-slru/rejectx-1_lru_366.475GB/
```

Each script generates one figure as a PDF file:

| Figure | Script                                 | Description                                  | Output                                         |
|------- |----------------------------------------|----------------------------------------------|------------------------------------------------|
| **1**  | `figure1_peak_dt.py`                   | Peak DT across eviction schemes (E0, E1, E2) | `Figure1_Peak_DT_across_Eviction_Schemes.pdf`  |
| **2**  | `figure2_median_dt.py`                 | Median DT vs request volume                  | `Figure2_Median_DT_across_Eviction_Schemes.pdf`|
| **3**  | `figure3_cache_hit_rate.py`            | Cache Hit Rate vs Cache Size                 | `Figure3_Cache_Hit_Rate_vs_Cache_Size.pdf`     |
| **4**  | `figure4_peak_dt_vs_cache_size.py`     | Peak DT vs Cache Size                        | `Figure4_Peak_DT_vs_Cache_Size.pdf`            |
| **5**  | `figure5_peak_dt_vs_tau_dt.py`         | Effect of τDT on Peak DT                     | `Figure5_Peak_DT_vs_tau_DT.pdf`                |
| **6**  | `figure6_peak_dt_vs_protected_cap.py`  | Impact of Protected Capacity on Peak DT      | `Figure6_Peak_DT_vs_Protected_Cap.pdf`         |
| **7**  | `figure7_peak_dt_vs_alpha_tti.py`      | Effect of αTTI on Peak DT                    | `Figure7_Peak_DT_vs_alpha_TTI.pdf`             |

---

## **How to Run**

Each figure can be generated independently:

```bash
python scripts/figureX_*.py
```

For example:
```bash
python scripts/figure5_peak_dt_vs_tau_dt.py
```

> ⚠️ **Note:** Paths are hardcoded (e.g., `/home/ubuntu/Baleen-FAST24/data/...`).  
> To use your own environment, edit the `data_dir` variable in each script.

**Expected Runtime:** 2–8 minutes per figure  
**Memory Usage:** ≤ 4 GB (scripts limit input to 50k entries)

---

## **Verification Checklist**

| Test ID | Description                   | Command                                                                               | Success Criteria                                           |
|---------|-------------------------------|---------------------------------------------------------------------------------------|------------------------------------------------------------|
| 1       | Peak DT bar chart (Fig 1)     | `python scripts/figure1_peak_dt.py`                                                   | Generates 3-bar PDF (E0/E1/E2), values in (50–200 ms)      |
| 2       | Median DT time series (Fig 2) | `python scripts/figure2_median_dt.py`                                                 | Produces a dual-axis smoothed line plot with min-DT marker |
| 3       | Cache Hit Rate trend (Fig 3)  | `python scripts/figure3_cache_hit_rate.py`                                            | Curve increases with cache size, no anomalies              |
| 4       | Parameter sweeps (Figs 4–7)   | `python scripts/figure4_peak_dt_vs_cache_size.py` … `figure7_peak_dt_vs_alpha_tti.py` | Each generates a valid multi-series with labeled axes      |
| 5       | Malformed input               | Insert # comment or invalid lines into any .trace file                                | Script skips bad lines with warnings; continues processing |
| 6       | Memory safety                 | Run any script on a trace >100k lines                                                 | No crash; memory usage stays ≤4 GB                         |
| 7       | Output completeness           | Check output directory after running all scripts                                      | All 7 PDFs exist and are non-empty                         |

---

## **Limitations**

1. **Hardcoded paths** — Input/output directories are embedded in the code; no CLI argument support.  
2. **Single-trace processing** — Most scripts process only the first .trace file found per directory, ignoring potential replicates.  
3. **Input truncation** — To control memory, scripts often limit parsing to 50,000 entries—this may reduce statistical robustness on
sparse or bursty workloads.
4. **Time unit assumption** —  Scripts assume timestamps in traces are in seconds; if original data uses microseconds, DT values will
be off by 1000×.
5. **Simplified E0/E1/E2 mapping** — Figure 1 assigns E0/E1/E2 via pipeline % 3, which may not reflect actual experimental policy
assignment.

