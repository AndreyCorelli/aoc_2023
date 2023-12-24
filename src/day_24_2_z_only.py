import random
from typing import TypeAlias, List, Optional, Set

import numpy as np
from scipy.optimize import linprog

from src.file_path import read_lines

Point: TypeAlias = tuple[int, int]
Point3: TypeAlias = tuple[int, int, int]

PointF: TypeAlias = tuple[float, float]


def solve_slae_with_constraints(
        a: np.ndarray,
        b: np.ndarray,
        stones_count: int) -> Optional[np.ndarray]:
    """
    :param a: coeffs matrix, a00 = 1, a10 = 0, ... aNN+2 = (vy - vyn)
    :param b: x1, y1, ..., yN
    :param stones_count: N
    :returns: [z, t1, ..., tN]
    """
    # objective function: a dummy one as we just need a feasible solution
    c = np.zeros(stones_count + 2)

    # Bounds for the variables: first 300 variables > 0, others unrestricted
    # z might be any value, while t1, ... tN might be >= 0 ( > 0?)
    x_bounds = [(None, None)] * 1 + [(0, None)] + [(1, None)] * stones_count

    # Solving the linear programming problem
    res = linprog(c, A_eq=a, b_eq=b, bounds=x_bounds, method='highs')

    if res.success:
        print("Solution found")
        print(res.x)
        return res.x
    return None


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
        for vz in range(1, 200):
            """
            Solve system:
            z + t1*vz - t1*vz1 = z1, ...
            z + tN*vz - tN*vzN = zN.
            
            a00 = a10 = aN0 = 1
            a01 = vz, a02 = -vz1, a03 ... a0N = 0            
            b1 = z1 + t1*vz1
            """

            # build coeff (a) and constant (b) matrix
            a_lst = []
            b_lst = []
            for i, stone in enumerate(self.stones):
                t_coeffs = [0] * len(self.stones)
                t_coeffs[i] = -stone.v[2]
                a_lst += [[1, vz] + t_coeffs]
                b_lst.append(stone.p[2])

            a = np.array(a_lst)
            b = np.array(b_lst)

            solved = solve_slae_with_constraints(a, b, len(self.stones))
            if solved is None:
                continue
            # we know z, t1, ..., tN
            # now we'll find x, y, vx, vy, vz
            impact = self.find_impact(solved)
            # if impact:
            #     print("Solution found, breaking")
            #     print(f"vz: {vz}")
            #     print(f"impact: {impact}")
            #     return

        print("No solution's found")

    def find_impact(self, z_times: np.ndarray) -> Optional[Stone]:
        vx = self._find_vector_dim(z_times, 0)
        vy = self._find_vector_dim(z_times, 1)

        x = self._get_x_knowing_vx(vx, z_times, 0)
        y = self._get_x_knowing_vx(vy, z_times, 1)

        # now we know (x, y, z)
        print(f"x: {x}, y: {y}, z: {z_times[0]}")

    def _get_x_knowing_vx(self, vx: float, z_times: np.ndarray, n_dim: int):
        vx1 = self.stones[0].v[n_dim]
        x1 = self.stones[0].p[n_dim]
        t1 = z_times[1]
        x = vx1 * t1 + x1 - vx * t1
        return x

    def _find_vector_dim(self, z_times: np.ndarray, dim_index: int) -> float:
        """
        For dim = 1 solve system:
        vx*t1 + x = vx1*t1 + x1, ...
        vx*tN + x = vxN*tN + xN.
        2 equations are enough
        """
        i = 0
        t1 = z_times[i + 1]
        vx1 = self.stones[i].v[dim_index]
        x1 = self.stones[i].p[dim_index]

        for j in range(1, len(self.stones)):
            tj = z_times[j + 1]
            if tj == t1:
                continue
            denom = (t1 - tj)
            vxj = self.stones[j].v[dim_index]
            xj = self.stones[j].p[dim_index]
            numer = vx1 * t1 + x1 - vxj * tj - xj

            vx = numer / denom
        return vx

    def load_from_file(self, file_path: str):
        lines = read_lines(file_path)
        for line in lines:
            self.stones.append(Stone.parse_line(line))


def solve_task():
    hail = Hail("input_d24_small.txt")  # 11246
    hail.solve()


if __name__ == "__main__":
    solve_task()
