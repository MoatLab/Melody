#!/bin/bash

# 1 = sample counters over time (perf stat -I), 0 = one aggregate count per run
PERF_INTERVAL_MODE=0

# Sampling period in milliseconds. 1000 = 1 second. Minimum accepted: 10.
PERF_INTERVAL_MS=1000

# Sub-directory of rst/ that holds time-series results (interval mode)
PERF_INTERVAL_SUBDIR="interval"

# Sub-directory of rst/ that holds aggregate results (non-interval mode)
PERF_AGGREGATE_SUBDIR="aggregate"
