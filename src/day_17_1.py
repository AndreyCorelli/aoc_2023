import copy
import random
from typing import List, TypeAlias, Set, Optional, Dict

# [0] - weight when came from the left, [1] - from the top, [2] - from the right, [3] - from the bottom
PointWeights: TypeAlias = tuple[int, int, int, int]

Point: TypeAlias = tuple[int, int]

# left, top, right, bottom
DIRECTIONS = [(-1, 0), (0, -1), (1, 0), (0, 1)]

REVERSE_MOVE = {0: 2, 1: 3, 2: 0, 3: 1}


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


class HeatMap:
    MAX_PATH_LEN = 3

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.matrix: List[List[int]] = []
        self.weights: List[List[PointWeights]] = []
        self.route_by_coords: Dict[Point, List[Route]] = {}

        self.w = 0
        self.h = 0
        self._read_from_file()

    def find_way(self) -> None:
        front = {Route((0, 0), self.matrix[0][0])}

        while True:
            new_front: Set[Route] = set()
            for point in front:
                counter = 4
                while counter > 0:
                    new_route = self._spread_heat(point)
                    if new_route:
                        new_front.add(new_route)
                        self.route_by_coords.setdefault(new_route.point, []).append(new_route)
                    else:
                        counter -= 1
            if not new_front:
                break
            front = new_front

        # the bottom-right corner is expected to have 2 routes
        routes = self.route_by_coords.get((self.w - 1, self.h - 1))
        routes.sort(key=lambda r: r.total_heat)
        print(f"Best route: {routes[0]}")
        self._print_route(routes[0])

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

    def _spread_heat(self, route: Route) -> Optional[Route]:
        # pick a direction randomly
        # if there is a wall, do nothing
        directions = [i for i in range(4)]

        # choose a new step randomly
        random.shuffle(directions)
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
            pw = self.weights[new_point[1]][new_point[0]]
            if pw[d] == 0 or pw[d] > heat:
                self.weights[new_point[1]][new_point[0]] = tuple(w if i != d else heat for i, w in enumerate(pw))
            else:
                continue

            route = route.copy()
            route.point = new_point
            route.total_heat = heat
            route.path.append(d)
            return route

        return None

    def _read_from_file(self):
        with open(self.file_path) as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        lines = [l for l in lines if l]
        self.matrix = [[int(c) for c in l] for l in lines]
        self.h = len(self.matrix)
        self.w = len(self.matrix[0])
        self.weights = [[(0, 0, 0, 0) for _ in range(self.w)] for _ in range(self.h)]


def main():
    path = "/Users/andreisitaev/Downloads/input_d17_small.txt"
    hm = HeatMap(path)
    hm.find_way()


if __name__ == "__main__":
    main()
