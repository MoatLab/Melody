#!/bin/bash
sudo apt update >/dev/null 2>&1
sudo apt install -y libtbb2 >/dev/null 2>&1 || exit

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# TODO : may need to change to other directory's name
cd /mnt/sda4

echo "Check pbbsbench ..."
[[ -d pbbsbench ]] && rm -rf pbbsbench && echo "pbbsbench removed"

git clone https://github.com/cmuparlay/pbbsbench.git >/dev/null 2>&1
cd pbbsbench
git checkout 596b670eb946c352368d265ae9888ce08a42468f >/dev/null 2>&1
git submodule update --init >/dev/null 2>&1
cp ${SCRIPT_PATH}/pbbs.patch .
git apply pbbs.patch >/dev/null 2>&1
cp ${SCRIPT_PATH}/Makefile .

make all 
make ext
