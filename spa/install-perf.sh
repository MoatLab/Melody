#!/bin/bash
LOGF=log
sudo apt update >/dev/null 2>&1
sudo apt install -y libelf-dev libdw-dev libnuma-dev python3-dev >/dev/null 2>&1
sudo apt install -y build-essential libssl-dev ncurses-dev xz-utils bc flex libelf-dev bison lz4 dwarves >/dev/null 2>&1

curr_dir="$PWD"
[[ ! -d linux ]] && git clone https://github.com/torvalds/linux.git >/dev/null 2>&1
echo "Compiling perf ..."
cd linux/tools/perf
make NO_LIBTRACEEVENT=1 PYTHON=python3 > $LOGF 2>&1 || exit
rm $LOGF
echo "Checking perf ..."
[[ -e perf ]] || exit
echo "Finished checking"
sudo ln -s ${curr_dir}/linux/tools/perf/perf /usr/local/bin/perf || echo "Cannot link" && exit
cd ${curr_dir}
