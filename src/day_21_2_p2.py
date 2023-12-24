import copy
import numpy as np
from typing import List, TypeAlias

from src.day_14_2 import find_cycle_period
from src.file_path import read_lines

Point: TypeAlias = tuple[int, int]


STEPS_TOTAL = 26501365


class FieldMap:

    def __init__(self):
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

    def spread_map(self):
        scale = 7
        for r in range(self.h):
            self.map[r] = scale * self.map[r]

        self.map = scale * self.map
        start_shift = round((scale - 1) / 2)

        self.start_point = (
            self.start_point[0] + self.h * start_shift,
            self.start_point[1] + self.w * start_shift
        )
        self.h *= scale
        self.w *= scale

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

    def solve(self, steps: int):
        self.waves[self.start_point[0]][self.start_point[1]] = 0
        for wave in range(0, steps):
            if not self._spread_wave(wave):
                break

        is_even = steps % 2 == 0
        if is_even:
            condition = lambda x: x >= 0 and x % 2 == 0
        else:
            condition = lambda x: x >= 0 and (x % 2 == 1)

        even_waves = sum([sum([1 for j in range(self.w)
                               if condition(self.waves[i][j])]) for i in range(self.h)])
        return even_waves

    def cleanup(self):
        self.waves = [[-1 for _ in range(self.w)] for _ in range(self.h)]

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
    field_map.load_from_file("input_d21.txt")  # 131x131, 3637
    field_map.spread_map()

    sequence = []
    #for i in range(1, 65 + 131 + 1):
    i = 65 + 131 * 2
    solution = field_map.solve(i)
    field_map.cleanup()
    sequence.append(solution)
    print(f"{i:3}: {solution}")

    #field_map.print_map()
    print(sequence)


def find_coeffs(points: List[Point], x_n: int) -> float:
    x_coords, y_coords = zip(*points)

    # Degree of the polynomial
    degree = len(points) - 1

    # Find polynomial coefficients
    coeffs = np.polyfit(x_coords, y_coords, degree)

    # Evaluate the polynomial at x_n
    y_n = np.polyval(coeffs, x_n)

    print(f"Predicted: {y_n}")

    return y_n


if __name__ == "__main__":
    #main()

    points = [
        (i, p) for i, p in enumerate([3699, 33137, 91951])  #, 122236])  #, 173636, 232442, 298530])
    ]

    map_steps = round((STEPS_TOTAL - 65) / 131)
    find_coeffs(points, map_steps)


"""
odd steps make a parabolic chart: y = a * x**b
y = 3.0948674082020795 * x^2.023905705158651 - good estimation, but answer (804230805093769) was too high
   

y = 0.9232922661346812 * x^1.9872682389164873
    0.9232922661346812*26501365**1.9872682389164873 = 521632218026886.3
approx: y=3*x**2+1810 (526741799901277 - too low)

x - number of even steps (26501365/2 + 1 = 13250683)
x = 526741799901277 <- too low
    804230805093770 <- too high
    601113643448699 Gosh!!!!
    


when the full square's filled, it's 7282 for odd, 7406 for even
130 steps to fill the full square
26501365 - ?

26501365 - 203856 * 130 + 85

"""