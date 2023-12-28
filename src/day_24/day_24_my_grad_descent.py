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
import copy
import math
import random
from typing import TypeAlias, List, Callable, Tuple

import numpy as np
from scipy.optimize import minimize

from src.file_path import read_lines

Point: TypeAlias = tuple[int, int]
Point3: TypeAlias = tuple[int, int, int]
Point6: TypeAlias = tuple[int, int, int, int, int, int]

ZERO_P6 = (0, 0, 0, 0 ,0 ,0)

PointF: TypeAlias = tuple[float, float]


def sum_point3(p1: Point3, p2: Point3) -> Point3:
    return p1[0] + p2[0], p1[1] + p2[1], p1[2] + p2[2]


def sub_point3(p1: Point3, p2: Point3) -> Point3:
    return p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]


def sum_point6(p1: Point6, p2: Point6) -> Point6:
    return p1[0] + p2[0], p1[1] + p2[1], p1[2] + p2[2], p1[3] + p2[3], p1[4] + p2[4], p1[5] + p2[5]


def sub_point6(p1: Point6, p2: Point6) -> Point6:
    return p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2], p1[3] - p2[3], p1[4] - p2[4], p1[5] - p2[5]


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
        def error_function(vars):
            vx, vy, vz = vars
            return self._error_function((vx, vy, vz))

        best_point = ZERO_P6
        min_error = math.inf

        for i in range(900000):
            # 300 random points to try
            gd = GradDescend(error_function)
            error, point = gd.solve(
                200, start_lr=15, end_lr=0.04
            )
            if error < min_error:
                min_error = error
                best_point = point
                print(f"New min {min_error} at {best_point}")

        gd.plot_error_chart()
        print(f"Completed, min error {min_error} at {best_point}")

    def _error_function(self, v: Point3) -> float:
        # knowing the rocket pos & speed, find the rocket's distance to each of the M stones
        # at the moments the rocket hits them
        p = self._find_point(v)
        tests = 3
        distance = 0
        for i in range(tests):
            distance += self._get_error_by_stones(p, v, self.stones[i])
        return distance / tests

    def _find_point(self, r: Point3) -> Point3:
        # knowing the rocket speed (r), find the rocket's position at the moments
        # the rocket hits each of the 3 stones
        a, b = self.stones[0], self.stones[1]

        dx1 = (r[0] - a.v[0])
        # equation for the first stone's y
        k1 = a.v[1] / dx1 - r[1] / dx1
        b1 = a.p[1] + a.v[1] * a.p[0] / dx1 - r[1] * a.p[0] / dx1

        # equation for the first stone's z
        k2 = a.v[2] / dx1 - r[2] / dx1
        b2 = a.p[2] + a.v[2] * a.p[0] / dx1 - r[2] * a.p[0] / dx1

        # equation for the second stone's y
        dx1 = (r[0] - b.v[0])
        k3 = b.v[1] / dx1 - r[1] / dx1
        b3 = b.p[1] + b.v[1] * b.p[0] / dx1 - r[1] * b.p[0] / dx1

        x = (b3 - b1) / (k3 - k1)
        y = b1 - k1 * x
        z = b2 - k2 * x

        return round(x), round(y), round(z)

    def _get_error_by_stones(self, p: Point3, v: Point3, stone: Stone) -> float:
        # knowing the rocket pos & speed, find the rocket's distance to each of the M stones
        # at the moments the rocket hits them

        # we try fix x, next time y, next time z
        # fixed_dim = (self._current_dim + 1) % 3

        # actually, on a smaller example it worked with z only
        fixed_dim = 2
        self._current_dim = fixed_dim

        denom = (v[fixed_dim] - stone.v[fixed_dim])
        if denom == 0:
            return 9999999999999999999999
        t = (stone.p[fixed_dim] - p[fixed_dim]) / denom
        if t < 0 or math.isinf(t):  # v[fixed_dim] is pointing in the wrong direction
            return 9999999999999999999999

        error = 0
        for dim in range(2):
            if dim == fixed_dim:
                continue
            d_p = (p[dim] + v[dim] * t - stone.p[dim] - stone.v[dim] * t)
            error += d_p * d_p
        return error ** 0.5

    def load_from_file(self, file_path: str):
        lines = read_lines(file_path)
        for line in lines:
            self.stones.append(Stone.parse_line(line))


class GradDescend:
    CONSTRAINTS = [
        (-943880319406260, 943880319406260),  # x
        (-943880319406260, 943880319406260),  # y
        (0, 9000000000),  # z
        (-4000, 4000),  # vx
        (-4000, 4000),  # vy
        (-1000, 1000),  # vz
    ]

    def __init__(self, error_function: Callable, verbose: bool = False):
        # error function accepts 6 args [x, y, z, vx, vy, vz] and returns a Tuple[float, float, float]:
        #  this is the error gradient by x, y, z, vx, vy, vz
        self.error_function = error_function
        self.verbose = verbose
        self.errors: List[float] = []
        self.x_lst: List[float] = []
        self.vx_lst: List[float] = []

    def solve(self,
              max_iter: int,
              start_lr: float = 1,
              end_lr: float = 0.08) -> Tuple[float, Point6]:
        self.errors: List[float] = []
        self.x_lst: List[float] = []
        self.vx_lst: List[float] = []

        min_error = math.inf
        point = self._get_random_point()
        #point = (187891, 170858, -232612, 1450, 2303, 1788)  #       176278095330572
        #point = (1038968, 1104307, -5268479, 461, 533, 384)  # error: 137314699575757

        current_error = self.error_function(point)
        best_point = point

        # avg coordinate / avg speed (by one axis) ~ 310862797921357 / 100
        # learning rate differs for (x, y, z) and (vx, vy, vz)

        lr_spd_k = 310862797921357 / 100
        start_lr_spd = start_lr / lr_spd_k
        end_lr_spd = end_lr / lr_spd_k

        initial_learning_rate = [start_lr, start_lr, start_lr, start_lr_spd, start_lr_spd, start_lr_spd]
        final_learning_rate = [end_lr, end_lr, end_lr, end_lr_spd, end_lr_spd, end_lr_spd]

        learning_rate = copy.copy(initial_learning_rate)

        for iteration in range(max_iter):
            gradient = []
            for i in range(6):
                step = random.randint(20, 80) - 51
                if step == 0:
                    step = 1
                p2 = point[:i] + (point[i] + step,) + point[i+1:]
                error = self.error_function(p2)

                delta_f = error - current_error
                delta_x = p2[i] - point[i]

                move = delta_f / delta_x if delta_x != 0 else delta_f
                gradient.append(move * learning_rate[i])

            # lower the learning_rate
            k = iteration / max_iter
            learning_rate = [
                a + (b - a) * k
                for a, b in zip(initial_learning_rate, final_learning_rate)]

            new_point = [point[i] - gradient[i] for i in range(6)]
            point = tuple(new_point)

            current_error = self.error_function(point)

            self.errors.append(current_error)
            self.x_lst.append(point[0])
            self.vx_lst.append(point[3])

            if current_error < min_error:
                min_error = current_error
                best_point = point

        if self.verbose:
            print(f"Reached min error {min_error} at {best_point}")
        #self.plot_error_chart()
        return current_error, point

    def _get_random_point(self) -> Point6:
        # x, y, z = 0, 0, 0
        # v is random
        #return tuple([0, 0, 0] + [
        #    random.randint(self.CONSTRAINTS[d][0], self.CONSTRAINTS[d][1])
        #    for d in range(3, 6)
        #])
        return tuple([
            random.randint(self.CONSTRAINTS[d][0], self.CONSTRAINTS[d][1])
            for d in range(6)
        ])

    def plot_error_chart(self):
        import matplotlib.pyplot as plt

        plt.plot(self.errors)
        plt.xlabel('iteration')
        plt.ylabel('error')
        plt.savefig('/Users/andreisitaev/sources/andrei/aoc_2023/output/optimizer_error.png')
        plt.close()

        plt.plot(self.x_lst)
        plt.xlabel('iteration')
        plt.ylabel('x')
        plt.savefig('/Users/andreisitaev/sources/andrei/aoc_2023/output/optimizer_x.png')
        plt.close()

        plt.plot(self.vx_lst)
        plt.xlabel('iteration')
        plt.ylabel('vx')
        plt.savefig('/Users/andreisitaev/sources/andrei/aoc_2023/output/optimizer_vx.png')

    def _get_neighbours(self, p: Point6) -> List[Point6]:
        nbs = []
        while len(nbs) < 8:
            p2 = p
            for j in range(6):
                step = round(4 * random.random() - 2)
                coord = p2[j] + step
                #if coord < self.CONSTRAINTS[j][0] or coord > self.CONSTRAINTS[j][1]:
                #    continue
                p2 = p2[:j] + (p2[j] + step,) + p2[j+1:]
            nbs.append(p2)
        return nbs


def test_descend():
    def error_function(p: Point6) -> float:
        p_center = (21400, -200, 0, 90, -30, -105)
        delta = sub_point6(p, p_center)
        return sum([d*d for d in delta])

    gd = GradDescend(error_function)
    point = gd.solve()
    print()


def solve_task():
    #test_descend()
    hail = Hail("input_d24.txt")
    hail.solve()


if __name__ == "__main__":
    solve_task()
