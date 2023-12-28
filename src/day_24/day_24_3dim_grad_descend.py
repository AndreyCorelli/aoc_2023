"""
The idea is to find a solution for the first 3 (might be more) stones using gradient descend:
- variables are x, y, z, vx, vy, vz
- error function is square distance between stones' and the rocket
- to define the distance between rocket (x, y, z) and stone (x_s, y_s, z_s):
  - if (x, y, z) == (x_s, y_s, z_s) then distance is 0
  - t = (z_s - z) / (vz - vx_z) - we know, z_s is never 0, and the signs of vz / vz_s are different
  - dx = (x + vx * t - x_s - vx_s * t), dy = ...
  - distance = dx* dx + dy * dy (dz == 0)
"""
import math
from typing import TypeAlias, List

import numpy as np
from scipy.optimize import minimize

from src.file_path import read_lines

Point: TypeAlias = tuple[int, int]
Point3: TypeAlias = tuple[int, int, int]

PointF: TypeAlias = tuple[float, float]


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

    def solve(self):

        def error_function(vars):
            vx, vy, vz = vars
            return self._error_function((vx, vy, vz))

        initial_guess = np.array([0, 0, 5])

        #res = minimize(error_function, initial_guess, method='BFGS')
        # I don't even know what BFGS is, I googled minimization
        #   now I know, that's Broyden–Fletcher–Goldfarb–Shanno algorithm
        res = minimize(error_function, initial_guess, method='Nelder-Mead', options={"maxiter": 1000000})
        #res = minimize(error_function, initial_guess, method='trust-constr', constraints=cons, options={"maxiter": 1000000})

        if res.success:
            optimized_vars = res.x
            print("Optimized variables:", optimized_vars)
        else:
            print("Optimization failed:", res.message)

    def _error_function(self, v: Point3) -> float:
        # knowing the rocket pos & speed, find the rocket's distance to each of the M stones
        # at the moments the rocket hits them
        p = self._find_point(v)
        tests = 3
        distance = 0
        for i in range(tests):
            distance += self._get_dist_squared(p, v, self.stones[i])
        return distance / tests

    def _find_point(self, r: Point3) -> Point3:
        # knowing the rocket speed (r), find the rocket's position at the moments
        # the rocket hits each of the 3 stones
        a, b = self.stones[0], self.stones[1]

        dx1 = (r[0] - a.v[0])
        if dx1 == 0:
            dx1 = 0.00001

        # equation for the first stone's y
        k1 = a.v[1] / dx1 - r[1] / dx1
        b1 = a.p[1] + a.v[1] * a.p[0] / dx1 - r[1] * a.p[0] / dx1

        # equation for the first stone's z
        k2 = a.v[2] / dx1 - r[2] / dx1
        b2 = a.p[2] + a.v[2] * a.p[0] / dx1 - r[2] * a.p[0] / dx1

        # equation for the second stone's y
        dx1 = (r[0] - b.v[0])
        if dx1 == 0:
            dx1 = 0.00001

        k3 = b.v[1] / dx1 - r[1] / dx1
        b3 = b.p[1] + b.v[1] * b.p[0] / dx1 - r[1] * b.p[0] / dx1

        x_denom = k3 - k1
        if x_denom == 0:
            x = 90000000000
        else:
            x = (b3 - b1) / (k3 - k1)
        y = b1 - k1 * x
        z = b2 - k2 * x

        return round(x), round(y), round(z)

    def _get_dist_squared(self, p: Point3, v: Point3, stone: Stone) -> float:
        # knowing the rocket pos & speed, find the rocket's distance to each of the M stones
        # at the moments the rocket hits them
        max_error = 99999999999999999999999
        t = (stone.p[2] - p[2]) / (v[2] - stone.v[2])
        if t < 0 or math.isinf(t):
            return max_error
        z = p[2] + v[2] * t
        if z < 0:
            return max_error

        dx = (p[0] + v[0] * t - stone.p[0] - stone.v[0] * t)
        dy = (p[1] + v[1] * t - stone.p[1] - stone.v[1] * t)
        error = dx * dx + dy * dy
        self._min_error = min(self._min_error, error)
        return error

    def load_from_file(self, file_path: str):
        lines = read_lines(file_path)
        for line in lines:
            self.stones.append(Stone.parse_line(line))


def solve_task():
    hail = Hail("input_d24_small.txt")
    #print(hail._find_point((-3, 1, 2)))  # 24, 13, 10
    hail.solve()


if __name__ == "__main__":
    solve_task()
