from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class AlmanacRange:
    dest_start: int
    src_start: int
    length: int

    def src_to_dst(self, src: int) -> Optional[int]:
        if src < self.src_start:
            return None
        if src >= self.src_start + self.length:
            return None
        offset = src - self.src_start
        return self.dest_start + offset

@dataclass
class AlmanacMap:
    src_name: str
    dest_name: str
    ranges: List[AlmanacRange]

    def __str__(self) -> str:
        return f"{self.src_name}-to-{self.dest_name}"

    def __repr__(self) -> str:
        return self.__str__()

    def src_to_dst(self, src: int) -> Optional[int]:
        for rng in self.ranges:
            dst = rng.src_to_dst(src)
            if dst is not None:
                return dst
        return src


@dataclass
class Almanac:
    seeds: List[int]
    maps: Dict[str, AlmanacMap]
    maps_order = ["seed-to-soil", "soil-to-fertilizer", "fertilizer-to-water",
                  "water-to-light", "light-to-temperature", "temperature-to-humidity",
                  "humidity-to-location"]

    def find_min_location(self) -> int:
        ordered_maps = [self.maps[map_name] for map_name in self.maps_order]
        seeds_locations = [self.find_seed_location(s, ordered_maps)
                           for s in self.seeds]
        # seeds_locations.sort()
        return min(seeds_locations)

    def find_seed_location(self, seed: int, ordered_maps: List[AlmanacMap]) -> int:
        for map in ordered_maps:
            seed = map.src_to_dst(seed)
        return seed


def parse_almanac(file_path: str) -> Almanac:
    with open(file_path, 'r') as file:
        lines = file.readlines()

    seeds = []
    maps = {}
    current_map = None

    for line in lines:
        line = line.strip()
        if line.startswith('seeds:'):
            seeds = list(map(int, line.split(':')[1].split()))
        elif '-to-' in line:
            src_name, dest_name = line.split('-to-')
            dest_name = dest_name.replace(" map:", "")
            current_map = AlmanacMap(src_name, dest_name, [])
            maps[str(current_map)] = current_map
        elif line and current_map:
            dest_start, src_start, length = map(int, line.split())
            current_map.ranges.append(AlmanacRange(dest_start, src_start, length))

    return Almanac(seeds, maps)


def solve():
    file_path = '/Users/andreisitaev/Downloads/input_d5_1.txt'
    almanac = parse_almanac(file_path)
    print(almanac)
    loc = almanac.find_min_location()
    print(f"Min loc: {loc}")


if __name__ == '__main__':
    solve()
