import math
from typing import List


class ControlPanel:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.matrix: List[List[str]] = []
        self.w = 0
        self.h = 0
        self._read_from_file()

        self.moves = [self._tilt_north, self._tilt_west, self._tilt_south, self._tilt_east]
        self._next_move = 0

    def __str__(self):
        return "\n".join(["".join(l) for l in self.matrix])

    def __repr__(self):
        return self.__str__()

    def solve(self) -> int:
        w = self._calc_weight()
        print(f"Solution: {w}")
        return w

    def move(self):
        self.moves[self._next_move]()
        self._next_move = (self._next_move + 1) % len(self.moves)

    def _tilt_north(self):
        for column in range(self.w):
            self._tilt_column(column, -1)

    def _tilt_south(self):
        for column in range(self.w):
            self._tilt_column(column, 1)

    def _tilt_west(self):
        for row in range(self.h):
            self._tilt_row(row, -1)

    def _tilt_east(self):
        for row in range(self.h):
            self._tilt_row(row, 1)

    def _calc_weight(self) -> int:
        weight = self.h
        total = 0
        for row in range(self.h):
            # get number of O chars in row
            o_count = self.matrix[row].count("O")
            total += o_count * weight
            weight -= 1
        return total

    def _tilt_column(self, column: int, direction: int):
        # direction: -1 = north, 1 = south
        # find indicies of O chars in the column
        boulders = []
        for row in range(self.h):
            if self.matrix[row][column] == "O":
                boulders.append(row)
        if direction == 1:
            boulders.reverse()
        # move boulders to the top, starting from the topmost, until
        # they hit another boulder, # or the top of the matrix
        for boulder in boulders:
            iterations = range(boulder - 1, -1, -1)
            if direction == 1:
                iterations = range(boulder + 1, self.h)

            for place in iterations:
                if self.matrix[place][column] in ["#", "O"]:
                    break
                self.matrix[place - direction][column] = "."
                self.matrix[place][column] = "O"

    def _tilt_row(self, row: int, direction: int):
        # direction: -1 = west, 1 = east
        # find indicies of O chars in the column
        boulders = []
        for column in range(self.w):
            if self.matrix[row][column] == "O":
                boulders.append(column)
        if direction == 1:
            boulders.reverse()
        # move boulders to the left (or right), starting from the left(right)most, until
        # they hit another boulder, or the left (right) of the matrix
        for boulder in boulders:
            iterations = range(boulder - 1, -1, -1)
            if direction == 1:
                iterations = range(boulder + 1, self.w)

            for place in iterations:
                if self.matrix[row][place] in ["#", "O"]:
                    break
                self.matrix[row][place - direction] = "."
                self.matrix[row][place] = "O"

    def _read_from_file(self):
        with open(self.file_path) as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
        self.matrix = [list(l) for l in lines]
        self.h = len(self.matrix)
        self.w = len(self.matrix[0])


def find_cycle_period(sequence):
    # NB: it takes some time for the sequence to stabilize
    # before getting periodic
    max_period = len(sequence) >> 2
    test_numb = len(sequence) >> 2
    seq = sequence
    if max_period+test_numb > len(sequence):
        return 1
    for i in range(1,len(seq)):
        for j in range(1,max_period):
            found =True
            for con in range(j+test_numb):
                if not (seq[-i-con]==seq[-i-j-con]):
                    found = False
            if found:
                minT=j
                return minT


def find_next_value(sequence: List[int], index: int) -> int:
    period = find_cycle_period(sequence)
    if period is None:
        return -1

    steps_back = math.ceil((index - len(sequence)) / period)
    index -= steps_back * period  # I'm not sure about -1

    return sequence[index]


def sample_test():
    panel = ControlPanel("/Users/andreisitaev/Downloads/input_d14.txt")  # 88680

    solutions = []
    for i in range(330):
        panel.move()
        panel.move()
        panel.move()
        panel.move()
        solutions.append(panel.solve())

    print(",".join([str(s) for s in solutions]))
    period = find_cycle_period(solutions)
    print(f"Period: {period}")
    index = 1000000000 - 1
    next_value = find_next_value(solutions, index)
    print(f"Predicted value: {next_value}")


def test_sequence():
    seq = [1, 2, 3, 4, 5, 6, 7, 8, 9] + [i + 10 for i in range(40)] * 100
    seq_short = seq[:330]
    period = find_cycle_period(seq_short)
    print(f"Test period: {period}")

    next_val = find_next_value(seq_short, 1000)
    real_val = seq[1000]
    print(f"Predicted value: {next_val}, real value: {real_val}")


if __name__ == "__main__":
    sample_test()
    #test_sequence()
