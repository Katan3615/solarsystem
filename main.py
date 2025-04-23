# The speed is increased to 1m times, but data speed (light speed) slowed down to 20 times 

import tkinter as tk
from bodies import CelestialBody
from engine import SimulationEngine
from mst import update_mst
from datetime import datetime
from math import pi
import time
from log_manager import LogManager
import config


last_real_time = time.time()

# === TIME ===
# Moved to config.py


# --- Simulation Control State ---
is_paused = False
sim_speed_factor = 1.0 # 1.0 for normal, 0.1 for slow
# ------------------------------
 
show_orbits = config.INITIAL_SHOW_ORBITS
show_labels = config.INITIAL_SHOW_LABELS
zoom_scale = config.INITIAL_ZOOM_SCALE


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
# ro_max = 30.1
MARGIN = 50
PIXELS_PER_AU = (CANVAS_WIDTH / 2 - MARGIN) / config.ro_max


root.geometry(f"{WIDTH}x{HEIGHT}")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()


# === Sun Initialization ===
sun = CelestialBody(
    name="sun",
    ro=0,
    r=config.SUN_RADIUS_AU,
    speed=0,
    color="yellow",
    pixels_per_au=PIXELS_PER_AU
)

sun.x = CENTER_X
sun.y = CENTER_Y

# === Planet Initialization ===
# planet_configs = [...]
planets = [
    CelestialBody(**conf, pixels_per_au=PIXELS_PER_AU)
    for conf in config.planet_configs
]

# satellite_configs = [...]
planet_by_name = {planet.name: planet for planet in planets}
planet_by_name["sun"] = sun # In this logic sun is a planet too :)

satellites = []
for i, conf in enumerate(config.satellite_configs):
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
log_manager = LogManager(canvas, WIDTH, HEIGHT, max_lines=10)
real_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
sim_time_str = config.SIM_START_DATE.strftime("%Y-%m-%d %H:%M:%S")
log_manager.log(f"Simulation started", timestamp=real_time_str)
log_manager.log("="*50)
log_manager.log(f"Sim time: {sim_time_str}")
log_manager.log(f"Press 'P' to pause/resume, 'S' to cycle speed (1x / 0.1x / 0.01x)")

def update():
    # Real time
    global last_real_time
    now = time.time()
    real_dt = now - last_real_time
    last_real_time = now

    # --- Pause Check --- 
    if is_paused:
        if root.winfo_exists():
            # Use constant delay even when paused to keep GUI responsive
            root.after(int(config.DT * 1000), update) 
        return
    # ---------------------

    # --- Effective Speed Calculation ---
    effective_sim_speed = config.SIM_SPEED * sim_speed_factor
    # -----------------------------------

    sim_dt = real_dt * effective_sim_speed
    engine.update(sim_dt, zoom_scale)

    sun.update_position(CENTER_X, CENTER_Y, sim_dt, zoom=zoom_scale)
    sun.draw(canvas, CENTER_X, CENTER_Y, zoom=zoom_scale)

    for planet in planets:
        planet.update_position(CENTER_X, CENTER_Y, sim_dt, zoom=zoom_scale)
        planet.draw(canvas, CENTER_X, CENTER_Y, zoom=zoom_scale)

    for sat in satellites:
        sat.update_position(CENTER_X, CENTER_Y, sim_dt, zoom=zoom_scale)
        sat.draw(canvas, CENTER_X, CENTER_Y, zoom=zoom_scale)

    canvas.delete("orbit")
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
    update_mst(canvas, satellites, planets + [sun], zoom=zoom_scale, center_x=CENTER_X, center_y=CENTER_Y)

    if root.winfo_exists():
        # Always schedule the next update using the base DT for consistent FPS
        root.after(int(config.DT * 1000), update) 


engine = SimulationEngine(
    satellites,
    canvas,
    object_speed=config.EFFECTIVE_DATA_SPEED,
    obstacles=planets + [sun],
    center_x=CENTER_X,
    center_y=CENTER_Y,
    sim_start_date=config.SIM_START_DATE
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
    zoom_scale *= config.ZOOM_STEP

def zoom_out(event=None):
    global zoom_scale
    zoom_scale /= config.ZOOM_STEP

def toggle_pause(event=None):
    global is_paused
    is_paused = not is_paused
    log_message = "Simulation paused" if is_paused else "Simulation resumed"
    log_manager.log(log_message)
    if not is_paused:
        # Schedule the next update immediately upon unpausing
        root.after(1, update)

def toggle_speed(event=None):
    global sim_speed_factor
    # Cycle through 1.0 -> 0.1 -> 0.01 -> 1.0
    if sim_speed_factor == 1.0:
        sim_speed_factor = 0.1
        log_message = "<< Simulation speed set to Slow (0.1x)"
    elif sim_speed_factor == 0.1:
        sim_speed_factor = 0.01
        log_message = "<< << Simulation speed set to Very Slow (0.01x)"
    else: # Must be 0.01
        sim_speed_factor = 1.0
        log_message = ">> Simulation speed set to Normal (1x)"
    log_manager.log(log_message)

# Binds
root.bind("p", toggle_pause)
root.bind("s", toggle_speed)
root.bind("o", toggle_orbits)
root.bind("l", toggle_labels)
root.bind("+", lambda e: zoom_in())
root.bind("-", lambda e: zoom_out())

date_label = None

update()
root.mainloop()