from typing import Set, Tuple


class Beam:
    def __init__(self, x: int, y: int, dx: int, dy: int):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def __str__(self) -> str:
        direction = "right" if self.dx >= 0 else "top" if self.dy <= 0 else "left" if self.dx <= 0 else "bottom"
        return f"({self.x}, {self.y}) {direction}"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def is_vertical(self) -> bool:
        return self.dx == 0

    def is_in_grid(self, w: int, h: int) -> bool:
        return 0 <= self.x < w and 0 <= self.y < h

    def move_next(self) -> None:
        self.x += self.dx
        self.y += self.dy

    def mirror(self, cell: str) -> None:
        if cell == "/":
            if self.dx == 1:
                self.dx = 0
                self.dy = -1
                return
            if self.dx == -1:
                self.dx = 0
                self.dy = 1
                return
            if self.dy == 1:
                self.dx = -1
                self.dy = 0
                return
            if self.dy == -1:
                self.dx = 1
                self.dy = 0
                return
        # cell == "\\"
        if self.dx == 1:
            self.dx = 0
            self.dy = 1
            return
        if self.dx == -1:
            self.dx = 0
            self.dy = -1
            return
        if self.dy == 1:
            self.dx = 1
            self.dy = 0
            return
        if self.dy == -1:
            self.dx = -1
            self.dy = 0
            return

    def make_copy(self) -> "Beam":
        return Beam(self.x, self.y, self.dx, self.dy)

    def to_vector(self) -> Tuple[int, int, int, int]:
        return self.x, self.y, self.dx, self.dy


class Machine:
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._grid: Tuple[str, ...] = ()
        self.w = 0
        self.h = 0
        self._energized: Set[Tuple[int, int]] = set()
        self._traced_beams: Set[Tuple[int, int, int, int]] = set()
        self._load()

    def _load(self):
        with open(self._file_path) as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines]
        self._grid = tuple([l for l in lines if l])
        self.w = len(self._grid[0])
        self.h = len(self._grid)

    def calc_energized(self) -> int:
        return len(self._energized)

    def trace_and_calc(self, beam: Beam) -> int:
        self.trace_beam(beam)
        return self.calc_energized()

    def trace_beam(self, beam: Beam):
        self._energized.add((beam.x, beam.y))
        while True:
            beam.move_next()
            if not beam.is_in_grid(self.w, self.h):
                return
            self._energized.add((beam.x, beam.y))
            cell = self._grid[beam.y][beam.x]
            if cell == ".":
                continue
            if cell == "/" or cell == "\\":
                beam.mirror(cell)
                if self._was_traced(beam):
                    break
                continue
            if cell == "|":
                if beam.is_vertical:
                    continue
                beam.dx = 0
                beam.dy = 1
                copy = beam.make_copy()
                copy.dy = -1
                if not self._was_traced(copy):
                    self.trace_beam(copy)
                if self._was_traced(beam):
                    break
                continue
            if cell == "-":
                if not beam.is_vertical:
                    continue
                beam.dx = 1
                beam.dy = 0
                copy = beam.make_copy()
                copy.dx = -1
                if not self._was_traced(copy):
                    self.trace_beam(copy)
                if self._was_traced(beam):
                    break
                continue

    def _was_traced(self, beam: Beam) -> bool:
        beam_vector = beam.to_vector()
        if beam_vector not in self._traced_beams:
            self._traced_beams.add(beam_vector)
            return False
        return True

    def print_grid(self, print_energized: bool = False):
        for row, line in enumerate(self._grid):
            for col, c in enumerate(line):
                is_energized = (col, row) in self._energized and print_energized
                smb = "#" if is_energized else c
                print(smb, end="")
            print("")


def main():
    path = "/Users/andreisitaev/Downloads/input_d16.txt"
    m = Machine(path)

    max_total = 0
    for col in range(m.w):
        # top row
        total = m.trace_and_calc(Beam(col, 0, 0, 1))
        m = Machine(path)
        max_total = max(max_total, total)

        # bottom row
        total = m.trace_and_calc(Beam(col, m.h - 1, 0, -1))
        m = Machine(path)
        max_total = max(max_total, total)

    for row in range(m.h):
        # left column
        total = m.trace_and_calc(Beam(0, row, 1, 0))
        m = Machine(path)
        max_total = max(max_total, total)

        # right column
        total = m.trace_and_calc(Beam(m.w - 1, row, -1, 0))
        m = Machine(path)
        max_total = max(max_total, total)

    print(f"Energized cells count: {max_total}")
    #m.print_grid(print_energized=True)


if __name__ == "__main__":
    # 8183
    main()
