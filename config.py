from datetime import datetime
from math import pi

# === TIME ===
SECONDS_IN_YEAR = 31_557_600  # 365.25 * 24 * 60 * 60
SECONDS_IN_DAY = 86400
SIM_SPEED = 1_000_000  # 1000000 times faster than real time
SIM_START_DATE = datetime(2161, 5, 19)
FPS = 120
DT = 1 / FPS # Base time step, might not be directly used if sim_dt is calculated from real time

# === PHYSICS / UNITS ===
EARTH_ORBITAL_SPEED = 2 * pi / SECONDS_IN_YEAR  # rad/sec (in simulation time)
BASE_OBJECT_SPEED = 0.002 # Base speed in AU / sim_sec. Speed of light is approx 0.002 AU/sec
DATA_SPEED_MULTIPLIER = 1000 # Make data visually faster relative to planets
EFFECTIVE_DATA_SPEED = BASE_OBJECT_SPEED * DATA_SPEED_MULTIPLIER # Speed passed to engine

# === OBJECT SETTINGS ===
SUN_RADIUS_AU = 0.00465 * 28 # increased for better visibility

# Max orbital radius for scaling calculations
ro_max = 30.1 

# === VISUAL DEFAULTS ===
# These might be overridden or controlled by GUI state in main.py
INITIAL_SHOW_ORBITS = False
INITIAL_SHOW_LABELS = False
INITIAL_ZOOM_SCALE = 2.0
ZOOM_STEP = 1.1

# === BODY CONFIGURATIONS ===
planet_configs = [
    # Speeds are in rad/sim_sec
    {"name": "mercury", "ro": 0.387,        "r": 0.015, "speed": 2 * pi / (87.97 * SECONDS_IN_DAY),     "color": "tan"},
    {"name": "venus",   "ro": 0.723,        "r": 0.035, "speed": 2 * pi / (224.7 * SECONDS_IN_DAY),     "color": "orange"},
    {"name": "earth",   "ro": 1.000,        "r": 0.04,  "speed": EARTH_ORBITAL_SPEED,                   "color": "lightblue"},
    {"name": "mars",    "ro": 1.524,        "r": 0.03,  "speed": 2 * pi / (686.98 * SECONDS_IN_DAY),    "color": "brown"},
    {"name": "jupiter", "ro": 5.203 * 0.7,  "r": 0.09,  "speed": 2 * pi / (4332.59 * SECONDS_IN_DAY),   "color": "peru"},
    {"name": "saturn",  "ro": 9.537 * 0.6,  "r": 0.07,  "speed": 2 * pi / (10759.22 * SECONDS_IN_DAY),  "color": "khaki"},
    {"name": "uranus",  "ro": 19.191 * 0.5, "r": 0.05,  "speed": 2 * pi / (30688.5 * SECONDS_IN_DAY),   "color": "turquoise"},
    {"name": "neptune", "ro": 30.07 * 0.4,  "r": 0.05,  "speed": 2 * pi / (60195 * SECONDS_IN_DAY),     "color": "navy"},
]

satellite_configs = [
    # Speeds are in rad/sim_sec
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