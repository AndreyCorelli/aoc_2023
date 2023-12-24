import math
from functools import reduce
from typing import Dict


class MapNode:
    def __init__(self, name: str, l: str, r: str):
        self.name = name
        self.l = l
        self.r = r

    def __str__(self) -> str:
        return f"{self.name} = ({self.l}, {self.r})"

    def __repr__(self) -> str:
        return str(self)


class RlMap:
    def __init__(self):
        self.path = ""
        self.nodes: Dict[str, MapNode] = {}

    def solve_map(self) -> int:
        nodes = [self.nodes[n] for n in self.nodes if n.endswith("A")]
        steps = [self._solve_one_map(n) for n in nodes]
        return self.lcm(steps)

    def _solve_one_map(self, node: MapNode) -> int:
        steps = 0
        while not node.name.endswith("Z"):
            step = steps % len(self.path)
            step_code = self.path[step]
            node = self.nodes[node.l] if step_code == "L" else self.nodes[node.r]
            steps += 1
        return steps

    @classmethod
    def lcm(cls, numbers) -> int:
        def lcm_of_two(a, b):
            return abs(a * b) // math.gcd(a, b)

        return reduce(lcm_of_two, numbers)

    @classmethod
    def parse_file(cls, file_path) -> "RlMap":
        rl_map = cls()
        with open(file_path, 'r') as file:
            lines = file.readlines()
            rl_map.path = lines[0].strip()

            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.strip().split(' = ')
                name = parts[0]
                l, r = parts[1].strip('()').split(', ')
                rl_map.nodes[name] = MapNode(name, l, r)

        return rl_map


if __name__ == "__main__":
    rl_map = RlMap.parse_file("/Users/andreisitaev/Downloads/input_d8_1.txt")
    #print(rl_map.path)
    #print(rl_map.nodes)
    steps = rl_map.solve_map()
    print(f"Solved in {steps} steps")
