import networkx as nx
import csv
import pickle
import haversine
import staticmap
import urllib
import osmnx as ox
import collections
import pandas as pd

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
DIGRAPH_FILENAME = 'barcelona.digraph'
SIZE = 800
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'


# We define this two tuples to save the highways and congestions information.
# For every highway, we save: its way_id, the name of the highway and the list
# of its coordinates.
# For every congestion, we save: its way_id, a code with the year, month, day,
# hour, minute and second of the collection of data, its actual state and its
# expected state in 15 minutes.
Highway = collections.namedtuple('Highway', 'way_id name coordinates')
Congestion = collections.namedtuple('Congestion', 'way_id time actual_state \
expected_state')


def obtain_graph(PLACE, file_name):
    """Function that returns a graph from de given "PLACE". It tries to load it
    from a file called "file_name". If not possible, it downloads it using a
    osmnx function.
    """
    if not exists_graph(file_name):
        graph = download_graph(PLACE)
        save_graph(graph, file_name)
    else:
        graph = load_graph(file_name)
    return graph


def obtain_digraph(graph, file_name):
    """Function that given a "graph", returns its directed graph. It tries to
    load it from a file called "file_name". If not possible, it gets it by
    using a osmnx function.
    """
    if not exists_graph(file_name):
        digraph = create_digraph(graph)
        save_graph(digraph, file_name)
    else:
        digraph = load_graph(file_name)
    return digraph


def exists_graph(file_name):
    """Function that determines whether a graph exists or not in a concret file
    named "file_name" that we pass as a parameter.
    """
    try:
        # If it can open the file file_name is that the graph exists
        with open(file_name) as file:
            return True
    except:
        # Otherwise, is that the graph does not exist
        return False


def download_graph(PLACE):
    """Function that downloads and returns a graph from a "PLACE" that we pass
    as a parameter.
    """
    graph = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
    return graph


def load_graph(file_name):
    """Function that loads a graph from the file named "file_name" and
    returns it.
    """
    with open(file_name, 'rb') as file:
        graph = pickle.load(file)
    return graph


def create_digraph(graph):
    """Function that given a "graph", returns its directed graph.
    """
    digraph = ox.utils_graph.get_digraph(graph, weight='length')
    return digraph


def save_graph(graph, file_name):
    """Function that saves a given "graph" that we pass as a parameter in a
    file named as the parameter "file_name".
    """
    with open(file_name, 'wb') as file:
        pickle.dump(graph, file)
    return


def plot_graph(graph):
    """Function that plots a given "graph" that we pass as a parameter.
    """
    return ox.plot_graph(graph)


def _adapt_to_list(coordinates):
    """Function that given a string with a list of "coordinates", separates
    them and return a list of pairs of coordinates, given each of them as a
    pair of its latitude and its longitude.
    It is used when we download the highways data.
    """
    # It separates the long string into the diferent elements separated by a ,
    coordinates = coordinates.split(',')

    # It creates an empty list in which it appends pairs of coordinates
    coord = []
    for i in range(0, len(coordinates), 2):
        coord.append([float(coordinates[i]), float(coordinates[i+1])])
    return coord


def download_highways(HIGHWAYS_URL):
    """Function that downloads the highways from a given URL ("HIGHWAYS_URL")
    and returns a list with all of them.
    """
    with urllib.request.urlopen(HIGHWAYS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        next(reader)  # It ignores the first line with description

        # It creates an empty list in which it appends each highway information
        highways = []
        for line in reader:
            way_id, description, coordinates = line
            coordinates = _adapt_to_list(coordinates)
            highways.append(Highway(way_id, description, coordinates))
        return highways


def _show_highways(highways):
    """Function that prints the information of all the "highways" that we pass
    as a parameter.
    """
    for i in range(len(highways)):
        print("way_id", highways[i].way_id, "description", highways[i].name,
              "coordinates", highways[i].coordinates)


def plot_highways(highways, name, SIZE):
    """Function that generates a ("SIZE" x "SIZE") PNG file called "name" in
    which it plots the "highways" in a map of the corresponding city.
    """
    m_bcn = staticmap.StaticMap(SIZE, SIZE)
    for i in range(len(highways)):
        coord = highways[i].coordinates
        line = staticmap.Line(coord, 'black', 2)
        m_bcn.add_line(line)
    image = m_bcn.render()
    image.save(name)


def download_congestions(CONGESTIONS_URL):
    """Function that downloads the congestions from a given URL
    ("CONGESTIONS_URL") and returns a list with all of them.
    """
    with urllib.request.urlopen(CONGESTIONS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter='#', quotechar='"')

        # It creates an empty list in which it appends each congestion info
        congestions = []
        for line in reader:
            way_id, code, actual_state, expected_state = line
            congestions.append(Congestion(way_id, code, int(actual_state),
                               int(expected_state)))
        return congestions


def _show_congestions(congestions):
    """Function that prints the information of all the "congestions" that we
    pass as a parameter.
    """
    for i in range(len(congestions)):
        print("way_id", congestions[i].way_id, "code", congestions[i].time,
              "actual state", congestions[i].actual_state, "estat previst",
              congestions[i].expected_state)


def plot_congestions(highways, congestions, name, SIZE):
    """Function that generates a ("SIZE" x "SIZE") PNG file called "name" in
    which it plots the "highways" with different colours depending on the
    "congestions" of the "highways" in a map of the corresponding city.
    """
    m_bcn = staticmap.StaticMap(SIZE, SIZE)
    for i in range(len(highways)):
        coord = highways[i].coordinates
        line = staticmap.Line(coord, _colour(congestions[i].actual_state), 2)
        m_bcn.add_line(line)
    image = m_bcn.render()
    image.save(name)


def _colour(congestion):
    """Function that given a number of "congestion", it returns a color
    depending on it.
    """
    if congestion == 0:  # sense dades
        return "white"
    if congestion == 1:  # molt fluid
        return "limegreen"
    if congestion == 2:  # fluid
        return "green"
    if congestion == 3:  # dens
        return "darkorange"
    if congestion == 4:  # molt dens
        return "red"
    if congestion == 5:  # congestio
        return "darkred"
    if congestion == 6:  # tallat
        return "black"


def _factor(congestion):
    """Function that given a number of "congestion", it returns a factor
    depending on it.
    """
    if congestion == 0:  # sense dades
        return 1.2   # we consider it as "fluid"
    if congestion == 1:  # molt fluid
        return 1
    if congestion == 2:  # fluid
        return 1.5
    if congestion == 3:  # dens
        return 3
    if congestion == 4:  # molt dens
        return 5
    if congestion == 5:  # congestio
        return 10
    if congestion == 6:  # tallat
        return 10000000


def spread_congestions(digraph, highways, congestions):
    """Function that spreads the congestions of the highways to the edges of
    the osmnx graph. Returns the same "digraph" with a new attribute on its
    edges containing the "congestions" value of the "highways".
    """
    # As we don't have congestion data in the osmnx graph, we spread the
    # congestions of the highways data on it
    for i in range(len(highways)):
        # It considers the extrems of a highway
        c_ori = highways[i].coordinates[0]
        c_dest = highways[i].coordinates[len(highways[i].coordinates)-1]

        # It looks for the nearest node to the extrems of the highway
        n_ori = ox.nearest_nodes(digraph, c_ori[0], c_ori[1])
        n_dest = ox.nearest_nodes(digraph, c_dest[0], c_dest[1])

        # If it exists a path within these two nodes, then all the edges of
        # this path will have the same congestion as the highway.
        # Otherwise, nothing is done.
        try:
            path = nx.shortest_path(digraph, n_ori, n_dest, "length")
            for k in range(len(path)-1):
                congestion = congestions[i].actual_state
                digraph.edges[path[k], path[k+1]]["congestion"] = congestion
        except:
            print('', end='')
    return digraph


def new_itime_attribute(digraph):
    """Function that for every edge in the "digraph", it creates a new
    attribute called "itime" which represents the aproximate time needed to
    travel through this edge.
    Computation of the itime value: given the length of an edge (d) and the
    maximum speed allowed on it (v), we know that the time to travel this edge
    is of d/v. This will happen in perfect conditions but we need to consider
    that there can be congestions or other factors that wouldn't allow us to
    travel at the maximum speed through all the edge.
    We have decided to manipulate the value of d/v by multiplying it by a
    factor c which depends on the congestion of the edge. Also, we decided to
    multiply this value by 2 in other to consider these other factors as
    traffic lights or pedestrians.
    Conclusion: itime = (d/v)*c*2
    Note: if the edge doesn't have a maximum speed value, we will consider that
    this value is of 50 km/h.
    Note: if the edge doesn't have a congestion value, we will consider that
    this value is of 0 "sense dades".
    """
    # For every edge in the osmnx graph, it creates a new attribute called
    # "itime" which represents the aproximate time needed to travel through an
    # edge.
    for node1, info1 in digraph.nodes.items():
        for node2, edge in digraph.adj[node1].items():
            d = float(digraph.edges[node1, node2]["length"])
            v = 0
            c = 0

            # As for every edge we don't have the "maxspeed" attribute, we will
            # consider that if it doesn't exists, the maxspeed is 50 km/h.
            try:
                v = float(digraph.edges[node1, node2]["maxspeed"])
            except:
                v = 50
            v = v * (1000/3600)  # conversion factor to m/s

            # As for every edge we don't have the "congestion" attribute, we
            # will consider that if it doesn't exists, its value is 0 ("sense
            # dades").
            try:
                c = float(digraph.edges[node1, node2]["congestion"])
            except:
                c = 0  # sense dades
            digraph.edges[node1, node2]["itime"] = (d/v) * _factor(c) * 2
    return digraph


def build_igraph(digraph, highways, congestions):
    """Function that builds an intelligent graph adding a new attribute to the
    edges of our "digraph" called "itime" in which we compute the approximate
    time to travel trough an edge. This value depends on the list of
    "congestions" of the "highways".
    """
    # It spreads the congestions of the highways to the osmnx graph.
    con_digraph = spread_congestions(digraph, highways, congestions)

    # It creates the new attribute for every edge of the graph named "itime".
    igraph = new_itime_attribute(con_digraph)

    return igraph


def get_shortest_path_with_ispeeds(igraph, actual_ubi, desti_ubi):
    """Function that given the "igraph" and two locations with its coordinates
    returns a list of nodes corresponding to the fastest path to go from
    "actual_ubi" to "desti_ubi" depending on the "itime" attribute of every
    edge.
    """
    # It looks for the closest nodes in the igraph of the locations given.
    origin = ox.nearest_nodes(igraph, actual_ubi[1], actual_ubi[0])
    destination = ox.nearest_nodes(igraph, desti_ubi[1], desti_ubi[0])

    # It computes the shortest path taking into account the "itime" attribute.
    # The return of this function is a list of nodes of the osmnx graph.
    path = nx.shortest_path(igraph, origin, destination, "itime")

    return path


def get_path_time(igraph, actual_ubi, desti_ubi):
    """Function that given the "igraph" and two locations with its coordinates
    returns the time to travel the shortest path to go from "actual_ubi" to
    "desti_ubi".
    """
    # It looks for the closest nodes in the igraph of the locations given.
    origin = ox.nearest_nodes(igraph, actual_ubi[1], actual_ubi[0])
    destination = ox.nearest_nodes(igraph, desti_ubi[1], desti_ubi[0])

    # It computes the shortest path taking into account the "itime" attribute
    # and calculates the time to travel through this path.
    path_time = nx.shortest_path_length(igraph, origin, destination, "itime")

    return path_time


def get_path_length(igraph, path):
    """Function that given the "igraph" and a "path", returns the length in
    meters of this path.
    """
    length = 0
    for i in range(len(path)-1):
        length += igraph.edges[path[i], path[i+1]]["length"]
    return length


def plot_path(igraph, path, name, SIZE):
    """Function that generates a ("SIZE" x "SIZE") PNG file called "name" in
    which it plots the "path" given in a map of the corresponding city.
    """
    # It creates an empty list in which it appends the coordinates of each node
    # of the shortest path passed as a parameter.
    coord_path = []
    for i in path:
        point = igraph.nodes[i]
        coord_path.append([point['x'], point['y']])

    # It generates the image with the path plot
    m_bcn = staticmap.StaticMap(SIZE, SIZE)
    line = staticmap.Line(coord_path, "blue", 2)
    m_bcn.add_line(line)
    image = m_bcn.render()
    image.save(name)


def test():
    # Obtention of the graph and its plot
    graph = obtain_graph(PLACE, GRAPH_FILENAME)
    plot_graph(graph)

    # Obtention of the digraph of the graph
    digraph = obtain_digraph(graph, DIGRAPH_FILENAME)

    # Download highways and plot them into a PNG image
    highways = download_highways(HIGHWAYS_URL)
    plot_highways(highways, 'highways.png', SIZE)

    # Download congestions and plot them into a PNG image
    congestions = download_congestions(CONGESTIONS_URL)
    plot_congestions(highways, congestions, 'congestions.png', SIZE)

    # Get the 'intelligent graph' version of a graph taking into account the
    # congestions of the highways
    igraph = build_igraph(digraph, highways, congestions)

    # Get 'intelligent path' between two addresses and plot it into a PNG image
    origin = ox.geocode("Campus Nord UPC")
    destination = ox.geocode("Sagrada Família")
    ipath = get_shortest_path_with_ispeeds(igraph, origin, destination)
    plot_path(igraph, ipath, 'itime_path.png', SIZE)


# test()
