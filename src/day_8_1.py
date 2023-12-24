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
        steps , node = 0, self.nodes["AAA"]
        while node.name != "ZZZ":
            step = steps % len(self.path)
            step_code = self.path[step]
            node = self.nodes[node.l] if step_code == "L" else self.nodes[node.r]
            steps += 1
        return steps

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
    print(rl_map.path)
    #print(rl_map.nodes)
    steps = rl_map.solve_map()
    print(f"Solved in {steps} steps")
