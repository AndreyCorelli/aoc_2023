from typing import List, Tuple, Dict


class SudokuLine:
    def __init__(self, line: str) -> None:
        self.orig_line = line
        self.groups: Tuple[int,] = ()
        self.line: str = ""
        self.total_solutions: int = 0
        self.tried_solutions: Dict[str, int] = {}
        self._parse()

    def __str__(self):
        return self.orig_line

    def __repr__(self):
        return self.__str__()

    def _parse(self):
        # line looks like ".??..??...?##. 1,1,3"
        line, groups_str = self.orig_line.split(" ")
        # bloat 5 times
        line = "?".join([line] * 5)
        groups_str = ",".join([groups_str] * 5)
        self.line = line
        self.groups = tuple([int(c) for c in groups_str.split(",")])

    def solve(self) -> int:
        self._solve_group(str(self.line), 0, 0)
        return self.total_solutions

    def _hash_groups_placement(self, line: str, group_index: int) -> str:
        return f"{line}->" + ",".join([str(g) for g in self.groups[group_index:]])

    def _solve_group(self, line: str, group_index: int, solutions: int):
        # line looks like "??????#?.???.??? 4,3", groups like [1]
        hash_code = self._hash_groups_placement(line, group_index)
        if hash_code in self.tried_solutions:
            placements_count = self.tried_solutions[hash_code]
            self.total_solutions += placements_count
            return

        try:
            if group_index == len(self.groups):
                # if there are more occupied places, the current location is incorrect
                if "#" not in line:
                    self.total_solutions += 1
                return

            if len(line) == 0:
                # we ate up whole line, all groups are placed
                if group_index == len(self.groups):
                    self.total_solutions += 1
                return

            # current group is placed, try the next one
            group = self.groups[group_index]
            if len(line) < group:
                return

            if line[0] == ".":
                # skip the empty smb, continue solving
                self._solve_group(line[1:], group_index, self.total_solutions)

            if line[0] == "?":
                self._solve_group(line[1:], group_index, self.total_solutions)
            if group > len(line):
                # no way to place the group
                return

            remnant = line[:group]
            if "." in remnant:
                return
            if group < len(line):
                if line[group] == "#":
                    # need a space or the end of the line after the group
                    return
            self._solve_group(line[group + 1:], group_index + 1, self.total_solutions)
        finally:
            if line and group_index < len(self.groups):
                # here we should solve the group already
                self.tried_solutions[hash_code] = self.total_solutions - solutions
            return


class Sudoku:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.board: List[SudokuLine] = []
        self._read_file()

    def solve(self) -> int:
        return sum([line.solve() for line in self.board])

    def _read_file(self) -> None:
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
        lines = [l.strip() for l in lines]
        self.board = [SudokuLine(l) for l in lines if l]


if __name__ == "__main__":
    sudoku = Sudoku("/Users/andreisitaev/Downloads/input_d12.txt")
    total = sudoku.solve()
    print(f"Total: {total}")

