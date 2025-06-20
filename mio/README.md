```
 __    __     __     ______   
/\ "-./  \   /\ \   /\  __ \  
\ \ \-./\ \  \ \ \  \ \ \/\ \ 
 \ \_\ \ \_\  \ \_\  \ \_____\
  \/_/  \/_/   \/_/   \/_____/   -- (CXL) Memory Latency Distribution Measurement Tool
```
## Description
It measures the average latency for each `n` pointer chasing memory access latency (`n` is set by `-I`), 
and then output the latency numbers into the log files, which forms the distribution of the memory access latency.
The number of threads for pointer-chasing can be set by `-t` when `-T` is set as `0`.
It can also output the latency values with the sequential read/write in the background. 
The background read/write intensity can be tuned by setting the number of threads with `-t`.

The [paper](https://dl.acm.org/doi/pdf/10.1145/3676641.3715987) shows that, 
the (loaded) latency distribution would be quite different on our CXL-DRAM devices, 
compared to regular DRAM.

## Usage
* Compile the files: run `make` in `src`. The compiled file is named as `bench`.
* All-in-one run: `./run.sh [nodes_list]`
  ```
  ./run.sh 0,1
  ```
  *`nodes_list` is a list separated by `,`. The number corresponds to each NUMA node.*

* For each type of memory accesses:
    >`pc` means 1-n threads pointer-chasing. `-T` is set as `0` for `bench`.
    
    >`rd` means 1-thread pointer-chasing with 0-(n-1) threads sequential reads. `-T` is set as `1` for `bench`.
    
    >`wr` means 1-thread pointer-chasing with 0-(n-1) threads sequential writes. `-T` is set as `2` for `bench`.

* The output files will be in `pc`, `rd`, and `wr`. 
Each line denotes the latency in nanoseconds.

## Notes
* `TSC_FREQ_GHZ` should be set as the machine's CPU frequency.
* `-I` is set as 8 for measuring the averaging latency for each 8 accesses.
* Tune of the number of threads in `runx.sh` in each folder for different access types to comply with different physical machines.
For example, `pc` currently uses `1,2,4,8` threads.
* The data buffer size is for each threads. 
The data buffer accessed by each thread is independent.
The size can be set with `-m` in MB.
* `-i` sets the number of iterations.
* `-r` sets which NUMA node is accessed.
* Use `-R` for enabling random pointer-chasing. 
The default setting (without `-R`) uses non-random pointer-chasing with prefetchers off for measuring latency. The suffling "window" and iterations can also be tuned in the code. 
* By default, the program pins the cores for each thread it uses, and the cores it tries to pin is starting from core `0`. For example, with `-t` set as 8, the program uses the cores from `0` to `7`. The starting core (`starting_core`  in the code) can be specified by using `-c`.

## Acknowledgments

The assembly code in `op_ptr_chase`, `op_ld`, and `op_st` is 
adapted from the source code in 
"Demystifying CXL Memory with Genuine CXL-Ready Systems and Devices" [MICRO'23]

