"""
This implementation works, though it's a bit too slow
"""
import datetime
import random
import numpy as np
from typing import List, Tuple, Iterable, Dict, Set

from file_path import read_lines


class Graph:
    def __init__(self):
        self.nodes: List[str] = []
        self.edges: List[Tuple[str, str]] = []
        self.edge_weights: Dict[Tuple[str, str], int] = {}
        # self.node_edges: Dict[str, List[Tuple[str, str]]] = {}
        self.node_affinity: np.ndarray = np.array([])
        self.node_index: Dict[str, int] = {}

    def find_min_cut(self) -> Tuple[int, str]:
        cut_by_weight: List[Tuple[int, str]] = []
        total_nodes = len(self.nodes)

        cut_weight = 0

        while len(self.nodes) > 1:
            started = datetime.datetime.now()
            a = []
            v = set(self.nodes)
            while v:
                node, cut_weight = self.get_tightest_bound_node(a, v)
                v.remove(node)
                a.append(node)

            # merge last two nodes
            x, y = a[-1], a[-2]
            _merged_name = self.merge_nodes(x, y)
            elapsed = round((datetime.datetime.now() - started).total_seconds())
            print(f"G contracted, {len(self.nodes)} nodes out of {total_nodes} left. Took {elapsed} seconds")

            group_a = x.split(" ")
            count_a = len(group_a)
            count_b = total_nodes - count_a

            cut_by_weight.append((cut_weight, f"[{count_a}][{count_b}]"))

        cut_by_weight.sort(key=lambda x: x[0])
        return cut_by_weight[0]

    def merge_nodes(self, x: str, y: str) -> str:
        new_name = f"{x} {y}"
        def retarget_edge(e: Tuple[str, str]) -> Tuple[str, str]:
            a = e[0]
            updated = False
            if a in [x, y]:
                updated = True
                a = new_name
            b = e[1]
            if b in [x, y]:
                updated = True
                b = new_name

            if not updated:
                return e
            new_e = (a, b)
            self.edge_weights[new_e] = self.edge_weights.get(new_e, 0) + 1
            return new_e

        for i in range(len(self.edges)):
            edge = retarget_edge(self.edges[i])
            self.edges[i] = edge
        # remove loops
        self.edges = [e for e in self.edges if e[0] != e[1]]
        # remove nodes being merged
        self.nodes = [n for n in self.nodes if n != x and n != y]
        self.nodes.append(new_name)

        self._build_node_affinity()
        return new_name

    def get_tightest_bound_node(self, a: List[str], v: Iterable[str]) -> Tuple[str, int]:
        if not a:
            return random.choice(list(v)), 0

        tightest_bound_node = None
        tightest_bound = -1
        lst_a = np.array([self.node_index[n] for n in a])
        for node in v:
            weight = self.get_node_to_set_weight(node, lst_a)
            if weight > tightest_bound:
                tightest_bound = weight
                tightest_bound_node = node
        return tightest_bound_node, tightest_bound

    def get_node_to_set_weight(self, node: str, node_set: Iterable[str]) -> int:
        row = self.node_index[node]
        affinity = self.node_affinity[row, node_set].sum()
        return affinity
        # this is still slow:
        # neighbours = self.neighbor_map[node]
        # keys = neighbours.keys() & node_set
        # total_sum = sum(neighbours[key] for key in keys)
        # return total_sum

        # this is super slow:
        # weight = 0
        # edges = self.node_edges[node]
        # for ea, eb in edges:
        #     if (node == ea and eb in node_set) or (node == eb and ea in node_set):
        #          weight += self.edge_weights[(ea, eb)]
        # return weight

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
        self.edge_weights = {e: 1 for e in self.edges}
        self._build_node_affinity()

    def _build_node_affinity(self) -> None:
        self.node_index = {n: i for i, n in enumerate(self.nodes)}
        self.node_affinity = np.zeros((len(self.nodes), len(self.nodes)), dtype=np.int32)
        for ea, eb in self.edges:
            weight = self.edge_weights[(ea, eb)]
            a_idx = self.node_index[ea]
            b_idx = self.node_index[eb]
            self.node_affinity[a_idx, b_idx] = self.node_affinity[a_idx, b_idx] + weight
            self.node_affinity[b_idx, a_idx] = self.node_affinity[b_idx, a_idx] + weight



def main():
    graph = Graph()
    graph.load_from_file("input_d25.txt")
    start = datetime.datetime.now()
    min_cut = graph.find_min_cut()
    elapsed = round((datetime.datetime.now() - start).total_seconds())
    print(f"All finished in {elapsed} seconds")
    print(min_cut)  # All finished in 1107 seconds, (3, '[727][733]')


if __name__ == "__main__":
    main()
