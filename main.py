# The speed is increased to 1m times, but data speed (light speed) slowed down to 20 times 

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
SIM_SPEED = 1_000_000  # 1000000 times faster than real time
SIM_START_DATE = datetime(2161, 5, 19)

# --- Simulation Control State ---
is_paused = False
sim_speed_factor = 1.0 # 1.0 for normal, 0.1 for slow
# ------------------------------

FPS = 120
DT = 1 / FPS

EARTH_ORBITAL_SPEED = 2 * pi / SECONDS_IN_YEAR  # rad/sec (in simulation time ≈ 1.99e-7 rad/sec)

BASE_OBJECT_SPEED = 0.002 * SIM_SPEED / 30 # in AU / sim_sec , 300_000 km/sec
# OBJECT_SPEED = 0.002 * SIM_SPEED # <<< REMOVE OR COMMENT THIS

# === SETTINGS ===
SUN_RADIUS_AU = 0.00465 * 28 # increased for better visibility
 
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
    {"name": "mercury", "ro": 0.387,        "r": 0.015, "speed": 2 * pi / (87.97 * SECONDS_IN_DAY),     "color": "tan"},
    {"name": "venus",   "ro": 0.723,        "r": 0.035, "speed": 2 * pi / (224.7 * SECONDS_IN_DAY),     "color": "orange"},
    {"name": "earth",   "ro": 1.000,        "r": 0.04,  "speed": EARTH_ORBITAL_SPEED,                   "color": "lightblue"},
    {"name": "mars",    "ro": 1.524,        "r": 0.03,  "speed": 2 * pi / (686.98 * SECONDS_IN_DAY),    "color": "brown"},
    {"name": "jupiter", "ro": 5.203 * 0.7,  "r": 0.09,  "speed": 2 * pi / (4332.59 * SECONDS_IN_DAY),   "color": "peru"},
    {"name": "saturn",  "ro": 9.537 * 0.6,  "r": 0.07,  "speed": 2 * pi / (10759.22 * SECONDS_IN_DAY),  "color": "khaki"},
    {"name": "uranus",  "ro": 19.191 * 0.5, "r": 0.05,  "speed": 2 * pi / (30688.5 * SECONDS_IN_DAY),   "color": "turquoise"},
    {"name": "neptune", "ro": 30.07 * 0.4,  "r": 0.05,  "speed": 2 * pi / (60195 * SECONDS_IN_DAY),     "color": "navy"},
]

planets = [
    CelestialBody(**conf, pixels_per_au=PIXELS_PER_AU)
    for conf in planet_configs
]

satellite_configs = [
    # Sun satellites
    {"parent": "sun", "ro": 240 / 195.91, "r": 0.01, "speed": 2 * pi / (600 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0, "name": "sun_sat_1"},
    {"parent": "sun", "ro": 550 / 195.91, "r": 0.01, "speed": 2 * pi / (1000 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0, "name": "sun_sat_2"},

    # Planets satellites
    {"parent": "mercury", "ro": 5 / 195.91,     "r": 0.003, "speed": 2 * pi / (10 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0, "name": "merc_sat_1"},
    {"parent": "venus",   "ro": 15 / 195.91,    "r": 0.004, "speed": 2 * pi / (30 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0, "name": "venus_sat_1"},
    {"parent": "earth",   "ro": 30 / 195.91,    "r": 0.005, "speed": 2 * pi / (27.3 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0, "name": "moon"},
    {"parent": "mars",    "ro": 25 / 195.91,    "r": 0.004, "speed": 2 * pi / (1.3 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0, "name": "mars_sat_1"},

    {"parent": "jupiter", "ro": 30 / 195.91,    "r": 0.005, "speed": 2 * pi / (1.8 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0, "name": "io"},
    {"parent": "jupiter", "ro": 40 / 195.91,    "r": 0.005, "speed": 2 * pi / (3.6 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0, "name": "europa"},

    {"parent": "saturn",  "ro": 45 / 195.91,    "r": 0.005, "speed": 2 * pi / (1.4 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0, "name": "pan"},
    {"parent": "saturn",  "ro": 60 / 195.91,    "r": 0.006, "speed": 2 * pi / (16 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0, "name": "titan"},

    {"parent": "uranus",  "ro": 35 / 195.91,    "r": 0.004, "speed": 2 * pi / (2 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0, "name": "uran_sat_1"},
    {"parent": "uranus",  "ro": 45 / 195.91,    "r": 0.004, "speed": 2 * pi / (4 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0, "name": "uran_sat_2"},

    {"parent": "neptune", "ro": 20 / 195.91,    "r": 0.003, "speed": 2 * pi / (1 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0, "name": "nept_sat_1"},
    {"parent": "neptune", "ro": 70 / 195.91,    "r": 0.004, "speed": 2 * pi / (5 * SECONDS_IN_DAY * 10), "color": "blue", "cooldown": 0, "name": "nept_sat_2"},

    # Far objects on the sun's orbit
    {"parent": "sun", "ro": 600 / 195.91, "r": 0.01, "speed": 2 * pi / (1500 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0, "name": "sun_sat_far_1"},
    {"parent": "sun", "ro": 700 / 195.91, "r": 0.01, "speed": 2 * pi / (2000 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0, "name": "sun_sat_far_2"},
    {"parent": "sun", "ro": 800 / 195.91, "r": 0.01, "speed": 2 * pi / (2500 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0, "name": "sun_sat_far_3"},
    {"parent": "sun", "ro": 850 / 195.91, "r": 0.01, "speed": 2 * pi / (2800 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0, "name": "sun_sat_far_4"},
    {"parent": "sun", "ro": 900 / 195.91, "r": 0.01, "speed": 2 * pi / (3200 * SECONDS_IN_DAY), "color": "blue", "cooldown": 0, "name": "sun_sat_far_5"},
]

planet_by_name = {planet.name: planet for planet in planets}
planet_by_name["sun"] = sun # In this logic sun is a planet too :)

satellites = []
for i, conf in enumerate(satellite_configs):
    parent = planet_by_name.get(conf["parent"]) if conf["parent"] else None
    # Assign a default name if not provided, ensuring uniqueness
    default_name = f"sat_{i+1}"
    sat_name = conf.get("name", default_name)
    
    sat = CelestialBody(
        name=sat_name, # Use provided or default name
        parent=parent,
        pixels_per_au=PIXELS_PER_AU,
        **{k: conf[k] for k in ("ro", "r", "speed", "color") if k != 'name'} # Exclude name from kwargs
        )
    satellites.append(sat)

# === Logging simulation start ===
log_manager = LogManager(canvas, WIDTH, HEIGHT)
real_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
sim_time_str = SIM_START_DATE.strftime("%Y-%m-%d %H:%M:%S")
log_manager.log(f"🚀 Simulation started", timestamp=real_time_str)
log_manager.log(f"🕒 Sim time: {sim_time_str}")
log_manager.log(f"ℹ️ Press 'P' to pause/resume, 'S' to toggle speed (1x / 0.1x)") # Add info log

def update():
    # Real time
    global last_real_time
    now = time.time()
    real_dt = now - last_real_time
    last_real_time = now

    # --- Pause Check --- 
    if is_paused:
        # Still need to schedule next update to keep GUI responsive
        if root.winfo_exists():
            root.after(int(DT * 1000), update)
        return # Skip simulation update if paused
    # ---------------------

    # --- Effective Speed Calculation ---
    effective_sim_speed = SIM_SPEED * sim_speed_factor
    # -----------------------------------

    sim_dt = real_dt * effective_sim_speed # Use effective speed
    engine.update(sim_dt, zoom_scale)

    sun.update_position(CENTER_X, CENTER_Y, sim_dt, zoom=zoom_scale)
    sun.draw(canvas, CENTER_X, CENTER_Y, zoom=zoom_scale)

    for planet in planets:
        planet.update_position(CENTER_X, CENTER_Y, sim_dt, zoom=zoom_scale)
        planet.draw(canvas, CENTER_X, CENTER_Y, zoom=zoom_scale)

    for sat in satellites:
        sat.update_position(CENTER_X, CENTER_Y, sim_dt, zoom=zoom_scale)
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
    object_speed=BASE_OBJECT_SPEED, # Use base speed
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

def toggle_pause(event=None):
    global is_paused
    is_paused = not is_paused
    log_message = "Simulation paused" if is_paused else "Simulation resumed"
    log_manager.log(log_message) # Log pause/resume

def toggle_speed(event=None):
    global sim_speed_factor
    if sim_speed_factor == 1.0:
        sim_speed_factor = 0.1
        log_message = "Simulation speed set to Slow (0.1x)"
    else:
        sim_speed_factor = 1.0
        log_message = "Simulation speed set to Normal (1x)"
    log_manager.log(log_message) # Log speed change

# Binds            
root.bind("p", toggle_pause) # Bind P for pause
root.bind("s", toggle_speed) # Bind S for speed
root.bind("o", toggle_orbits)
root.bind("l", toggle_labels)
root.bind("+", lambda e: zoom_in())
root.bind("-", lambda e: zoom_out())

date_label = None

update()
root.mainloop()