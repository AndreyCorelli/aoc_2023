from collections import deque
from typing import TypeAlias, Dict, List, Optional, Set, Deque, Tuple

from src.file_path import read_lines

Signal: TypeAlias = int
LOW, ZERO, HIGH = -1, 0, 1


class Module:
    def __init__(self, name: str):
        self.current_signal: Signal = ZERO
        self.name = name
        self.input: Signal = ZERO
        self.output_names: List[str] = []

    def process(self) -> Signal:
        signal = self.input
        self.current_signal = signal
        return signal

    def set_input(self, signal: Signal, name: Optional[str] = None):
        self.input = signal

    @classmethod
    def parse_module(cls, line: str) -> "Module":
        """
        broadcaster -> a, b, c
        %a -> b
        &inv -> a
        """
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

        self.current_signal = output
        return self.state


class AndNot(Module):
    def __init__(self, name: str):
        super().__init__(name)
        self.inputs: Dict[str, Signal] = {}

    def set_input(self, signal: Signal, name: Optional[str] = None):
        self.inputs[name or ""] = signal

    def process(self) -> Signal:
        all_high = all([self.inputs.get(key, HIGH) == HIGH for key in self.inputs])
        new_state = LOW if all_high else HIGH
        return new_state


class Circuit:
    def __init__(self):
        self.modules: Dict[str, Module] = {}
        self.module_index: Dict[str, int] = {}
        self.modules_to_trigger: List[Module] = []
        self.low_pulses: int = 0
        self.high_pulses: int = 0

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

    def press_button(self):
        for m in self.modules_to_trigger:
            m.set_input(LOW)
        self.low_pulses += 1 + len(self.modules_to_trigger)
        self.tick()

    def tick(self):
        modules = self.modules_to_trigger
        iterations = 0
        while True:
            iterations += 1
            signals_to_pass: Dict[str, Tuple[Signal, str]] = {}
            next_modules: Set[Module] = set()

            for m in modules:
                prev_signal = m.current_signal
                output = m.process()
                if prev_signal == output:
                    continue
                next_modules.update([self.modules[n] for n in m.output_names])

                if output == LOW:
                    self.low_pulses += len(m.output_names)
                elif output == HIGH:
                    self.high_pulses += len(m.output_names)
                # m.print_signal(output)

                for output_name in m.output_names:
                    signals_to_pass.update({output_name: (output, m.name)})

            for output_module_name, (signal, name) in signals_to_pass.items():
                output_module = self.modules[output_module_name]
                output_module.set_input(signal, name)

            if not next_modules:
                break

            modules = list(next_modules)


def main():
    circuit = Circuit()
    # wrong high pulses
    circuit.load_from_file("input_d20.txt")

    for i in range(1000):
        circuit.press_button()
        print(f"Pressed {i+1} times")
    product = circuit.low_pulses * circuit.high_pulses
    print(f"Circuit's pulses: LOW: {circuit.low_pulses}, HIGH: {circuit.high_pulses} ({product})")


if __name__ == "__main__":
    main()
