import sys
import csv
import numpy as np
import os
import math
import pandas as pd
from collections import OrderedDict

directory = 'rst'
modes = ["aggregate", "interval"]
mem_types = ["LOCAL", "NUMA"]
type_to_file = {"LOCAL": "L100-100.data", "NUMA": "L0-1.data"}

events = ["time", "instructions", "cycles", "CYCLE_ACTIVITY.STALLS_MEM_ANY", \
  "EXE_ACTIVITY.BOUND_ON_STORES", "CYCLE_ACTIVITY.STALLS_L3_MISS", \
  "CYCLE_ACTIVITY.STALLS_L2_MISS", "CYCLE_ACTIVITY.STALLS_L1D_MISS", \
  "EXE_ACTIVITY.1_PORTS_UTIL", "EXE_ACTIVITY.2_PORTS_UTIL", "PARTIAL_RAT_STALLS.SCOREBOARD"]

counters = [e for e in events if e != "time"]

def list_workloads(directory):
  files = []
  for filename in os.listdir(directory):
    if os.path.isdir(os.path.join(directory, filename)):
      files.append(filename)
  files.sort()
  return files

def read_file(file, workload_id, workload_name, mem_type):
  res = OrderedDict()
  res["workload_id"] = workload_id
  res["workload_name"] = workload_name
  res["mem_type"] = mem_type
  with open(file) as csv_file:
    csv_header = csv.reader(csv_file, delimiter=' ')
    line_count = 0
    for row in csv_header:
      line_count += 1
      processed_row = [item for item in row if item]
      if '<not' in processed_row and 'counted>' in processed_row:
        print(processed_row)
        break
      for e in events:
        if e in processed_row:
          value = float(processed_row[0].replace(',', ''))
          res[e] = value
  return res

def read_data(directory, mem_type):
  files = list_workloads(directory)
  data = []
  for i, filename in enumerate(files):
    f = os.path.join(directory, filename)
    f1 = os.path.join(f, type_to_file[mem_type])
    assert os.path.isfile(f1)
    res = read_file(f1, filename+'..'+mem_type, filename, mem_type)
    data.append(res)
  return data

def tocsv(directory, mem_type, csv_path):
  data = read_data(directory, mem_type)
  df = pd.DataFrame(data)
  df.set_index("workload_id", inplace=True)
  filename = os.path.join(csv_path, 'm'+str(mem_type)+'.csv')
  df.to_csv(filename)

def new_separate_csv(directory, csv_path):
  for lat in mem_types:
    tocsv(directory, lat, csv_path)

def merge_csv(csv_path):
  merged_df = pd.DataFrame()
  for t in mem_types:
    filename = os.path.join(csv_path, 'm'+str(t)+'.csv')
    df = pd.read_csv(filename)
    merged_df = pd.concat([merged_df, df])
  out_file = os.path.join(csv_path, 'merged.csv')
  merged_df.set_index("workload_id", inplace=True)
  merged_df.to_csv(out_file)

def read_interval_file(file):
  samples = OrderedDict()
  with open(file) as csv_file:
    csv_header = csv.reader(csv_file, delimiter=' ')
    for row in csv_header:
      processed_row = [item for item in row if item]
      if not processed_row or processed_row[0].startswith('#'):
        continue
      if len(processed_row) < 3:
        continue
      if '<not' in processed_row:
        samples[processed_row[0]] = None
        continue
      event = processed_row[2]
      if event not in counters:
        continue
      ts = processed_row[0]
      if ts not in samples:
        samples[ts] = OrderedDict()
      if samples[ts] is None:
        continue
      samples[ts][event] = float(processed_row[1].replace(',', ''))

  res = []
  dropped = 0
  cum = {e: 0.0 for e in counters}
  prev_time = 0.0
  for ts, values in samples.items():
    if values is None or len(values) != len(counters):
      dropped += 1
      continue
    row = OrderedDict()
    row["interval"] = len(res)
    row["time"] = float(ts)
    row["delta_time"] = float(ts) - prev_time
    prev_time = float(ts)
    for e in counters:
      row[e] = values[e]
    for e in counters:
      cum[e] += values[e]
      row["cum_"+e] = cum[e]
    res.append(row)
  if dropped:
    print("  warning: %s: dropped %d incomplete interval(s)" % (file, dropped))
  return res

def interval_tocsv(directory, mem_type, csv_path):
  files = list_workloads(directory)
  data = []
  for filename in files:
    f1 = os.path.join(directory, filename, type_to_file[mem_type])
    assert os.path.isfile(f1)
    rows = read_interval_file(f1)
    if not rows:
      print("  warning: %s: no usable intervals, skipped" % f1)
      continue

    df = pd.DataFrame(rows)
    df.set_index("interval", inplace=True)
    df.to_csv(os.path.join(csv_path, filename+'.'+mem_type+'.csv'))

    for row in rows:
      out = OrderedDict()
      out["workload_id"] = filename+'..'+mem_type
      out["workload_name"] = filename
      out["mem_type"] = mem_type
      out.update(row)
      data.append(out)

  df = pd.DataFrame(data)
  df.set_index("workload_id", inplace=True)
  df.to_csv(os.path.join(csv_path, 'm'+str(mem_type)+'.csv'))

def interval_separate_csv(directory, csv_path):
  for lat in mem_types:
    interval_tocsv(directory, lat, csv_path)

def process_mode(mode, rst_dir, csv_path):
  if not os.path.exists(csv_path):
    os.makedirs(csv_path)
  print("==> %s: %s -> %s" % (mode, rst_dir, csv_path))
  if mode == "interval":
    interval_separate_csv(rst_dir, csv_path)
  else:
    new_separate_csv(rst_dir, csv_path)
  merge_csv(csv_path)

def main():
  csv_root = "csv"
  wanted = sys.argv[1:] if len(sys.argv) > 1 else modes
  for mode in wanted:
    if mode not in modes:
      print("error: unknown mode '%s', expected one of %s" % (mode, modes))
      exit(1)

  found = [m for m in wanted if os.path.isdir(os.path.join(directory, m))]
  if not found:
    if len(sys.argv) > 1:
      print("error: none of %s exist under %s/" % (wanted, directory))
      exit(1)
    if list_workloads(directory):
      print("==> no mode sub-dir under %s/, treating it as aggregate" % directory)
      process_mode("aggregate", directory, os.path.join(csv_root, "aggregate"))
      return
    print("error: no results found under %s/" % directory)
    exit(1)

  for mode in wanted:
    if mode not in found:
      print("==> %s/%s not found, skipped" % (directory, mode))
      continue
    process_mode(mode, os.path.join(directory, mode), os.path.join(csv_root, mode))

if __name__ == "__main__":
  main()
