from typing import TypeAlias, Dict, List, Optional, Set

from src.file_path import read_lines

Signal: TypeAlias = bool
LOW, HIGH = False, True


class Module:
    def __init__(self, name: str):
        self.current_signal: Optional[Signal] = None
        self.name = name
        self.inputs: Dict[str, Signal] = {}
        self.output_names: List[str] = []

    def process(self) -> Signal:
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
        signal = any(self.inputs.values())
        if signal == LOW:
            self.state = not self.state
        self.current_signal = signal
        return self.state


class AndNot(Module):
    def __init__(self, name: str):
        super().__init__(name)

    def process(self) -> Signal:
        output = not all(self.inputs.values())
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
        self.input.inputs[""] = LOW
        self.low_pulses += 1
        self.tick([self.input])

    def tick(self, modules: List[Module]):
        print("tick")
        next_modules: Set[Module] = set()
        any_updated = False

        inputs_to_update = {}

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

            # update the inputs only right in before next tick!
            for next_module in output_modules:
                inputs_to_update[next_module.name] = (m.name, output)

            next_modules.update(output_modules)

        for module_name in inputs_to_update:
            module = self.modules[module_name]
            input_name, input_signal = inputs_to_update[module_name]
            module.inputs[input_name] = input_signal

        if not any_updated:
            return

        # to_process = list(next_modules)
        to_process = list(self.modules.values())
        # to_process = [m for m in self.modules.values() if m.name != "broadcaster"]
        to_process.sort(key=lambda m: self.module_index[m.name])
        self.tick(to_process)


def main():
    circuit = Circuit()
    circuit.load_from_file("input_d20_small_01.txt")
    # print(circuit.modules)

    circuit.press_button()
    product = circuit.low_pulses * circuit.high_pulses
    print(f"Circuit's pulses: LOW: {circuit.low_pulses}, HIGH: {circuit.high_pulses} ({product})")


if __name__ == "__main__":
    main()
