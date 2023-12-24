import math
from typing import List, Tuple, Any, TypeAlias

Cell: TypeAlias = Tuple[int, int]


class GalaxyObserver:
    def __init__(self, path_to_file: str) -> None:
        self.path_to_file = path_to_file
        self.w = 0
        self.h = 0
        self.map: Tuple[Tuple[int]] = ()
        self.row_weights: Tuple[int] = ()
        self.col_weights: Tuple[int] = ()
        self._init_map()

    def calc_total_distance(self) -> int:
        galaxies = self._get_galaxy_coords()

        total_distance = 0
        for i in range(len(galaxies)):
            for j in range(i + 1, len(galaxies)):
                dist = self._get_dist_between_galaxies(galaxies[i], galaxies[j])
                total_distance += dist
        print(f"Total distance: {total_distance}")
        return total_distance

    def _get_dist_between_galaxies(self, galaxy1: Cell, galaxy2: Cell) -> int:
        dist = 0
        start_x, end_x = min(galaxy1[0], galaxy2[0]), max(galaxy1[0], galaxy2[0])
        for x in range(start_x + 1, end_x):
            dist += self.col_weights[x]

        start_y, end_y = min(galaxy1[1], galaxy2[1]), max(galaxy1[1], galaxy2[1])
        for y in range(start_y + 1, end_y):
            dist += self.row_weights[y]

        return dist

    def _get_galaxy_coords(self) -> List[Cell]:  # (row, col)
        return [(y, x) for x in range(self.w) for y in range(self.h) if self.map[y][x] == 1]

    def __str__(self) -> str:
        return "\n".join(["".join([str(c) for c in row]) for row in self.map])

    def __repr__(self) -> str:
        return self.__str__()

    def _init_map(self):
        orig_map = self._read_file()
        self.map = tuple(tuple([1 if c == '#' else 0 for c in row]) for row in orig_map)
        self.w = len(self.map[0])
        self.h = len(self.map)

        # columns, where all symbols are ".":
        empty_columns = [i for i, col in enumerate(zip(*orig_map)) if all([c == "." for c in col])]
        # rows, where all symbols are ".":
        empty_rows = [i for i, row in enumerate(orig_map) if all([c == "." for c in row])]

        inflate_rate = 1000000
        col_weights = [inflate_rate if i in empty_columns else 1 for i in range(self.w)]
        row_weights = [inflate_rate if i in empty_rows else 1 for i in range(self.h)]

        self.col_weights = tuple(col_weights)
        self.row_weights = tuple(row_weights)

    def _read_file(self) -> List[List[str]]:
        with open(self.path_to_file, 'r') as file:
            lines = file.readlines()
        lines = [l.strip() for l in lines]
        lines = [list(l) for l in lines if l]
        return lines


if __name__ == "__main__":
    galaxy_observer = GalaxyObserver("/Users/andreisitaev/Downloads/input_d11.txt")
    # print(galaxy_observer)
    total_dist = galaxy_observer.calc_total_distance()
