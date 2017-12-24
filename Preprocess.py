import csv
import pandas as pd
import time
import json
## PREPROCESSING

for csv_file in ['business.csv','review-1m.csv','photos.csv']:
    header = list(pd.read_csv(csv_file, nrows = 1).columns.values)
    index = dict.fromkeys(header)
    with open(csv_file, 'r') as fin:
        reader = csv.DictReader(fin)
        for col in header:
            index[col] = dict()
        for i,line in enumerate(reader):
            for col in header:
                if is_float(line[col]):
                    new_key = float(line[col])
                elif line[col].isdigit():
                    new_key = int(line[col])
                else:
                    new_key = line[col]

                if new_key not in index[col].keys():
                    index[col][new_key] = [i]
                else:
                    index[col][new_key].append(i)

        shape = i+1

    for col in header:
        if 'attributes' not in col and 'hours' not in col:
            keylen = max([len(str(l)) for l in list(index[col].keys())])
            if keylen < 30 and len(index[col].keys()) < int(0.3 * shape):
                save_index = index[col]

                with open(csv_file+'_'+col+'_indexing.json', 'w') as outfile:
                    json.dump(save_index, outfile)

    shape_d = {}
    shape_d[0] = shape
    with open(csv_file + '_shape.json', 'w') as outfile:
        json.dump(shape_d, outfile)
