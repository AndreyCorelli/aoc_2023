import os
from contextlib import contextmanager
from typing import Generator, List

BASE_PATH = "/Users/andreisitaev/sources/andrei/aoc_2023/data"


@contextmanager
def open_file(file_name: str) -> Generator:
    f = open(os.path.join(BASE_PATH, file_name))
    try:
        yield f
    finally:
        f.close()


def read_lines(file_name: str) -> List[str]:
    with open_file(os.path.join(BASE_PATH, file_name)) as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
    return lines
