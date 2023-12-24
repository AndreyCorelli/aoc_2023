from typing import TypeAlias, List, Optional

import numpy as np

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


class Stone:
    def __init__(self, point: Point3, v: Point3):
        self.point = point
        self.v = v
        self.p2d = (point[0], point[1])
        self.v2d = (v[0], v[1])

    def __repr__(self):
        return f"{self.p2d} @{self.v2d}"

    def __str__(self):
        return self.__repr__()

    @classmethod
    def parse_line(cls, line: str):
        line = line.replace(" @ ", ", ")
        x, y, z, vx, vy, vz = [int(p) for p in line.split(", ")]
        return Stone((x, y, z), (vx, vy, vz))

    @classmethod
    def intersect(cls, a: "Stone", b: "Stone") -> Optional[PointF]:
        p_ax, p_ay = a.p2d
        v_ax, v_ay = a.v2d
        p_bx, p_by = b.p2d
        v_bx, v_by = b.v2d

        denom = v_ax * v_by - v_ay * v_bx
        if denom == 0:
            # parallel or exact copies
            return None

        t = ((p_bx - p_ax) * v_by - (p_by - p_ay) * v_bx) / denom
        s = ((p_bx - p_ax) * v_ay - (p_by - p_ay) * v_ax) / denom

        if t >= 0 and s >= 0:
            intersection_x = p_ax + t * v_ax
            intersection_y = p_ay + t * v_ay
            return intersection_x, intersection_y

        return None


class Hail:
    def __init__(self, file_path: str):
        self.stones: List[Stone] = []
        self.load_from_file(file_path)

    def solve_2d(self):
        # find the (x, y) and (vx, vy) of the rayX, that intersects all the rays


    def load_from_file(self, file_path: str):
        lines = read_lines(file_path)
        for line in lines:
            self.stones.append(Stone.parse_line(line))


def solve_task():
    hail = Hail("input_d24.txt")  # 11246
    hail.solve_2d()


if __name__ == "__main__":
    solve_task()


"""
Any vector will do, unless v not equal to any of the other vectors (?)
- or not collinear?
"""