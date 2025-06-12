#!/bin/bash
THIS_SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_SCRIPT_PATH/config.sh || exit
arr=(pc rd wr)

PREF_OFF_RES="results-pref-off"
PREF_ON_RES="results-pref-on"
sysinfof="sysinfo.txt"
mlcf="mlc.txt"

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 [nodes_list]"
  echo "Note: nodes_list is seperated by ,"
  echo "Example: $0 1,2,3"
  exit 1
fi

nodes_list=$1
IFS=',' read -ra nodes <<< "$nodes_list"
echo -n "Nodes: "
for n in "${nodes[@]}"; do
  echo -n "$n "
done
echo ""
nodes_cnt=$(numactl -H | grep "available:" | awk '{print $2}')
numactl -H | grep "available:"
for n in "${nodes[@]}"; do
  if [ $n -gt ${nodes_cnt} ] || [ $n -eq ${nodes_cnt} ]; then
    echo "Node $n is unavailable"
    exit 1
  fi
done

run()
{
  local type=$1
  local res_dir=$2
  echo "START..." $type
  flush_fs_caches
  cd $type;
  [[ ! -d ${res_dir} ]] && mkdir -p ${res_dir};
  cd ${res_dir}; sudo rm -rf **; cd ..
  for n in "${nodes[@]}"; do
    echo "running on node $n ..."
    sudo ./runx.sh ${res_dir} $n;
  done
  cd ..
  echo "FINISHED " $type
}

exp()
{
  local pref_on=$1
  bring_all_cpus_online
  if [[ $pref_on -eq 0 ]]; then
    sudo wrmsr -a 0x1a4 0xf && echo "prefetchers disabled"
  else
    sudo wrmsr -a 0x1a4 0x0 && echo "prefetchers enabled"
  fi
  check_cxl_conf
  echo "START bench: $(date)"
  for name in "${arr[@]}"; do
    if [[ $pref_on -eq 0 ]]; then
      run $name $PREF_OFF_RES
    else
      run $name $PREF_ON_RES
    fi
  done
  bring_all_cpus_online
  sudo wrmsr -a 0x1a4 0x0
  echo "FINISHED bench: $(date)"
}

run_mlc()
{
  echo "START mlc ..."
  bring_all_cpus_online
  check_cxl_conf
  sudo ./mlc > $mlcf 2>&1
  bring_all_cpus_online
  echo "FINISHED mlc"
}

main()
{
  sudo modprobe msr
  # run_mlc
  get_sysinfo > $sysinfof 2>&1

  echo "exp with prefetchers off"
  exp 0
  echo "exp with prefetchers on"
  exp 1
}

main
