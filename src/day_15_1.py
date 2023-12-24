def get_hash(s: str) -> int:
    total = 0
    for c in s:
        # get ASCII code of c
        code = ord(c)
        total += code
        total *= 17
        total = total % 256
    return total


def get_hash_of_file(file_path: str) -> int:
    with open(file_path) as f:
        line = f.read().strip()

    total = 0
    current = ""
    for c in line:
        if c == ",":
            total += get_hash(current)
            current = ""
        else:
            current += c
    total += get_hash(current)

    print(f"Total hash: {total}")
    return total


def main():
    path = "/Users/andreisitaev/Downloads/input_d15.txt"  # 511257
    get_hash_of_file(path)


if __name__ == "__main__":
    main()
