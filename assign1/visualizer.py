from glob import glob
import pandas as pd
import seaborn as sns

FILES = glob("data/*.csv")

frames = list()
for file_loc in FILES:
    filename = file_loc.split("/")[-1]
    filename = filename.split(".csv")[0]
    params = dict(zip(
        ('peers', 'transactions', 'interarrival', 'mining', 'z'),
        map(float, filename.strip().split('_'))))
    df = pd.read_csv(file_loc)
    for param in params:
        df[param] = params[param]
    frames.append(df)
df = pd.concat(frames)
df = df.groupby(['peer', 'mining', 'transactions', 'interarrival', 'z', 'is_fast'])
df = (df.number.apply(lambda x: x.max()/x.count())).reset_index()
