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
