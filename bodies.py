import math

class CelestialBody:
    def __init__(self, name, ro, r, speed, color, parent=None):
        self.name = name
        self.ro = ro              # orbit radius
        self.r = r                # radius
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

    def draw(self, canvas):
        if self.circle:
            canvas.coords(self.circle,
                          self.x - self.r, self.y - self.r,
                          self.x + self.r, self.y + self.r)
        else:
            self.circle = canvas.create_oval(
                self.x - self.r, self.y - self.r,
                self.x + self.r, self.y + self.r,
                fill=self.color
            )

    def draw_orbit(self, canvas, center_x, center_y):
        if self.parent is None:
          orbit_center_x = center_x
          orbit_center_y = center_y
        else:
            orbit_center_x = self.parent.x
            orbit_center_y = self.parent.y

        canvas.create_oval(
            orbit_center_x - self.ro,
            orbit_center_y - self.ro,
            orbit_center_x + self.ro,
            orbit_center_y + self.ro,
            outline=self.color,
            dash=(2, 4),
            tags="orbit"
        )
        
    def draw_label(self, canvas):
        if self.label_object:
            canvas.coords(
                self.label_object,
                self.x + self.r + 5, self.y - self.r - 5
            )
        else:
            self.label_object = canvas.create_text(
                self.x + self.r + 5, self.y - self.r - 5,
                text=self.label_text,
                fill="white",
                font=("Arial", 10),
                tags="label"
            )

