import sys
import csv
import numpy as np
import os
import math
import pandas as pd
from collections import OrderedDict

directory = 'rst'
mem_types = ["LOCAL", "NUMA"]
type_to_file = {"LOCAL": "L100-100.data", "NUMA": "L0-1.data"}

events = ["time", "instructions", "cycles", "CYCLE_ACTIVITY.STALLS_MEM_ANY", \
  "EXE_ACTIVITY.BOUND_ON_STORES", "CYCLE_ACTIVITY.STALLS_L3_MISS", \
  "CYCLE_ACTIVITY.STALLS_L2_MISS", "CYCLE_ACTIVITY.STALLS_L1D_MISS", \
  "EXE_ACTIVITY.1_PORTS_UTIL", "EXE_ACTIVITY.2_PORTS_UTIL", "PARTIAL_RAT_STALLS.SCOREBOARD"]

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
  files = []
  for filename in os.listdir(directory):
    files.append(filename)
  files.sort()
  data = []
  for i, filename in enumerate(files):
    f = os.path.join(directory, filename)
    f1 = os.path.join(f, type_to_file[mem_type])
    assert os.path.isfile(f1)
    res = read_file(f1, filename+'..'+mem_type, filename, mem_type)
    data.append(res)
  return data

def tocsv(mem_type, csv_path):
  data = read_data(directory, mem_type)
  df = pd.DataFrame(data)
  df.set_index("workload_id", inplace=True)
  filename = os.path.join(csv_path, 'm'+str(mem_type)+'.csv')
  df.to_csv(filename)

def new_separate_csv(csv_path):
  for lat in mem_types:
    tocsv(lat, csv_path)

def merge_csv(csv_path):
  merged_df = pd.DataFrame()
  for t in mem_types:
    filename = os.path.join(csv_path, 'm'+str(t)+'.csv')
    df = pd.read_csv(filename)
    merged_df = pd.concat([merged_df, df])
  out_file = os.path.join(csv_path, 'merged.csv')
  merged_df.set_index("workload_id", inplace=True)
  merged_df.to_csv(out_file)

def main():
  csv_path = "csv"
  isExist = os.path.exists(csv_path)
  if not isExist:
    os.makedirs(csv_path)

  new_separate_csv(csv_path)
  merge_csv(csv_path)

if __name__ == "__main__":
  mem_types = ["LOCAL", "NUMA"]
  main()

