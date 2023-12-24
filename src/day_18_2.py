from typing import List, Tuple

DIRECTIONS = {'L': (-1, 0), 'R': (1, 0), 'U': (0, -1), 'D': (0, 1)}


def calculate_polygon_area(path):
    n = len(path)
    area = 0

    for i in range(n):
        j = (i + 1) % n
        area += path[i][0] * path[j][1]
        area -= path[j][0] * path[i][1]

    return abs(area) / 2.0


class DigAction:
    def __init__(self, dx: int, dy: int, steps: int, color: str):
        self.dx = dx
        self.dy = dy
        self.steps = steps
        self.color = color

    def __str__(self):
        return f"({self.dx, self.dy}) x{self.steps} #{self.color}"


class DigPlan:
    def __init__(self, plan_path: str):
        self._plan_path = plan_path
        self.path: List[Tuple[int, int]] = [(0, 0)]
        self.actions: List[DigAction] = []
        self.trench_length = 0
        self._load_file()

    def solve(self) -> float:
        self._dig_trench()
        inner_area = calculate_polygon_area(self.path)
        # plus 1/2 of the border's surface
        border_area = self.trench_length / 2 + 1
        # why 1? to match the correct answer :) And it worked!!!!!!!!!!!!
        return inner_area + border_area

    def _load_file(self):
        with open(self._plan_path) as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
        for line in lines:
            # R 6 (#70c710)
            parts = line.split(" ")
            #direct = DIRECTIONS[parts[0]]
            #steps = int(parts[1])
            color = parts[2].strip("()#")
            steps = int(color[:5], 16)
            # 0 means R, 1 means D, 2 means L, and 3 means U.
            direct_str = "R" if color[-1] == "0" else "D" if color[-1] == "1" else "L" if color[-1] == "2" else "U"
            direct = DIRECTIONS[direct_str]

            self.actions.append(DigAction(direct[0], direct[1], steps, color))

    def _dig_trench(self):
        cur = 0, 0
        min_x, min_y = 0, 0
        for action in self.actions:
            self.trench_length += action.steps
            cur = (cur[0] + action.dx * action.steps,
                   cur[1] + action.dy * action.steps)
            min_x = min(min_x, cur[0])
            min_y = min(min_y, cur[1])
            self.path.append(cur)
        # make all coords non-negative
        self.path = [(p[0] - min_x, p[1] - min_y) for p in self.path]


def main():
    # 46797 - too low
    plan = DigPlan("/Users/andreisitaev/Downloads/input_d18.txt")
    result = plan.solve()
    print(f"Total: {result}")


if __name__ == "__main__":
    main()
