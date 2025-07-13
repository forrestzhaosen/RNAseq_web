import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv('splice_vault.tsv.gz', sep='\t')
engine = create_engine('sqlite:///splice_vault.db')
df.to_sql('splice_vault', engine, if_exists='replace', index=False)
