import sys
import csv
import matplotlib.pyplot as plt
import numpy as np
import os
import pylab
import pandas as pd

modes = ["aggregate", "interval"]
mem_types = ["LOCAL", "NUMA"]

NUM_INTERVALS = 200

events = ["time", "instructions", "cycles", "CYCLE_ACTIVITY.STALLS_MEM_ANY", \
  "EXE_ACTIVITY.BOUND_ON_STORES", "CYCLE_ACTIVITY.STALLS_L3_MISS", \
  "CYCLE_ACTIVITY.STALLS_L2_MISS", "CYCLE_ACTIVITY.STALLS_L1D_MISS", \
  "EXE_ACTIVITY.1_PORTS_UTIL", "EXE_ACTIVITY.2_PORTS_UTIL", "PARTIAL_RAT_STALLS.SCOREBOARD"]

counters = [e for e in events if e != "time"]

sd_m = ["cycles"]
load_sd_m = ["CYCLE_ACTIVITY.STALLS_MEM_ANY", "cycles"]
store_sd_m = ["EXE_ACTIVITY.BOUND_ON_STORES", "cycles"]
cache_sd_m = ["CYCLE_ACTIVITY.STALLS_MEM_ANY", "CYCLE_ACTIVITY.STALLS_L3_MISS", "cycles"]
dram_sd_m = ["CYCLE_ACTIVITY.STALLS_L3_MISS", "cycles"]
l1_sd_m = ["CYCLE_ACTIVITY.STALLS_MEM_ANY", "CYCLE_ACTIVITY.STALLS_L1D_MISS", "cycles"]
l2_sd_m = ["CYCLE_ACTIVITY.STALLS_L1D_MISS", "CYCLE_ACTIVITY.STALLS_L2_MISS", "cycles"]
l3_sd_m = ["CYCLE_ACTIVITY.STALLS_L2_MISS", "CYCLE_ACTIVITY.STALLS_L3_MISS", "cycles"]
core_sd_m = ["EXE_ACTIVITY.1_PORTS_UTIL", "EXE_ACTIVITY.2_PORTS_UTIL", "PARTIAL_RAT_STALLS.SCOREBOARD", "cycles"]

breakdown_m = [store_sd_m, dram_sd_m, l3_sd_m, l2_sd_m, l1_sd_m, core_sd_m]
breakdown_labels = ['store', 'DRAM', 'l3', 'l2', 'l1', 'core', 'other']
breakdown_colors = ['lightcoral', 'cornflowerblue', 'darkgreen', 'forestgreen', \
  'lime', 'violet', 'gold']

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

def slowdown_from_vals(metric, v1, v2):
  if len(metric) == 1:
    a1, a2 = v1[metric[0]], v2[metric[0]]
    return (a2-a1)/a1
  elif len(metric) == 2:
    a1, a2 = v1[metric[0]], v2[metric[0]]
    cyc1 = v1[metric[1]]
    return (a2 - a1)/cyc1
  elif len(metric) == 3:
    a1, a2 = v1[metric[0]], v2[metric[0]]
    b1, b2 = v1[metric[1]], v2[metric[1]]
    cyc1 = v1[metric[2]]
    return ((a2-b2)-(a1-b1))/cyc1
  elif len(metric) == 4:
    a1, a2 = v1[metric[0]], v2[metric[0]]
    b1, b2 = v1[metric[1]], v2[metric[1]]
    c1, c2 = v1[metric[2]], v2[metric[2]]
    cyc1 = v1[metric[3]]
    return ((a2-a1)+(b2-b1)+(c2-c1))/cyc1
  print("error")
  exit(0)

def get_slowdowns(t1, t2, metric, csv_path):
  v1 = {e: get_vals(e, t1, csv_path) for e in metric}
  v2 = {e: get_vals(e, t2, csv_path) for e in metric}
  return slowdown_from_vals(metric, v1, v2)

def get_breakdown(get_sd):
  sd = get_sd(sd_m)
  parts = [get_sd(m) for m in breakdown_m]
  other = sd
  for p in parts:
    other = other - p
  return sd, parts + [other]

def cal_vals(metric, latency, csv_path):
  vals = []
  events = metric['events']
  for e in events:
    vals.append(get_vals(e, latency, csv_path))
  return metric['function'](vals)

def read_interval_series(csv_path, workload, mem_type):
  filename = os.path.join(csv_path, workload+'.'+mem_type+'.csv')
  check_file_exist(filename)
  df = pd.read_csv(filename)
  return {e: np.asarray(df[e], dtype=float) for e in counters}

def cal_interval(series1, series2, num_intervals):
  total1, total2 = series1["instructions"].sum(), series2["instructions"].sum()
  return int(min(total1, total2)/num_intervals)

def process_integrate_data(series, instr_interval):
  instructions = series["instructions"]
  others = [e for e in series if e != "instructions"]

  cum_instr = []
  results = {e: [] for e in others}

  delta_instr = 0.0
  sum_instr = 0.0
  delta_others = {e: 0.0 for e in others}
  instr_in_prev = 0.0
  others_in_prev = {e: 0.0 for e in others}

  for i in range(len(instructions)):
    delta_instr += instructions[i]
    for e in others:
      delta_others[e] += series[e][i]

    while delta_instr >= instr_interval:
      instr_in_new_interval = instr_interval - instr_in_prev
      proportion = float(instr_in_new_interval)/float(instructions[i])

      sum_instr += instr_in_new_interval + instr_in_prev
      cum_instr.append(sum_instr)

      for e in others:
        results[e].append(proportion*series[e][i] + others_in_prev[e])
        delta_others[e] -= results[e][-1]

      delta_instr -= instr_interval
      instr_in_prev = 0.0
      for e in others:
        others_in_prev[e] = 0.0

    assert delta_instr < instr_interval
    instr_in_prev = delta_instr
    for e in others:
      others_in_prev[e] = delta_others[e]

  if delta_instr > 0:
    sum_instr += delta_instr
    cum_instr.append(sum_instr)
    for e in others:
      results[e].append(delta_others[e])

  return np.asarray(cum_instr), {e: np.asarray(v) for e, v in results.items()}

def trim_2_arr(x1, x2):
  if len(x1) < len(x2):
    x2 = x2[:len(x1)-1]
    x1 = x1[:-1]
  elif len(x2) < len(x1):
    x1 = x1[:len(x2)-1]
    x2 = x2[:-1]
  else:
    x1 = x1[:-1]
    x2 = x2[:-1]
  assert len(x1) == len(x2)
  return np.asarray(x1), np.asarray(x2)

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

def plot_one(x, y, output_path, filename, xlabel, ylabel, title):
  assert len(x) == len(y)
  plt.plot(x, y, marker='', linewidth=0.8)
  plt.xlim(left=0)
  plt.ylim(bottom=0)
  plt.xlabel(xlabel, fontsize=9)
  plt.ylabel(ylabel, fontsize=9)
  plt.title(title, fontsize=10)
  plt.savefig(output_path+'/'+filename+'.png', format='png')
  plt.clf()

def draw_area_b(data, x, output_path, filename, xlabel, ylabel, title):
  bottom = np.zeros(len(x))
  for vals, label, color in zip(data, breakdown_labels, breakdown_colors):
    top = bottom + vals
    plt.plot(x, top, marker='', linewidth=0.5, color=color)
    plt.fill_between(x, bottom, top, color=color, label=label)
    bottom = top
  plt.plot(x, bottom, marker='', linewidth=0.8, color='black', label='slowdown')
  plt.xlim(left=0)
  plt.ylim(bottom=0)
  plt.xlabel(xlabel, fontsize=9)
  plt.ylabel(ylabel, fontsize=9)
  plt.title(title, fontsize=10)
  plt.legend(loc='upper center', borderpad=0.0, labelspacing=0.1, \
    bbox_to_anchor=(0.17, 1.01), prop={'size': 7})
  plt.savefig(output_path+'/'+filename+'.png', format='png')
  plt.clf()

def run_aggregate(csv_path, plots_path):
  filename = os.path.join(csv_path, 'merged.csv')
  check_file_exist(filename)
  df = pd.read_csv(filename, index_col ="workload_id")
  workloads = get_workloads(df)

  sd, data = get_breakdown( \
    lambda m: get_slowdowns(mem_types[0], mem_types[1], m, csv_path))

  if not os.path.exists(plots_path):
    os.makedirs(plots_path)
  draw_bars_b(data, workloads, plots_path, "sd_breakdown", [0.17, 1.01], \
    "Workloads", "Slowdown", "Slowdown Breakdown")

def run_interval(csv_path, plots_path, num_intervals):
  filename = os.path.join(csv_path, 'merged.csv')
  check_file_exist(filename)
  df = pd.read_csv(filename, index_col ="workload_id")
  workloads = get_workloads(df)

  for w in workloads:
    s1 = read_interval_series(csv_path, w, mem_types[0])
    s2 = read_interval_series(csv_path, w, mem_types[1])

    instr_interval = cal_interval(s1, s2, num_intervals)
    if instr_interval <= 0:
      print("  warning: %s: too few instructions for %d intervals, skipped" \
        % (w, num_intervals))
      continue

    instr_1, b1 = process_integrate_data(s1, instr_interval)
    instr_2, b2 = process_integrate_data(s2, instr_interval)
    instr_1, instr_2 = trim_2_arr(instr_1, instr_2)
    length = len(instr_1)
    v1 = {e: b1[e][:length] for e in b1}
    v2 = {e: b2[e][:length] for e in b2}

    sd, data = get_breakdown(lambda m: slowdown_from_vals(m, v1, v2))

    output_path = os.path.join(plots_path, w)
    if not os.path.exists(output_path):
      os.makedirs(output_path)
    plot_one(instr_1, sd, output_path, "slowdown", \
      "Instructions", "Slowdown", w + ": Overall Slowdown")
    draw_area_b(data, instr_1, output_path, "breakdown", \
      "Instructions", "Slowdown", w + ": Slowdown Breakdown")
    print("  %s: %d intervals of %d instructions" % (w, length, instr_interval))

def main():
  csv_root = "csv"
  plots_root = "plots"

  args = sys.argv[1:]
  num_intervals = NUM_INTERVALS
  wanted = []
  i = 0
  while i < len(args):
    if args[i] == "--bins":
      if i+1 >= len(args):
        print("error: --bins needs a value")
        exit(1)
      num_intervals = int(args[i+1])
      i += 1
    elif args[i].startswith("--bins="):
      num_intervals = int(args[i].split("=", 1)[1])
    else:
      wanted.append(args[i])
    i += 1

  if num_intervals < 1:
    print("error: --bins must be >= 1")
    exit(1)
  if not wanted:
    wanted = modes
  for mode in wanted:
    if mode not in modes:
      print("error: unknown mode '%s', expected one of %s" % (mode, modes))
      exit(1)

  found = [m for m in wanted if os.path.isdir(os.path.join(csv_root, m))]
  if not found:
    print("error: none of %s exist under %s/, run update_data.py first" \
      % (wanted, csv_root))
    exit(1)

  for mode in wanted:
    if mode not in found:
      print("==> %s/%s not found, skipped" % (csv_root, mode))
      continue
    csv_path = os.path.join(csv_root, mode)
    plots_path = os.path.join(plots_root, mode)
    print("==> %s: %s -> %s" % (mode, csv_path, plots_path))
    if mode == "interval":
      run_interval(csv_path, plots_path, num_intervals)
    else:
      run_aggregate(csv_path, plots_path)

if __name__ == "__main__":
  main()
