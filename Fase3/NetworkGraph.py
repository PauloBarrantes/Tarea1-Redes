
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
# Build a dataframe with your connections
fig1 = plt.figure()

df = pd.DataFrame({ 'from':['8080', '8081', '8082','8080'], 'to':['8083', '8080', '8084','8082'], 'value':['typeA', 'typeA', 'typeB', 'typeB']})
df

# And I need to transform my categorical column in a numerical value typeA->1, typeB->2...
df['value']=pd.Categorical(df['value'])
df['value'].cat.codes

def update(i):
    print("GG")
    plt.clf()
    G=nx.from_pandas_edgelist(df, 'from', 'to', create_using=nx.Graph() )
    nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_color=df['value'].cat.codes, width=10.0, edge_cmap=plt.cm.Set2)

# Build your graph
# Custom the nodes:
G=nx.from_pandas_edgelist(df, 'from', 'to', create_using=nx.Graph() )

nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_color=df['value'].cat.codes, width=10.0, edge_cmap=plt.cm.Set2)

ani = animation.FuncAnimation(fig1, update, frames=6, interval=2000, repeat=True)
plt.show()



# Custom the nodes:
