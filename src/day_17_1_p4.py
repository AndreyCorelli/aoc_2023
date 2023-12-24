import copy
import random
from typing import List, TypeAlias, Set, Optional, Dict, Tuple

Point: TypeAlias = tuple[int, int]

MAX_PATH_LEN = 3

# left, top, right, bottom
DIRECTIONS = [(-1, 0), (0, -1), (1, 0), (0, 1)]

REVERSE_MOVE = {0: 2, 1: 3, 2: 0, 3: 1}

DIRECTIONS_PROB = []


def _populate_direction_probs():
    # 24 permutations of 4 directions
    permutations = [
        (2, 3, 0, 1),
        (2, 3, 1, 0),
        (2, 0, 3, 1),
        (2, 0, 1, 3),
        (2, 1, 3, 0),
        (2, 1, 0, 3),
        (3, 2, 0, 1),
        (3, 2, 1, 0),
        (3, 0, 2, 1),
        (3, 0, 1, 2),
        (3, 1, 2, 0),
        (3, 1, 0, 2),
        (0, 2, 3, 1),
        (0, 2, 1, 3),
        (0, 3, 2, 1),
        (0, 3, 1, 2),
        (0, 1, 2, 3),
        (0, 1, 3, 2),
        (1, 2, 3, 0),
        (1, 2, 0, 3),
        (1, 3, 2, 0),
        (1, 3, 0, 2),
        (1, 0, 2, 3),
        (1, 0, 3, 2)
    ]
    weighted = [
        (sum([(4 if d in {3, 2} else 1) * 2**(3-i) for i, d in enumerate(p)]), p) for p in permutations
    ]
    weighted.sort(key=lambda x: x[0], reverse=True)
    # the less the index, the higher the weight
    w0 = 1/24 / 4
    d = (1 - 24 * w0) * 2 / (24 * 23)

    total_prob = 0
    for i, (weight, p) in enumerate(reversed(weighted)):
        total_prob += w0 + i * d
        DIRECTIONS_PROB.append((w0 + i * d, p))
    print(f"Total prob: {total_prob}")

_populate_direction_probs()


def get_random_directions() -> Tuple[int, int, int, int]:
    r = random.random()
    total = 0
    for w, p in DIRECTIONS_PROB:
        total += w
        if r < total:
            return p
    return DIRECTIONS_PROB[-1]


def in_bounds(point: Point, w: int, h: int) -> bool:
    x, y = point
    return 0 <= x < w and 0 <= y < h


class Route:
    def __init__(self, point: Point, total_heat: int, path: Optional[List[int]] = None, track: Set[Point] = None):
        self.point = point
        self.total_heat = total_heat
        self.path = path or []
        self.track: Set[Point] = track or set()

    def __str__(self) -> str:
        return f"{self.point} h: {self.total_heat} {self.path}"

    def __repr__(self) -> str:
        return self.__str__()

    def copy(self) -> "Route":
        return Route(self.point, self.total_heat, [p for p in self.path], copy.copy(self.track))

    def _get_shortcuts(self, last_point: int) -> List[Tuple[int, int]]:
        # get all shortcuts from the prev point to the last
        shortcuts = []
        last_move = self.path[-1] if self.path else -1
        neighbours = []
        if last_move != 2:
            neighbours.append((self.point[0] - 1, self.point[1]))
        if last_move != 0:
            neighbours.append((self.point[0] + 1, self.point[1]))
        if last_move != 3:
            neighbours.append((self.point[0], self.point[1] - 1))
        if last_move != 1:
            neighbours.append((self.point[0], self.point[1] + 1))
        for neighbour in neighbours:
            if neighbour not in self.track:
                continue
            # find the previous point in neighbour coords
            cur = (0, 0)
            for i, d in enumerate(self.path):
                dx, dy = DIRECTIONS[d]
                cur = (cur[0] + dx, cur[1] + dy)
                if cur == neighbour:
                    shortcuts.append(i)
                    break
        return shortcuts

    def build_shortcuts(self, heat_matrix: List[List[int]]):
        shortcuts = self._get_shortcuts()
        if not shortcuts:
            return

        short_routes = []
        for shortcut in shortcuts:
            short_route = self._build_shortcut(shortcut, heat_matrix)
            if short_route:
                short_routes.append(short_route)

        if short_routes:
            short_routes.sort(key=lambda x: x.total_heat)
            if short_routes[0].total_heat < self.total_heat:
                if len(self.path) - len(short_routes[0].path) < 2:
                    print("loop")
                self.path = short_routes[0].path
                self.total_heat = short_routes[0].total_heat
                self.track = short_routes[0].track
                self.point = short_routes[0].point

    def _build_shortcut(self, shortcut: int, heat_matrix:List[List[int]]) -> Optional["Route"]:
        # follow the original path until the shortcut index
        point = (0, 0)
        total_heat = 0
        track = set()
        path = []
        for i in range(shortcut + 1):
            dx, dy = DIRECTIONS[self.path[i]]
            point = (point[0] + dx, point[1] + dy)
            total_heat += heat_matrix[point[1]][point[0]]
            path.append(self.path[i])
            track.add(point)
        # leap from shortcut's step to the last step
        a, b = point, self.point
        direct = 2 if a[0] < b[0] else 0 if a[0] > b[0] else 3 if a[1] < b[1] else 1
        # can move this direction?
        if len(path) >= MAX_PATH_LEN:
            if path[-1] == direct and path[-2] == direct and path[-3] == direct:
                return None
        point = self.point
        total_heat += heat_matrix[point[1]][point[0]]
        path.append(direct)
        track.add(point)
        return Route(point, total_heat, path, track)


class HeatMap:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.matrix: List[List[int]] = []
        self.best_score = 1508  # 2397 is the best result so far
        self.best_route: Optional[Route] = None

        self.w = 0
        self.h = 0
        self._read_from_file()

    def find_way(self) -> int:
        iterations_since_update = 0
        score_updated = False
        while True:
            updated_score = self._build_route()
            if updated_score:
                print(f"New best score: {updated_score} ({iterations_since_update} iterations before updated)")
                iterations_since_update = 0
                score_updated = True
            else:
                iterations_since_update += 1

            if iterations_since_update > 1000000 and score_updated:
                break

        # the bottom-right corner is expected to have 2 routes
        print(f"Best route: {self.best_route}")
        self._print_route(self.best_route)
        return self.best_route.total_heat - self.matrix[0][0]

    def _print_route(self, route: Route) -> None:
        route_points = [(0, 0)]
        for d in route.path:
            dx, dy = DIRECTIONS[d]
            route_points.append((route_points[-1][0] + dx, route_points[-1][1] + dy))

        route_points = set(route_points)

        for row_index, row in enumerate(self.matrix):
            for col, heat in enumerate(row):
                smb = str(heat)
                if (col, row_index) in route_points:
                    smb = f"\033[31m{smb}\033[0m"
                print(f"{smb} ", end="")
            print("")

    def _build_route(self) -> int:
        route = Route((0, 0), self.matrix[0][0])
        counter = 0
        while True:
            counter += 1
            if counter > 100:
                print("loop")
            new_ways_found = False
            if self.best_score and route.total_heat > self.best_score:
                return 0

            # choose a new step randomly
            directions = get_random_directions()

            for d in directions:
                if route.path:
                    if route.path[-1] == REVERSE_MOVE[d]:
                        # don't step back
                        continue
                dx, dy = DIRECTIONS[d]
                new_point = (route.point[0] + dx, route.point[1] + dy)
                if not in_bounds(new_point, self.w, self.h):
                    # don't step outside
                    continue
                # have we crossed the track?
                if new_point in route.track:
                    continue

                # don't step more than N steps in one direction
                if len(route.path) >= MAX_PATH_LEN:
                    if route.path[-1] == d and route.path[-2] == d and route.path[-3] == d:
                        continue

                heat = route.total_heat + self.matrix[new_point[1]][new_point[0]]
                # have we already reached a worse score (lost more heat)?
                if self.best_score and heat >= self.best_score:
                    continue
                route.path.append(d)
                route.point = new_point
                route.total_heat = heat
                route.track.add(new_point)
                new_ways_found = True

                # if reached bottom right
                if route.point == (self.w - 1, self.h - 1):

                    # try all shortcuts in the route
                    route.build_shortcuts(self.matrix)

                    if not self.best_score or route.total_heat < self.best_score:
                        self.best_score = route.total_heat
                        self.best_route = route.copy()
                    return route.total_heat
                break

            if not new_ways_found:
                return 0
        return 0

    def _read_from_file(self):
        with open(self.file_path) as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
        self.matrix = [[int(c) for c in l] for l in lines]
        self.h = len(self.matrix)
        self.w = len(self.matrix[0])


def main():
    path = "/Users/andreisitaev/Downloads/input_d17_small.txt"  # 2710 - too high
    hm = HeatMap(path)
    total_heat = hm.find_way()
    print(f"Total heat: {total_heat}")


if __name__ == "__main__":
    main()
