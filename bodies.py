import math

class CelestialBody:
    def __init__(self, name, ro, r, speed, color, parent=None):
        self.name = name
        self.ro = ro
        self.r = r
        self.speed = speed
        self.color = color
        self.parent = parent
        self.angle = 0
        self.x = 0
        self.y = 0
        self.circle = None
        self.cooldown = 0
        self.label_object = None
        self.label_text = name

    def update_position(self, center_x, center_y):
        self.angle += self.speed
        self.angle %= 2 * math.pi

        if self.parent is None:
            self.x = center_x + self.ro * math.cos(self.angle)
            self.y = center_y + self.ro * math.sin(self.angle)
        else:
            px, py = self.parent.x, self.parent.y
            self.x = px + self.ro * math.cos(self.angle)
            self.y = py + self.ro * math.sin(self.angle)

    def _scale_pos(self, center_x, center_y, zoom):
        x = center_x + (self.x - center_x) * zoom
        y = center_y + (self.y - center_y) * zoom
        return x, y

    def draw(self, canvas, center_x, center_y, zoom=1.0):
        x, y = self._scale_pos(center_x, center_y, zoom)
        r = self.r * zoom

        if self.circle:
            canvas.coords(self.circle, x - r, y - r, x + r, y + r)
        else:
            self.circle = canvas.create_oval(x - r, y - r, x + r, y + r, fill=self.color)

    def draw_orbit(self, canvas, center_x, center_y, zoom=1.0):
        if self.parent is None:
            orbit_center_x, orbit_center_y = center_x, center_y
        else:
            orbit_center_x = center_x + (self.parent.x - center_x) * zoom
            orbit_center_y = center_y + (self.parent.y - center_y) * zoom

        ro = self.ro * zoom

        canvas.create_oval(
            orbit_center_x - ro,
            orbit_center_y - ro,
            orbit_center_x + ro,
            orbit_center_y + ro,
            outline=self.color,
            dash=(2, 4),
            tags="orbit"
        )


    def draw_label(self, canvas, center_x, center_y, zoom=1.0):
        x, y = self._scale_pos(center_x, center_y, zoom)
        r = self.r * zoom

        if self.label_object:
            canvas.coords(self.label_object, x + r + 5, y - r - 5)
        else:
            self.label_object = canvas.create_text(
                x + r + 5, y - r - 5,
                text=self.label_text,
                fill="white",
                font=("Arial", 10),
                tags="label"
            )
