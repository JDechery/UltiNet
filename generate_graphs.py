import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpim
import csv
import codecs
import numpy as np
from haversine import haversine


def get_team_locations_df(filepath):
    """
    Read csv data from filepath with lines as (team, city, state)
    and return DataFrame.
    """
    data = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row:
                data.append(row)
    data = list(zip(*data))
    towns = pd.DataFrame(data={'team': data[0], 'city': data[1], 'state': data[2]})
    towns['city'] = towns['city'].map(lambda x: x.title())
    anecdotes = {'Greater Detroit': 'Detroit',
                 'Nyc': 'New York',
                 'Baton Rouge/New Orleans': 'New Orleans'}
    towns['city'] = towns['city'].replace(anecdotes)
    towns['city'] = towns['city'].apply(lambda x: x.split('/')[0])
    return towns


def get_city_locations(filepath):
    """
    Read in city locations txt file from
    https://www.maxmind.com/en/free-world-cities-database
    Encoding issues require codecs to ignore errors.
    """
    citydata = []
    usecols = [1, 3, 5, 6]
    keep_countries = ['ca', 'us']
    # Cannot figure out encoding of this data. Need to make custom codec to ignore decoding errors
    with codecs.open(filepath, encoding='utf-8', errors='ignore') as f:
        for line in f:
            fields = line.strip('\n').split(',')
            if fields[0] in keep_countries:
                citydata.append(tuple(fields[x] for x in usecols))
    return citydata


def get_score_df(filepath):
    """Convert scores csv file to DataFrame."""
    scores = pd.read_csv(filepath)
    # remove seeds from team names
    scores['home'] = scores['home'].apply(lambda x: str(x).split('(')[0].strip('!'))
    scores['away'] = scores['away'].apply(lambda x: str(x).split('(')[0].strip('!'))
    # remove games from cancelled tournaments => teamname is 'nan'
    scores = scores[scores['home'] != 'nan']
    scores = scores[scores['away'] != 'nan']
    # remove games with no score reported
    scores = scores[~scores['homescore'].isin(['W', 'L', 'F'])]
    scores[['homescore', 'awayscore']] = scores[['homescore', 'awayscore']].astype(int)
    scores = scores[~scores['awayscore'].isin(['W', 'L', 'F'])]
    scores = scores[scores[['homescore', 'awayscore']].apply(sum, axis=1) > 0]
    return scores


# %%
citydata = get_city_locations("geodata\\worldcitiespop.txt")
citydf = pd.DataFrame.from_records(data=citydata[1:], columns=['city', 'state', 'latitude', 'longitude'])
citydf['city'] = citydf['city'].map(lambda x: x.title())
citydf['latitude'] = citydf['latitude'].astype(float)
citydf['longitude'] = citydf['longitude'].astype(float)

# %% merge town & location data
towns = get_team_locations_df("ultiscores\\hometowns_Mixed.csv")
team_locations = towns.merge(citydf, how='left', on=['city', 'state'])
team_locations.dropna(axis=0, inplace=True)

# %% get score data and create nx graph
scores = get_score_df('ultiscores\\2016_mixed_regular_season_results.csv')
graph = nx.from_pandas_dataframe(scores, source='home', target='away', create_using=nx.Graph())
missing_cities = set(graph.nodes()).difference(set(team_locations['team']))
graph.remove_nodes_from(missing_cities)

# %% load usmap image and plot team locations
# Future direction to find the affine transform to fit map overlay
usmap = mpim.imread("geodata\\USA-Map-Blank.gif")
node_location = dict(zip(team_locations['team'], team_locations[['longitude', 'latitude']].values))
boundaries = [-125.5, -66.5, 26., 49.5]  # empirically found latitude/longitude of contiguous us border

plt.figure(figsize=(30, 5))
nx.draw(graph, node_size=15, pos=node_location, node_color='b')
plt.imshow(usmap, extent=boundaries, alpha=.4)
plt.title('Regular season competition graph (US state overlay only for visual guide; not to scale)', fontsize=14)
plt.show()

# %% create ER graph for comparison
N = graph.number_of_nodes()
ergraphs = [nx.erdos_renyi_graph(N, graph.number_of_edges() / (N**2-N)) for x in range(20)]

# %% look at graph clustering
bin_edges = np.linspace(0, 1, 10)
clustering = nx.clustering(graph)
erclust = [nx.clustering(erg) for erg in ergraphs]
erclust = np.asarray([list(x.values()) for x in erclust])
data_clust = np.histogram(np.asarray(list(clustering.values())), bins=bin_edges)[0]
data_clust = np.divide(data_clust, sum(data_clust))
mean_er_clust = np.zeros_like(data_clust)
for rep in range(20):
    mean_er_clust += np.histogram(erclust[rep, :], bins=bin_edges)[0]
mean_er_clust = np.divide(mean_er_clust, sum(mean_er_clust))
# %% plotfig
fig, ax = plt.subplots(1, figsize=(7, 5))
bdata = ax.bar(bin_edges[:-1], data_clust, width=.05, color='b')
brand = ax.bar(.05+bin_edges[:-1], mean_er_clust, width=.05, color='r')
ax.set_ylabel('Probability', fontsize=13)
ax.set_xlabel('Node clustering coefficient', fontsize=13)
ax.legend((bdata[0], brand[0]), ('data', '<ER>'), fontsize=13)
plt.show()

# %% look at mean distance of edges. Distance found with haversize formula on lat/long points
dists = {}
for team in graph.nodes_iter():
    opponents = [opp[1] for opp in graph.edges_iter([team])]
    points = team_locations[['latitude', 'longitude']].loc[team_locations['team'].isin(opponents)]
    points = [tuple(row) for _, row in points.iterrows()]
    source_pt = tuple(team_locations[['latitude', 'longitude']].loc[team_locations['team'] == team].values[0])
    dists[team] = [haversine(source_pt, pt, miles=True) for pt in points]
    dists[team] = list(filter(lambda x: x != 0, dists[team]))

meandist = {key: np.mean(val) for key, val in dists.items()}
ngames = {key: len(val) for key, val in dists.items()}
# %% plotfig
pts = [(ngames[key], meandist[key]) for key in meandist]
xpt, ypt = zip(*pts)
plt.scatter(list(xpt), list(ypt))
plt.show()
