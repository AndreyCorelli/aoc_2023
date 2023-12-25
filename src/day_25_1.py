import itertools
from typing import List, Dict, Tuple, Set

from file_path import read_lines


class Node:
    def __init__(self, name: str):
        self.name = name
        self.neighbours: List["Node"] = []
        # non-overlapping groups of neighbours and neighbours' neighbours etc
        # example: {"c": "c b d a e", ...}
        self.neighbour_group: Dict[str, str] = {}

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return f"{self.name}"

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.name == other.name
        return False


class Edge:
    def __init__(self, node_a: Node, node_b: Node):
        self.node_a = node_a
        self.node_b = node_b

    def __repr__(self):
        return f"{self.node_a} - {self.node_b}"

    def __str__(self):
        return f"{self.node_a} - {self.node_b}"

    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.node_a == other.node_a and self.node_b == other.node_b
        return False


class Graph:
    def __init__(self):
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []

    def solve(self):
        self._clusterize_nodes()
        # find at least 3 groups that repeat.
        group_occurs: Dict[str, int] = {}
        for node in self.nodes:
            for group in node.neighbour_group.values():
                group_occurs[group] = group_occurs.get(group, 0) + 1

        group_lst = [(g, c) for g, c in group_occurs.items()]
        group_lst.sort(key=lambda x: (x[1], len(x[0])), reverse=True)

        # find edges, connecting these groups
        edge_by_names = {(e.node_a.name, e.node_b.name): e for e in self.edges}
        edges: List[Edge] = []
        for group_names, _ in group_lst[:10]:
            # find all edges, adjacent to the groups
            for node in self.nodes:
                for k, v in node.neighbour_group.items():
                    if v == group_names:
                        name_a = node.name
                        name_b = k
                        edge = edge_by_names.get((name_a, name_b))
                        if not edge:
                            edge = edge_by_names.get((name_b, name_a))
                        if edge not in edges:
                            edges.append(edge)

        # drop first 3 edges (do I need more if it doesn't work?)
        self._try_cutting_edges(edges[:10])

    def _try_cutting_edges(self, edges: List[Edge]):
        three_cuts = list(itertools.permutations(edges, 3))

        # selected = [("hfx", "pzl"), ("bvb", "cmg"), ("nvd", "jqt")]
        # edges = [
        #     [e for e in self.edges
        #      if (e.node_a.name == a and e.node_b.name == b) or (e.node_a.name == b and e.node_b.name == a)][0]
        #     for a, b in selected
        # ]
        # # three_cuts = [[self.edges[0], self.edges[1], self.edges[2]]]
        # three_cuts = [edges]

        for edge_to_cut in three_cuts:
            graph = self.get_modified_graph(list(edge_to_cut))
            clusters = graph.get_graph_clusters()
            print(clusters)
            if len(clusters) == 2:
                print("Found")
                return

    def get_modified_graph(self, edges_to_cut: List[Edge]) -> "Graph":
        graph = Graph()
        graph.edges = [e for e in self.edges if e not in edges_to_cut]

        cut_by_names = {(e.node_a.name, e.node_b.name): e for e in edges_to_cut}

        for node in self.nodes:
            new_node = Node(node.name)
            for nb in node.neighbours:
                a, b = node.name, nb.name
                if (a, b) in cut_by_names or (b, a) in cut_by_names:
                    continue
                new_node.neighbours.append(nb.name)
            graph.nodes.append(new_node)

        node_by_name = {n.name: n for n in graph.nodes}
        for node in graph.nodes:
            node.neighbours = [node_by_name[n] for n in node.neighbours]

        return graph

    def get_graph_clusters(self) -> List[int]:
        # calculate the number of clusters in graph
        # use breadth scan
        clusters = []
        visited: Set[str] = set()
        for node in self.nodes:
            if node.name in visited:
                continue
            queue: List[Node] = [node]
            cluster = 0
            while queue:
                next_node = queue.pop(0)
                if next_node.name in visited:
                    continue
                visited.add(next_node.name)
                cluster += 1
                for neighbour in next_node.neighbours:
                    queue.append(neighbour)
            clusters.append(cluster)
        return clusters

    def _clusterize_nodes(self):
        for node in self.nodes:
            self._clusterize_node(node)

    def _clusterize_node(self, node: Node):
        # use breadth scan
        if not node.neighbours:
            return
        clusters = {n.name: [] for n in node.neighbours}
        visited: Set[str] = {node.name}

        queue: List[Tuple[str, Node]] = []
        for neighbour in node.neighbours:
            queue.append((neighbour.name, neighbour))

        while queue:
            cluster_name, next_node = queue.pop(0)
            if next_node.name in visited:
                continue
            lst = clusters[cluster_name]
            lst.append(next_node.name)
            visited.add(next_node.name)
            for neighbour in next_node.neighbours:
                queue.append((cluster_name, neighbour))
        for key, value in clusters.items():
            node.neighbour_group[key] = " ".join(sorted(value))

    def load_from_file(self, file_path: str) -> None:
        added_nodes: Dict[str, Node] = {}
        added_edges: Dict[Tuple[str, str], Edge] = {}

        lines = read_lines(file_path)
        for line in lines:
            # line: "jqt: rhn xhk nvd"
            line = line.replace(":", "")
            parts = line.split(" ")
            part_a = added_nodes.get(parts[0])
            if not part_a:
                part_a = Node(parts[0])
                added_nodes[parts[0]] = part_a
                self.nodes.append(part_a)

            for part_b_name in parts[1:]:
                part_b = added_nodes.get(part_b_name)
                if not part_b:
                    part_b = Node(part_b_name)
                    added_nodes[part_b_name] = part_b
                    self.nodes.append(part_b)

                edge = added_edges.get((part_a.name, part_b.name))
                if not edge:
                    edge = Edge(part_a, part_b)
                    added_edges[(part_a.name, part_b.name)] = edge
                    self.edges.append(edge)
                part_a.neighbours.append(part_b)
                part_b.neighbours.append(part_a)

        # populate neighbours list
        for edge in self.edges:
            edge.node_a.neighbours.append(edge.node_b)
            edge.node_b.neighbours.append(edge.node_a)

        for node in self.nodes:
            node.neighbours = list({n.name: n for n in node.neighbours}.values())


def main():
    graph = Graph()
    # 1460 - too low (1 isn't an answer)
    # 35875 = (1460-25)*25 - too low (25 isn't an answer)
    graph.load_from_file("input_d25_small.txt")
    graph.solve()
    print(graph)


if __name__ == "__main__":
    main()


"""
Using breadth scan, split each node's neighbours into non-overlapping groups.
Find 3 groups, that repeat.
Delete the corresponding edges.
"""