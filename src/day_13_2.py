from typing import List, Optional, Set, Tuple


class MirrorDetector:
    def __init__(self, lines: List[str]):
        self.lines = lines
        self.smudges: Set[Tuple[int, int]] = set()

    def detect(self) -> int:
        blem_columns = self._find_symmetric_column(self.lines, True)
        lines = self._transpose(self.lines)
        blem_rows = self._find_symmetric_column(lines, True)

        total = sum(blem_columns) + 100 * sum(blem_rows)
        return total

    @classmethod
    def _transpose(cls, lines: List[str]) -> List[str]:
        return [''.join(row) for row in zip(*lines)]

    def _find_symmetric_column(self, lines: List[str], fix_smudges: bool) -> List[int]:
        columns = []
        for i in range(1, len(lines[0])):
            if self._is_symmetric(i, lines, fix_smudges):
                columns.append(i)
        return columns

    def _is_symmetric(self, column: int, lines: List[str], fix_smudges: bool) -> bool:
        blemishes = 0
        sm_col, sm_row = -1, -1 
        for i in range(len(lines)):
            left = lines[i][:column]
            right = lines[i][column:]

            left_trimmed = 0
            if len(right) > len(left):
                right = right[:len(left)]
            if len(left) > len(right):
                left_trimmed = len(left) - len(right)
                left = left[-len(right):] if right else ""

            right = right[::-1]
            if left != right:
                if not fix_smudges:
                    return False
                if blemishes > 0:
                    return False
                blemishes += 1
                # find a smudge
                sm_index = self._find_smudge(left, right)
                if sm_index is None:  # multiple smudges
                    return False
                sm_col = sm_index + left_trimmed
                sm_row = i

        # rows are symmetrical, but the smudge has to be fixed
        if fix_smudges and not blemishes:
            return False
        if sm_row >= 0 and sm_col >= 0:
            if (sm_row, sm_col) in self.smudges:
                return False
            orig_smb = lines[sm_row][sm_col]
            new_smb = "." if orig_smb == "#" else "#"
            lines[sm_row] = lines[sm_row][:sm_col] + new_smb + lines[sm_row][sm_col + 1:]
            print(f"Fixed smudge ({orig_smb}) at {sm_row}, {sm_col}")
            self.smudges.add((sm_row, sm_col))
        return True

    @classmethod
    def _find_smudge(cls, left: str, right: str) -> Optional[int]:
        index = -1
        for i in range(len(left)):
            if left[i] != right[i]:
                if index >= 0:
                    return None
                index = i
        return index


def test_sample():
    lines = """
##########.
###.##.####
..######...
.##....##..
##......###
###....####
..#.##.#..#
    """.split("\n")
    lines = [l.strip() for l in lines]
    lines = [l for l in lines if l]
    detector = MirrorDetector(lines)
    print(detector.detect())


def test_full():
    # 34443 <- too high, should be 33438
    with open("/Users/andreisitaev/Downloads/input_d13.txt", "r") as file:
        lines = file.readlines()
    lines = [l.strip() for l in lines]
    matrix_lines = []
    total = 0
    for line in lines:
        if line:
            matrix_lines.append(line)
        else:
            detector = MirrorDetector(matrix_lines)
            detected = detector.detect()

            total += detected
            matrix_lines = []
    if matrix_lines:
        detector = MirrorDetector(matrix_lines)
        total += detector.detect()
        print(f"Total: {total}")


if __name__ == "__main__":
    #test_sample()  # Row 9 is symmetric  Column (row) 7 is symmetric
    # 29130
    test_full()
