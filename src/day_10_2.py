from typing import TypeAlias, Tuple, Dict, List, Set

Cell: TypeAlias = Tuple[bool, bool, bool, bool]  # l, u, r, d

"""
| is a vertical pipe connecting north and south.
- is a horizontal pipe connecting east and west.
L is a 90-degree bend connecting north and east.
J is a 90-degree bend connecting north and west.
7 is a 90-degree bend connecting south and west.
F is a 90-degree bend connecting south and east.
. is ground; there is no pipe in this tile.
S is the starting position of the animal; there is a pipe on this tile, but your sketch doesn't show what shape the pipe has.
"""


class Maze:
    SMB_TO_CELL: Dict[str, Cell] = {
        ".": (False, False, False, False),
        "|": (False, True, False, True),
        "-": (True, False, True, False),
        "L": (False, True, True, False),
        "J": (True, True, False, False),
        "7": (True, False, False, True),
        "F": (False, False, True, True),
        "S": (True, True, True, True),
    }

    # a better-looking version of the above
    NICE_SMB_TO_CELL: Dict[str, Cell] = {
        (False, False, False, False): ".",
        (False, True, False, True): "|",
        (True, False, True, False): "-",
        (False, True, True, False): "└",
        (True, True, False, False): "┘",
        (True, False, False, True): "┐",
        (False, False, True, True): "┌",
        (True, True, True, True): "┼"
    }

    DOUBLE_LINED_SMB_TO_CELL: Dict[str, Cell] = {
        (False, False, False, False): " ",
        (False, True, False, True): "║",
        (True, False, True, False): "═",
        (False, True, True, False): "╚",
        (True, True, False, False): "╝",
        (True, False, False, True): "╗",
        (False, False, True, True): "╔",
        (True, True, True, True): "╬"
    }

    VERT_BLOCKERS = {
        (False, True, False, True),  # "|"
        (False, True, True, False),  # "└"
        (True, True, False, False),  # "┘",
    }

    def __init__(self, file_path: str):
        self.start = (0, 0)
        self.file_path = ""
        self.orig_grid: Tuple[Tuple[Cell]] = ()
        self.grid: Tuple[Tuple[Cell]] = ()
        self.wave: List[List[int]] = []
        self.H = 0
        self.W = 0
        self.last_wave_front: List[Tuple[int, int]] = []
        self._parse_input(file_path)

    def calc_inner_dots(self):
        paths = self._find_paths()
        count_total, count_inside = 0, 0
        insider_points = []
        for i in range(self.H):
            for j in range(self.W):
                # if cell is occupied, skip it
                #if self.grid[i][j] != (False, False, False, False):
                #    continue
                if (i, j) in paths:
                    continue
                count_total += 1
                # is point (i, j) inside the path?
                # count all crossings from the point to the right
                # if there are odd number of crossings, the point is inside the path
                is_inside = self._is_inside(i, j, paths)
                if is_inside:
                    count_inside += 1
                    insider_points.append((i, j))

        # print the grid
        print("Printing...")
        self._print_nice_looking(paths, set(insider_points))
        print(f"Total: {count_total} spots, out of them {count_inside} are inside the path")

    def _is_inside(self, y: int, x: int, paths: Set[Tuple[int, int]]) -> bool:
        crossings = 0
        for j in range(x + 1, self.W):
            if self.grid[y][j] in self.VERT_BLOCKERS:
                if (y, j) in paths:
                    crossings += 1
        return crossings % 2 == 1

    def _find_paths(self) -> Set[Tuple[int, int]]:
        last_wave_front = self._spread_wave()
        all_paths: Set[Tuple[int, int]] = set()
        for start_point in last_wave_front:  # [[row, column], ... ]
            for direction in range(24):
                found_path = set(self._end_to_start(start_point, direction))
                all_paths = all_paths.union(found_path)
        return all_paths

    def _print_nice_looking(self, all_paths: Set[Tuple[int, int]], extra_paths: Set[Tuple[int, int]]) -> None:
        new_path = f"{self.file_path.replace('.txt', '_paths.txt')}"
        with open(new_path, 'w') as file:
            for i, row in enumerate(self.orig_grid):
                for j, cell in enumerate(row):
                    smb = self.NICE_SMB_TO_CELL[cell]
                    if (i, j) in all_paths:
                        smb = self.DOUBLE_LINED_SMB_TO_CELL[cell]
                    if i == self.start[0] and j == self.start[1]:
                        smb = 'S'
                    if (i, j) in extra_paths:
                        smb = '*'
                    file.write(smb)
                file.write('\n')

    def _end_to_start(self,
                      end_point: Tuple[int, int],
                      check_direction: int) -> List[Tuple[int, int]]:
        path = [end_point]
        wave = self.wave[end_point[0]][end_point[1]]

        def check_left(point: Tuple[int, int]) -> bool:
            if point[1] > 0 and self.wave[point[0]][point[1] - 1] == wave:
                point = (point[0], point[1] - 1)
                path.append(point)
                return True
            return False

        def check_up(point: Tuple[int, int]) -> bool:
            if point[0] > 0 and self.wave[point[0] - 1][point[1]] == wave:
                point = (point[0] - 1, point[1])
                path.append(point)
                return True
            return False

        def check_right(point: Tuple[int, int]) -> bool:
            if point[1] < self.W - 1 and self.wave[point[0]][point[1] + 1] == wave:
                point = (point[0], point[1] + 1)
                path.append(point)
                return True
            return False

        def check_down(point: Tuple[int, int]) -> bool:
            if point[0] < self.H - 1 and self.wave[point[0] + 1][point[1]] == wave:
                point = (point[0] + 1, point[1])
                path.append(point)
                return True
            return False

        # a list of all 16 combinations of 4 checks:
        checks = [
            [check_left, check_up, check_right, check_down],
            [check_left, check_up, check_down, check_right],
            [check_left, check_right, check_up, check_down],
            [check_left, check_right, check_down, check_up],
            [check_left, check_down, check_up, check_right],
            [check_left, check_down, check_right, check_up],
            [check_up, check_left, check_right, check_down],
            [check_up, check_left, check_down, check_right],
            [check_up, check_right, check_left, check_down],
            [check_up, check_right, check_down, check_left],
            [check_up, check_down, check_left, check_right],
            [check_up, check_down, check_right, check_left],
            [check_right, check_left, check_up, check_down],
            [check_right, check_left, check_down, check_up],
            [check_right, check_up, check_left, check_down],
            [check_right, check_up, check_down, check_left],
            [check_right, check_down, check_left, check_up],
            [check_right, check_down, check_up, check_left],
            [check_down, check_left, check_up, check_right],
            [check_down, check_left, check_right, check_up],
            [check_down, check_up, check_left, check_right],
            [check_down, check_up, check_right, check_left],
            [check_down, check_right, check_left, check_up],
            [check_down, check_right, check_up, check_left],
        ]

        check_functions = checks[check_direction]

        cur_point = end_point
        while wave > 0:
            wave -= 1
            found = False
            for check in check_functions:
                if check(cur_point):
                    found = True
                    cur_point = path[-1]
                    break
            if not found:
                break
        return path

    def _spread_wave(self) -> List[Tuple[int, int]]:
        # fill the wave grid step by step until we reach the end
        print("Spreading the wave...")
        wave = 0
        self.wave[self.start[0]][self.start[1]] = wave

        # get all cells, adjacent to the current wave
        last_front = [self.start]
        while True:
            very_last_front = self._spread_wave_front(wave)
            if not very_last_front:
                break
            last_front = very_last_front
            wave += 1
        print(f"Last front stopped at: {last_front}, front: {wave}")
        return last_front

    def _spread_wave_front(self, wave_front: int) -> List[Tuple[int, int]]:
        # return values: row, column
        last_front: List[Tuple[int, int]] = []
        for i in range(self.H):
            for j in range(self.W):
                if self.wave[i][j] != wave_front:
                    continue
                cell = self.grid[i][j]
                if cell[0] and j > 0 and self.wave[i][j - 1] < 0:  # is there a way l?
                    self.wave[i][j - 1] = wave_front + 1
                    last_front.append((i, j - 1))

                if cell[1] and i > 0 and self.wave[i - 1][j] < 0:  # is there a way u?
                    self.wave[i - 1][j] = wave_front + 1
                    last_front.append((i - 1, j))

                if cell[2] and j < self.W - 1 and self.wave[i][j + 1] < 0:  # is there a way r?
                    self.wave[i][j + 1] = wave_front + 1
                    last_front.append((i, j + 1))

                if cell[3] and i < self.H - 1 and self.wave[i + 1][j] < 0:  # is there a way d?
                    self.wave[i + 1][j] = wave_front + 1
                    last_front.append((i + 1, j))
        return last_front

    def _parse_input(self, file_path: str) -> None:
        self.file_path = file_path
        with open(file_path, 'r') as file:
            lines = file.readlines()
        lines = [l.strip() for l in lines]

        rows = []
        for line in [l for l in lines if l]:
            cells = [self.SMB_TO_CELL[c] for c in line]
            rows.append(tuple(cells))
            # if there's a start, save it
            if 'S' in line:
                self.start = (len(rows) - 1, line.index('S'))

        self.H = len(rows)
        self.W = len(rows[0])
        self.grid = tuple(rows)
        self.orig_grid = tuple(rows)
        self._fix_mutual_connections()
        self.wave = [[-1 for _c in r] for r in rows]

    def _fix_mutual_connections(self) -> None:
        new_rows = []
        for i, row in enumerate(self.grid):
            new_cells = []
            for j, cell in enumerate(row):
                if cell[0] and not (j > 0 and self.grid[i][j - 1][2]):
                    cell = (False, cell[1], cell[2], cell[3])
                if cell[1] and not (i > 0 and self.grid[i - 1][j][3]):
                    cell = (cell[0], False, cell[2], cell[3])
                if cell[2] and not (j < len(row) - 1 and self.grid[i][j + 1][0]):
                    cell = (cell[0], cell[1], False, cell[3])
                if cell[3] and not (i < len(self.grid) - 1 and self.grid[i + 1][j][1]):
                    cell = (cell[0], cell[1], cell[2], False)
                new_cells.append(cell)
            new_rows.append(tuple(new_cells))
        self.grid = tuple(new_rows)


if __name__ == "__main__":
    # Total: 2515 spots, out of them 1109 are inside the path  -> too high
    # Total: 2515 spots, out of them 217 are inside the path  -> too low
    # Total: 6198 spots, out of them 303 are inside the path  ?
    maze = Maze("/Users/andreisitaev/Downloads/input_d10.txt")
    # maze = Maze("/Users/andreisitaev/Downloads/input_d10_small_4.txt")
    maze.calc_inner_dots()
