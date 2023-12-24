import json
from typing import List, Dict


class Toy:
    def __init__(self, x: int, m: int, a: int, s: int):
        self.x: int = x
        self.m: int = m
        self.a: int = a
        self.s: int = s

    def __str__(self) -> str:
        return f"x:{self.x} m:{self.m} a:{self.a} s:{self.s}"

    def __repr__(self):
        return self.__str__()

    def total(self) -> int:
        return self.x + self.m + self.a + self.s

    @classmethod
    def parse_str(cls, s: str) -> "Toy":
        # s like {x=331,m=147,a=1060,s=2496}
        s = s.strip("{}")
        parts = s.split(",")
        parts = [p.strip() for p in parts]
        parts = [p.split("=") for p in parts]
        parts = {p[0]: int(p[1]) for p in parts}
        return Toy(parts["x"], parts["m"], parts["a"], parts["s"])


class Condition:
    def __init__(self, function_str: str, target: str):
        self.target: str = target
        # function_str is like "a<19"
        operators = {"<", ">", "="}

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

    def get_target_by_condition(self, toy: Toy) -> str:
        if not self.operator:
            return self.target
        if self.operator == "<":
            return self.target if getattr(toy, self.operand_a) < self.operand_b else None
        elif self.operator == ">":
            return self.target if getattr(toy, self.operand_a) > self.operand_b else None
        return self.target if getattr(toy, self.operand_a) == self.operand_b else None


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

    def process_toy(self, toy: Toy) -> str:
        for condition in self.conditions:
            target = condition.get_target_by_condition(toy)
            if target:
                return target
        return "R"  # shouldn't be reached

    def __str__(self) -> str:
        return f"{self.name} -> {self.conditions}"

    def __repr__(self):
        return self.__str__()


class Pipeline:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.workflows: Dict[str, Workflow] = {}
        self.init_wf: Workflow = Workflow("init")
        self.toys: List[Toy] = []
        self._total_accepted = 0
        self._load_file()

    def _load_file(self):
        with open(self.file_path) as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
        for line in lines:
            if line.startswith("{"):
                self.toys.append(Toy.parse_str(line))
            else:
                wf = Workflow.parse_str(line)
                self.workflows[wf.name] = wf
        self.init_wf = self.workflows["in"]

    def run(self) -> None:
        for toy in self.toys:
            self._process_toy(toy)
        print(f"Total accepted: {self._total_accepted}")

    def _process_toy(self, toy: Toy) -> None:
        wf = self.init_wf

        while True:
            action = wf.process_toy(toy)
            if action == "A":
                self._total_accepted += toy.total()
                return
            if action == "R":
                return
            wf = self.workflows[action]


def main():
    pipeline = Pipeline("/Users/andreisitaev/Downloads/input_d19.txt")
    pipeline.run()


if __name__ == "__main__":
    main()
