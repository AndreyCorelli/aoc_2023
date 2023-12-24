from decimal import Decimal
from typing import List, Dict, TypeAlias, Tuple, Optional

MAX_SCALAR = 4000


Range: TypeAlias = tuple[int, int]


class Toy:
    def __init__(self):
        self.ranges: Dict[str, Range] = {}

    @classmethod
    def get_default(cls) -> "Toy":
        toy = Toy()
        toy.ranges = {
            "x": (1, MAX_SCALAR),
            "m": (1, MAX_SCALAR),
            "a": (1, MAX_SCALAR),
            "s": (1, MAX_SCALAR)
        }
        return toy

    def __str__(self):
        return f"{self.ranges}"

    def __repr__(self):
        return self.__str__()

    def make_copy(self) -> "Toy":
        toy = Toy()
        toy.ranges = self.ranges.copy()
        return toy

    @property
    def is_empty(self) -> bool:
        for rng in self.ranges.values():
            if rng[0]:
                return False
        return True

    def get_total(self) -> int:
        total = 1
        for rng in self.ranges.values():
            if rng[0] == 0:
                return 0
            total *= rng[1] - rng[0] + 1
        return total


class Condition:
    def __init__(self, function_str: str, target: str):
        self.target: str = target
        self.share: Decimal = Decimal(0)
        # function_str is like "a<19"
        operators = {"<", ">"}

        if function_str:
            # index of operator in function_str
            operator_index = -1
            for i, c in enumerate(function_str):
                if c in operators:
                    operator_index = i
                    break
            self.operand_a = function_str[:operator_index]
            self.operand_b = int(function_str[operator_index + 1:])
            self.operator = function_str[operator_index]
        else:
            self.operand_a = ""
            self.operand_b = 0
            self.operator = None

    def __str__(self) -> str:
        return f"{self.operand_a}{self.operator}{self.operand_b} -> {self.target}"

    def __repr__(self):
        return self.__str__()

    def filter_toy(self, toy: Toy) -> Tuple[Toy, Optional[Toy], str]:
        # filtered part, remaining part, target
        t = toy.make_copy()
        if not self.operator:
            return t, None, self.target
        rng = t.ranges[self.operand_a]
        rem = (rng[0], rng[1])

        if self.operator == "<":
            rng = (rng[0], min(rng[1], self.operand_b - 1))
            rem = (max(rem[0], self.operand_b), rem[1])
        else:  # >
            rng = (max(rng[0], self.operand_b + 1), rng[1])
            rem = (rem[0], min(rem[1], self.operand_b))

        if rng[1] < rng[0]:
            rng = (0, 0)
        if rem[1] < rem[0]:
            rem = (0, 0)

        reminder = t.make_copy()
        reminder.ranges[self.operand_a] = rem
        t.ranges[self.operand_a] = rng
        return t, reminder, self.target


class Workflow:
    def __init__(self, name: str):
        self.name: str = name
        self.conditions: List[Condition] = []

    @classmethod
    def parse_str(cls, s: str) -> "Workflow":
        # str is like px{a<2006:qkq,m>2090:A,rfg}
        name, conditions_str = s.split("{")
        name = name.strip()
        wf = Workflow(name)

        conditions_str = conditions_str.strip("}")
        condition_parts = conditions_str.split(",")
        for condition_part in condition_parts:
            condition_part = condition_part.strip()
            if not condition_part:
                continue
            condition_subparts = condition_part.split(":")  # x<100;A
            function_str = condition_subparts[0] if len(condition_subparts) > 1 else ""
            condition_target = condition_subparts[-1]
            condition = Condition(function_str, condition_target)
            if condition:
                wf.conditions.append(condition)
        return wf

    def __str__(self) -> str:
        return f"{self.name} -> {self.conditions}"

    def __repr__(self):
        return self.__str__()


class Pipeline:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.workflows: Dict[str, Workflow] = {}
        self.init_wf: Workflow = Workflow("init")
        self._total_share_accepted = Decimal(0)
        self._load_file()

    def _load_file(self):
        with open(self.file_path) as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
        for line in lines:
            if not line.startswith("{"):
                wf = Workflow.parse_str(line)
                self.workflows[wf.name] = wf
        self.init_wf = self.workflows["in"]

    def solve(self) -> Decimal:
        self._solve_node(self.init_wf, Toy.get_default())
        share = self._total_share_accepted
        answer = share
        print(f"Answer: {answer}")
        return answer

    def _solve_node(self, node: Workflow, toy: Toy):
        # distribute share among nodes
        for condition in node.conditions:
            if not toy or toy.is_empty:
                break
            filtered, reminder, target = condition.filter_toy(toy)
            toy = reminder
            if target == "A":
                self._total_share_accepted += filtered.get_total()
                continue
            if target == "R":
                continue
            # if target in self.workflows:
            self._solve_node(self.workflows[condition.target], filtered)


def main():
    # 167409079868000 (right)
    # 167245503449662
    # 256000000000000 (max)
    pipeline = Pipeline("/Users/andreisitaev/Downloads/input_d19.txt")
    pipeline.solve()


if __name__ == "__main__":
    main()
