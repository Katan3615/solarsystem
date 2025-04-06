import tkinter as tk
import math
import itertools
import random
from bodies import CelestialBody

# === SETTINGS ===
SCALE_SPEED = 0.3  # global speed scaler
OBJECT_SPEED = 10 * SCALE_SPEED  # data speed
FPS = 60
DT = 1 / FPS
SUN_RADIUS = 84 / 2 # decreased for better visibility

# === GUI SETTINGS ===
root = tk.Tk()
root.title("Solar System")
root.deiconify()
PADDING = 50
WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()
CANVAS_WIDTH = WIDTH - 2 * PADDING
CANVAS_HEIGHT = HEIGHT - 2 * PADDING
CENTER_X = CANVAS_WIDTH // 2
CENTER_Y = CANVAS_HEIGHT // 2

root.geometry(f"{WIDTH}x{HEIGHT}")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()

# === Sun Initialization ===
sun = CelestialBody(name="sun", ro=0, r=SUN_RADIUS, speed=0, color="yellow")
sun.x = CENTER_X
sun.y = CENTER_Y
canvas.create_oval(
    sun.x - SUN_RADIUS, sun.y - SUN_RADIUS,
    sun.x + SUN_RADIUS, sun.y + SUN_RADIUS,
    fill="yellow", outline="black", width=10
)

# === Planet Initialization ===
planet_configs = [
    {"name": "mercury", "ro": 90.31, "r": 0.4, "speed": 0.047 * SCALE_SPEED, "color": "tan"},
    {"name": "venus", "ro": 141.31, "r": 0.9, "speed": 0.035 * SCALE_SPEED, "color": "orange"},
    {"name": "earth", "ro": 195.91, "r": 1.3, "speed": 0.03 * SCALE_SPEED, "color": "lightblue"},
    {"name": "mars", "ro": 297.31, "r": 1, "speed": 0.024 * SCALE_SPEED, "color": "brown"},
    {"name": "jupiter", "ro": 360, "r": 8.4, "speed": 0.013 * SCALE_SPEED, "color": "peru"},
    {"name": "saturn", "ro": 410, "r": 6.96, "speed": 0.0097 * SCALE_SPEED, "color": "khaki"},
    {"name": "uranus", "ro": 440, "r": 3, "speed": 0.0068 * SCALE_SPEED, "color": "turquoise"},
    {"name": "neptune", "ro": 500, "r": 2.88, "speed": 0.0054 * SCALE_SPEED, "color": "navy"},
]

planets = [
    CelestialBody(**conf)
    for conf in planet_configs
]

satellite_configs = [
    {"parent": "sun", "ro": 240, "r": 5, "speed": 0.005 * SCALE_SPEED, "color": "blue", "cooldown": 0},
    {"parent": "sun", "ro": 550, "r": 5, "speed": 0.004 * SCALE_SPEED, "color": "blue", "cooldown": 0},
    {"parent": "mercury", "ro": 5, "r": 1, "speed": 0.04 * SCALE_SPEED, "color": "blue", "cooldown": 0},
    {"parent": "venus", "ro": 15, "r": 2, "speed": 0.035 * SCALE_SPEED, "color": "blue", "cooldown": 0},
    {"parent": "mars", "ro": 25, "r": 2, "speed": 0.025 * SCALE_SPEED, "color": "blue", "cooldown": 0},
    {"parent": "earth", "ro": 30, "r": 3, "speed": 0.03 * SCALE_SPEED, "color": "blue", "cooldown": 0},
    {"parent": "jupiter", "ro": 40, "r": 4, "speed": 0.02 * SCALE_SPEED, "color": "blue", "cooldown": 0},
    {"parent": "saturn", "ro": 45, "r": 4, "speed": 0.018 * SCALE_SPEED, "color": "blue", "cooldown": 0},
    {"parent": "uranus", "ro": 35, "r": 3, "speed": 0.015 * SCALE_SPEED, "color": "blue", "cooldown": 0},
]

planet_by_name = {planet.name: planet for planet in planets}
planet_by_name["sun"] = sun # In this logic sun is a planet too :)

satellites = []
for conf in satellite_configs:
    parent = planet_by_name.get(conf["parent"]) if conf["parent"] else None
    sat = CelestialBody(name=conf.get("name", "sat"), parent=parent, **{k: conf[k] for k in ("ro", "r", "speed", "color")})
    satellites.append(sat)

data_objects = []

def update():
    for planet in planets:
        planet.update_position(CENTER_X, CENTER_Y)
        planet.draw(canvas)

    for sat in satellites:
        sat.update_position(CENTER_X, CENTER_Y)
        sat.draw(canvas)    

    if root.winfo_exists():
        root.after(int(DT * 1000), update)


def generate_data(dt):
    for sat in satellites:
        # Инициализация cooldown, если его ещё нет
        if not hasattr(sat, "cooldown"):
            sat.cooldown = random.expovariate(1 / 30)


        sat.cooldown -= dt
        if sat.cooldown <= 0:
            # Генерация уникального объекта
            data = {
                "x": sat.x,
                "y": sat.y,
                "current": sat,
                "target": None,
                "id": random.randint(10000, 99999),
                "visited": {id(sat)}
            }
            data_objects.append(data)

            # Новый таймер на следующий запуск
            sat.cooldown = random.expovariate(1 / 30)


def intersects_circle(x1, y1, x2, y2, cx, cy, cr):
    ax, ay = x1 - cx, y1 - cy
    bx, by = x2 - cx, y2 - cy
    dx, dy = bx - ax, by - ay
    a = dx * dx + dy * dy
    b = 2 * (ax * dx + ay * dy)
    c = ax * ax + ay * ay - cr * cr

    if a == 0:
        return math.sqrt(ax * ax + ay * ay) < cr

    det = b * b - 4 * a * c
    if det < 0:
        return False

    det = math.sqrt(det)
    t1, t2 = (-b - det) / (2 * a), (-b + det) / (2 * a)

    return (0 <= t1 <= 1) or (0 <= t2 <= 1)

def find_mst():
    parent = {id(sat): id(sat) for sat in satellites}

    def find(v):
        if parent[v] == v:
            return v
        parent[v] = find(parent[v])
        return parent[v]

    def union(v1, v2):
        root1, root2 = find(v1), find(v2)
        if root1 != root2:
            parent[root2] = root1


    def build_graph():
        edges = []
        for sat1, sat2 in itertools.combinations(satellites, 2):
            x1, y1 = sat1.x, sat1.y
            x2, y2 = sat2.x, sat2.y
            visible = True

            for obj in planets + [sun]:
                if intersects_circle(x1, y1, x2, y2, obj.x, obj.y, obj.r):
                    visible = False
                    break

            if visible:
                weight = (x2 - x1) ** 2 + (y2 - y1) ** 2
                edges.append((weight, sat1, sat2))

        return edges

    edges = sorted(build_graph())
    mst = []

    for weight, sat1, sat2 in edges:
        if find(id(sat1)) != find(id(sat2)):
            union(id(sat1), id(sat2))
            mst.append((sat1, sat2))

    return mst

def update_mst():
    canvas.delete("mst_edge")
    for sat1, sat2 in find_mst():
        x1, y1 = sat1.x, sat1.y
        x2, y2 = sat2.y, sat2.y
        canvas.create_line(x1, y1, x2, y2, fill="blue", dash=(4, 2), tags="mst_edge")

def move_data():
    mst_edges = find_mst()
    to_remove = []

    for data in data_objects:
        if not data.get("target"):
            # Найти соседей, которые ещё не были посещены
            neighbors = [
                sat2 if sat1 == data["current"] else sat1
                for sat1, sat2 in mst_edges
                if (sat1 == data["current"] or sat2 == data["current"]) and
                   id(sat2 if sat1 == data["current"] else sat1) not in data["visited"]
            ]

            if neighbors:
                target = random.choice(neighbors)
                data["target"] = target
                data["target_pos"] = (target.x, target.y)  # Fixing the target position
            else:
                to_remove.append(data)
                continue

        if data.get("target_pos"):
            tx, ty = data["target_pos"]
            dx, dy = tx - data["x"], ty - data["y"]
            dist = math.hypot(dx, dy)
            speed = OBJECT_SPEED

            if dist > speed:
                data["x"] += dx / dist * speed
                data["y"] += dy / dist * speed
            else:
                data["x"], data["y"] = tx, ty
                data["visited"].add(id(data["target"]))
                data["current"] = data["target"]
                data["target"] = None
                data["target_pos"] = None

    # Удалить данные, которые обошли всех соседей
    for d in to_remove:
        data_objects.remove(d)

def draw_data():
    canvas.delete("data_object")
    for data in data_objects:
        canvas.create_rectangle(data["x"] - 2, data["y"] - 2, data["x"] + 2, data["y"] + 2, fill="white", tags="data_object")

def update_simulation():
    generate_data(0.016)
    move_data()
    draw_data()
    if root.winfo_exists():
        root.after(16, update_simulation)

update()
update_simulation()
root.mainloop()