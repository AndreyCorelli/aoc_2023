from typing import TypeAlias, Dict, List, Optional, Tuple

from src.day_14_2 import find_cycle_period
from src.file_path import read_lines

Signal: TypeAlias = int
LOW, ZERO, HIGH = -1, 0, 1


class Module:
    def __init__(self, name: str):
        self.name = name
        self.input: Signal = ZERO
        self.output_names: List[str] = []

    def process(self) -> Signal:
        signal = self.input
        return signal

    def set_input(self, signal: Signal, name: Optional[str] = None):
        self.input = signal

    @classmethod
    def parse_module(cls, line: str) -> "Module":
        input_output = [p.strip() for p in line.split("->")]
        name = input_output[0]
        module_type = ""
        if name[0] in "%&":
            module_type = name[0]
            name = name[1:]
        outputs = [o.strip() for o in input_output[1].split(",")]

        module_class = Module
        if module_type == "%":
            module_class = FlipFlop
        elif module_type == "&":
            module_class = AndNot
        module = module_class(name)
        module.output_names = outputs
        return module

    def __str__(self):
        type_name = type(self).__name__
        return f"{type_name} {self.name} -> {self.output_names}"

    def __repr__(self):
        return str(self)

    def print_signal(self, signal: int):
        print(f"{self.name} -> {'HIGH' if signal == HIGH else 'LOW' if signal == LOW else 'ZERO'} "
              f"-> {self.output_names}")


class FlipFlop(Module):
    def __init__(self, name: str):
        super().__init__(name)
        self.state: Signal = LOW

    def process(self) -> Signal:
        output = ZERO
        had_pulse = self.input == LOW

        if had_pulse:
            self.state = LOW if self.state == HIGH else HIGH
            output = self.state

        return output


class AndNot(Module):
    def __init__(self, name: str):
        super().__init__(name)
        self.inputs: Dict[str, Signal] = {}
        self.last_output = ZERO

    def set_input(self, signal: Signal, name: Optional[str] = None):
        self.inputs[name or ""] = signal

    def process(self) -> Signal:
        all_high = all([self.inputs.get(key, HIGH) == HIGH for key in self.inputs])
        new_state = LOW if all_high else HIGH
        self.last_output = new_state
        return new_state


class Circuit:
    def __init__(self, verbose: bool = False):
        self.modules: Dict[str, Module] = {}
        self.module_index: Dict[str, int] = {}
        self.modules_to_trigger: List[Module] = []
        self.low_pulses: int = 0
        self.high_pulses: int = 0
        self.verbose = verbose

        self.memory_dump: Dict[str, List[Signal]] = {}
        self.module_period: Dict[str, int] = {}
        self.ticks = 0

    def load_from_file(self, file_name: str):
        lines = read_lines(file_name)
        index = 0
        for line in lines:
            module = Module.parse_module(line)
            self.modules[module.name] = module
            self.module_index[module.name] = index
            index += 1

        # some modules might not be defined, however, they might be used as outputs
        modules = list(self.modules.values())
        for module in modules:
            for output_name in module.output_names:
                if output_name not in self.modules:
                    self.modules[output_name] = Module(output_name)
                    self.module_index[module.name] = index
                    index += 1

        input_module = self.modules["broadcaster"]
        self.modules_to_trigger = [
            self.modules[m] for m in input_module.output_names
        ]
        del self.modules["broadcaster"]

        # set all inputs to LOW
        for m in modules:
            for output_name in m.output_names:
                self.modules[output_name].set_input(LOW, m.name)

        self.memory_dump = {m.name: [] for m in self.modules.values() if m.__class__ == FlipFlop}

    def press_button(self):
        for m in self.modules_to_trigger:
            m.set_input(LOW)
        self.low_pulses += 1
        self.tick()

    def find_cycles(self):
        for module, sequence in self.memory_dump.items():
            self.module_period[module] = find_cycle_period(sequence)
        print("Periods: " + ", ".join([f"[{k}]: {v}" for k, v in self.module_period.items()]))

    def tick(self):
        self.ticks += 1
        modules = self.modules_to_trigger
        signals_to_pass: List[Tuple[Module, Signal, str]] = [
            (m, LOW, "") for m in modules
        ]

        while signals_to_pass:
            m, signal, input_name = signals_to_pass[0]
            m.set_input(signal, input_name)
            signals_to_pass = signals_to_pass[1:]

            if signal == LOW:
                self.low_pulses += 1
            elif signal == HIGH:
                self.high_pulses += 1

            output = m.process()
            if output == ZERO:
                continue

            if m.output_names and self.verbose:
                m.print_signal(output)

            for output_name in m.output_names:
                signals_to_pass.append((self.modules[output_name], output, m.name))

            # dump inputs for the final (pre-final &)
            line = "".join(["H" if o == HIGH else "." for o in
                           [self.modules[m].last_output for m in ["qz", "cq", "jx", "tt"]]])
            if line != "....":
                print(f"Found:  {line}, ticks: {self.ticks}")
                self.ticks = 0

        self._dump_memory()

    def _dump_memory(self):
        for m in self.modules.values():
            if m.__class__ == FlipFlop:
                self.memory_dump[m.name].append(m.state)


def main():
    circuit = Circuit()

    circuit.load_from_file("input_d20.txt")

    """
    What's changed on every button press? Flip-flops' memory.
    - is there a pattern (loop) in each flip-flop's memory's changes with button presses?
    - yes!
    """

    # (&qz, &cq, &jx, &tt) -> qn
    # (1, 1, 1, 1)&qn -> rx
    # for m in circuit.modules.values():
    #     print(m)
    # return

    for i in range(20000):
        circuit.press_button()
        # print(f"Pressed {i+1} times")

    #print("Finding cycles...")
    #circuit.find_cycles()


if __name__ == "__main__":
    main()
