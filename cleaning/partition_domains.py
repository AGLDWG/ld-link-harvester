import pandas as pd

IN_FILE = 'aus-domain-urls.txt'
START_IDX = 0
BLOCK_SIZE = [10, 20, 50, 100, 1000, 100000, 1000000]
OUT_FILE_PREFIX = 'aus-domain-urls'

data = pd.read_csv(IN_FILE)
data_length = len(data)
for i in range(len(BLOCK_SIZE)):
    if i == 0:
        lower_bound = 0
    else:
        lower_bound = upper_bound
    if i == len(BLOCK_SIZE) - 1:
        upper_bound = data_length
    else:
        upper_bound = lower_bound + BLOCK_SIZE[i]
    out_file = '{}_{}_{}_{}.txt'.format(OUT_FILE_PREFIX, lower_bound, upper_bound, upper_bound - lower_bound)
    (data.iloc[ lower_bound:upper_bound, : ]).to_csv(out_file, header=False, index=None, sep=" ")

