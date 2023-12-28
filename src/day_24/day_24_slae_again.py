import random
from typing import TypeAlias, List, Optional, Set

import numpy as np
from scipy.optimize import linprog

from src.file_path import read_lines

Point: TypeAlias = tuple[int, int]
Point3: TypeAlias = tuple[int, int, int]

PointF: TypeAlias = tuple[float, float]


def are_collinear(a: Point3, b: Point3) -> bool:
    # Convert tuples to numpy arrays
    vec_a = np.array(a)
    vec_b = np.array(b)

    # Compute the cross product
    cross_prod = np.cross(vec_a, vec_b)

    # Check if the cross product is close to zero vector
    return np.allclose(cross_prod, [0, 0, 0])


def solve_slae_with_constraints(
        a: np.ndarray,
        b: np.ndarray,
        stones_count: int) -> bool:
    """
    :param a: coeffs matrix, a00 = 1, a10 = 0, ... aNN+3 = (vz - vzn)
    :param b: x1, y1, z1, ..., zN
    :param stones_count: N
    """
    # objective function: a dummy one as we just need a feasible solution
    c = np.zeros(stones_count + 3)

    # Bounds for the variables: first 300 variables > 0, others unrestricted
    # x, y might be any values, while z, t1, ... tN might be >= 0
    x_bounds = [(None, None)] * 2 + [(0, None)] * (stones_count + 1)

    # Solving the linear programming problem
    res = linprog(c, A_eq=a, b_eq=b, bounds=x_bounds, method='highs')

    if res.success:
        print("Solution found")
        print(res.x)
        return True
    return False


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


class Hail:
    def __init__(self, file_path: str):
        self.stones: List[Stone] = []
        self.load_from_file(file_path)

    def solve(self):
        """
        t1 - when rocket & stone1 collide
        t1 = (x1 - x) / (vx - vx1)



        :return:
        """



    def load_from_file(self, file_path: str):
        lines = read_lines(file_path)
        for line in lines:
            self.stones.append(Stone.parse_line(line))


def solve_task():
    hail = Hail("input_d24_small.txt")
    hail.solve()


if __name__ == "__main__":
    solve_task()

