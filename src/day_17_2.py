import copy
from typing import List, TypeAlias, Optional, Dict, Set

# [0] - weight when came from the left, [1] - from the top, [2] - from the right, [3] - from the bottom
PointWeights: TypeAlias = tuple[int, int, int, int]

Point: TypeAlias = tuple[int, int]

# left, top, right, bottom
DIRECTIONS = [(-1, 0), (0, -1), (1, 0), (0, 1)]

REVERSE_MOVE = {0: 2, 1: 3, 2: 0, 3: 1}

VISITED_KEY: TypeAlias = tuple[int, int, int, 4]


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
        return f"{self.point} (d={self.point[0] + self.point[1]}) h: {self.total_heat} {self.path}"

    def __repr__(self) -> str:
        return self.__str__()

    def copy(self) -> "Route":
        return Route(self.point, self.total_heat, [p for p in self.path], copy.copy(self.track))

    def can_move(self, d: int, is_finish: bool) -> bool:
        if not self.path:
            return True
        sequence = 1
        # amount of last items in path, that has the same value
        last = self.path[-1]
        for p in reversed(self.path[:-1]):
            if p == last:
                sequence += 1
            else:
                break
        if is_finish:
            # at least sequence of 4 is required
            return 2 < sequence < 10 and d == last

        if d == last:
            # can continue, unless 10 in a row
            return sequence < 10
        return sequence > 3


class DeadCellMap:
    def __init__(self):
        self.visited: Dict[VISITED_KEY, int] = {}

    def is_visited(self, route: Route, new_point: Point, new_dir: int, total_heat: int) -> bool:
        sequence = 1
        for p in reversed(route.path):
            if p == new_dir:
                sequence += 1
            else:
                break

        key = (new_point[0],
               new_point[1],
               new_dir,
               sequence)

        stored = self.visited.get(key)
        if not stored or stored > total_heat:
            self.visited[key] = total_heat
            return False

        return True


class HeatMap:
    MAX_PATH_LEN = 10

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.matrix: List[List[int]] = []
        self.visited = DeadCellMap()
        self.route_by_coords: Dict[Point, List[Route]] = {}
        self.score_limit = 3508  # don't know yet

        self.w = 0
        self.h = 0
        self._read_from_file()

    def find_way(self) -> int:
        front = [Route((0, 0), self.matrix[0][0])]
        front_index = 0

        while True:
            front_updated = False
            new_front: List[Route] = []
            for point in front:
                new_routes = self._spread_heat(point)
                if new_routes:
                    new_front += new_routes
                    for new_route in new_routes:
                        self.route_by_coords.setdefault(new_route.point, []).append(new_route)
                    front_updated = True

            if not front_updated:
                break

            # prune new_front
            front = new_front
            front = self._prune_front(front)
            front_index += 1

            print(f"Completed fronts: {front_index}. Front size: {len(front)}")

        routes = self.route_by_coords.get((self.w - 1, self.h - 1))
        routes.sort(key=lambda r: r.total_heat)
        print(f"Best route: {routes[0]}")
        self._print_route(routes[0])
        return routes[0].total_heat - self.matrix[0][0]

    def _prune_front(self, front: List[Route]) -> List[Route]:
        front.sort(key=lambda r: r.total_heat)  # / (r.point[0] + r.point[1]))
        max_len = 250000
        if len(front) > max_len * 1.1:
            print(f"Pruning front ({len(front)} -> {max_len}), "
                  f"min heat: {front[0].total_heat}, max heat: {front[-1].total_heat}")
            front = front[:max_len]

        return front

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

    def _spread_heat(self, route: Route) -> List[Route]:
        routes: List[Route] = []
        directions = [2, 3, 0, 1]
        for d in directions:
            if route.path:
                if route.path[-1] == REVERSE_MOVE[d]:
                    # don't step back
                    continue
            dx, dy = DIRECTIONS[d]
            new_point = (route.point[0] + dx, route.point[1] + dy)
            if not in_bounds(new_point, self.w, self.h):
                continue
            if not route.can_move(d, new_point == (self.w - 1, self.h - 1)):
                continue

            heat = route.total_heat + self.matrix[new_point[1]][new_point[0]]

            if heat > self.score_limit:
                # we lost already, the desired value should be less
                continue

            # have we crossed the track?
            if new_point in route.track:
                continue

            # have we visited this point already?
            if self.visited.is_visited(route, new_point, d, heat):
                continue

            distance = new_point[0] + new_point[1]
            if distance == 0:
                # returned to the start
                continue

            new_route = route.copy()
            new_route.point = new_point
            new_route.total_heat = heat
            new_route.path.append(d)
            new_route.track.add(new_point)
            routes.append(new_route)
        return routes

    def _read_from_file(self):
        with open(self.file_path) as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
        self.matrix = [[int(c) for c in l] for l in lines]
        self.h = len(self.matrix)
        self.w = len(self.matrix[0])


def main():
    path = "/Users/andreisitaev/Downloads/input_d17.txt"
    hm = HeatMap(path)
    total_heat = hm.find_way()
    print(f"Total heat: {total_heat}")


if __name__ == "__main__":
    main()
