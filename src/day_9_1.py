from typing import List


def read_sequences(f_path: str) -> List[List[int]]:
    with open(f_path, 'r') as file:
        return [[int(i) for i in line.strip().split(' ')] for line in file.readlines() if line and line.strip()]


class SeqSolver:
    def __init__(self, seq: List[int]):
        self.seq = seq

    def solve(self) -> int:
        steps = [self.seq[0]]
        self._get_next_step(steps, self.seq)
        next_val = sum(steps)
        return next_val

    def _get_next_step(self, steps: List[int], seq: List[int]):
        while len(seq) > 1:
            difs = [seq[i - 1] - seq[i] for i in range(1, len(seq))]
            if not any([d for d in difs]):
                return
            steps.append(difs[0])
            seq = difs


if __name__ == "__main__":
    sqs = read_sequences("/Users/andreisitaev/Downloads/input_d9_1.txt")
    total_sum = 0
    for sq in sqs:
        solver = SeqSolver(sq)
        next_val = solver.solve()
        print(next_val)
        total_sum += next_val

    print(f"Total is: {total_sum}")
