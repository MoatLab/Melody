#!/bin/bash

THIS_SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNDIR=$(echo "$(dirname "$PWD")")
REDIS_RUN_DIR="$RUNDIR/redis"
RSTDIR="${REDIS_RUN_DIR}/rst"
PERF_EVENTS_FILE="${REDIS_RUN_DIR}/perf_events.txt"
#PERF="${RUNDIR}/linux/tools/perf/perf"
PERF=$(which perf)
if [[ -z "$PERF" ]]; then
  echo "Error: perf not found"
  exit 1
fi

if [[ ! -f "$PERF_EVENTS_FILE" ]]; then
  echo "Error: perf events file not found: $PERF_EVENTS_FILE"
  exit 1
fi
YCSB_DIR="/tdata/YCSB"

REDIS_SERVER=10.10.1.1
REDIS_CLIENT=10.10.1.2

source $RUNDIR/config.sh || exit

echo "==> Result directory: $RSTDIR"

TIME_FORMAT="\n\n\nReal: %e %E\nUser: %U\nSys: %S\nCmdline: %C\nAvg-total-Mem-kb: %K\nMax-RSS-kb: %M\nSys-pgsize-kb: %Z\nNr-voluntary-context-switches: %w\nCmd-exit-status: %x"
if [[ ! -e /usr/bin/time ]]; then
  echo "Please install GNU time first!"
  exit
fi

echo "Checking perf ..."
[[ -e $PERF ]] || exit
echo "Finished checking"

warr=(workloada workloadb workloadc workloadd workloade workloadf)
marr=(19024 19024 19024 19024 19024 19024)
carr=(2 2 2 2 3 2)

if [[ $# != 1 && $# != 2 ]]; then
  echo "$0 wi.txt"; echo "$0 w.txt 1"; exit
fi

wf=$1
LID=$2
[[ ! -e $wf ]] && echo "$wf does not exist .." && exit

if [[ $# == 1 ]]; then
  warr=($(cat $wf | awk '{print $1}'))
  marr=($(cat $wf | awk '{print $2}'))
  carr=($(cat $wf | awk '{print $3}'))
elif [[ $# == 2 ]]; then
  warr=($(cat $wf | awk -vline=$LID 'NR == line {print $1}'))
  marr=($(cat $wf | awk -vline=$LID 'NR == line {print $2}'))
  carr=($(cat $wf | awk -vline=$LID 'NR == line {print $3}'))
fi

echo ${warr[@]}
echo ${marr[@]}
echo ${carr[@]}

stop_redis_server() {
  pid=$(ps -ef  |grep redis-server | grep -v grep | awk '{print $2}')
  for p in $pid; do sudo kill -9 $p >/dev/null 2>&1; done
  killall redis-server >/dev/null 2>&1
}

run_one_exp() {
  local w=$1
  local et=$2
  local id=$3
  local propid=$4
  local run_cmd="bash cmd.sh"

  echo "run_one_exp 1"

  if [[ $et == "L100" ]]; then
    CPREFIX="numactl --cpunodebind 0 --membind 0"
    run_cmd="numactl --cpunodebind 0 --membind 0 -- ""${run_cmd}"
  elif [[ $et == "L0" ]]; then
    CPREFIX="numactl --cpunodebind 0 --membind 1"
    run_cmd="numactl --cpunodebind 0 --membind 1 -- ""${run_cmd}"
  else
    pass
  fi
  local output_dir="$RSTDIR/$w"
  [[ ! -d ${output_dir} ]] && mkdir -p ${output_dir}

  nthreads=10
  accessmode="zipfian"
  local RUN_F_PREFIX="${output_dir}/${et}-${accessmode}-${nthreads}t-${id}"
  local logf=${RUN_F_PREFIX}.log
  local timef=${RUN_F_PREFIX}.time
  local loadoutputf=${RUN_F_PREFIX}.loadoutput
  local outputf=${RUN_F_PREFIX}.output
  local rawlatf=${RUN_F_PREFIX}.rawlat
  local perfoutput=${output_dir}/${et}-${id}.data

  local perf_events
  perf_events=$(grep -v '^\s*#' "$PERF_EVENTS_FILE" | grep -v '^\s*$' | paste -sd,)
  perf_cmd="$PERF stat -e ${perf_events} -o $perfoutput  "

  flush_fs_caches
  echo "$run_cmd" > r.sh
  echo "        => Start [$w - $et - $accessmode - ${nthreads}t - $id]: $(date)"

  stop_redis_server >/dev/null 2>&1
  bash r.sh >/dev/null 2>&1 # daemon mode
  sleep 3

  local R_YCSB_LOAD_CMD="cd ${YCSB_DIR}; mkdir -p ${output_dir}; $CPREFIX -- ./bin/ycsb load redis -s -P workloads/${w} -P ${REDIS_RUN_DIR}/redis-load${propid}.properties > ${loadoutputf} 2>&1"

  echo "        => YCSB Loading data ..."
  ssh -T "${REDIS_CLIENT}" "${R_YCSB_LOAD_CMD}"

  echo "        => Running [$w - $et - ${accessmode} - ${nthreads}t - $id]"
  local R_YCSB_RUN_CMD="cd ${YCSB_DIR}; mkdir -p ${output_dir}; $CPREFIX -- ./bin/ycsb run redis -P workloads/${w} -P ${REDIS_RUN_DIR}/redis-run${propid}.properties -p redis.host=${REDIS_SERVER} -p requestdistribution=${accessmode} -p threadcount=${nthreads} -p measurement.raw.output_file=${rawlatf} >${outputf} 2>&1"

  ssh -T "${REDIS_CLIENT}" "${R_YCSB_RUN_CMD}" &
  cpid=$!

  gpid=$(pgrep redis-server)
  echo "gpid:"; echo ${gpid}
  ${perf_cmd} -p $gpid &
  perf_pid=$!

  wait $cpid 2>/dev/null

  kill -SIGINT ${perf_pid}

  stop_redis_server
  echo "        => End [$w - $et - $accessmode - ${nthreads}t - $id]: $(date)"
  rm -rf r.sh
}

run_seq_cxl_L100() {
  check_cxl_conf
  #bring_all_cpus_online
  for ((i = 0; i < ${#warr[@]}; i++)); do
    w=${warr[$i]}
    m=${marr[$i]}
    propid=${carr[$i]}
    run_one_exp "$w" "L100" "100" "$propid"
  done
}

run_seq_cxl_L0() {
  check_cxl_conf
  local id=$1
  for ((i = 0; i < ${#warr[@]}; i++)); do
    w=${warr[$i]}
    m=${marr[$i]}
    propid=${carr[$i]}
    run_one_exp "$w" "L0" "$id" "$propid"
  done
}

main() {
  ./mod-uncore-freq.sh 2000000 2000000 2000000 2000000
  run_seq_cxl_L100
  run_seq_cxl_L0 1
  ./mod-uncore-freq.sh 2000000 2000000 500000 500000
  run_seq_cxl_L0 2
}
main

exit
