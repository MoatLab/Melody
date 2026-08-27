
```
 ____  ____   _    
/ ___||  _ \ / \   
\___ \| |_) / _ \  
 ___) |  __/ ___ \ 
|____/|_| /_/   \_\ -- Stall-based Performance Analysis
```

## Description

The key insight of SPA is that drilling down the differential CPU stalls between slow and fast memory 
can yield accurate performance slowdown analysis whereas standalone setup cannot. 
SPA aims to pinpoint the specific stall sources that contribute to slowdowns, 
bridging the gap between architectural level and workload-level performance.

The memory performance slowdown is composed of several sections, which are defined in the [paper](https://dl.acm.org/doi/pdf/10.1145/3676641.3715987):
(1) DRAM slowdown, (2) Cache slowdown (L1/L2/L3), (3) Store slowdown, (4) Core slowdown, and (5) Other.
The slowdown is mainly dominated by (1) DRAM slowdown, (2) Cache slowdown (L1/L2/L3), (3) Store slowdown, while (4) and (5) have minimal contribution on the overall slowdown.

## Usage
It measures the performance counters used in the paper.
The output files are in `rst` for each workload suite.
The data processing files are provided in `proc`.

*The use cases demonstrated in the [paper](https://dl.acm.org/doi/pdf/10.1145/3676641.3715987) are mainly related to CXL/remote memory performance analysis. 
Howerer, I believe the analysis methodology should not be limited to CXL/remote memory. 
Welcome to find out more use cases for this method.*

### Steps

* Setup (Install packages and perf)
  ```
  ./setup.sh
  ```
* Go to a workload suite directory, (for example, cpu2017), run the 1st workload in the suite:
  ```
  sudo ./run.sh w.txt 1
  ```
  Run all workloads:
  ```
  sudo ./run.sh w.txt
  ```

  Set `PERF_INTERVAL_MODE=0` in `config.sh` to save one aggregate count per run in `rst/aggregate`.
  To sample the counters over time, set `PERF_INTERVAL_MODE=1` and configure the sampling period with
  `PERF_INTERVAL_MS` (milliseconds). The time-series results are saved in `rst/interval`.

* Collect the performance counters from the output files. 
`proc` provides a basic processing code for visualizing 
the slowdown breakdown.

  + Copy the `rst` to the directory where `update_data.py` and `process.py` is.
  + Generate data files in `csv`   
  ```
  python3 update_data.py
  ```
  Process only one mode when needed:
  ```
  python3 update_data.py aggregate
  python3 update_data.py interval
  ```
  + Process the data in `csv` and generate plots in `plots`
  ```
  python3 process.py
  ```
  Process only one mode when needed:
  ```
  python3 process.py aggregate
  python3 process.py interval
  ```
  The aggregate plot is generated in `plots/aggregate`. Interval plots are generated for each workload
  in `plots/interval`; use `--bins` to set the number of instruction intervals (default: `200`):
  ```
  python3 process.py interval --bins 100
  ```

### Notes

* The `run.sh` files run each workload once on local (NUMA node `0`) and once on remote (NUMA node `1`). 
The default remote NUMA node is set as `1`. 
For the remote memory other than NUMA node `1` in multi-nodes servers, set `--membind 1` to other values.
