import copy
import random
from typing import List, TypeAlias, Set, Optional, Dict

# [0] - weight when came from the left, [1] - from the top, [2] - from the right, [3] - from the bottom
PointWeights: TypeAlias = tuple[int, int, int, int]

Point: TypeAlias = tuple[int, int]

# left, top, right, bottom
DIRECTIONS = [(-1, 0), (0, -1), (1, 0), (0, 1)]

REVERSE_MOVE = {0: 2, 1: 3, 2: 0, 3: 1}

# (x, y, path[0], path[1], path[2])
VISITED_KEY: TypeAlias = tuple[int, int, int, int, int]


def in_bounds(point: Point, w: int, h: int) -> bool:
    x, y = point
    return 0 <= x < w and 0 <= y < h


class Route:
    def __init__(self, point: Point, total_heat: int, path: Optional[List[int]] = None):
        self.point = point
        self.total_heat = total_heat
        self.path = path or []

    def __str__(self) -> str:
        return f"{self.point} h: {self.total_heat} {self.path}"

    def __repr__(self) -> str:
        return self.__str__()

    def copy(self) -> "Route":
        return Route(self.point, self.total_heat, [p for p in self.path])

    # def get_key(self) -> VISITED_KEY:
    #     visited_key = (
    #         self.point[0],
    #         self.point[1],
    #         self.path[-2] if len(route.path) > 1 else -1,
    #         route.path[-1] if route.path else -1,
    #         d)


class HeatMap:
    MAX_PATH_LEN = 3

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.matrix: List[List[int]] = []
        self.visited: Dict[VISITED_KEY, int] = {}
        self.route_by_coords: Dict[Point, List[Route]] = {}

        self.w = 0
        self.h = 0
        self._read_from_file()

    def find_way(self) -> int:
        front = [Route((0, 0), self.matrix[0][0])]
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

            front = new_front
            front_index += 1
            coverage = len(self.visited) * 100 / total_points
            print(f"Completed fronts: {front_index}. Visited coverage: {coverage:.2f}%")

        # the bottom-right corner is expected to have 2 routes
        routes = self.route_by_coords.get((self.w - 1, self.h - 1))
        routes.sort(key=lambda r: r.total_heat)
        #print(f"Best route: {routes[0]}")
        self._print_route(routes[0])
        return routes[0].total_heat - self.matrix[0][0]

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
        directions = [i for i in range(4)]
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
            # have we visited this point already?
            visited_key = (
                new_point[0],
                new_point[1],
                route.path[-2] if len(route.path) > 1 else -1,
                route.path[-1] if route.path else -1,
                d)
            pw = self.visited.get(visited_key, 0)
            if not pw or pw > heat:
                self.visited[visited_key] = heat
            else:
                continue

            new_route = route.copy()
            new_route.point = new_point
            new_route.total_heat = heat
            new_route.path.append(d)
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
