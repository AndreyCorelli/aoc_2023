import copy
from typing import List, TypeAlias

from src.file_path import read_lines

Point: TypeAlias = tuple[int, int]


class FieldMap:

    def __init__(self, verbose: bool = False):
        self.map: List[List[str]] = []
        self.waves: List[List[int]] = []
        self.w = 0
        self.h = 0
        self.start_point: Point = (0, 0)

    def load_from_file(self, file_name: str):
        lines = read_lines(file_name)
        for line in lines:
            self.map.append(list(line))
        self.w = len(self.map[0])
        self.h = len(self.map)

        for i in range(self.h):
            for j in range(self.w):
                if self.map[i][j] == "S":
                    self.start_point = (i, j)
                    self.map[i][j] = "."
                    break
        self.waves = [[-1 for _ in range(self.w)] for _ in range(self.h)]

    def print_map(self):
        templates = [f"\033[31mSMB\033[0m", f"\033[32mSMB\033[0m"]
        index = 0

        for row in range(self.h):
            for col in range(self.w):
                index = (index + 1) % 2
                template = templates[index]

                value = self.waves[row][col]
                smb = f"{value:2}"
                smb = template.replace("SMB", smb)
                if value < 0:
                    smb = self.map[row][col] * 2

                print(smb, end="")
            print("")

    def solve(self):
        self.waves[self.start_point[0]][self.start_point[1]] = 0
        for wave in range(0, 64):
            if not self._spread_wave(wave):
                break
        even_waves = sum([sum([1 for j in range(self.w)
                               if self.waves[i][j] >= 0 and self.waves[i][j] % 2 == 0]) for i in range(self.h)])
        print(f"Solution: {even_waves}")
        return even_waves

    def _spread_wave(self, wave: int) -> bool:
        are_updated = False

        new_wave: List[List[int]] = copy.deepcopy(self.waves)
        for r in range(self.h):
            for c in range(self.w):
                if self.waves[r][c] == wave:
                    has_added = self._spread_wave_to_neighbours(r, c, new_wave, wave + 1)
                    if has_added:
                        are_updated = True
        self.waves = new_wave
        return are_updated

    def _spread_wave_to_neighbours(self, r: int, c: int, new_wave: List[List[int]], wave: int) -> bool:
        updated = False
        if r > 0 and self.waves[r - 1][c] == -1 and self.map[r - 1][c] == ".":
            updated = True
            new_wave[r - 1][c] = wave
        if r < self.h - 1 and self.waves[r + 1][c] == -1 and self.map[r + 1][c] == ".":
            updated = True
            new_wave[r + 1][c] = wave
        if c > 0 and self.waves[r][c - 1] == -1 and self.map[r][c - 1] == ".":
            updated = True
            new_wave[r][c - 1] = wave
        if c < self.w - 1 and self.waves[r][c + 1] == -1 and self.map[r][c + 1] == ".":
            updated = True
            new_wave[r][c + 1] = wave
        return updated


def main():
    field_map = FieldMap()
    field_map.load_from_file("input_d21.txt")  # 3637
    field_map.solve()
    field_map.print_map()


if __name__ == "__main__":
    main()
"""
if the front is an odd number, then we could go back to any odd front...?
could we go back to an even front?
"""