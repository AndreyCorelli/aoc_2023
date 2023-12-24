from typing import List


def get_hash(s: str) -> int:
    total = 0
    for c in s:
        # get ASCII code of c
        code = ord(c)
        total += code
        total *= 17
        total = total % 256
    return total


class Lense:
    def __init__(self, label: str, focal_length: int):
        self.label = label
        self.focal_length = focal_length

    def __str__(self) -> str:
        return f"{self.label} {self.focal_length}"

    def __repr__(self) -> str:
        return self.__str__()


class LensMassive:
    def __init__(self, path_to_file: str):
        self.path_to_file = path_to_file
        self.lenses = []
        self.boxes: List[List[Lense]] = [[] for _ in range(256)]
        self._load_lenses()

    def get_total_focus(self) -> int:
        total = 0
        for i, box in enumerate(self.boxes):
            for j, lense in enumerate(box):
                total += (i + 1) * (j + 1) * lense.focal_length

        print(f"Total focus: {total}")
        return total

    def _load_lenses(self):
        with open(self.path_to_file) as f:
            line = f.read().strip()

        total = 0
        current = ""
        for c in line:
            if c == ",":
                self._process_record(current)
                current = ""
            else:
                current += c
        self._process_record(current)

    def _process_record(self, record: str) -> None:
        """
        cm-    label ("cm") -> hash
        rb=9   9 - focal length
        """
        cmd, focal = "-", 0
        cmd_index = record.find("-")
        if cmd_index < 0:
            cmd = "="
            cmd_index = record.find("=")
            focal = int(record[cmd_index + 1:])
        label = record[:cmd_index]
        index = get_hash(label)

        if cmd == "-":
            box = self.boxes[index]
            for lense in box:
                if lense.label == label:
                    box.remove(lense)
                    break
        elif cmd == "=":
            box = self.boxes[index]
            found = False
            for lense in box:
                if lense.label == label:
                    lense.focal_length = focal
                    found = True
                    break
            if not found:
                box.append(Lense(label, focal))


def main():
    path = "/Users/andreisitaev/Downloads/input_d15.txt"  # 145
    lm = LensMassive(path)
    lm.get_total_focus()


if __name__ == "__main__":
    main()
