from glob import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

FILES = glob("data/*.csv")

frames = list()
for file_loc in FILES:
    filename = file_loc.split("/")[-1]
    filename = filename.split(".csv")[0]
    params = dict(zip(
        ('peers', '# transactions', 'mean transaction interarrival time', 'mean mining time', 'fraction of slow nodes'),
        map(float, filename.strip().split('_'))))
    df = pd.read_csv(file_loc)
    for param in params:
        df[param] = params[param]
    df = df[df['peer']==1]
    print(df)
    break


import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import matplotlib.pyplot as plt
G = nx.DiGraph()

nodes = set(df.parent_hash.unique()).union(set(df.hash.unique()))
for n in nodes:
    G.add_node(n)

for i, row in df.iterrows():
    G.add_edge(row.parent_hash, row.hash)

# write dot file to use with graphviz
# run "dot -Tpng test.dot >test.png"
write_dot(G,'test.dot')

# same layout using matplotlib with no labels
plt.title('Blockchain tree')
pos=graphviz_layout(G, prog='dot')
nx.draw(G, pos, with_labels=False, arrows=True)
plt.savefig('nx_test.png')



'''
    frames.append(df)
##
df = pd.concat(frames)
#import pdb; pdb.set_trace()
df.rename({"is_fast": 'speed'}, axis=1, inplace=True)
print(df.head())
df.speed = df.speed.replace(True, 'Fast')
df.speed = df.speed.replace(False, 'Slow')
df = df.groupby(['peer', 'mean mining time', '# transactions', 'mean transaction interarrival time', 'fraction of slow nodes', 'speed'])
df = (df.number.apply(lambda x: x.max()/x.count())).reset_index()
df.rename({"number": 'useful blocks'}, axis=1, inplace=True)
# plot = sns.pairplot(df, y_vars=['useful blocks'], x_vars=['mining', 'transactions', 'interarrival', 'z'], hue="speed")
plot = sns.lmplot(data=df, x='mean mining time', y='useful blocks', hue='speed', scatter_kws={'alpha':0.3})
plt.title("Fraction of longest-chain-blocks v. Mean mining time")
plot.savefig("data/output0.png")
plot = sns.lmplot(data=df, x='# transactions', y='useful blocks', hue='speed', scatter_kws={'alpha':0.3})
plt.title("Fraction of longest-chain-blocks v. Number of transactions")
plot.savefig("data/output1.png")
plot = sns.lmplot(data=df, x='mean transaction interarrival time', y='useful blocks', hue='speed', scatter_kws={'alpha':0.3})
plt.title("Fraction of longest-chain-blocks v. Mean interarrival time")
plot.savefig("data/output2.png")
plot = sns.lmplot(data=df, x='fraction of slow nodes', y='useful blocks', hue='speed', scatter_kws={'alpha':0.3})
plt.title("Fraction of longest-chain-blocks v. Fraction of slow nodes")
plot.savefig("data/output3.png")
# plot = sns.lmplot(data=df, x='speed', y='useful blocks')
# plt.title("Fraction of longest-chain-blocks v. Speed")
# plot.savefig("data/output4.png")
'''
