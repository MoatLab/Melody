#!/bin/bash
PBBS_SRC_DIR="/mnt/sda4/pbbsbench"
cd $PBBS_SRC_DIR/benchmarks/longestRepeatedSubstring/doubling; ./testInputs -r 3 -p 8 -x -g -k; cd -
