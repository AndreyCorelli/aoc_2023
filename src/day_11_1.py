import math
from typing import List, Tuple, Any, TypeAlias

Cell: TypeAlias = Tuple[int, int]


class GalaxyObserver:
    def __init__(self, path_to_file: str) -> None:
        self.path_to_file = path_to_file
        self.w = 0
        self.h = 0
        self.map: Tuple[Tuple[int]] = ()
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

    @classmethod
    def _get_dist_between_galaxies(cls, galaxy1: Cell, galaxy2: Cell) -> int:
        return abs(galaxy1[0] - galaxy2[0]) + abs(galaxy1[1] - galaxy2[1])

    def _get_galaxy_coords(self) -> List[Cell]:  # (row, col)
        return [(y, x) for x in range(self.w) for y in range(self.h) if self.map[y][x] == 1]

    def __str__(self) -> str:
        return "\n".join(["".join([str(c) for c in row]) for row in self.map])

    def __repr__(self) -> str:
        return self.__str__()

    def _init_map(self):
        orig_map = self._read_file()
        # columns, where all symbols are ".":
        empty_columns = [i for i, col in enumerate(zip(*orig_map)) if all([c == "." for c in col])]
        # rows, where all symbols are ".":
        empty_rows = [i for i, row in enumerate(orig_map) if all([c == "." for c in row])]

        # wrong
        # duplicate empty columns:
        for row in orig_map:
            self._inflate_list(row, empty_columns, ".")
        # duplicate empty rows:
        self._inflate_list(orig_map, empty_rows, ["."] * len(orig_map[0]))

        self.map = tuple(tuple([1 if c == '#' else 0 for c in row]) for row in orig_map)
        self.w = len(self.map[0])
        self.h = len(self.map)

    def _read_file(self) -> List[List[str]]:
        with open(self.path_to_file, 'r') as file:
            lines = file.readlines()
        lines = [l.strip() for l in lines]
        lines = [list(l) for l in lines if l]
        return lines

    @classmethod
    def _inflate_list(cls, lst: List[Any], indices: List[int], val: Any) -> List[Any]:
        accumulator = 0
        for i in indices:
            lst.insert(i + accumulator, val)
            accumulator += 1
            lst.insert(i + accumulator, val)
            accumulator += 1
        return lst


if __name__ == "__main__":
    galaxy_observer = GalaxyObserver("/Users/andreisitaev/Downloads/input_d11.txt")
    # +1 -> 374
    # +2 -> 456
    # +3 -> 538
    # +10 -> 1030 = (82 * 8) + 374

    # +1 -> 9445168
    # +2 -> 10187466
    # +1000000 = (10187466 - 9445168) * (1000000 - 2) + 9445168 = 742305960572
    # print(galaxy_observer)
    total_dist = galaxy_observer.calc_total_distance()
