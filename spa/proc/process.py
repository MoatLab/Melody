import sys
import csv
import matplotlib.pyplot as plt
import numpy as np
import os
import pylab
import pandas as pd

events = ["time", "instructions", "cycles", "CYCLE_ACTIVITY.STALLS_MEM_ANY", \
  "EXE_ACTIVITY.BOUND_ON_STORES", "CYCLE_ACTIVITY.STALLS_L3_MISS", \
  "CYCLE_ACTIVITY.STALLS_L2_MISS", "CYCLE_ACTIVITY.STALLS_L1D_MISS", \
  "EXE_ACTIVITY.1_PORTS_UTIL", "EXE_ACTIVITY.2_PORTS_UTIL", "PARTIAL_RAT_STALLS.SCOREBOARD"]

sd_m = ["cycles"]
load_sd_m = ["CYCLE_ACTIVITY.STALLS_MEM_ANY", "cycles"]
store_sd_m = ["EXE_ACTIVITY.BOUND_ON_STORES", "cycles"]
cache_sd_m = ["CYCLE_ACTIVITY.STALLS_MEM_ANY", "CYCLE_ACTIVITY.STALLS_L3_MISS", "cycles"]
dram_sd_m = ["CYCLE_ACTIVITY.STALLS_L3_MISS", "cycles"]
l1_sd_m = ["CYCLE_ACTIVITY.STALLS_MEM_ANY", "CYCLE_ACTIVITY.STALLS_L1D_MISS", "cycles"]
l2_sd_m = ["CYCLE_ACTIVITY.STALLS_L1D_MISS", "CYCLE_ACTIVITY.STALLS_L2_MISS", "cycles"]
l3_sd_m = ["CYCLE_ACTIVITY.STALLS_L2_MISS", "CYCLE_ACTIVITY.STALLS_L3_MISS", "cycles"]
core_sd_m = ["EXE_ACTIVITY.1_PORTS_UTIL", "EXE_ACTIVITY.2_PORTS_UTIL", "PARTIAL_RAT_STALLS.SCOREBOARD", "cycles"]

def check_file_exist(file):
  if not os.path.isfile(file):
    print(file + "is not existed")
    exit(0)

def get_vals(event_name, mem_type, csv_path):
  filename = os.path.join(csv_path, 'm'+str(mem_type)+'.csv')
  check_file_exist(filename)
  df = pd.read_csv(filename, index_col ="workload_id")
  columns = df.columns.values.tolist()
  assert event_name in events
  assert event_name in columns
  res = []
  for val in df[event_name]:
    res.append(val)
  return np.asarray(res)

def get_workloads(df):
  columns = df.columns.values.tolist()
  assert "workload_name" in columns
  workloads = []
  for name in df["workload_name"]:
    if name not in workloads:
      workloads.append(name)
  return workloads

def get_slowdowns(t1, t2, metric, csv_path):
  if len(metric) == 1:
    v1, v2 = get_vals(metric[0], t1, csv_path), get_vals(metric[0], t2, csv_path)
    return (v2-v1)/v1
  elif len(metric) == 2:
    v1, v2 = get_vals(metric[0], t1, csv_path), get_vals(metric[0], t2, csv_path)
    cyc1 = get_vals(metric[1], t1, csv_path)
    return (v2 - v1)/cyc1
  elif len(metric) == 3:
    a1, a2 = get_vals(metric[0], t1, csv_path), get_vals(metric[0], t2, csv_path)
    b1, b2 = get_vals(metric[1], t1, csv_path), get_vals(metric[1], t2, csv_path)
    cyc1 = get_vals(metric[2], t1, csv_path)
    return ((a2-b2)-(a1-b1))/cyc1
  elif len(metric) == 4:
    a1, a2 = get_vals(metric[0], t1, csv_path), get_vals(metric[0], t2, csv_path)
    b1, b2 = get_vals(metric[1], t1, csv_path), get_vals(metric[1], t2, csv_path)
    c1, c2 = get_vals(metric[2], t1, csv_path), get_vals(metric[2], t2, csv_path)
    cyc1 = get_vals(metric[3], t1, csv_path)
    return ((a2-a1)+(b2-b1)+(c2-c1))/cyc1
  print("error")
  exit(0)

def cal_vals(metric, latency, csv_path):
  vals = []
  events = metric['events']
  for e in events:
    vals.append(get_vals(e, latency, csv_path))
  return metric['function'](vals)

def draw_bars_b(data, x, output_path, filename, loc, xlabel, ylabel, title):
  xs = range(len(x))
  [store_sd, dram_sd, l3_sd, l2_sd, l1_sd, core_sd, other] = data

  plt.bar([i for i in xs], height=store_sd, width=0.3, \
    label='store', color='lightcoral')
  plt.bar([i for i in xs], height=dram_sd, width=0.3, \
    bottom=store_sd, label='DRAM', color='cornflowerblue')
  plt.bar([i for i in xs], height=l3_sd, width=0.3, \
    bottom=store_sd+dram_sd, label='l3', color='darkgreen')
  plt.bar([i for i in xs], height=l2_sd, width=0.3, \
    bottom=store_sd+dram_sd+l3_sd, label='l2', color='forestgreen')
  plt.bar([i for i in xs], height=l1_sd, width=0.3, \
    bottom=store_sd+dram_sd+l3_sd+l2_sd, label='l1', color='lime')
  plt.bar([i for i in xs], height=core_sd, width=0.3, \
    bottom=store_sd+dram_sd+l3_sd+l2_sd+l1_sd, label='core', color='violet')
  plt.bar([i for i in xs], height=other, width=0.3, \
    bottom=store_sd+dram_sd+l3_sd+l2_sd+l1_sd+core_sd, label='other', color='gold')
  plt.xticks(xs, x, rotation='vertical', fontsize=6)
  plt.xlabel(xlabel, fontsize=9)
  plt.ylabel(ylabel, fontsize=9)
  plt.subplots_adjust(bottom=0.25)
  plt.title(title, fontsize=10)
  plt.legend(loc='upper center', borderpad=0.0, labelspacing=0.1, \
    bbox_to_anchor=(loc[0], loc[1]), prop={'size': 7})
  plt.savefig(output_path+'/'+filename+'.png', format='png')
  plt.clf()

def main():
  csv_path = "csv"
  isExist = os.path.exists(csv_path)
  if not isExist:
    print("error: csv is not exist")
    exit()
  filename = os.path.join(csv_path, 'merged.csv')
  df = pd.read_csv(filename, index_col ="workload_id")
  workloads = get_workloads(df)
  # workloads.sort()
  # print(workloads)
  sd = get_slowdowns("LOCAL", "NUMA", sd_m, csv_path)
  dram_sd = get_slowdowns("LOCAL", "NUMA", dram_sd_m, csv_path)
  l3_sd = get_slowdowns("LOCAL", "NUMA", l3_sd_m, csv_path)
  l2_sd = get_slowdowns("LOCAL", "NUMA", l2_sd_m, csv_path)
  l1_sd = get_slowdowns("LOCAL", "NUMA", l1_sd_m, csv_path)
  store_sd = get_slowdowns("LOCAL", "NUMA", store_sd_m, csv_path)
  core_sd = get_slowdowns("LOCAL", "NUMA", core_sd_m, csv_path)
  other = sd - dram_sd - l3_sd - l2_sd - l1_sd - store_sd - core_sd

  output_path = "plots"
  isExist = os.path.exists(output_path)
  if not isExist:
    os.makedirs(output_path)
  draw_bars_b([store_sd, dram_sd, l3_sd, l2_sd, l1_sd, core_sd, other], \
    workloads, output_path, "sd_breakdown", [0.17, 1.01], \
    "Workloads", "Slowdown", "Slowdown Breakdown")

if __name__ == "__main__":
  main()
