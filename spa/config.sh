#!/bin/bash

get_sysinfo()
{
  uname -a
  echo "--------------------------"
  sudo numactl --hardware
  echo "--------------------------"
  lscpu
  echo "--------------------------"
  cat /proc/cpuinfo
  echo "--------------------------"
  cat /proc/meminfo
}

disable_thp()
{
  echo "never" | sudo tee /sys/kernel/mm/transparent_hugepage/enabled >/dev/null 2>&1
}

disable_numa_balancing()
{
  echo 0 | sudo tee /proc/sys/kernel/numa_balancing >/dev/null 2>&1
}

disable_ksm()
{
  echo 0 | sudo tee /sys/kernel/mm/ksm/run >/dev/null 2>&1
}

disable_turbo()
{
  echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo >/dev/null 2>&1
}

disable_nmi_watchdog()
{
  echo 0 | sudo tee /proc/sys/kernel/nmi_watchdog >/dev/null 2>&1
}

flush_fs_caches()
{
  echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null 2>&1
  sleep 5
}

disable_ht()
{
  echo off | sudo tee /sys/devices/system/cpu/smt/control >/dev/null 2>&1
}

bring_all_cpus_online()
{
  echo 1 | sudo tee /sys/devices/system/cpu/cpu*/online >/dev/null 2>&1
}

set_performance_mode()
{
  for governor in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance | sudo tee $governor >/dev/null 2>&1
  done
}

configure_cxl_exp_cores()
{
  echo 1 | sudo tee /sys/devices/system/cpu/cpu*/online >/dev/null 2>&1
  echo 0 | sudo tee /sys/devices/system/node/node1/cpu*/online >/dev/null 2>&1
}

disable_va_aslr()
{
  echo 0 | sudo tee /proc/sys/kernel/randomize_va_space >/dev/null 2>&1
}

disable_swap()
{
  sudo swapoff -a
}

check_cxl_conf()
{
  set_performance_mode
  disable_nmi_watchdog
  disable_va_aslr
  disable_ksm
  disable_numa_balancing
  disable_thp
  disable_ht
  disable_turbo
  disable_swap
  configure_cxl_exp_cores
}

check_conf()
{
  set_performance_mode
  disable_nmi_watchdog
  disable_va_aslr
  disable_ksm
  disable_numa_balancing
  disable_thp
  disable_ht
  disable_turbo
  disable_swap
}

monitor_resource_util()
{
  while true; do
    local o=$(sudo numactl --hardware)
    local node0_free_mb=$(echo "$o" | grep "node 0 free" | awk '{print $4}')
    local node1_free_mb=$(echo "$o" | grep "node 1 free" | awk '{print $4}')
    echo "$(date +"%D %H%M%S") ${node0_free_mb} ${node1_free_mb}"
    sleep 5
  done
}

