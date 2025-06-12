#!/bin/bash
sudo apt update >/dev/null 2>&1
sudo apt install -y libgfortran5 >/dev/null 2>&1
sudo apt install -y vmtouch >/dev/null 2>&1
sudo apt install -y libxmu6 >/dev/null 2>&1
./install-perf.sh
echo "DONE"
