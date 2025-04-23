import math
from bodies import CelestialBody

def intersects_circle(x1, y1, x2, y2, cx, cy, cr_pixels):
    """Проверяет пересечение отрезка с окружностью (в пикселях)."""
    dx = x2 - x1
    dy = y2 - y1

    # If the line is a point
    if dx == 0 and dy == 0:
        # Просто проверим, попадает ли точка внутрь круга
        return math.hypot(x1 - cx, y1 - cy) <= cr_pixels

    fx = x1 - cx
    fy = y1 - cy

    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - cr_pixels * cr_pixels

    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return False  # no intersection

    discriminant = math.sqrt(discriminant)
    t1 = (-b - discriminant) / (2 * a)
    t2 = (-b + discriminant) / (2 * a)

    return (0 <= t1 <= 1) or (0 <= t2 <= 1)


def find_mst(satellites: list[CelestialBody], obstacles: list[CelestialBody], zoom=1.0):
    n = len(satellites)
    edges = []

    for i in range(n):
        for j in range(i + 1, n):
            sat1 = satellites[i]
            sat2 = satellites[j]
            blocked = False

            for obs in obstacles:
                obs_r_px = obs.r * obs.pixels_per_au * zoom
                if intersects_circle(sat1.x, sat1.y, sat2.x, sat2.y, obs.x, obs.y, obs_r_px):
                    # print(f"DEBUG MST: Path [{sat1.name}] <-> [{sat2.name}] blocked by [{obs.name}]") # Commented log
                    blocked = True
                    break
            if blocked:
                continue

            dx = sat1.x - sat2.x
            dy = sat1.y - sat2.y
            dist_sq = dx * dx + dy * dy
            edges.append((dist_sq, i, j))

    edges.sort(key=lambda e: e[0])
    parent = list(range(n))
    rank = [0] * n

    def find_set(a):
        if parent[a] != a:
            parent[a] = find_set(parent[a])
        return parent[a]

    def union_set(a, b):
        ra = find_set(a)
        rb = find_set(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        elif rank[ra] > rank[rb]:
            parent[rb] = ra
        else:
            parent[rb] = ra
            rank[ra] += 1
        return True

    mst_edges = []
    for dist_sq, i, j in edges:
        if union_set(i, j):
            # print(f"DEBUG MST: Added edge [{satellites[i].name}] <-> [{satellites[j].name}]") # Commented log
            mst_edges.append((satellites[i], satellites[j]))
        if len(mst_edges) == n - 1:
            break

    return mst_edges

def update_mst(canvas, satellites: list[CelestialBody], obstacles: list[CelestialBody], zoom=1.0, center_x=0, center_y=0):
    canvas.delete("mst_edge")
    mst_edges = find_mst(satellites, obstacles, zoom=zoom)

    for sat1, sat2 in mst_edges:
        canvas.create_line(
            sat1.x, sat1.y, sat2.x, sat2.y,
            fill="blue", dash=(4, 2), tags="mst_edge"
        )
