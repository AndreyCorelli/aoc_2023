from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


class SeedSeq:
    start: int
    count: int
    mapped: bool

    def __init__(self, start: int, count: int, mapped: bool = False) -> None:
        self.start = start
        self.count = count
        self.mapped = mapped

    def __str__(self) -> str:
        mapped_str = "M" if self.mapped else " "
        return f"({self.start}, {self.count}) [{mapped_str}]"

    def __repr__(self) -> str:
        return self.__str__()

@dataclass
class AlmanacRange:
    dest_start: int
    src_start: int
    length: int

    def map_range_old(self, rn: SeedSeq) -> List[SeedSeq]:
        start, end = rn.start, rn.start + rn.count - 1
        own_end = self.src_start + self.length - 1
        if end < self.src_start:
            return [rn]
        if rn.start > own_end:
            return [rn]
        ranges = []
        if start < self.src_start:
            range_start = start
            start = self.src_start
            ranges.append(SeedSeq(start=range_start, count=self.src_start - range_start, mapped=False))

        range_end = min(end, own_end)
        if start <= range_end:
            ln = (range_end - start) + 1
            ranges.append(SeedSeq(start=self.dest_start, count=ln, mapped=True))
            start = range_end + 1

        if start <= end:
            ranges.append(SeedSeq(start=start, count=end - start + 1, mapped=False))
        return ranges

    def map_range(self, s: SeedSeq) -> List[SeedSeq]:
        mapped_sequences = []

        # Check for no intersection
        if s.start > self.src_start + self.length - 1 or (s.start + s.count - 1) < self.src_start:
            return [SeedSeq(s.start, s.count, False)]

        # Pre-intersection
        if s.start < self.src_start:
            pre_count = self.src_start - s.start
            mapped_sequences.append(SeedSeq(s.start, pre_count, False))

        # Intersection
        intersect_start = max(s.start, self.src_start)
        intersect_end = min(s.start + s.count - 1, self.src_start + self.length - 1)
        intersect_count = intersect_end - intersect_start + 1
        mapped_sequences.append(SeedSeq(self.dest_start + (intersect_start - self.src_start), intersect_count, True))

        # Post-intersection
        if s.start + s.count - 1 > self.src_start + self.length - 1:
            post_start = self.src_start + self.length
            post_count = (s.start + s.count) - post_start
            mapped_sequences.append(SeedSeq(post_start, post_count, False))

        return mapped_sequences

@dataclass
class AlmanacMap:
    src_name: str
    dest_name: str
    ranges: List[AlmanacRange]

    def __str__(self) -> str:
        return f"{self.src_name}-to-{self.dest_name}"

    def __repr__(self) -> str:
        return self.__str__()

    def map_range(self, rn: SeedSeq) -> List[SeedSeq]:
        ranges_to_map = [rn]
        ranges_ready = []
        for rng in self.ranges:
            updated_ranges_to_map = []
            for r in ranges_to_map:
                all_ranges = rng.map_range(r)
                ranges_ready += [r for r in all_ranges if r.mapped]
                updated_ranges_to_map += [r for r in all_ranges if not r.mapped]
            ranges_to_map = updated_ranges_to_map

        return ranges_ready + ranges_to_map


@dataclass
class Almanac:
    seeds: List[int]
    maps: Dict[str, AlmanacMap]
    maps_order = ["seed-to-soil", "soil-to-fertilizer", "fertilizer-to-water",
                  "water-to-light", "light-to-temperature", "temperature-to-humidity",
                  "humidity-to-location"]

    def find_min_location(self) -> int:
        ordered_maps = [self.maps[map_name] for map_name in self.maps_order]

        seed_ranges = []
        for i in range(len(self.seeds) >> 1):
            a, b = self.seeds[i * 2], self.seeds[i * 2 + 1]
            seed_ranges.append(SeedSeq(a, b))

        for map in ordered_maps:
            all_seed_ranges = []
            for rng in seed_ranges:
                new_ranges = map.map_range(rng)
                all_seed_ranges += new_ranges
            seed_ranges = all_seed_ranges
            for r in seed_ranges:
                r.mapped = False

        seed_locations = seed_ranges
        seed_locations.sort(key=lambda l: l.start)
        return seed_locations[0].start


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
    rn = AlmanacRange(src_start=98, dest_start=50, length=2)
    rn_2 = AlmanacRange(src_start=50, dest_start=52, length=48)
    m = AlmanacMap(src_name="a", dest_name="b", ranges=[rn, rn_2])

    # print(m.map_range(SeedSeq(79, 14)))
    # print(m.map_range(SeedSeq(55, 13)))
    # return

    file_path = '/Users/andreisitaev/Downloads/input_d5_1.txt'
    almanac = parse_almanac(file_path)
    print(almanac)
    loc = almanac.find_min_location()
    print(f"Min loc: {loc}")


if __name__ == '__main__':
    solve()
