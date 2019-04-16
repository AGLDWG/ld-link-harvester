import pandas as pd

IN_FILE = 'aus-domain-urls.txt'
START_IDX = 1186
BLOCK_SIZE = 100
OUT_FILE_PREFIX = 'partition_data/aus-domain-urls'

data = pd.read_csv(IN_FILE)
data_length = len(data)
for i in range(int(data_length - START_IDX / BLOCK_SIZE)):
    if i == 0:
        lower_bound = START_IDX
    else:
        lower_bound = upper_bound
    upper_bound = lower_bound + BLOCK_SIZE
    if upper_bound >= data_length:
        upper_bound = data_length - 1
        out_file = '{}_{}_{}_{}.txt'.format(OUT_FILE_PREFIX, lower_bound, upper_bound, upper_bound - lower_bound)
        (data.iloc[lower_bound:upper_bound, :]).to_csv(out_file, header=False, index=None, sep=" ")
        break
    out_file = '{}_{}_{}_{}.txt'.format(OUT_FILE_PREFIX, lower_bound, upper_bound, upper_bound - lower_bound)
    (data.iloc[ lower_bound:upper_bound, : ]).to_csv(out_file, header=False, index=None, sep=" ")

