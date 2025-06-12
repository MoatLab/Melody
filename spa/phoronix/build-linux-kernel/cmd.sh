#!/bin/bash
phoronix_dir="/mnt/sda4/phoronix-test-suite"

export FORCE_TIMES_TO_RUN=1
$phoronix_dir/phoronix-test-suite batch-run build-linux-kernel
