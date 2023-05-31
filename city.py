from typing import TypeAlias
from dataclasses import dataclass

import osmnx as ox
import pickle
import networkx as nx
from buses import *

Coord: TypeAlias = tuple[float, float]   # (latitude, longitude
CityGraph: TypeAlias = nx.Graph
OsmnxGraph: TypeAlias = nx.MultiDiGraph


@dataclass
class Edge:
    ...


@dataclass
class Path:
    ...


def get_osmnx_graph() -> OsmnxGraph:
    '''Funció que obte i retorna el graf
    dels carrers de Barcelona'''

    graph: OsmnxGraph = ox.graph_from_place("Barcelona",
                                            network_type='walk',
                                            simplify=True)  # type: ignore

    for u, v, key, geom in graph.edges(data="geometry", keys=True):
        if geom is not None:
            del (graph[u][v][key]["geometry"])
    for node in graph.nodes():
        graph.nodes[node]['pos'] = (graph.nodes[node]['x'], graph.nodes[node]['y'])
    return graph


def find_path(ox_g: OsmnxGraph, g: CityGraph,
              src: Coord, dst: Coord) -> Path:
    '''Retorna el camí (Path) més curt entre
    els punts src i dst. '''
    ...


def save_osmnx_graph(g: OsmnxGraph, filename: str) -> None:
    '''Guarda el graf g al fitxer filename'''
    file = open(filename, 'wb')
    pickle.dump(g, file)
    file.close()


def load_osmnx_graph(filename: str) -> OsmnxGraph:
    '''Retorna el graf guardat al fitxer filename'''

    file = open(filename, 'rb')
    g = pickle.load(file)
    file.close()
    assert isinstance(g, OsmnxGraph)
    return g


#                                                                  (Unknown)
def nearest_node(g: OsmnxGraph, point: Coord) -> None | int:  # node id (int?)
    '''Funció que retorna el node més proper al punt donat
    al graf g. Retorna None si la distància és major a {?}'''
    X, Y = point[0], point[1]
    nodes, dist = ox.nearest_nodes(g, X, Y, return_dist=True)

    if dist > 1000:  # assumint que torna distància en metres (en teoria si xd)
        return None
    if type(nodes) == list:
        assert nodes[0] in g.nodes
        return nodes[0]  # quansevol d'aquests nodes ja ens està bé!
    return nodes


def nearest_node2(g: OsmnxGraph, point: Coord) -> int:
    '''Funció que retorna el node més proper al punt donat
    al graf g. Retorna None si la distància és major a {?}'''
    X, Y = point[0], point[1]
    nodes = ox.nearest_nodes(g, X, Y)

    if type(nodes) == list:
        print(nodes)
        return nodes[0]  # quansevol d'aquests nodes ja ens està bé!
    return nodes  # type: ignore


def build_city_graph(g1: OsmnxGraph, g2: BusesGraph) -> CityGraph:
    '''Retorna un graf fusió de g1 i g2'''
    city: CityGraph = nx.Graph()
    # add cinemas here?

    for u, nbrsdict in g1.adjacency():
        attr = g1.nodes[u]
        city.add_node(u, **attr)
        city.nodes[u]['tipus'] = 'Cruilla'
        # for each adjacent node v and its (u, v) edges' information ...
        for v, edgesdict in nbrsdict.items():
            attr = g1.nodes[v]
            city.add_node(v, **attr)
            city.nodes[v]['tipus'] = 'Cruilla'  # no caldira, ja ho fem lin. 37

            eattr = edgesdict[0]
            if u != v:
                city.add_edge(u, v, **eattr)

     # Parada: Cruilla

    print('checkpoint 1')

    nearest_nodes: dict[int, int] = {}
    list_x: list[float] = []
    list_y: list[float] = []

    for u in g2.nodes:
        assert g2.nodes[u]['tipus'] == 'Parada'
        attr = g2.nodes[u]
        city.add_node(u, **attr)
        list_x.append(g2.nodes[u]['pos'][0])  # ojo amb girar coordenades xd
        list_y.append(g2.nodes[u]['pos'][1])

    parada_cruilla: list[int] = ox.nearest_nodes(g1,
                                                   list_x,
                                                   list_y, return_dist=False)


    for i, u in enumerate(g2.nodes()):
        nearest_nodes[u] = parada_cruilla[i]

    assert len(parada_cruilla) == len(nearest_nodes)
    print('checkpoint 2')

    for edge in g2.edges():
        #  assert g2.nodes[edge]['tipus'] == 'Bus'
        u, v = edge
        if u == v:
            continue
        i = nearest_nodes[u]
        j = nearest_nodes[v]
        dist = nx.shortest_path_length(g1, i, j, weight='length') / 3
        city.add_edge(u, v, weight=dist)  # **attr
        city.add_edge(i, u, weight=0)
        city.add_edge(j, v, weight=0)

    '''for u, nbrsdict in g2.adjacency():
        assert g2.nodes[u]['tipus'] == 'Parada'
        city.add_node(u)

        if u not in nearest_nodes: pass
        for v, edge in nbrsdict.items():
            city.add_node(v)

            
            i = nearest_node2(g1, g2.nodes[u]['pos'])
            j = nearest_node2(g1, g2.nodes[v]['pos'])
            dist = nx.shortest_path_length(g1, i, j, weight='length') / 3
            #  attr = {"weight": dist}
            city.add_edge(u, v, weight=dist)  # **attr
            city.add_edge(i, u, weight=0)
            city.add_edge(j, v, weight=0)'''

    return city


def show(g: CityGraph) -> None:
    '''Mostra g de forma interactiva en una finestra'''
    posicions = nx.get_node_attributes(g,'pos')
    nx.draw(g, pos = posicions, with_labels=False, node_size=20, node_color='lightblue', edge_color='gray')
    plt.show()


def plot(g: CityGraph, filename: str) -> None:
    '''Desa g com una imatge amb el mapa de la
    cuitat de fons en l'arxiu filename'''
    ...


def plot_path(g: CityGraph, p: Path, filename: str) -> None:
    '''Mostra el camí p en l'arxiu filename'''
    ...


def print_osmnx_graph(g: OsmnxGraph) -> None:
    street_graph_projected = ox.project_graph(g)
    ox.plot_graph(street_graph_projected)



try:
    raise Exception
    c = load_osmnx_graph('prova.pickle')
    print(type(c))
    b = get_buses_graph()
    print(type(b))
except Exception:
    c = get_osmnx_graph()
    save_osmnx_graph(c, 'prova.pickle')
    b = get_buses_graph()
    print(type(b))



input('press enter to continu')

city = build_city_graph(c, b)
print(type(city))

a = input('press enter to Show')

show(city)

input('show <egrnsfm')

print_osmnx_graph(c)
