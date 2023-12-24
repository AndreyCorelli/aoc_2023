from collections import deque
from typing import TypeAlias, Dict, List, Optional, Set, Deque

from src.file_path import read_lines

Signal: TypeAlias = bool
LOW, HIGH = False, True


class Module:
    def __init__(self, name: str):
        self.current_signal: Optional[Signal] = None
        self.name = name
        self.inputs: Dict[str, Signal] = {}
        self.new_inputs: Dict[str, Signal] = {}
        self.output_names: List[str] = []

    def process(self) -> Signal:
        self.inputs.update(self.new_inputs)
        signal = next(iter(self.inputs.values()), LOW)
        self.current_signal = signal
        return signal

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


class FlipFlop(Module):
    def __init__(self, name: str):
        super().__init__(name)
        self.state: Signal = LOW

    def process(self) -> Signal:
        had_pulse = False
        for key in self.new_inputs:
            if self.new_inputs[key] is HIGH:
                old_value = self.inputs.get(key, None)
                had_pulse = old_value is None or old_value is LOW
                if had_pulse:
                    break
        self.inputs = self.new_inputs

        if had_pulse:
            self.state = not self.state

        self.current_signal = self.state
        return self.state


class AndNot(Module):
    def __init__(self, name: str):
        super().__init__(name)

    def process(self) -> Signal:
        all_high, all_low = False, False
        if self.new_inputs:
            all_high, all_low = True, True
            for key in self.new_inputs:
                if not(self.new_inputs[key] is LOW and self.inputs.get(key, None) != HIGH):
                    all_high = False
                if not (self.new_inputs[key] is HIGH and self.inputs.get(key, None) != LOW):
                    all_low = False
        if all_low and all_high:
            all_high, all_low = False, False

        self.inputs = self.new_inputs
        output = not all_high
        self.current_signal = output
        return output


class Circuit:
    def __init__(self):
        self.modules: Dict[str, Module] = {}
        self.module_index: Dict[str, int] = {}
        self.input: Module = Module("input")
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
        self.input = self.modules["broadcaster"]
        self.input.inputs = {"": HIGH}

    def press_button(self):
        self.input.new_inputs[""] = LOW
        self.low_pulses += 1
        self.tick()

    def tick(self):
        print("tick")
        any_updated = False

        modules = list(self.modules.values())

        while True:
            for m in modules:
                prev_signal = m.current_signal
                output = m.process()

                # reset broadcaster
                if m.name == "broadcaster":
                    m.inputs = {"": HIGH}

                if output == LOW:
                    self.low_pulses += len(m.output_names)
                else:
                    self.high_pulses += len(m.output_names)
                print(f"{m.name} -> {'HIGH' if output else 'LOW'} -> {m.output_names}")
                output_modules = [self.modules[m] for m in m.output_names]
                if prev_signal != output:
                    any_updated = True

                for output_module in output_modules:
                    output_module.new_inputs[m.name] = output

            if modules[0].name == "broadcaster":
                modules = modules[1:]
            if not any_updated:
                break


def main():
    circuit = Circuit()
    circuit.load_from_file("input_d20_small_01.txt")
    # print(circuit.modules)

    circuit.press_button()
    product = circuit.low_pulses * circuit.high_pulses
    print(f"Circuit's pulses: LOW: {circuit.low_pulses}, HIGH: {circuit.high_pulses} ({product})")


if __name__ == "__main__":
    main()
