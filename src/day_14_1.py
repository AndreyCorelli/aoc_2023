from typing import List


class ControlPanel:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.matrix: List[List[str]] = []
        self.w = 0
        self.h = 0
        self._read_from_file()

    def __str__(self):
        return "\n".join(["".join(l) for l in self.matrix])

    def __repr__(self):
        return self.__str__()

    def solve(self):
        self._tilt_north()
        w = self._calc_weight()
        print(f"Solution: {w}")

    def _tilt_north(self):
        for column in range(self.w):
            self._tilt_column_north(column)

    def _calc_weight(self) -> int:
        weight = self.h
        total = 0
        for row in range(self.h):
            # get number of O chars in row
            o_count = self.matrix[row].count("O")
            total += o_count * weight
            weight -= 1
        return total

    def _tilt_column_north(self, column: int):
        # find indicies of O chars in the column
        boulders = []
        for row in range(self.h):
            if self.matrix[row][column] == "O":
                boulders.append(row)
        # move boulders to the top, starting from the topmost, until
        # they hit another boulder, # or the top of the matrix
        for boulder in boulders:
            for place in range(boulder - 1, -1, -1):
                if self.matrix[place][column] in ["#", "O"]:
                    break
                self.matrix[place + 1][column] = "."
                self.matrix[place][column] = "O"

    def _read_from_file(self):
        with open(self.file_path) as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
        self.matrix = [list(l) for l in lines]
        self.h = len(self.matrix)
        self.w = len(self.matrix[0])


def sample_test():
    panel = ControlPanel("/Users/andreisitaev/Downloads/input_d14.txt")  # 105249
    # print(panel)
    # panel._tilt_north()
    # print("\nTilted:")
    # print(panel)
    panel.solve()


if __name__ == "__main__":
    sample_test()
