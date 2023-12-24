from typing import TypeAlias, Tuple, Dict, List

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
        (False, False, False, False): " ",
        (False, True, False, True): "|",
        (True, False, True, False): "-",
        (False, True, True, False): "└",
        (True, True, False, False): "┌",
        (True, False, False, True): "┐",
        (False, False, True, True): "┘",
        (True, True, True, True): "┼"
    }

    def __init__(self, file_path: str):
        self.start = (0, 0)
        self.orig_grid: Tuple[Tuple[Cell]] = ()
        self.grid: Tuple[Tuple[Cell]] = ()
        self.wave: List[List[int]] = []
        self.last_wave_front: List[Tuple[int, int]] = []
        self._parse_input(file_path)

    def spread_wave(self) -> None:
        # fill the wave grid step by step until we reach the end
        wave = 0
        self.wave[self.start[1]][self.start[0]] = wave

        # get all cells, adjacent to the current wave
        last_front = [self.start]
        while True:
            very_last_front = self._spread_wave(wave)
            if not very_last_front:
                break
            last_front = very_last_front
            wave += 1
        print(f"Last front stopped at: {last_front}, front: {wave}")

    def save_nice_looking_version(self, file_path: str) -> None:
        with open(file_path, 'w') as file:
            for i, row in enumerate(self.orig_grid):
                for j, cell in enumerate(row):
                    smb = self.NICE_SMB_TO_CELL[cell]
                    if i == self.start[1] and j == self.start[0]:
                        smb = 'S'
                    file.write(smb)
                file.write('\n')

    def _spread_wave(self, wave_front: int) -> List[Tuple[int, int]]:
        last_front: List[Tuple[int, int]] = []
        for i in range(len(self.wave)):
            for j in range(len(self.wave[i])):
                if self.wave[i][j] != wave_front:
                    continue
                cell = self.grid[i][j]
                if cell[0] and j > 0 and self.wave[i][j - 1] < 0:  # is there a way l?
                    self.wave[i][j - 1] = wave_front + 1
                    last_front.append((j - 1, i))

                if cell[1] and i > 0 and self.wave[i - 1][j] < 0:  # is there a way u?
                    self.wave[i - 1][j] = wave_front + 1
                    last_front.append((j, i - 1))

                if cell[2] and j < len(self.grid[i]) - 1 and self.wave[i][j + 1] < 0:  # is there a way r?
                    self.wave[i][j + 1] = wave_front + 1
                    last_front.append((j + 1, i))

                if cell[3] and i < len(self.grid) - 1 and self.wave[i + 1][j] < 0:  # is there a way d?
                    self.wave[i + 1][j] = wave_front + 1
                    last_front.append((j, i + 1))
        return last_front

    def _parse_input(self, file_path: str) -> None:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        lines = [l.strip() for l in lines]

        rows = []
        for line in [l for l in lines if l]:
            cells = [self.SMB_TO_CELL[c] for c in line]
            rows.append(tuple(cells))
            # if there's a start, save it
            if 'S' in line:
                self.start = (line.index('S'), len(rows) - 1)

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

    # def _fix_start_point(self, rows: List[Tuple[Cell]]) -> None:
    #     fixed_cell = [False, False, False, False]
    #     if self.start[0] > 0:  # check to the left
    #         if rows[self.start[1]][self.start[0] - 1][2]:
    #             fixed_cell[0] = True
    #     if self.start[1] > 0:  # check to the top
    #         if rows[self.start[1] - 1][self.start[0]][3]:
    #             fixed_cell[1] = True
    #     if self.start[0] < len(rows[0]) - 1:  # check to the right
    #         if rows[self.start[1]][self.start[0] + 1][0]:
    #             fixed_cell[2] = True
    #     if self.start[1] < len(rows) - 1:  # check to the bottom
    #         if rows[self.start[1] + 1][self.start[0]][1]:
    #             fixed_cell[3] = True
    #     rows[self.start[0]] = [c if i != self.start[1] else tuple(fixed_cell) for i, c in enumerate(rows[self.start[0]])]


if __name__ == "__main__":
    maze = Maze("/Users/andreisitaev/Downloads/input_d10.txt")  # [(43, 122)], front: 6690 is Wrong
    maze.save_nice_looking_version("/Users/andreisitaev/Downloads/input_d10_2_nice.txt")
    #maze.spread_wave()
