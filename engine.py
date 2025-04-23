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
        self.object_speed = object_speed # Base speed in AU/sim_sec
        self.obstacles = obstacles or []
        self.id_colors = {}
        self.center_x = center_x
        self.center_y = center_y
        self.sim_datetime = sim_start_date
        # Remove old log attributes
        # self.log_lines = []
        # self.max_log_lines = 7
        # self.log_file = open("log.txt", "w")
        self.data_counter = 0 # Ensure counter starts at 0
        self.log_manager = None
        self.last_generation_hour = -1 # Initialize to -1 to trigger generation on first hour
        self.tracked_packet_ids = set() # Set to store IDs we want to debug
        self.max_tracked_packets = 5    # Limit the number of packets to track


    def _get_color_for_id(self, data_id):
        if data_id not in self.id_colors:
            #random color generation in format #RRGGBB
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            self.id_colors[data_id] = color
        return self.id_colors[data_id]

    def generate_data(self, dt):
        # Generate data once per simulation hour
        if not self.satellites: # Don't generate if no satellites exist
            return
            
        current_hour = self.sim_datetime.hour
        if current_hour != self.last_generation_hour:
            # Hour has changed, generate one packet from a random satellite
            sat = random.choice(self.satellites)
            
            self.data_counter += 1 # Increment counter ONLY when generating
            data_id = self.data_counter
            generation_time = self.sim_datetime # Capture generation time

            # --- Track first few packet IDs --- 
            if len(self.tracked_packet_ids) < self.max_tracked_packets:
                self.tracked_packet_ids.add(data_id)
                print(f"[DEBUG] Now tracking packet ID: {data_id}\n") # Log which IDs are tracked
            # ----------------------------------

            data = {
                "id": data_id, # Use the counter as the primary ID
                "x": sat.x,
                "y": sat.y,
                "current": sat,
                "target": None,
                "visited": {id(sat)},
                "timestamp": generation_time # Store generation/departure time
            }
            self.data_objects.append(data)
            
            # Log using LogManager with sim_datetime
            if self.log_manager:
                sender = data["current"]
                self.log_manager.log(f"Data [#{data_id:06}] sent from [{sender.name}, {sender.parent.name if sender.parent else 'sun'}]", timestamp=generation_time)

            # Update the last generation hour
            self.last_generation_hour = current_hour
            
    def move_data(self, zoom, sim_dt): # Add sim_dt parameter
        mst_edges = find_mst(self.satellites, self.obstacles, zoom) # Pass zoom to find_mst as well
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
                    data["target"] = target
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

            # --- Movement towards target (DYNAMICALLY recalculate target position) --- 
            if data.get("target"):
                # Get target's CURRENT position each frame
                target_satellite = data["target"]
                tx = target_satellite.x
                ty = target_satellite.y
                
                # Recalculate dx, dy towards the current target position each frame
                dx = tx - data["x"]
                dy = ty - data["y"]
                dist = math.hypot(dx, dy)

                # Calculate distance to move in this frame based on sim_dt
                distance_this_step = self.object_speed * sim_dt

                # --- Conditional Detailed Debug Log --- 
                if data['id'] in self.tracked_packet_ids: # Only print for tracked IDs
                    print(f"[MOVE DEBUG] SimTime: {self.sim_datetime.strftime('%Y-%m-%d %H:%M:%S')}, sim_dt: {sim_dt:.4f}, PktID: {data['id']}, "
                          f"Current: ({data['x']:.3f},{data['y']:.3f}), Target: {target_satellite.name}({tx:.3f},{ty:.3f}), " # Log target name and current coords
                          f"Dist: {dist:.4f}, BaseSpeed: {self.object_speed:.5f}, StepDist: {distance_this_step:.6f}\n", flush=True)
                # ------------------------------------

                if dist > distance_this_step: # Check if distance to target is greater than movement this frame
                    # Calculate the next potential position towards the static target point
                    # Move by distance_this_step in the correct direction
                    step_dx = dx / dist * distance_this_step
                    step_dy = dy / dist * distance_this_step
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
                        continue # Skip to the next data object
                    else:
                        # No collision, take the step
                        data["x"] = next_x
                        data["y"] = next_y
                else:
                    # Reached the target satellite (or close enough)
                    packet_id = data["id"]
                    arrival_time = self.sim_datetime
                    departure_time = data["timestamp"]
                    travel_time = arrival_time - departure_time
                    source = data["current"]
                    destination = data["target"] # Target is still set here

                    # Log arrival via LogManager
                    if self.log_manager:
                         # Format timedelta nicely (e.g., total seconds with precision)
                        travel_time_str = f"{travel_time.total_seconds():.2f}s"
                        self.log_manager.log(f"Data [#{packet_id:06}] arrived at [{destination.name}] from [{source.name}] in {travel_time_str}", timestamp=arrival_time)

                    # print(f"DEBUG ENGINE: Data [{data['id']}] arriving at TARGET POSITION for [{data['target'].name}] from [{data['current'].name}]") # Commented log
                    data["x"], data["y"] = tx, ty # Snap to target position
                    data["visited"].add(id(data["target"]))
                    data["current"] = data["target"]
                    data["timestamp"] = arrival_time # Update timestamp for next hop BEFORE clearing target
                    # print(f"DEBUG ENGINE: Data [{data['id']}] new current is [{data['current'].name}]") # Commented log
                    data["target"] = None

                    if data['id'] in self.tracked_packet_ids: # Log arrival for tracked packets
                         print(f"[MOVE DEBUG] PktID: {packet_id} ARRIVED at {destination.name} ({tx:.3f},{ty:.3f}) from {source.name}. TravelTime: {travel_time.total_seconds():.2f}s", flush=True) # Log arrival coords


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
        self.move_data(zoom, dt) # Pass sim_dt (dt) here
        self.draw_data()
        self.sim_datetime += timedelta(seconds=dt)