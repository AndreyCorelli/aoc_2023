from typing import TypeAlias, List, Tuple, Dict

from src.file_path import read_lines

Point2: TypeAlias = tuple[int, int]
Point3: TypeAlias = tuple[int, int, int]

Span2: TypeAlias = tuple[Point2, Point2]


class Brick:
    def __init__(self):
        self.span: Span2 = ((0, 0), (0, 0))
        self.bottom: int = 0
        self.top: int = 0
        self.index = 0

    def __str__(self):
        z_str = self.bottom
        if self.top != self.bottom:
            z_str = f"{self.bottom}~{self.top}"
        return f"[{self.index}][{self.span[0][0]}, {self.span[0][1]} - {self.span[1][0]}, {self.span[1][1]}] {z_str}"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def load_from_file(cls, file_path: str) -> List["Brick"]:
        lines = read_lines(file_path)
        bricks = [cls.from_str(line) for line in lines]
        for i, brick in enumerate(bricks):
            brick.index = i
        return bricks

    @classmethod
    def from_str(cls, brick_str: str) -> "Brick":
        # 0,2,3~2,2,3
        brick_str = brick_str.replace("~", ",")
        parts = brick_str.split(",")
        x1, y1, z1, x2, y2, z2 = [int(part) for part in parts]

        brick = cls()
        brick.span = ((x1, y1), (x2, y2))
        brick.bottom = min(z1, z2)
        brick.top = max(z1, z2)
        return brick

    def spans_intersect(self, other: "Brick") -> bool:
        return self.span[0][0] <= other.span[1][0] and self.span[1][0] >= other.span[0][0] and \
               self.span[0][1] <= other.span[1][1] and self.span[1][1] >= other.span[0][1]

    def move_to_level(self, new_bottom: int):
        delta = self.bottom - new_bottom
        self.bottom = new_bottom
        self.top -= delta


class BrickLayer:
    def __init__(self, order: str):
        self.order = order
        self.bricks: Dict[int, List[Brick]] = {}

    @classmethod
    def build_layer(cls, order: str, bricks: List[Brick]) -> "BrickLayer":
        layer = cls(order)
        bricks_by_z = {}
        for brick in bricks:
            brick_z = brick.top if order == "top" else brick.bottom
            if brick_z not in bricks_by_z:
                bricks_by_z[brick_z] = []
            bricks_by_z[brick_z].append(brick)
        layer.bricks = bricks_by_z
        return layer


class Jenga:
    def __init__(self, file_path: str):
        self.bricks: List[Brick] = Brick.load_from_file(file_path)
        # {8: [3, 2]} means brick 8 lies on bricks 3 and 2
        self.lies_on: Dict[int, List[int]] = {}

    def detect_removable(self) -> int:
        """
        detect bricks that could be removed: bricks that aren't the only foundation for some other bricks
        lies_on = {0: [], 1: [0], 2: [0], 3: [1, 2], 4: [1, 2], 5: [3, 4], 6: [5]}
        removable = [6, 4, 3, 2, 1]
        """

        foundation = {f[0] for f in self.lies_on.values() if len(f) == 1}
        removable = []
        for i in range(len(self.bricks)):
            if i not in foundation:
                removable.append(i)
        print(f"Bricks {removable} are removable")
        print(f"{len(removable)} in total")
        return len(removable)

    def zip_bricks(self):
        # let bricks fall until all lay on the ground / one on another
        bottoms = BrickLayer.build_layer("bottom", self.bricks)

        bottom_keys = [k for k in bottoms.bricks.keys() if k > 0]
        bottom_keys.sort()

        for bottom_key in bottom_keys:
            for brick in bottoms.bricks[bottom_key]:
                self.move_brick(brick)

    def move_brick(self, brick: Brick):
        # find a brick, that has top lower than passed brick's bottom
        # and that intersects with passed brick:
        min_level = 0
        intersected = []
        for b in self.bricks:
            if b.top >= brick.bottom:
                continue
            if not b.spans_intersect(brick):
                continue
            if b.top == brick.bottom - 1:
                # brick "brick" already lies on top of b
                continue
            intersected.append(b)
            min_level = max(min_level, b.top + 1)

        brick.move_to_level(min_level)
        # find the bricks, the "brick" lies on
        foundation = [b for b in intersected if b.top == brick.bottom - 1]
        self.lies_on[brick.index] = [b.index for b in foundation]


def test_spans_intersect():
    a = Brick.from_str("0,2,3~0,2,3")
    b = Brick.from_str("0,2,3~1,2,3")
    assert a.spans_intersect(b)

    a = Brick.from_str("0,1,5~3,1,5")
    b = Brick.from_str("1,0,3~1,2,3")
    assert a.spans_intersect(b)

    a = Brick.from_str("2,2,5~3,2,5")
    b = Brick.from_str("1,0,3~1,2,3")
    assert not a.spans_intersect(b)


def test_all():
    test_spans_intersect()


def check_small():
    jenga = Jenga("input_d22_small.txt")
    jenga.zip_bricks()
    jenga.detect_removable()


def solve():
    jenga = Jenga("input_d22.txt")
    jenga.zip_bricks()
    jenga.detect_removable()


if __name__ == "__main__":
    solve()
