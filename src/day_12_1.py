from typing import List, Tuple, Optional


class SudokuLine:
    def __init__(self, line: str) -> None:
        self.orig_line = line
        self.groups: Tuple[int,] = ()
        self.line: str = ""
        self.total_solutions: int = 0
        self._parse()

    def __str__(self):
        return self.orig_line

    def __repr__(self):
        return self.__str__()

    def _parse(self):
        # line looks like ".??..??...?##. 1,1,3"
        line, groups_str = self.orig_line.split(" ")
        self.line = line
        self.groups = tuple([int(c) for c in groups_str.split(",")])

    def solve(self) -> int:
        self._solve_group(str(self.line), 0)
        return self.total_solutions

    def _solve_group(self, line: str, group_index: int):
        # line looks like "??????#?.???.??? 4,3"
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
            self._solve_group(line[1:], group_index)

        if line[0] == "?":
            self._solve_group(line[1:], group_index)
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
        self._solve_group(line[group + 1:], group_index + 1)
        #
        #
        # # fit the group into the spot
        # while len(line) >= group:
        #     if line[0] == ".":
        #         line = line[1:]
        #         continue
        #
        #     group_spot = line[:group]
        #     if "." in group_spot:
        #         line = line[1:]
        #         continue
        #
        #     # after the "group" # characters, there should be a "." or "?"
        #     # if it's "?", we'll replace "?" with "."
        #     next_smb = line[group] if group < len(line) else None
        #     if next_smb == "#":
        #         line = line[1:]
        #         continue
        #
        #     if group_index == len(self.groups) - 1:
        #         self.total_solutions += 1
        #         line = line[group:]
        #     else:
        #         self._solve_group(line[group + 1:], group_index + 1)
        #         line = line[1:]

    @classmethod
    def _find_spot(cls, s: str, start_index: int) -> Optional[Tuple[int, int]]:
        # find first position of either # or ? in s
        a, b = s.find("#", start_index), s.find("?", start_index)
        if a == -1 and b == -1:
            return None
        first_index = a if b < 0 else (b if a < 0 else min(a, b))
        if first_index == -1:
            return None
        group_length = 1
        while first_index + group_length < len(s) and s[first_index + group_length] in {"?", "#"}:
            group_length += 1

        return first_index, group_length


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
    #l = SudokuLine("??????#?.???.??? 4,3")  # Calc: 4, while true is 5
    #print(l.solve())

    # 7674
    sudoku = Sudoku("/Users/andreisitaev/Downloads/input_d12.txt")
    #print(sudoku.board[-1].solve())  # OK
    #print(sudoku.board[1].solve())  # OK
    #print(sudoku.board[2].solve())  # 0?
    total = sudoku.solve()
    print(f"Total: {total}")

"""
Full set: 6800 <- too low (expected 7674)
"""
"""
???.### 1,1,3: 1 - OK
.??..??...?##. 1,1,3: 4 - OK
?#?#?#?#?#?#?#? 1,3,1,6: 1  - OK
????.#...#... 4,1,1: 1 - OK
????.######..#####. 1,6,5: 4 - OK
?###???????? 3,2,1: 10 - OK
"""
