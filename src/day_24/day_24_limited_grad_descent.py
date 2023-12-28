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
            x, y, z, vx, vy, vz = vars
            return self._error_function((x, y, z), (vx, vy, vz))

        initial_guess = np.array([0, 0, 0, 0, 0, 5])

        max_v_module = 999

        def constraint_vx(x):
            return max_v_module - abs(x[3])
        def constraint_vy(x):
            return max_v_module - abs(x[4])
        def constraint_vz(x):
            return max_v_module - abs(x[5])
        def constraint_vz_positive(x):
            return x[5]

        cons = [{'type': 'ineq', 'fun': constraint_vx},
                {'type': 'ineq', 'fun': constraint_vy},
                {'type': 'ineq', 'fun': constraint_vz},
                {'type': 'ineq', 'fun': constraint_vz_positive}]

        res = minimize(error_function, initial_guess, method='BFGS')
        # I don't even know what BFGS is, I googled minimization
        #   now I know, that's Broyden–Fletcher–Goldfarb–Shanno algorithm
        #res = minimize(error_function, initial_guess, method='Nelder-Mead', options={"maxiter": 1000000})
        #res = minimize(error_function, initial_guess, method='trust-constr', constraints=cons, options={"maxiter": 1000000})

        if res.success:
            optimized_vars = res.x
            print("Optimized variables:", optimized_vars)
        else:
            print("Optimization failed:", res.message)

    def _error_function(self, p: Point3, v: Point3) -> float:
        # knowing the rocket pos & speed, find the rocket's distance to each of the M stones
        # at the moments the rocket hits them
        tests = 3
        distance = 0
        for i in range(tests):
            distance += self._get_dist_squared(p, v, self.stones[i])
        return distance / tests

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
            # make huge coords smaller
            # k = 1000000
            # self.stones[-1].p = (self.stones[-1].p[0] / k, self.stones[-1].p[1] / k, self.stones[-1].p[2] / k)
            # self.stones[-1].v = (self.stones[-1].v[0] / k, self.stones[-1].v[1] / k, self.stones[-1].v[2] / k)


def solve_task():
    hail = Hail("input_d24.txt")
    """
    BFGS works on the small example, but not on the full set of data :(
    BFGS doesn't work for the full set of data
    
    Nelder-Mead works, but returns rubbish 
    
    80 tests (stones):
    Nelder-Mead,  10000 iters: (-165.52200646  126.83658049  -36.85936161)
    
    L-BFGS-B: (0, 0, 0), (133, 447, -13)
    """
    hail.solve()


if __name__ == "__main__":
    solve_task()


"""
Any vector will do, unless v not equal to any of the other vectors (?)
- or not collinear?
"""