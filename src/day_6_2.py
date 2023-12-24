from math import sqrt, floor, ceil
from typing import List, Tuple, Optional


class Race:
    def __init__(self, time, distance):
        self.time = time
        self.distance = distance

    def get_win_nums(self) -> int:
        roots = self.get_roots()
        if roots is None:
            return 0
        count = roots[1] - roots[0] + 1
        return count

    def get_roots(self) -> Optional[Tuple[int, int]]:
        # a*(t - a) - d > 0
        # a^2 - at + d > 0
        d2 = self.time**2 - self.distance * 4
        if d2 < 0:
            return None
        d = sqrt(d2) / 2
        r1 = floor(self.time / 2 - d) + 1
        r2 = ceil(self.time / 2 + d) - 1
        return max(r1, 1), max(r2, 1)

    def get_max_distance(self) -> int:
        v = self.time << 1
        d = v * (self.time - v)
        return d

    @staticmethod
    def parse_file(file_path):
        races = []
        with open(file_path, 'r') as file:
            # Assuming the first line is time and the second line is distance
            time_line = "".join(file.readline().strip().split()[1:])
            distance_line = "".join(file.readline().strip().split()[1:])

            # Extracting numbers from the lines
            times = [int(time_line)]
            distances = [int(distance_line)]

            # Pairing times and distances
            for t, d in zip(times, distances):
                races.append(Race(t, d))

        return races


def solve():
    file_path = '/Users/andreisitaev/Downloads/input_d6_1.txt'
    races = Race.parse_file(file_path)
    total = 1
    for race in races:
        print(f"Time: {race.time}, Distance: {race.distance}, Wins: {race.get_win_nums()}")
        w = race.get_win_nums()
        if w == 0:
            print(f"Race {race}: impossible to win")
            w = 1
        total *= w

    print(f"Total wins mult: {total}")


if __name__ == '__main__':
    solve()
