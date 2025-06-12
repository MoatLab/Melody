#!/bin/bash
VMTOUCH="/usr/bin/vmtouch"
DATA_DIR="/mnt/sda4/pbbsbench/testData/graphData/data"

if [[ $# != 1 ]]; then
	echo ""
	echo "$0 tag"
	echo ""
	exit
fi

if [[ ! -e $VMTOUCH ]]; then
	echo "Please install vmtouch first!"; exit
fi

tag=$1

datasets=("randLocalGraph_E_10_20000000" "rMatGraph_E_10_20000000" "2Dgrid_E_64000000")

echo "    => Loading graph into page cache first"
if [[ $tag == "L100" ]]; then
	for i in "${datasets[@]}"
	do
		numactl --membind 0 ${VMTOUCH} -f -t ${DATA_DIR}/${i}
	done
elif [[ $tag == "L0" ]]; then
	for i in "${datasets[@]}"
	do
		numactl --membind 1 ${VMTOUCH} -f -t ${DATA_DIR}/${i}
	done
elif [[ $tag == "CXL-Interleave" ]]; then
	for i in "${datasets[@]}"
	do
		numactl --interleave=all ${VMTOUCH} -f -t ${DATA_DIR}/${i}
	done
fi
