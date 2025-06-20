#!/bin/bash

#RST_DIR="results"
RST_DIR=$1
mem_node=$2

threads=( 1 2 4 8 )
bsize=( 4096 2048 1024 512 )
iter=( 3 3 3 3 )

for (( i=0; i < ${#threads[@]}; i++ ))
do
  th=${threads[$i]}
  bs=${bsize[$i]}
  it=${iter[$i]}
  SECONDS=0
  ../src/bench -t $th -r ${mem_node} -i $it -I 8 -T 0 -m $bs > $RST_DIR/N0m${mem_node}_$th.txt
  echo $SECONDS
done
