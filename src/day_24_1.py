from typing import TypeAlias, List, Optional

from src.file_path import read_lines

Point: TypeAlias = tuple[int, int]
Point3: TypeAlias = tuple[int, int, int]

PointF: TypeAlias = tuple[float, float]


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
    MIN_DIM = 200000000000000
    MAX_DIM = 400000000000000

    def __init__(self, file_path: str):
        self.stones: List[Stone] = []
        self.load_from_file(file_path)

    def solve(self) -> int:
        total = 0
        for i in range(len(self.stones)):
            for j in range(i + 1, len(self.stones)):
                if p := Stone.intersect(self.stones[i], self.stones[j]):
                    if self.MIN_DIM <= p[0] <= self.MAX_DIM and self.MIN_DIM <= p[1] <= self.MAX_DIM:
                        total += 1
        print(f"Found {total} intersections")
        return total

    def load_from_file(self, file_path: str):
        lines = read_lines(file_path)
        for line in lines:
            self.stones.append(Stone.parse_line(line))


def test_inter_coords():
    a = Stone((20, 25, 34), (-2, -2, -4))
    b = Stone((12, 31, 28), (-1, -2, -1))
    assert Stone.intersect(a, b) == (-2, 3)


def test_all():
    test_inter_coords()


def solve_task():
    hail = Hail("input_d24.txt")  # 11246
    hail.solve()


if __name__ == "__main__":
    #test_all()
    solve_task()
