import tkinter as tk
from bodies import CelestialBody
from engine import SimulationEngine
from mst import update_mst
from datetime import datetime
from math import pi
import time
from log_manager import LogManager


last_real_time = time.time()

# === TIME ===
SECONDS_IN_YEAR = 31_557_600  # 365.25 * 24 * 60 * 60
SECONDS_IN_DAY = 86400
SIM_SPEED = 10000  # 1000 times faster than real time
SIM_START_DATE = datetime(2161, 5, 19)

FPS = 60
DT = 1 / FPS

EARTH_ORBITAL_SPEED = 2 * pi / SECONDS_IN_YEAR  # ≈ 1.99e-7 rad/sec

OBJECT_SPEED = 0.002 * SIM_SPEED # в а.е./сек (примерно, 300_000 км/сек / SIM_SPEED)

# === SETTINGS ===
SUN_RADIUS_AU = 0.00465 * 30 # increased for better visibility
 
show_orbits = False
show_labels = False
zoom_scale = 2.0
ZOOM_STEP = 1.1

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
ro_max = 30.1
MARGIN = 50
PIXELS_PER_AU = (CANVAS_WIDTH / 2 - MARGIN) / ro_max


root.geometry(f"{WIDTH}x{HEIGHT}")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()


# === Sun Initialization ===
sun = CelestialBody(
    name="sun",
    ro=0,
    r=SUN_RADIUS_AU,
    speed=0,
    color="yellow",
    pixels_per_au=PIXELS_PER_AU
)

sun.x = CENTER_X
sun.y = CENTER_Y

# === Planet Initialization ===
planet_configs = [
    {"name": "mercury", "ro": 0.387, "r": 0.015, "speed": SIM_SPEED * 2 * pi / (87.97 * 24 * 3600), "color": "tan"},
    {"name": "venus",   "ro": 0.723, "r": 0.035, "speed": SIM_SPEED * 2 * pi / (224.7 * 24 * 3600), "color": "orange"},
    {"name": "earth",   "ro": 1.000, "r": 0.04,  "speed": SIM_SPEED * EARTH_ORBITAL_SPEED,          "color": "lightblue"},
    {"name": "mars",    "ro": 1.524, "r": 0.03,  "speed": SIM_SPEED * 2 * pi / (686.98 * 24 * 3600), "color": "brown"},
    {"name": "jupiter", "ro": 5.203 * 0.7, "r": 0.09,  "speed": SIM_SPEED * 2 * pi / (4332.59 * 24 * 3600), "color": "peru"},
    {"name": "saturn",  "ro": 9.537 * 0.6, "r": 0.07,  "speed": SIM_SPEED * 2 * pi / (10759.22 * 24 * 3600), "color": "khaki"},
    {"name": "uranus",  "ro": 19.191 * 0.5, "r": 0.05, "speed": SIM_SPEED * 2 * pi / (30688.5 * 24 * 3600), "color": "turquoise"},
    {"name": "neptune", "ro": 30.07 * 0.4, "r": 0.05,  "speed": SIM_SPEED * 2 * pi / (60195 * 24 * 3600),   "color": "navy"},
]

planets = [
    CelestialBody(**conf, pixels_per_au=PIXELS_PER_AU)
    for conf in planet_configs
]

satellite_configs = [
    # Sun satellites
    {"parent": "sun", "ro": 240 / 195.91, "r": 0.01, "speed": SIM_SPEED * 2 * pi / (600 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0},
    {"parent": "sun", "ro": 550 / 195.91, "r": 0.01, "speed": SIM_SPEED * 2 * pi / (1000 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0},

    # Planets satellites
    {"parent": "mercury", "ro": 5 / 195.91, "r": 0.003, "speed": SIM_SPEED * 2 * pi / (10 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0},
    {"parent": "venus",   "ro": 15 / 195.91, "r": 0.004, "speed": SIM_SPEED * 2 * pi / (30 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0},
    {"parent": "earth",   "ro": 30 / 195.91, "r": 0.005, "speed": SIM_SPEED * 2 * pi / (27.3 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0},  # Moon
    {"parent": "mars",    "ro": 25 / 195.91, "r": 0.004, "speed": SIM_SPEED * 2 * pi / (1.3 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0},

    {"parent": "jupiter", "ro": 30 / 195.91, "r": 0.005, "speed": SIM_SPEED * 2 * pi / (1.8 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0},  # Io
    {"parent": "jupiter", "ro": 40 / 195.91, "r": 0.005, "speed": SIM_SPEED * 2 * pi / (3.6 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0},  # Europe

    {"parent": "saturn",  "ro": 45 / 195.91, "r": 0.005, "speed": SIM_SPEED * 2 * pi / (1.4 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0},  # Pan
    {"parent": "saturn",  "ro": 60 / 195.91, "r": 0.006, "speed": SIM_SPEED * 2 * pi / (16 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0},   # Titan

    {"parent": "uranus",  "ro": 35 / 195.91, "r": 0.004, "speed": SIM_SPEED * 2 * pi / (2 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0},
    {"parent": "uranus",  "ro": 45 / 195.91, "r": 0.004, "speed": SIM_SPEED * 2 * pi / (4 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0},

    {"parent": "neptune", "ro": 20 / 195.91, "r": 0.003, "speed": SIM_SPEED * 2 * pi / (1 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0},
    {"parent": "neptune", "ro": 70 / 195.91, "r": 0.004, "speed": SIM_SPEED * 2 * pi / (5 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0},

    # Far objects on the sun's orbit
    {"parent": "sun", "ro": 600 / 195.91, "r": 0.01, "speed": SIM_SPEED * 2 * pi / (1500 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0},
    {"parent": "sun", "ro": 700 / 195.91, "r": 0.01, "speed": SIM_SPEED * 2 * pi / (2000 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0},
    {"parent": "sun", "ro": 800 / 195.91, "r": 0.01, "speed": SIM_SPEED * 2 * pi / (2500 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0},
    {"parent": "sun", "ro": 850 / 195.91, "r": 0.01, "speed": SIM_SPEED * 2 * pi / (2800 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0},
    {"parent": "sun", "ro": 900 / 195.91, "r": 0.01, "speed": SIM_SPEED * 2 * pi / (3200 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0},
]

planet_by_name = {planet.name: planet for planet in planets}
planet_by_name["sun"] = sun # In this logic sun is a planet too :)

satellites = []
for conf in satellite_configs:
    parent = planet_by_name.get(conf["parent"]) if conf["parent"] else None
    sat = CelestialBody(
        name=conf.get("name", "sat"),
        parent=parent,
        pixels_per_au=PIXELS_PER_AU,
        **{k: conf[k] for k in ("ro", "r", "speed", "color")}
        )
    satellites.append(sat)

# === Logging simulation start ===
log_manager = LogManager(canvas, WIDTH, HEIGHT)
real_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
sim_time_str = SIM_START_DATE.strftime("%Y-%m-%d %H:%M:%S")
log_manager.log(f"🚀 Simulation started", timestamp=real_time_str)
log_manager.log(f"🕒 Sim time: {sim_time_str}")

def update():
    # Real time
    global last_real_time
    now = time.time()
    real_dt = now - last_real_time
    last_real_time = now

    sim_dt = real_dt * SIM_SPEED
    engine.update(sim_dt)

    sun.update_position(CENTER_X, CENTER_Y, zoom=zoom_scale)
    sun.draw(canvas, CENTER_X, CENTER_Y, zoom=zoom_scale)

    for planet in planets:
        planet.update_position(CENTER_X, CENTER_Y, zoom=zoom_scale)
        planet.draw(canvas, CENTER_X, CENTER_Y, zoom=zoom_scale)

    for sat in satellites:
        sat.update_position(CENTER_X, CENTER_Y, zoom=zoom_scale)
        sat.draw(canvas, CENTER_X, CENTER_Y, zoom=zoom_scale)

    canvas.delete("orbit")  # Clear previous orbits
    if show_orbits:
        for planet in planets:
            planet.draw_orbit(canvas, CENTER_X, CENTER_Y, zoom=zoom_scale)
        for sat in satellites:
            sat.draw_orbit(canvas, CENTER_X, CENTER_Y, zoom=zoom_scale) 

    if show_labels:
        for body in planets + satellites:
            body.draw_label(canvas, CENTER_X, CENTER_Y, zoom=zoom_scale)

    # === SIMULATION DATE ===
    date_text = engine.sim_datetime.strftime("%Y-%m-%d %H:%M:%S")

    global date_label
    if date_label is None:
        date_label = canvas.create_text(
            WIDTH - 100, 30,
            text=date_text,
            fill="white",
            font=("Consolas", 14),
            anchor="e",
            tags="sim_date"
        )
    else:
        canvas.itemconfigure(date_label, text=date_text)

    log_manager.draw()
    update_mst(canvas, satellites, planets + [sun], zoom=zoom_scale, center_x=CENTER_X, center_y=CENTER_Y) # Update the MST edges    

    if root.winfo_exists():
        root.after(int(DT * 1000), update)
    

engine = SimulationEngine(
    satellites,
    canvas,
    object_speed=OBJECT_SPEED,
    obstacles=planets + [sun],
    center_x=CENTER_X,
    center_y=CENTER_Y,
    sim_start_date=SIM_START_DATE
)
engine.log_manager = log_manager

# Bind the "o" key to toggle orbits
def toggle_orbits(event=None):
    global show_orbits
    show_orbits = not show_orbits

def toggle_labels(event=None):
    global show_labels
    show_labels = not show_labels
    for body in planets + satellites:
        if body.label_object:
            canvas.itemconfigure(
                body.label_object,
                state="normal" if show_labels else "hidden"
            )

def zoom_in(event=None):
    global zoom_scale
    zoom_scale *= ZOOM_STEP

def zoom_out(event=None):
    global zoom_scale
    zoom_scale /= ZOOM_STEP

# Binds            
root.bind("o", toggle_orbits)
root.bind("l", toggle_labels)
root.bind("+", lambda e: zoom_in())
root.bind("-", lambda e: zoom_out())

date_label = None

update()
root.mainloop()