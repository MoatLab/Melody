#!/bin/bash
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_PATH}/paths.sh"
SRC_DIR="${REDIS_SRC_DIR}"
arr=( redis-benchmark redis-check-aof redis-check-rdb redis-cli redis-sentinel redis-server )

for ((i = 0; i < ${#arr[@]}; i++)); do
	exe=${arr[$i]}
	sudo rm ${BIN_DIR}/$exe
done
