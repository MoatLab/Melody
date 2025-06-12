#!/bin/bash
PBBS_SRC_DIR="/mnt/sda4/pbbsbench"
cd $PBBS_SRC_DIR/benchmarks/minSpanningForest/serialMST; ./testInputs -r 1 -p 1 -x -g -k; cd -
