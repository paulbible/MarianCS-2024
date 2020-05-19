'''
    A class to represent a grid graph
'''
from collections import deque


class Graph(object):
    def __init__(self, n):
        self.V = n
        self.matrix = []
        for i in range(n):
            self.matrix.append([0 for i in range(n)])

    def add_edge(self, s, t):
        self.matrix[s][t] = 1
        self.matrix[t][s] = 1

    def remove_edge(self, s, t):
        self.matrix[s][t] = 0
        self.matrix[t][s] = 0

    def is_adjacent(self, s, t):
        return bool(self.matrix[s][t])

    def get_adjacent(self, s):
        adjacent_vertices = []
        for i in range(self.V):
            if self.is_adjacent(s, i):
                adjacent_vertices.append(i)
        return adjacent_vertices

    def get_vertex_xy(self, vertex, grid_width, grid_height):
        r, c = vertex_to_rc(vertex, 10, 10)
        x = (c * grid_width) + grid_width/2
        y = (r * grid_height) + grid_height/2
        # print(r, c, x, y)
        return x, y

    def __str__(self):
        return "Graph: vertices = %s" % str(self.V)


def vertex_to_rc(vertex_id, grid_rows, grid_cols):
    r = int(vertex_id / grid_rows)
    c = vertex_id % grid_cols
    return r, c


def rc_to_vertex(r, c, grid_rows):
    return r*grid_rows + c


def create_tile_graph(filename):
    tile_map = []
    with open(filename, 'r') as f:
        for i in range(10):
            line = f.readline()
            if line:
                tile_map.append(line[:10])
    grid_rows = len(tile_map)
    grid_cols = len(tile_map[0])
    n_tiles = grid_rows * grid_cols
    graph = Graph(n_tiles)

    # build a square grid
    for i in range(n_tiles):
        if int(i / grid_rows) != 0:
            graph.add_edge(i, i - grid_cols)  # upper neighbor

        if int(i / grid_rows) != (grid_rows - 1):
            graph.add_edge(i, i + grid_cols)  # lower neighbor

        if i % grid_cols != 0:
            graph.add_edge(i, i - 1)  # left neighbor

        if i % grid_cols != (grid_cols - 1):
            graph.add_edge(i, i + 1)  # right neighbor

    # remove the wall tiles
    for r in range(grid_rows):
        for c in range(grid_cols):
            if tile_map[r][c] == '#':
                vertex = rc_to_vertex(r, c, grid_rows)
                adjacent_vertices = graph.get_adjacent(vertex)
                for i in adjacent_vertices:
                    graph.remove_edge(vertex, i)
    return graph


def get_shortest_path(start_r, start_c, goal_r, goal_c, graph):
    start_vertex = rc_to_vertex(start_r, start_c, 10)
    goal_vertex = rc_to_vertex(goal_r, goal_c, 10)

    queue = deque()
    queue.append(start_vertex)
    seen = set()
    seen.add(start_vertex)
    predecessors = {}
    predecessors[start_vertex] = -1

    while queue:
        v = queue.popleft()
        if v == goal_vertex:
            break

        for adj_v in graph.get_adjacent(v):
            if adj_v not in seen:
                seen.add(adj_v)
                predecessors[adj_v] = v
                queue.append(adj_v)

    if goal_vertex not in predecessors:
        return []

    path = [goal_vertex]
    pred = predecessors[goal_vertex]
    while pred != -1:
        path.insert(0, pred)  # insert the vertex at the beginning
        pred = predecessors[pred]

    return path


