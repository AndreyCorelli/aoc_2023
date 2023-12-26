"""
This implementation just doesn't find the min cut
"""

import random
from typing import List, Tuple, Set

from file_path import read_lines

class Graph:
    def __init__(self):
        self.nodes: List[str] = []
        self.edges: List[Tuple[str, str]] = []

    def find_min_cut(self) -> Tuple[int, int, int]:  # weight, count_a, count_b
        return self._find_min_cut(self.make_copy())

    def _find_min_cut(self, graph: "Graph") -> Tuple[int, int, int]:  # weight, count_a, count_b
        stop_point = len(graph.nodes) // 2**0.5
        if stop_point < 4:
            stop_point = 2

        while len(graph.nodes) > stop_point:
            edge = random.choice(graph.edges)
            x, y = edge
            _merged_name = graph.merge_nodes(x, y)

        if len(graph.nodes) == 2:
            a, b = graph.nodes
            edges_to_cut = [e for e in self.edges
                            if (e[0] in a and e[1] not in a) or
                            (e[1] in a and e[0] not in a)]
            cut_weight = len(edges_to_cut)
            return cut_weight, len(graph.nodes[0].split(" ")), len(graph.nodes[1].split(" "))
        w1, a1, b1 = self._find_min_cut(graph.make_copy())
        w2, a2, b2 = self._find_min_cut(graph.make_copy())
        return (w1, a1, b1) if w1 < w2 else (w2, a2, b2)

    def merge_nodes(self, x: str, y: str) -> str:
        new_name = f"{x} {y}"

        for i in range(len(self.edges)):
            if self.edges[i][0] in (x, y):
                self.edges[i] = (new_name, self.edges[i][1])
            if self.edges[i][1] in (x, y):
                self.edges[i] = (self.edges[i][0], new_name)
        # remove loops
        self.edges = [e for e in self.edges if e[0] != e[1]]
        # remove duplicates
        self.edges = list(set(self.edges))
        # remove nodes being merged
        self.nodes = [n for n in self.nodes if n != x and n != y]
        self.nodes.append(new_name)
        return new_name

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

    def make_copy(self) -> "Graph":
        new_graph = Graph()
        new_graph.nodes = self.nodes.copy()
        new_graph.edges = self.edges.copy()
        return new_graph


def main():
    graph = Graph()
    graph.load_from_file("input_d25_small.txt")
    min_cut = graph.find_min_cut()
    print(min_cut)


def test_merge():
    graph = Graph()
    graph.nodes = ["a", "b", "c"]
    graph.edges = [("a", "b"), ("a", "c"), ("b", "c")]
    graph.merge_nodes("c", "b")
    assert graph.nodes == ["a", "c b"]
    assert graph.edges[0] == ("a", "c b")
    assert len(graph.edges) == 1


if __name__ == "__main__":
    #test_merge()
    main()
