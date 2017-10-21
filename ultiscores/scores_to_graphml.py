import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def createGraph(tourneyScores):
    gameResults = pd.DataFrame()
    winnerBool = tourneyScores['homescore'].astype(int) > tourneyScores['awayscore'].astype(int)
    gameResults['winner'] = pd.concat([tourneyScores.loc[winnerBool, 'home'], tourneyScores.loc[~winnerBool, 'away']])
    gameResults['loser'] = pd.concat([tourneyScores.loc[winnerBool,'away'], tourneyScores.loc[~winnerBool, 'home']])
    graph = nx.from_pandas_dataframe(gameResults, source='loser', target='winner', create_using=nx.MultiDiGraph())
    return graph

scores = pd.read_csv('scores.csv')
#remove seeds from team names
scores['home'] = scores['home'].apply(lambda x: str(x).split('(')[0])
scores['away'] = scores['away'].apply(lambda x: str(x).split('(')[0])
#remove games from cancelled tournaments => teamname is 'nan'
scores = scores[scores['home'] != 'nan']
scores = scores[scores['away'] != 'nan']
###start with only mens games
scores = scores[scores['div'] == 'Men']
###remove games with no score reported
scores = scores[~scores['homescore'].isin(['W','L','F'])]
scores = scores[~scores['awayscore'].isin(['W','L','F'])]
scores[['homescore','awayscore']] = scores[['homescore','awayscore']].astype(int)
scores = scores[scores[['homescore', 'awayscore']].apply(sum, axis=1) > 0]

men_graph = createGraph(scores[scores['div']== 'Men'])
women_graph = createGraph(scores[scores['div']== 'Women'])
mixed_graph = createGraph(scores[scores['div']== 'Mixed'])
nx.write_graphml(men_graph, 'men_games.graphml')
nx.write_graphml(women_graph, 'women_games.graphml')
nx.write_graphml(mixed_graph, 'mixed_games.graphml')
#nx.draw(graph)
#nx.draw_networkx_labels(graph, pos=nx.spring_layout(graph))
#plt.show()