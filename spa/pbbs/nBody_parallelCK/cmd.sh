#!/bin/bash
PBBS_SRC_DIR="/mnt/sda4/pbbsbench"
cd $PBBS_SRC_DIR/benchmarks/nBody/parallelCK; ./testInputs -r 3 -p 8; cd -
