from typing import TypeAlias, Dict, List, Optional, Set, Tuple

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

        return output


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
    def __init__(self, verbose: bool = False):
        self.modules: Dict[str, Module] = {}
        self.module_index: Dict[str, int] = {}
        self.modules_to_trigger: List[Module] = []
        self.low_pulses: int = 0
        self.high_pulses: int = 0
        self.verbose = verbose

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
        self.low_pulses += 1
        self.tick()

    def tick(self):
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
                if output_name == "qn" and output == HIGH:
                    print(f"Found [{m.name}] -> {output_name} -> {output}")
                signals_to_pass.append((self.modules[output_name], output, m.name))


def test_one_run():
    circuit = Circuit(True)
    circuit.load_from_file("input_d20_small.txt")
    circuit.press_button()

    product = circuit.low_pulses * circuit.high_pulses
    print(f"Circuit's pulses: LOW: {circuit.low_pulses}, HIGH: {circuit.high_pulses} ({product})")


def main():
    circuit = Circuit()
    # 925955316
    circuit.load_from_file("input_d20.txt")

    for i in range(10000):
        circuit.press_button()
        #print(f"Pressed {i+1} times")
    product = circuit.low_pulses * circuit.high_pulses
    #print(f"Circuit's pulses: LOW: {circuit.low_pulses}, HIGH: {circuit.high_pulses} ({product})")


if __name__ == "__main__":
    # test_one_run()
    main()
