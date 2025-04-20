# engine.py
import random
import math
from mst import find_mst

class SimulationEngine:
    def __init__(self, satellites, canvas, object_speed=3, obstacles=None, center_x=0, center_y=0):
        self.satellites = satellites
        self.canvas = canvas
        self.data_objects = []
        self.object_speed = object_speed
        self.obstacles = obstacles or []
        self.id_colors = {}
        self.current_time = 0.0
        self.center_x = center_x
        self.center_y = center_y

    def _get_color_for_id(self, data_id):
        if data_id not in self.id_colors:
            #random color generation in format #RRGGBB
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            self.id_colors[data_id] = color
        return self.id_colors[data_id]

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

                    # Predicting the time to reach the target
                    dx = target.x - data["x"]
                    dy = target.y - data["y"]
                    distance = math.hypot(dx, dy)
                    time_to_reach = distance / self.object_speed
                    arrival_time = self.current_time + time_to_reach

                    # Predicting the target's future position
                    future_angle = target.angle + target.speed * time_to_reach
                    future_angle %= 2 * math.pi

                    # The orbit center
                    if target.parent:
                        cx, cy = target.parent.x, target.parent.y
                    else:
                        cx, cy = self.center_x, self.center_y

                    #  Predicting the position
                    future_x = cx + target.ro * math.cos(future_angle)
                    future_y = cy + target.ro * math.sin(future_angle)

                    # Setting up the target
                    data["target"] = target
                    data["target_eta"] = arrival_time
                    data["target_pos"] = (future_x, future_y)

                    # print("\n=== DATA TRANSFER ===")
                    # print(f"current_time: {self.current_time:.2f}")
                    # print(f"from: {data['current'].name} -> to: {target.name}")
                    # print(f"current_pos: ({data['x']:.1f}, {data['y']:.1f})")
                    # print(f"target.angle: {target.angle:.4f}, speed: {target.speed:.6f}")
                    # print(f"time_to_reach: {time_to_reach:.2f}")
                    # print(f"future_angle: {future_angle:.4f}")
                    # print(f"predicted pos: ({future_x:.1f}, {future_y:.1f})")
                    # print(f"target now at: ({target.x:.1f}, {target.y:.1f})")
                else:
                    to_remove.append(data)
                    continue

            # Recalculating the target position
            arrival_time = data.get("target_eta", self.current_time + 1)  # fallback
            remaining_time = arrival_time - self.current_time
            remaining_time = max(remaining_time, 0)  # не даём уйти в минус

            future_angle = data["target"].angle + data["target"].speed * remaining_time
            future_angle %= 2 * math.pi

            if data["target"].parent:
                parent = data["target"].parent
                pcx, pcy = (parent.x, parent.y)
            else:
                pcx, pcy = self.center_x, self.center_y

            tx = pcx + data["target"].ro * math.cos(future_angle)
            ty = pcy + data["target"].ro * math.sin(future_angle)

            # === движение к предсказанным координатам ===
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
                data["target_eta"] = None


        for d in to_remove:
            self.data_objects.remove(d)

    def draw_data(self):
        self.canvas.delete("data_object")
        for data in self.data_objects:
            color = self._get_color_for_id(data["id"])
            self.canvas.create_rectangle(
                data["x"] - 2, data["y"] - 2,
                data["x"] + 2, data["y"] + 2,
                fill=color, tags="data_object"
            )

    def update(self, dt):
        self.generate_data(dt)
        self.move_data()
        self.draw_data()
        self.current_time += dt
