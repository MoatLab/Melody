#!/bin/bash
VMTOUCH="/usr/bin/vmtouch"
DATA_DIR="/mnt/sda4/pbbsbench/testData/sequenceData/data"

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

datasets=("randomSeq_100M_double" "exptSeq_100M_double" "almostSortedSeq_100M_double" "randomSeq_100M_double_pair_double" "trigramSeq_100M")

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
