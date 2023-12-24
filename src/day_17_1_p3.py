import copy
from typing import List, TypeAlias, Optional, Dict, Set

# [0] - weight when came from the left, [1] - from the top, [2] - from the right, [3] - from the bottom
PointWeights: TypeAlias = tuple[int, int, int, int]

Point: TypeAlias = tuple[int, int]

# left, top, right, bottom
DIRECTIONS = [(-1, 0), (0, -1), (1, 0), (0, 1)]

REVERSE_MOVE = {0: 2, 1: 3, 2: 0, 3: 1}

# 3 last path's points
VISITED_KEY: TypeAlias = tuple[int, int, int]


def in_bounds(point: Point, w: int, h: int) -> bool:
    x, y = point
    return 0 <= x < w and 0 <= y < h


class PointVisits:
    def __init__(self, path: VISITED_KEY, heat: int):
        self.heat_by_path: Dict[VISITED_KEY, int] = {path: heat}
        self.min_heat = heat

    def try_add_path(self, path: VISITED_KEY, heat: int) -> bool:
        max_heat = self.min_heat + 50
        if heat > max_heat:
            return False
        existing_record = self.heat_by_path.get(path)
        if existing_record and existing_record < heat:
            return False
        self.heat_by_path[path] = heat
        self.min_heat = min(self.min_heat, heat)
        return True

    def __str__(self):
        return f"{self.min_heat}, {self.heat_by_path}"

    def __repr__(self):
        return self.__str__()


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


class VisitMap:
    def __init__(self):
        self.visited: Dict[Point, PointVisits] = {}
        self.paths_total: int = 0
        self.paths_filtered: int = 0

    def has_better_ways(self, point: Point, route: Route, cur_direction: int, heat: int) -> bool:
        visits = self.visited.get(point)
        route_path = (
            cur_direction,
            route.path[-1] if route.path else -1,
            route.path[-2] if len(route.path) > 1 else -1
        )
        if not visits:
            self.visited[point] = PointVisits(route_path, heat)
            self.paths_total += 1
            return False
        if visits.try_add_path(route_path, heat):
            self.paths_total += 1
            return False
        self.paths_filtered += 1
        return True


class HeatMap:
    MAX_PATH_LEN = 3

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.matrix: List[List[int]] = []
        self.visited = VisitMap()
        self.route_by_coords: Dict[Point, List[Route]] = {}
        self.score_limit = 1508  # get from day_17_1_p4 - I know the score should be less than 1508
        self.dead_cells: Set[Point] = set()
        self.best_heat_at_distance: Dict[int, int] = {}

        self.w = 0
        self.h = 0
        self._read_from_file()

    def find_way(self) -> int:
        front = [Route((0, 0), self.matrix[0][0])]
        prev_fronts = [[], [], [], []]
        front_index = 0
        total_points = self.w * self.h

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
            new_front = self._prune_front(new_front)

            for i in range(len(prev_fronts)):
                prev_fronts[i] = prev_fronts[i + 1] if i + 1 < len(prev_fronts) else front
            self.dead_cells = self.dead_cells.union(set([r.point for r in prev_fronts[0]]))
            front = new_front
            front_index += 1

            dead_percent = len(self.dead_cells) / total_points * 100

            print(f"Completed fronts: {front_index}. Dead cells: {dead_percent:.2f}%. Front size: {len(front)}")
            # if front_index == 87:
            #     print("Stopping at front 87")
            #     break

        # the bottom-right corner is expected to have 2 routes
        routes = self.route_by_coords.get((self.w - 1, self.h - 1))
        routes.sort(key=lambda r: r.total_heat)
        print(f"Best route: {routes[0]}")
        self._print_route(routes[0])
        return routes[0].total_heat - self.matrix[0][0]

    def _prune_front(self, front: List[Route]) -> List[Route]:
        max_len = 50000
        if len(front) <= max_len * 1.1:
            return front
        front.sort(key=lambda r: (r.point[0] + r.point[1]) * 100000 - r.total_heat, reverse=True)
        max_d = front[0].point[0] + front[0].point[1]
        min_d = front[-1].point[0] + front[-1].point[1]
        total_dist = self.w + self.h
        d_percent = 100 * max_d / total_dist
        print(f"Pruning front, max d: {max_d} ({d_percent:.2f}%), min d: {min_d}")
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
        # pick a direction randomly
        # if there is a wall, do nothing
        routes: List[Route] = []
        directions = [2, 3, 0, 1]
        # choose a new step randomly
        # random.shuffle(directions)
        for d in directions:
            if route.path:
                if route.path[-1] == REVERSE_MOVE[d]:
                    # don't step back
                    continue
            dx, dy = DIRECTIONS[d]
            new_point = (route.point[0] + dx, route.point[1] + dy)
            if not in_bounds(new_point, self.w, self.h):
                continue
            # does the point make line of N?
            if len(route.path) >= self.MAX_PATH_LEN:
                if route.path[-1] == d and route.path[-2] == d and route.path[-3] == d:
                    continue
            heat = route.total_heat + self.matrix[new_point[1]][new_point[0]]

            if heat > self.score_limit:
                # we lost already, the desired value should be less
                continue

            # have we crossed the track?
            if new_point in route.track:
                continue

            if new_point in self.dead_cells:
                continue
            # have we visited this point already?
            # if self.visited.has_better_ways(new_point, route, d, heat):
            #     continue

            distance = new_point[0] + new_point[1]
            if distance == 0:
                # returned to the start
                continue

            # if distance not in self.best_heat_at_distance:
            #     self.best_heat_at_distance[distance] = heat
            # else:
            #     if heat > self.best_heat_at_distance[distance] + 50:
            #         continue

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
