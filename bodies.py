import math

class CelestialBody:
    def __init__(self, name, ro, r, speed, color, parent=None, pixels_per_au=100):
        self.name = name
        self.ro = ro
        self.r = r
        self.speed = speed
        self.color = color
        self.parent = parent
        self.pixels_per_au = pixels_per_au # Default value, can be set externally

        self.angle = 0
        self.x = 0
        self.y = 0
        self.circle = None
        self.cooldown = 0
        self.label_object = None
        self.label_text = name

    def update_position(self, center_x, center_y, zoom=1.0):
        self.angle += self.speed
        self.angle %= 2 * math.pi

        scaled_ro = self.ro * zoom * self.pixels_per_au

        if self.parent is None:
            self.x = center_x + scaled_ro * math.cos(self.angle)
            self.y = center_y + scaled_ro * math.sin(self.angle)
        else:
            px, py = self.parent.x, self.parent.y
            self.x = px + scaled_ro * math.cos(self.angle)
            self.y = py + scaled_ro * math.sin(self.angle)
        
        # print(f"[{self.name}] angle += {self.speed:.2e} => {self.angle:.4f}") # Commented out log

    # def _scale_pos(self, center_x, center_y, zoom):
    #     x = center_x + (self.x - center_x) * zoom
    #     y = center_y + (self.y - center_y) * zoom
    #     return x, y

    def draw(self, canvas, center_x, center_y, zoom=1.0):
        pixel_r = self.r * zoom * self.pixels_per_au
        if self.circle:
            canvas.coords(
                self.circle,
                self.x - pixel_r, self.y - pixel_r,
                self.x + pixel_r, self.y + pixel_r
            )
        else:
            self.circle = canvas.create_oval(
                self.x - pixel_r, self.y - pixel_r,
                self.x + pixel_r, self.y + pixel_r,
                fill=self.color
            )
    def draw_orbit(self, canvas, center_x, center_y, zoom=1.0):
        scaled_ro = self.ro * zoom * self.pixels_per_au

        if self.parent is None:
            orbit_center_x = center_x
            orbit_center_y = center_y
        else:
            orbit_center_x = self.parent.x
            orbit_center_y = self.parent.y

        canvas.create_oval(
            orbit_center_x - scaled_ro,
            orbit_center_y - scaled_ro,
            orbit_center_x + scaled_ro,
            orbit_center_y + scaled_ro,
            outline=self.color,
            dash=(2, 4),
            tags="orbit"
        )


    def draw_label(self, canvas, center_x, center_y, zoom=1.0):
        pixel_r = self.r * zoom * self.pixels_per_au
        label_x = self.x + pixel_r + 5
        label_y = self.y - pixel_r - 5

        if self.label_object:
            canvas.coords(self.label_object, label_x, label_y)
        else:
            self.label_object = canvas.create_text(
                label_x, label_y,
                text=self.label_text,
                fill="white",
                font=("Arial", 10),
                tags="label"
            )