import math
from kivy.uix.widget import Widget
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Rectangle

# Cannon Class: Responsible for rendering and controlling the cannon's rotation and projectile launch position


class Cannon(Widget):
    def __init__(self, position, angle=30, **kwargs):
        super().__init__(**kwargs)
        self.position = position    # logical center position of the cannon
        self.angle = angle          # initial rotation angle (in degrees)
        self.barrel_length = 60     # length of the cannon barrel

        # set up the cannon image with rotation transformation
        with self.canvas:
            PushMatrix()
            self.rotation = Rotate(angle=self.angle, origin=self.position)  # rotation transformation
            self.image = Rectangle(
                source="images/small_images/cannon_widget.png",
                size=(170, 128),                                            # dimensions of the cannon image
                pos=(self.position[0] - 50, self.position[1] - 25)          # position adjusted to center the image
            )
            PopMatrix()

    def rotate(self, direction):
        # adjusts the cannon's angle based on the given direction and updates its rotation. :param direction: "up" to increase the angle; "down" to decrease the angle.
        if direction == "up":
            self.angle = min(self.angle + 5, 360)  # increase angle; upper limit is 360°
        elif direction == "down":
            self.angle = max(self.angle - 5, -90)  # decrease angle; lower limit is -90°

        # update the rotation transformation and request a redraw
        self.rotation.angle = self.angle
        self.canvas.ask_update()
        print(f"Cannon rotated to angle: {self.angle}")

    def get_angle(self):
        # returns the current rotation angle of the cannon. :return: Current angle in degrees.
        return self.angle

    def get_tip_position(self):
        # calculates and returns the position of the cannon barrel's tip. This position is used as the starting point for projectiles. :return: A list [tip_x, tip_y] representing the tip position.
        radian_angle = math.radians(self.angle)
        tip_x = self.position[0] + math.cos(radian_angle) * (self.barrel_length + 10)  # adjusted length
        tip_y = self.position[1] + math.sin(radian_angle) * (self.barrel_length + 10)  # adjusted length
        return [tip_x, tip_y]
