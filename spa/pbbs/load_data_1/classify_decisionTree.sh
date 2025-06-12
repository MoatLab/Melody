#!/bin/bash
VMTOUCH="/usr/bin/vmtouch"
DATA_DIR="/mnt/sda4/pbbsbench/testData/sequenceData/data"

if [[ $# != 2 ]]; then
	echo ""
	echo "$0 tag id"
	echo ""
	exit
fi

if [[ ! -e $VMTOUCH ]]; then
	echo "Please install vmtouch first!"; exit
fi

tag=$1
id=$2

datasets=("covtype.data.train" "covtype.data.test" "kddcup.data.train" "kddcup.data.test")

echo "    => Loading graph into page cache first"
if [[ $tag == "L100" ]]; then
	for i in "${datasets[@]}"
	do
		numactl --membind 1 ${VMTOUCH} -f -t ${DATA_DIR}/${i}
	done
elif [[ $tag == "L0" ]]; then
	for i in "${datasets[@]}"
	do
		if [[ $id == "1" ]]; then
			numactl --membind 0 ${VMTOUCH} -f -t ${DATA_DIR}/${i}
		else
			numactl --membind 3 ${VMTOUCH} -f -t ${DATA_DIR}/${i}
		fi
	done
elif [[ $tag == "CXL-Interleave" ]]; then
	for i in "${datasets[@]}"
	do
		numactl --interleave=all ${VMTOUCH} -f -t ${DATA_DIR}/${i}
	done
fi
