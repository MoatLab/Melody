## Description

This directory contains performance slowdowns for workloads running on remote
NUMA and CXL memory. Results are normalized to execution time using local memory:

    slowdown = remote or CXL memory runtime / local memory runtime

For example, `1.20` represents a 20% slowdown. A few values below `1.00` can be attributed
to measurement error.

The CSV files are organized by CPU platform and memory setup. Each row specifies
the workload suite, workload name, platform, memory setup, and measured slowdown.
The dataset includes workloads that are highly memory-bandwidth-bound, which
generally experience much greater slowdown.
