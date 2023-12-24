from typing import Tuple


class MirrorDetector:
    def __init__(self, lines: Tuple[str, ...]):
        self.lines = lines

    def detect(self) -> int:
        sym_col = self._find_symmetric_column(self.lines)
        lines = self._transpose(self.lines)

        print("Transposed: \n\n")
        print("\n".join(lines))

        sym_row = self._find_symmetric_column(lines)

        return sym_col + 100 * sym_row

    @classmethod
    def _transpose(cls, lines: Tuple[str, ...]) -> Tuple[str, ...]:
        return tuple(''.join(row) for row in zip(*lines))
        new_lines = [""] * len(lines[0])
        for c in range(len(lines[0])):
            for r in range(len(lines)):
                new_lines[c] += lines[r][c]
        #new_lines = [l[::-1] for l in new_lines]
        return tuple(new_lines)

    def _find_symmetric_column(self, lines: Tuple[str, ...]) -> int:
        columns = 0
        for i in range(1, len(lines[0])):
            if self._is_symmetric(i, lines):
                columns += i
                print(f"Column (row) {i} is symmetric")
        return columns

    def _is_symmetric(self, column: int, lines: Tuple[str, ...]) -> bool:
        for i in range(len(lines)):
            left = lines[i][:column]
            right = lines[i][column:]
            if len(right) < len(left):
                left = left[-len(right):]
                right = right[::-1]
            else:
                right = right[:len(left)]
                left = left[::-1]
            if left != right:
                return False
        return True


def test_sample():
    lines = """
#.#..#.#.
#...#####
.#..##..#
##..#.#.#
..##.###.
..##.###.
##..#.#.#
.#..##..#
##..#####
#.#..#.#.
.###.#.#.
###.#...#
..#.#.#..
...##.#..
...##.#..
    """.split("\n")
    lines = [l.strip() for l in lines]
    lines = tuple([l for l in lines if l])
    detector = MirrorDetector(lines)
    print(detector.detect())


def test_full():
    with open("/Users/andreisitaev/Downloads/input_d13.txt", "r") as file:
        lines = file.readlines()
    lines = [l.strip() for l in lines]
    matrix_lines = []
    total = 0
    for line in lines:
        if line:
            matrix_lines.append(line)
        else:
            detector = MirrorDetector(tuple(matrix_lines))
            detected = detector.detect()
            total += detected
            matrix_lines = []
    if matrix_lines:
        detector = MirrorDetector(tuple(matrix_lines))
        total += detector.detect()
        print(f"Total: {total}")


if __name__ == "__main__":
    #test_sample()  # Row 9 is symmetric  Column (row) 7 is symmetric
    # 29130
    test_full()

