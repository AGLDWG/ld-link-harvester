import pandas as pd

INPUT_FILE = 'au-domains-latest.csv'
data = pd.read_csv(INPUT_FILE)
('http://' + data['domain']).to_csv('aus-domain-urls.txt', header=False, index=None, sep=" ")

