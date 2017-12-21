import csv
import pandas as pd
import time
import json
from helperAGAIN import *
## PREPROCESSING
# def is_float(string):
#   try:
#     return float(string) and '.' in string  # True if string is a number contains a dot
#   except ValueError:  # String is not a number
#     return False
#
# def Pre_process(csv_file):
#     indexed_attribute = []
#     header = list(pd.read_csv(csv_file, nrows = 1).columns.values)
#     index = dict.fromkeys(header)
#     with open(csv_file, 'r') as fin:
#         reader = csv.DictReader(fin)
#         for col in header:
#             index[col] = dict()
#         for i,line in enumerate(reader):
#             for col in header:
#                 if is_float(line[col]):
#                     new_key = float(line[col])
#                 elif line[col].isdigit():
#                     new_key = int(line[col])
#                 else:
#                     new_key = line[col]
#
#                 if new_key not in index[col].keys():
#                     index[col][new_key] = [i]
#                 else:
#                     index[col][new_key].append(i)
#
#         for col in header:
#             if not isinstance(list(index[col].keys())[0], str) and len(index[col].keys()) < (i+1):
#                 indexed_attribute.append(col)
#                 with open(csv_file+'_'+col, 'w') as outfile:
#                     json.dump(index[col], outfile)
#         shape = i+1
#
#     file = pd.read_csv(csv_file)
#     return index, shape, file, indexed_attribute

t11 = time.time()
file = ['business.csv','review-1m.csv','photos.csv']
index_pre = {}
keylist_pre = {}
shape_pre = {}
in_memory = {}
index_attribute = {}
for i in range(len(file)):
    #index_pre[file[i]], shape_pre[file[i]], in_memory[file[i]], index_attribute[file[i]] = Pre_process(file[i])
    index_pre[file[i]], keylist_pre[file[i]], shape_pre[file[i]], in_memory[file[i]] = Pre_process(file[i])
#csv_file = 'review-1m.csv'
#index, keylist, shape = Pre_process2(csv_file)
t12 = time.time()
print('preprocess takes time ', t12-t11)

