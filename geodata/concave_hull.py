from scipy.spatial import Delaunay, ConvexHull
import networkx as nx


def concave(points, alpha_x=150, alpha_y=250):
    """Find concave hull of points."""
    points = [(i[0], i[1]) if type(i) is tuple else i for i in points]
    de = Delaunay(points)
    dec = []
    a = alpha_x
    b = alpha_y
    for i in de.simplices:
        tmp = []
        j = [points[c] for c in i]
        if abs(j[0][1] - j[1][1]) > a or abs(j[1][1]-j[2][1]) > a or abs(j[0][1]-j[2][1]) > a or abs(j[0][0]-j[1][0]) > b or abs(j[1][0]-j[2][0]) > b or abs(j[0][0]-j[2][0]) > b:
            continue
        for c in i:
            tmp.append(points[c])
        dec.append(tmp)
    G = nx.Graph()
    for i in dec:
            G.add_edge(i[0], i[1])
            G.add_edge(i[0], i[2])
            G.add_edge(i[1], i[2])
    ret = []
    for graph in nx.connected_component_subgraphs(G):
        ch = ConvexHull(graph.nodes())
        tmp = []
        for i in ch.simplices:
            tmp.append(graph.nodes()[i[0]])
            tmp.append(graph.nodes()[i[1]])
        ret.append(tmp)
    return ret
