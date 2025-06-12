#!/bin/bash
sudo apt update >/dev/null 2>&1
sudo apt install -y php-cli php-xml >/dev/null 2>&1 || exit

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# TODO : may need to change to other directory's name
cd /mnt/sda4

echo "Check phoronix ..."
[[ -d phoronix-test-suite ]] && rm -rf phoronix-test-suite && echo "phoronix-test-suite removed"
git clone https://github.com/phoronix-test-suite/phoronix-test-suite.git >/dev/null 2>&1
