import copy
import math
from typing import List, TypeAlias

from src.day_14_2 import find_cycle_period
from src.file_path import read_lines

Point: TypeAlias = tuple[int, int]


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
        scale = 13
        for r in range(self.h):
            self.map[r] = scale * self.map[r]

        self.map = scale * self.map
        self.start_point = (self.start_point[0] + self.h, self.start_point[1] + self.h)
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
    i = 65 + 131 * 6
    solution = field_map.solve(i)
    field_map.cleanup()
    sequence.append(solution)
    print(f"{i:3}: {solution}")

    #field_map.print_map()
    print(sequence)


def find_period():
    sequence = [4, 8, 15, 24, 31, 41, 55, 71, 85, 102, 118, 142, 164, 193, 212, 247, 267, 305, 327, 371, 401, 446, 470, 524, 553, 615, 645, 707, 732, 806, 841, 917, 952, 1036, 1073, 1155, 1201, 1272, 1329, 1403, 1459, 1538, 1600, 1687, 1749, 1842, 1915, 2013, 2083, 2185, 2251, 2350, 2411, 2525, 2595, 2718, 2784, 2914, 2974, 3123, 3183, 3371, 3438, 3637, 3699, 3901, 3967, 4173, 4199, 4398, 4431, 4648, 4689, 4916, 4948, 5187, 5213, 5452, 5477, 5718, 5759, 5999, 6045, 6274, 6338, 6566, 6633, 6867, 6953, 7170, 7261, 7472, 7566, 7784, 7883, 8110, 8226, 8449, 8571, 8792, 8917, 9142, 9266, 9503, 9623, 9858, 9984, 10232, 10340, 10606, 10724, 10983, 11104, 11364, 11501, 11757, 11899, 12166, 12316, 12573, 12735, 12993, 13154, 13387, 13574, 13801, 14006, 14233, 14448, 14666, 14878]
    odd = [x for i, x in enumerate(sequence) if i % 2 == 0]
    print("Sequence (odd):")
    print(odd)

    print(f"S[65]={sequence[64]}, S[131]={sequence[130]}")
    # 65: 3699, 195: 32947, 326: 77020, 457: 121984

    src = sequence
    print("Diffs:")
    for _ in range(4):
        diffs = [src[i + 1] - src[i] for i in range(len(src) - 1)]
        print(diffs)
        src = diffs


def find_coeffs(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    b = math.log(y1 / y2) / math.log(x1 / x2)
    a = y1 / x1 ** b
    print(f"y = {a} * x^{b}")

    steps = 202300
    y_predicted = steps ** b * a
    print(f"Predicted: {y_predicted}")


if __name__ == "__main__":
    main()
    #find_period()
    #find_coeffs((2, 77208), (5, 232442))


"""
odd steps make a parabolic chart: y = a * x**b
y = 3.0948674082020795 * x^2.023905705158651 - good estimation, but answer (804230805093769) was too high
   

y = 0.9232922661346812 * x^1.9872682389164873
    0.9232922661346812*26501365**1.9872682389164873 = 521632218026886.3
approx: y=3*x**2+1810 (526741799901277 - too low)

x - number of even steps (26501365/2 + 1 = 13250683)
x = 526741799901277 <- too low
    804230805093770 <- too high
    80865221361 <- WTF?


when the full square's filled, it's 7282 for odd, 7406 for even
130 steps to fill the full square
26501365 - ?

26501365 - 203856 * 130 + 85

"""