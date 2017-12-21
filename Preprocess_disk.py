import csv
import pandas as pd
import time
import json
from helperAGAIN import *
t11 = time.time()
file = ['business.csv','review-1m.csv','photos.csv']
index_pre = {}
keylist_pre = {}
shape_pre = {}
in_memory = {}
index_attribute = {}
for i in range(len(file)):
    #index_pre[file[i]], shape_pre[file[i]], in_memory[file[i]], index_attribute[file[i]] = Pre_process(file[i])
    index_pre[file[i]], keylist_pre[file[i]], shape_pre[file[i]] = Pre_process_disk(file[i])
#csv_file = 'review-1m.csv'
#index, keylist, shape = Pre_process2(csv_file)
t12 = time.time()
print('preprocess takes time ', t12-t11)

