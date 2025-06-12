```
 __ __       _         _      
|  \  \ ___ | | ___  _| | _ _ 
|     |/ ._>| |/ . \/ . || | |
|_|_|_|\___.|_|\___/\___|`_. |
                         <___'  --- CXL performance analysis suite
```

## To Be Released
* Time-series analysis code for [SPA](spa)
* The full set scripts for all workloads in [SPA](spa)
* Upload workload performance slowdown data

## Description
Melody is a framework for systematic characterization and analysis of CXL memory performance. 
Melody builds on an extensive evaluation spanning hundered of workloads on different CPU platforms with 4 CXL devices. 
It revealed several interesting insights: 
workload sensitivity to sub-microsecond CXL latencies (140–410 ns), 
the first disclosure of CXL tail latencies, CPU tolerance to CXL-induced delays, 
a novel approach [SPA](spa) for pinpointing CXL bottlenecks, 
and CPU prefetcher inefficiencies caused by CXL's high latency.

It contains:
+ [MIO](mio): latency microbenchmark
+ [SPA](spa): Stall-based Performance Analysis

For more detail, please read the paper: 
[Systematic CXL Memory Characterization and Performance Analysis at Scale](https://dl.acm.org/doi/pdf/10.1145/3676641.3715987) [ASPLOS'25]

## Testing Platforms
Platforms tested in the paper:

+ SKX A: Two Intel Xeon Silver 4114 10-core CPUs at 2.20 GHz, 192GB DDR4 Memory
+ SKX B: Eight Intel Xeon Platinum 8180 28-core CPUs at 2.50GHz, 376GB DDR4 Memory
+ SPR: Two Intel Xeon Gold 6430 32-core CPUs at 2.10 GHz, 256GB DDR5 Memory
+ EMR A: Two Intel Xeon Gold 6530 32-core CPUs at 2.10 GHz, 256GB DDR5 Memory
+ EMR B: Two Intel Xeon Platinum 8573C 52-core CPUs at at 2.30 GHz, 3TB DDR5 Memory

## Citation

```
@inproceedings{10.1145/3676641.3715987,
author = {Liu, Jinshu and Hadian, Hamid and Wang, Yuyue and Berger, Daniel S. and Nguyen, Marie and Jian, Xun and Noh, Sam H. and Li, Huaicheng},
title = {Systematic CXL Memory Characterization and Performance Analysis at Scale},
year = {2025},
isbn = {9798400710797},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3676641.3715987},
doi = {10.1145/3676641.3715987},
booktitle = {Proceedings of the 30th ACM International Conference on Architectural Support for Programming Languages and Operating Systems, Volume 2}
}
```

## Contact
Maintainer: Jinshu Liu, jinshu@vt.edu
