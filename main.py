import tkinter as tk
from bodies import CelestialBody
from engine import SimulationEngine
from mst import update_mst

# === SETTINGS ===
SCALE_SPEED = 0.06  # global speed scaler
OBJECT_SPEED = 100 * SCALE_SPEED  # data speed
FPS = 60
DT = 1 / FPS
SUN_RADIUS = 84 / 2 # decreased for better visibility
show_orbits = True

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
    {"parent": "neptune", "ro": 42, "r": 2, "speed": 0.01 * SCALE_SPEED, "color": "blue", "cooldown": 0},
]

planet_by_name = {planet.name: planet for planet in planets}
planet_by_name["sun"] = sun # In this logic sun is a planet too :)

satellites = []
for conf in satellite_configs:
    parent = planet_by_name.get(conf["parent"]) if conf["parent"] else None
    sat = CelestialBody(name=conf.get("name", "sat"), parent=parent, **{k: conf[k] for k in ("ro", "r", "speed", "color")})
    satellites.append(sat)

# data_objects = []

def update():
    for planet in planets:
        planet.update_position(CENTER_X, CENTER_Y)
        planet.draw(canvas)

    for sat in satellites:
        sat.update_position(CENTER_X, CENTER_Y)
        sat.draw(canvas)

    canvas.delete("orbit")  # Clear previous orbits
    if show_orbits:
        for planet in planets:
            planet.draw_orbit(canvas, CENTER_X, CENTER_Y)
        for sat in satellites:
            sat.draw_orbit(canvas, CENTER_X, CENTER_Y)        

    update_mst(canvas, satellites, planets + [sun]) # Update the MST edges

    if root.winfo_exists():
        root.after(int(DT * 1000), update)

engine = SimulationEngine(satellites, canvas, object_speed=OBJECT_SPEED, obstacles=planets+[sun])

def update_simulation():
    engine.update(DT)
    if root.winfo_exists():
        root.after(int(DT * 1000), update_simulation)

# Bind the "o" key to toggle orbits
def toggle_orbits(event=None):
    global show_orbits
    show_orbits = not show_orbits

root.bind("o", toggle_orbits)

update()
update_simulation()
root.mainloop()