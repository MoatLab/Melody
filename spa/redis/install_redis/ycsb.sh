#!/bin/bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_PATH}/../paths.sh"

sudo apt install maven -y

cd "${YCSB_BASE_DIR}"
[[ -d YCSB ]] && rm -rf YCSB && echo "ycsb removed"

git clone http://github.com/brianfrankcooper/YCSB.git

cd YCSB
mvn -pl site.ycsb:redis-binding -am clean package
