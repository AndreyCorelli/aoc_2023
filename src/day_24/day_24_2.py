"""
I would try random rocket speeds, checking if the speed vectors and any of
the stone vectors aint collinear.

Then I would try to find a solution for the system of equations, where I pass the speed vector,
found previously.
"""

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
        for _ in range(10000):
            v = self.find_vector()   # e.g. (-3, 1, 2)
            # v = (-3, 1, 2)  # it works for the sample input ([24. 13.  5.  5.  3.  4.  6.  1.])
            # v = self._make_random_vector()

            # build coeff (a) and constant (b) matrix
            a_lst = []
            b_lst = []
            for i, stone in enumerate(self.stones):
                x_coeffs = [0] * len(self.stones)
                x_coeffs[i] = (v[0] - stone.v[0])
                a_lst += [[1, 0, 0] + x_coeffs]

                y_coeffs = [0] * len(self.stones)
                y_coeffs[i] = (v[1] - stone.v[1])
                a_lst += [[0, 1, 0] + y_coeffs]

                z_coeffs = [0] * len(self.stones)
                z_coeffs[i] = (v[2] - stone.v[2])
                a_lst += [[0, 0, 2] + z_coeffs]

                b_lst += [stone.p[0], stone.p[1], stone.p[2]]

            a = np.array(a_lst)
            b = np.array(b_lst)

            solved = solve_slae_with_constraints(a, b, len(self.stones))
            if solved:
                print("Solution found, breaking")
                print(f"v: {v}")
                return
        print("No solution's found")

    def find_vector(self) -> Optional[Point3]:
        # find any vector with z > 0, not collinear with any other vector
        checked_vectors: Set[Point3] = set()

        for attempt in range(300):
            v = self._make_random_vector()
            # v = (-3, 1, 2)  # this one works for the test input
            if v in checked_vectors:
                continue
            checked_vectors.add(v)

            pass_checks = True
            for stone in self.stones:
                if are_collinear(stone.v, v):
                    pass_checks = False
                    break
            if pass_checks:
                print(f"Found vector {v} at {attempt + 1} attempt")
                return v

        print("No vector found")
        return None

    @classmethod
    def _make_random_vector(cls) -> Point3:
        vx = random.randint(-150, 150)
        vy = random.randint(-150, 150)
        vz = random.randint(1, 150)
        v = (vx, vy, vz)
        return v

    def load_from_file(self, file_path: str):
        lines = read_lines(file_path)
        for line in lines:
            self.stones.append(Stone.parse_line(line))


def solve_task():
    hail = Hail("input_d24_small.txt")
    hail.solve()


if __name__ == "__main__":
    solve_task()


"""
Any vector will do, unless v not equal to any of the other vectors (?)
- or not collinear?
"""