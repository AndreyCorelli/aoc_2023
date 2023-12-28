"""
- Knowing rocket's speed we can calculate the rocket's position at the moments
and check if it hits all the stones.

- Rocket speed changes in a narrow range, unlike rocket coords, thus I can just brute force it
as I failed with the gradient descent approach.
"""
import math
from typing import TypeAlias, List, Optional

from src.file_path import read_lines

Point3: TypeAlias = tuple[int, int, int]


class Stone:
    def __init__(self, p: Point3, v: Point3):
        self.p = p
        self.v = v

    def __repr__(self):
        return f"{self.p} @{self.v}"

    def __str__(self):
        return self.__repr__()

    @classmethod
    def parse_line(cls, line: str):
        line = line.replace(" @ ", ", ")
        x, y, z, vx, vy, vz = [int(p) for p in line.split(", ")]
        return Stone((x, y, z), (vx, vy, vz))

    def copy(self) -> "Stone":
        return Stone(self.p, self.v)


class Hail:
    def __init__(self, file_path: str):
        self.stones: List[Stone] = []
        self.load_from_file(file_path)
        self._min_error = math.inf
        self._current_dim = 0

    def solve(self):
        # Found a solution: p=(116689373784735, 348350724549432, 251559839225936) @ v=(330, -94, 53)
        for vx in range(-600, 600):
            print(f"Checking vx={vx}")
            for vy in range(-600, 600):
                for vz in range(-200, 600):
                    if self.point_fits((vx, vy, vz)):
                        return
        print("All solutions checked, not found")

    def point_fits(self, v: Point3) -> bool:
        # knowing the rocket speed, find the rocket's distance to each of the M stones
        # at the moments the rocket hits them
        p = self._find_point(v)
        if p is None:
            return False

        for stone in self.stones:
            t_d = v[0] - stone.v[0]
            if t_d == 0:
                return False
            t = (stone.p[0] - p[0]) / t_d

            if p[1] + v[1] * t != stone.p[1] + stone.v[1] * t:
                return False
            if p[2] + v[2] * t != stone.p[2] + stone.v[2] * t:
                return False

        print(f"Found a solution: p={p} @ v={v}")
        return True

    def _find_point(self, r: Point3) -> Optional[Point3]:
        # knowing the rocket speed (r), find the rocket's position at the moments
        # the rocket hits each of the 3 stones
        a, b = self.stones[0], self.stones[1]

        dx1 = (r[0] - a.v[0])
        if dx1 == 0:
            return None

        # equation for the first stone's y
        k1 = a.v[1] / dx1 - r[1] / dx1
        b1 = a.p[1] + a.v[1] * a.p[0] / dx1 - r[1] * a.p[0] / dx1

        # equation for the first stone's z
        k2 = a.v[2] / dx1 - r[2] / dx1
        b2 = a.p[2] + a.v[2] * a.p[0] / dx1 - r[2] * a.p[0] / dx1

        # equation for the second stone's y
        dx1 = (r[0] - b.v[0])
        if dx1 == 0:
            return None

        k3 = b.v[1] / dx1 - r[1] / dx1
        b3 = b.p[1] + b.v[1] * b.p[0] / dx1 - r[1] * b.p[0] / dx1

        x_denom = k3 - k1
        if x_denom == 0:
            return None
        else:
            x = (b3 - b1) / (k3 - k1)
        y = b1 - k1 * x
        z = b2 - k2 * x

        return round(x), round(y), round(z)

    def load_from_file(self, file_path: str):
        lines = read_lines(file_path)
        for line in lines:
            self.stones.append(Stone.parse_line(line))


def solve_task():
    hail = Hail("input_d24.txt")
    hail.solve()


if __name__ == "__main__":
    solve_task()
