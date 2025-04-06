# engine.py
import random
import math
from mst import find_mst

class SimulationEngine:
    def __init__(self, satellites, canvas, object_speed=3, obstacles=None):
        self.satellites = satellites
        self.canvas = canvas
        self.data_objects = []
        self.object_speed = object_speed
        self.obstacles = obstacles or []

    def generate_data(self, dt):
        for sat in self.satellites:
            if not hasattr(sat, "cooldown"):
                sat.cooldown = random.expovariate(1 / 30)

            sat.cooldown -= dt
            if sat.cooldown <= 0:
                data = {
                    "x": sat.x,
                    "y": sat.y,
                    "current": sat,
                    "target": None,
                    "id": random.randint(10000, 99999),
                    "visited": {id(sat)}
                }
                self.data_objects.append(data)
                sat.cooldown = random.expovariate(1 / 30)

    def move_data(self):
        mst_edges = find_mst(self.satellites, self.obstacles)
        to_remove = []

        for data in self.data_objects:
            if not data.get("target"):
                neighbors = [
                    sat2 if sat1 == data["current"] else sat1
                    for sat1, sat2 in mst_edges
                    if (sat1 == data["current"] or sat2 == data["current"]) and
                    id(sat2 if sat1 == data["current"] else sat1) not in data["visited"]
                ]
                if neighbors:
                    target = random.choice(neighbors)
                    data["target"] = target
                    data["target_pos"] = (target.x, target.y)
                else:
                    to_remove.append(data)
                    continue

            if data.get("target_pos"):
                tx, ty = data["target_pos"]
                dx, dy = tx - data["x"], ty - data["y"]
                dist = math.hypot(dx, dy)

                if dist > self.object_speed:
                    data["x"] += dx / dist * self.object_speed
                    data["y"] += dy / dist * self.object_speed
                else:
                    data["x"], data["y"] = tx, ty
                    data["visited"].add(id(data["target"]))
                    data["current"] = data["target"]
                    data["target"] = None
                    data["target_pos"] = None

        for d in to_remove:
            self.data_objects.remove(d)

    def draw_data(self):
        self.canvas.delete("data_object")
        for data in self.data_objects:
            self.canvas.create_rectangle(
                data["x"] - 2, data["y"] - 2,
                data["x"] + 2, data["y"] + 2,
                fill="white", tags="data_object"
            )

    def update(self, dt):
        self.generate_data(dt)
        self.move_data()
        self.draw_data()
