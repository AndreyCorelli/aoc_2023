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
    total = 0
    for left, right in rows:
        card_weight = 0
        for num in left:
            if num in right:
                card_weight = 1 if not card_weight else 2 * card_weight
        total += card_weight
    print(total)


if __name__ == "__main__":
    solve()