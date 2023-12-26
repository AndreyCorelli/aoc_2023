"""
This is a simplified version of the Stoer-Wagner algorithm.
The algorithm supposes that the local optimum (the most tightly connected node) should be joined to
the current subset A, to finally form a tightly connected cluster.

This greedy algo adds the most tightly connected node "node" to the subset A
 - here this calculation is faster, because there ain't no edge weights...
 - therefore, we can calculate the intersection of the node's neighbours with the rest of the nodes
After each step the algorithm it calculates cuts (edges from A to the rest)

Works fine.
"""
import random
from typing import List, Tuple, Iterable, Dict, Set

from file_path import read_lines


class Graph:
    def __init__(self):
        self.nodes: List[str] = []
        self.edges: List[Tuple[str, str]] = []
        self.neighbor_map: Dict[str, Set[str]] = {}

    def find_min_cut(self) -> Tuple[int, str]:
        for _ in range(1000):
            a = set()
            v = set(self.nodes)
            while len(v) > 1:
                node, _node_bound = self.get_tightest_bound_node(a, v)
                v.remove(node)
                a.add(node)
                cut_weight = self.get_set_to_set_weight(a, v)
                if cut_weight < 4:
                    msg = f"Found a cut of w{cut_weight}, ({len(a)}, {len(v)})"
                    print(msg)
                    return len(a), msg

        return 0, "Not found"

    def get_tightest_bound_node(self, a: Set[str], v: Iterable[str]) -> Tuple[str, int]:
        if not a:
            return random.choice(list(v)), 0

        tightest_bound_node = None
        tightest_bound = -1
        for node in v:
            weight = self.get_node_to_set_weight(node, a)
            if weight > tightest_bound:
                tightest_bound = weight
                tightest_bound_node = node
        return tightest_bound_node, tightest_bound

    def get_node_to_set_weight(self, node: str, node_set: Iterable[str]) -> int:
        neighbours = self.neighbor_map[node]
        intersection = neighbours.intersection(node_set)
        return len(intersection)

    def get_set_to_set_weight(self, a: Set[str], b: Set[str]) -> int:
        weight = 0
        for ea, eb in self.edges:
            if (ea in a and eb in b) or (ea in b and eb in a):
                weight += 1
        return weight

    def load_from_file(self, file_path: str) -> None:
        lines = read_lines(file_path)
        nodes: Set[str] = set()
        edges: Set[Tuple[str, str]] = set()

        for line in lines:
            line = line.replace(":", "")
            parts = line.split(" ")
            for p in parts:
                nodes.add(p)

            for i in range(1, len(parts)):
                edges.add((parts[0], parts[i]))

        self.nodes = list(set(nodes))
        self.edges = list(set(edges))
        self._find_neighbours()

    def _find_neighbours(self) -> None:
        for ea, eb in self.edges:
            self.neighbor_map[ea] = self.neighbor_map.get(ea, set())
            self.neighbor_map[ea].add(eb)
            self.neighbor_map[eb] = self.neighbor_map.get(eb, set())
            self.neighbor_map[eb].add(ea)


def main():
    graph = Graph()
    graph.load_from_file("input_d25.txt")
    min_cut = graph.find_min_cut()
    print(min_cut)


if __name__ == "__main__":
    #test_all()
    main()
