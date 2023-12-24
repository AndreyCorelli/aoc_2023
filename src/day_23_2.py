import copy
from typing import List, TypeAlias, Set, Tuple, Dict

from src.file_path import read_lines

Point: TypeAlias = tuple[int, int]

SLOPES = {"<", ">", "^", "v"}


class Node:
    MAX_WEIGHT = 1000000000

    def __init__(self, point: Point):
        self.point = point
        self.weight = self.MAX_WEIGHT
        self.neighbours: List[Tuple[Node, int]] = []

    @property
    def reached(self) -> bool:
        return self.weight != self.MAX_WEIGHT

    def __repr__(self):
        nbs = ", ".join([f"{n[0].point} ({n[1]})" for n in self.neighbours])
        return f"{self.point}. Neighbours: {nbs}"

    def __str__(self):
        return self.__repr__()

    def __lt__(self, other):  # < operator
        return True


class Edge:
    def __init__(self,
                 point_a: Point,
                 point_b: Point,
                 length: int = 0):
        self.point_a = point_a
        self.point_b = point_b
        self.length = length

    def __repr__(self):
        return f"{self.point_a} -> {self.point_b} ({self.length})"

    def __str__(self):
        return self.__repr__()


class Graph:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.edges_dict: Dict[Tuple[int, int, int, int], Edge] = {}
        self.edges: List[Edge] = []
        self.node_coords: Set[Point] = set()
        self.nodes: List[Node] = []
        self.start: Node = None
        self.end: Node = None

    def solve(self) -> int:
        self._build_nodes()
        # find the longest path from start to end using brute force
        result = self.brute_force(self.start, set(), 0, 0) - 1
        print(f"Result: {result}")
        return result

    def brute_force(self, start_node: Node, visited: Set[Node], ln: int, max_len: int) -> int:
        visited.add(start_node)
        for neighbour, length in start_node.neighbours:
            if neighbour in visited:
                continue
            if neighbour == self.end:
                if ln + length > max_len:
                    max_len = ln + length
                return max_len
            max_len = self.brute_force(neighbour, copy.copy(visited), ln + length, max_len)
        return max_len

    def add_edge_if_not_exists(self, edge: Edge) -> bool:
        key = (edge.point_a[0], edge.point_a[1], edge.point_b[0], edge.point_b[1])
        if key in self.edges_dict:
            return False
        self.edges_dict[key] = edge
        self.edges.append(edge)
        return True

    def _build_nodes(self):
        node_by_coord: Dict[Point, Node] = {}

        for coord in self.node_coords:
            node = self._ensure_node(coord, node_by_coord)

            # find node's neighbours
            for edge in self.edges:
                if edge.point_a == coord:
                    node.neighbours.append(
                        (self._ensure_node(edge.point_b, node_by_coord), edge.length))
                elif edge.point_b == coord:
                    node.neighbours.append(
                        (self._ensure_node(edge.point_a, node_by_coord), edge.length))
        self.nodes = list(node_by_coord.values())
        # remove duplicated neighbours
        for node in self.nodes:
            node.neighbours = list(set(node.neighbours))

        self.start = [n for n in self.nodes if n.point == (1, 0)][0]
        self.end = [n for n in self.nodes if n.point == (self.w - 2, self.h - 1)][0]

    def _ensure_node(self, coord: Point, node_by_coord: Dict[Point, Node]) -> Node:
        node = node_by_coord.get(coord)
        if not node:
            node = Node(coord)
            node_by_coord[coord] = node
        return node


class Island:
    def __init__(self, file_path: str):
        self.surface: List[List[str]] = []
        self.w = 0
        self.h = 0
        self.start: Point = (0, 0)
        self.end: Point = (0, 0)
        self._read_file(file_path)
        self.graph = Graph(self.w, self.h)

    def solve(self) -> int:
        node = self.start
        self.graph.node_coords.add(node)
        self._build_graph(node, (node[0], node[1]), set())
        print("Graph built")
        return self.graph.solve()

    def print(self):
        template = f"\033[31mSMB\033[0m"

        for y in range(self.h):
            for x in range(self.w):
                smb = self.surface[y][x]
                # is a graph point?
                if (x, y) in self.graph.node_coords:
                    smb = template.replace("SMB", "o" if smb == "." else smb)
                print(smb, end="")
            print("")

    def _build_graph(self, prev_node: Point, start: Point, visited: Set[Point]):
        cur = start
        visited.add(cur)
        path_len = 1

        while True:
            # find all directions
            next_points = self._get_next_steps(cur, visited)
            if not next_points:
                break
            if len(next_points) == 1:
                path_len += 1
                cur = next_points[0]
                visited.add(cur)
                if cur == self.end:
                    self.graph.add_edge_if_not_exists(Edge(prev_node, cur, path_len))
                    self.graph.node_coords.add(cur)
                    break
                continue

            # bifurcation point
            is_new_edge = self.graph.add_edge_if_not_exists(Edge(prev_node, cur, path_len))
            if not is_new_edge:
                break
            self.graph.node_coords.add(cur)
            for nxt in next_points:
                self._build_graph(cur, nxt, copy.copy(visited))
            break
        return

    def _get_next_steps(self, start: Point, visited: Set[Point]) -> List[Point]:
        options = []
        nxt = (start[0] - 1, start[1])

        if nxt[0] > 0 and self.surface[nxt[1]][nxt[0]] == "." \
                and nxt not in visited:
            options.append(nxt)
        nxt = (start[0] + 1, start[1])
        if nxt[0] < self.w and self.surface[nxt[1]][nxt[0]] == "." \
                and nxt not in visited:
            options.append(nxt)
        nxt = (start[0], start[1] - 1)
        if nxt[1] > 0 and self.surface[nxt[1]][nxt[0]] == "." \
                and nxt not in visited:
            options.append(nxt)
        nxt = (start[0], start[1] + 1)
        if nxt[1] < self.h and self.surface[nxt[1]][nxt[0]] == "." \
                and nxt not in visited:
            options.append(nxt)
        return options

    def _read_file(self, file_path: str):
        lines = read_lines(file_path)
        self.surface = [list(l) for l in lines]
        self.w = len(self.surface[0])
        self.h = len(self.surface)

        for y in range(self.h):
            for x in range(self.w):
                smb = self.surface[y][x]
                if smb in SLOPES:
                    smb = "."
                self.surface[y][x] = smb

        self.start = (1, 0)
        self.end = (self.w - 2, self.h - 1)


def small_run():
    island = Island("input_d23.txt")
    island.solve()
    # island.print()


if __name__ == "__main__":
    small_run()
