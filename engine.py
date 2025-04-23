# engine.py
import random
import math
from mst import find_mst, intersects_circle
from datetime import datetime, timedelta
class SimulationEngine:
    def __init__(self, satellites, canvas, object_speed=3, obstacles=None, center_x=0, center_y=0, sim_start_date=None):
        self.satellites = satellites
        self.canvas = canvas
        self.data_objects = []
        self.object_speed = object_speed
        self.obstacles = obstacles or []
        self.id_colors = {}
        self.center_x = center_x
        self.center_y = center_y
        self.sim_datetime = sim_start_date
        self.log_lines = []
        self.max_log_lines = 7
        self.log_file = open("log.txt", "w")
        self.data_counter = 0
        self.log_manager = None


    def _get_color_for_id(self, data_id):
        if data_id not in self.id_colors:
            #random color generation in format #RRGGBB
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            self.id_colors[data_id] = color
        return self.id_colors[data_id]

    def generate_data(self, dt):
        for sat in self.satellites:
            if not hasattr(sat, "cooldown"):
                sat.cooldown = random.expovariate(1 / 30000) # 3000 - many data
            data_id = self.data_counter
            self.data_counter += 1

            sat.cooldown -= dt
            if sat.cooldown <= 0:
                data = {
                    "id": data_id,
                    "x": sat.x,
                    "y": sat.y,
                    "current": sat,
                    "target": None,
                    "id": random.randint(10000, 99999),
                    "visited": {id(sat)}
                }
                self.data_objects.append(data)
                sat.cooldown = random.expovariate(1 / 30000)
                # print(f"DEBUG ENGINE: Generated Data [{data_id:06}] at [{sat.name}]") # Commented log
                if self.log_manager:
                    sender = data["current"]
                    self.log_manager.log(f"Data [#{data_id:06}] has been sent from [{sender.name}, {sender.parent.name if sender.parent else 'sun'}]")

    def move_data(self, zoom):
        mst_edges = find_mst(self.satellites, self.obstacles, zoom)
        to_remove = []

        for data in self.data_objects:
            if not data.get("target"):
                # Find potential neighbors from MST edges connected to the current satellite
                potential_neighbors = []
                current_sat = data["current"]
                for sat1, sat2 in mst_edges:
                    neighbor = None
                    if sat1 == current_sat:
                        neighbor = sat2
                    elif sat2 == current_sat:
                        neighbor = sat1
                    
                    if neighbor:
                        potential_neighbors.append(neighbor)

                # Filter neighbors: must be a satellite and not visited
                valid_neighbors = [
                    neighbor for neighbor in potential_neighbors
                    if neighbor in self.satellites and id(neighbor) not in data["visited"]
                ]

                target = None # Initialize target
                while valid_neighbors: # Loop until we find an unblocked neighbor or run out
                    potential_target = random.choice(valid_neighbors)
                    path_blocked = False
                    for obs in self.obstacles:
                        # Use current positions for the immediate path check
                        if intersects_circle(data["x"], data["y"], potential_target.x, potential_target.y, 
                                             obs.x, obs.y, obs.r * obs.pixels_per_au * zoom): # Use passed zoom parameter
                            # print(f"DEBUG ENGINE: Immediate path Data [{data['id']}] -> [{potential_target.name}] blocked by [{obs.name}]. Trying another neighbor.") # Commented log
                            path_blocked = True
                            valid_neighbors.remove(potential_target) # Remove blocked target from options
                            break # Stop checking obstacles for this target
                    
                    if not path_blocked:
                        target = potential_target # Found an unblocked target
                        # print(f"DEBUG ENGINE: Data [{data['id']}] at [{data['current'].name}] chose UNBLOCKED target [{target.name}] from neighbors: {[n.name for n in valid_neighbors+[target]]}") # Commented log
                        break # Exit the while loop

                if target: # Proceed only if an unblocked target was found
                    # Set target and target position to the current location of the target satellite
                    data["target"] = target
                    data["target_pos"] = (target.x, target.y) # Use target's current position

                else:
                    # No valid/unblocked neighbors found
                    if not any(neighbor in self.satellites and id(neighbor) not in data["visited"] for neighbor in potential_neighbors): 
                         # print(f"DEBUG ENGINE: Data [{data['id']}] at [{data['current'].name}] has no valid neighbors left. Marking for removal.") # Commented log
                         pass # Keep the logic, just comment the print
                    else:
                         # print(f"DEBUG ENGINE: Data [{data['id']}] at [{data['current'].name}] had neighbors, but all immediate paths were blocked. Marking for removal.") # Commented log
                         pass # Keep the logic, just comment the print
                    to_remove.append(data)
                    continue

            # --- Movement towards target_pos --- 
            if data.get("target_pos"):
                tx, ty = data["target_pos"] # Get target coordinates (current pos of target sat)
                
                # Recalculate dx, dy towards the static target position each frame
                dx = tx - data["x"]
                dy = ty - data["y"] 
                dist = math.hypot(dx, dy)

                if dist > self.object_speed: # Check if not already at the target position
                    # Calculate the next potential position towards the static target point
                    step_dx = dx / dist * self.object_speed
                    step_dy = dy / dist * self.object_speed
                    next_x = data["x"] + step_dx
                    next_y = data["y"] + step_dy

                    # Check for collision on this step
                    collision_detected = False
                    for obs in self.obstacles:
                        # Check if the step segment intersects the obstacle
                        if intersects_circle(data["x"], data["y"], next_x, next_y, 
                                             obs.x, obs.y, obs.r * obs.pixels_per_au * zoom):
                            # print(f"DEBUG ENGINE: Data [{data['id']}] movement {data['current'].name} -> {data['target'].name} collided with [{obs.name}] during transit. Removing.") # Commented log
                            collision_detected = True
                            break # Stop checking obstacles
                    
                    if collision_detected:
                        to_remove.append(data) # Mark for removal if collision detected
                        # Clear target info so it doesn't try to move further this frame
                        data["target"] = None 
                        data["target_pos"] = None
                        continue # Skip to the next data object
                    else:
                        # No collision, take the step
                        data["x"] = next_x
                        data["y"] = next_y
                else:
                    # Reached the target position
                    # print(f"DEBUG ENGINE: Data [{data['id']}] arriving at TARGET POSITION for [{data['target'].name}] from [{data['current'].name}]") # Commented log
                    data["x"], data["y"] = tx, ty # Snap to target position
                    data["visited"].add(id(data["target"]))
                    data["current"] = data["target"]
                    # print(f"DEBUG ENGINE: Data [{data['id']}] new current is [{data['current'].name}]") # Commented log
                    data["target"] = None
                    data["target_pos"] = None # Clear target position


        # Remove data packets marked for removal
        for d in to_remove:
            # print(f"DEBUG ENGINE: Removing data [{d['id']}] finally.") # Commented log
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

    def update(self, dt, zoom):
        self.generate_data(dt)
        self.move_data(zoom)
        self.draw_data()
        self.sim_datetime += timedelta(seconds=dt)

    def log(self, message: str):
        # Add the line to the list
        timestamp = self.sim_datetime.strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        self.log_lines.append(full_message)

        # Set the maximum number of lines
        if len(self.log_lines) > self.max_log_lines:
            self.log_lines.pop(0)

        # Print to file
        self.log_file.write(full_message + "\n")
        self.log_file.flush()