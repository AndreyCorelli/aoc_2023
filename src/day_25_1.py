from typing import List, Dict, Tuple

from file_path import read_lines


class Node:
    def __init__(self, name: str):
        self.name = name
        self.neighbours: List["Node"] = []

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
    graph.load_from_file("input_d25_small.txt")
    print(graph)


if __name__ == "__main__":
    main()


"""
Using breadth scan, split each node's neighbours into non-overlapping groups.
Find 3 groups, that repeat.
Delete the corresponding edges.
"""