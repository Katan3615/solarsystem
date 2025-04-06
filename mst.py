import itertools
import math
from bodies import CelestialBody

def intersects_circle(x1, y1, x2, y2, cx, cy, cr):
    """Проверяет пересечение отрезка (x1,y1)-(x2,y2) с кругом центра (cx,cy) и радиуса cr."""
    # 1. Check if either endpoint is inside the circle
    dist1_sq = (x1 - cx)**2 + (y1 - cy)**2
    dist2_sq = (x2 - cx)**2 + (y2 - cy)**2
    if dist1_sq <= cr**2 or dist2_sq <= cr**2:
        return True  # one of the endpoints is inside the circle
    
    # 2. Counting the t parameter of the projection of the center of the circle onto the line defined by the segment
    dx = x2 - x1
    dy = y2 - y1
    length_sq = dx*dx + dy*dy
    if length_sq == 0:
        return False  # if it is a dot, no intersection
    t = ((cx - x1) * dx + (cy - y1) * dy) / length_sq

    # 3. Check if the projection falls within the segment
    if t < 0 or t > 1:
        return False

    # 4. Look for the closest point on the segment to the center of the circle
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    dist_closest_sq = (closest_x - cx)**2 + (closest_y - cy)**2
    
    # Have an intersection if the distance <= cr (touch or cross)
    return dist_closest_sq <= cr**2

def find_mst(satellites: list[CelestialBody], obstacles: list[CelestialBody]):
    """Вычисляет MST для списка спутников с учётом препятствий. Возвращает список рёбер (sat1, sat2)."""
    n = len(satellites)
    edges = []  # list of edges (distance, i, j)

    # 1. Make a list of all edges between satellites
    for i in range(n):
        for j in range(i+1, n):
            sat1 = satellites[i]
            sat2 = satellites[j]
            # Check every obstacle for intersection with the edge (sat1, sat2)
            blocked = False
            for obs in obstacles:
                if intersects_circle(sat1.x, sat1.y, sat2.x, sat2.y, obs.x, obs.y, obs.r):
                    blocked = True
                    break
            if blocked:
                continue  # can not
            # Counting the distance between satellites
            dx = sat1.x - sat2.x
            dy = sat1.y - sat2.y
            dist_sq = dx*dx + dy*dy
            edges.append((dist_sq, i, j))
    # 2. Sorting edges by distance
    edges.sort(key=lambda e: e[0])

    # 3. Initializing the union-find structure for Kruskal's algorithm
    parent = list(range(n))
    rank = [0] * n
    def find_set(a):
        # Find the root of the set containing a. Path compression is used to speed up future queries.
        if parent[a] != a:
            parent[a] = find_set(parent[a])
            a = parent[a]
        return a
    def union_set(a, b):
        # Union the sets containing a and b. Union by rank is used to keep the tree flat.
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

    # Choose the right edges to form the MST
    mst_edges = []
    for dist_sq, i, j in edges:
        if union_set(i, j):
            # If the edge is added to the MST, add it to the list of edges
            mst_edges.append((satellites[i], satellites[j]))
        if len(mst_edges) == n - 1:
            break  # MST is complete (n-1 edges for n vertices)
    
    return mst_edges


def update_mst(canvas, satellites: list[CelestialBody], obstacles: list[CelestialBody]):
    """Вычисляет MST между спутниками и рисует его рёбра наCanvas."""
    canvas.delete("mst_edge")  # Clear previous MST edges

    # Get the MST edges
    mst_edges = find_mst(satellites, obstacles)
    # Draw the edges on the canvas
    for sat1, sat2 in mst_edges:
        canvas.create_line(
            sat1.x, sat1.y, sat2.x, sat2.y,
            fill="blue", dash=(4,2), tags="mst_edge"
        )