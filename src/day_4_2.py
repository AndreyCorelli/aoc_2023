import re
from typing import List, Tuple, Set


def read_file_lines(file_path: str) -> List[Tuple[List[int], Set[int]]]:
    with open(file_path, "r") as file:
        lines = file.readlines()
    rows = []
    reg = re.compile(r"^Card\s+\d+:\s+")
    for line in lines:
        line = line.strip()
        line = reg.sub("", line)
        left_right = line.split("|")
        left = [int(s) for s in left_right[0].strip().split(" ") if s]
        right = set([int(s) for s in left_right[1].strip().split(" ") if s])
        rows.append((left, right))
    return rows


def solve():
    rows = read_file_lines("/Users/andreisitaev/Downloads/input_d4_1.txt")
    total = len(rows)
    multipliers = {}
    for i, left_right in enumerate(rows):
        left, right = left_right
        num_wins = 0
        for num in left:
            if num in right:
                num_wins += 1
        multiplier = multipliers.get(i, 1)
        for _ in range(multiplier):
            for j in range(num_wins):
                multipliers[i + j + 1] = multipliers.get(i + j + 1, 1) + 1
            total += num_wins
    print(total)


if __name__ == "__main__":
    solve()