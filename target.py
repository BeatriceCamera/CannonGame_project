from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
import random
import math

# Target Class: Represents a destructible target in the game, managing its visual appearance, dynamic movement, collision detection, and damage processing.

class Target(Widget):
    def __init__(self, game, image, pos, size, movable=True, **kwargs):
        super().__init__(**kwargs)
        # set target-specific attributes
        self.obstacle_type = "target"
        self.game = game
        self.size = size
        self.position = list(pos)
        self.initial_pos = self.position[:] 
        self.health = 3
        self.movable = movable
        # set movement velocity if the target is movable
        if self.movable:
            self.vx = random.uniform(-5, 5)
            # ensure minimum horizontal speed for noticeable movement
            if abs(self.vx) < 1: 
                self.vx = 1
            self.vy = random.uniform(-5, 5)
            # ensure minimum vertical speed for noticeable movement
            if abs(self.vy) < 1:
                self.vy = 1
        else:
            self.vx = 0
            self.vy = 0
        self.radius = 30    # define the base collision radius for the target
        # create and position the image widget that represents the target
        self.image_widget = Image(source=image, size=self.size)
        self.image_widget.center = self.position
        self.add_widget(self.image_widget)
    
    def update(self, dt):
        # only update position if the target is movable
        if self.movable:
            self.position[0] += self.vx * dt    # update horizontal position
            self.position[1] += self.vy * dt    # update vertical position
            # check horizontal boundaries; reverse direction if the target hits an edge
            if self.position[0] - self.radius <= 0 or self.position[0] + self.radius >= Window.width:
                self.vx = -self.vx
            # check vertical boundaries; reverse direction if the target hits an edge
            if self.position[1] - self.radius <= 0 or self.position[1] + self.radius >= Window.height:
                self.vy = -self.vy
        # update the image widget's center to keep it aligned with the target's logical position
        if hasattr(self, 'image_widget'):
            self.image_widget.center = self.position
    
    def collision(self, projectile):
        # retrieve the projectile's current position
        proj_x, proj_y = projectile.get_position()
        effective_radius = 40 
        # calculate the Euclidean distance between the target and the projectile
        distance = math.sqrt((proj_x - self.position[0])**2 + (proj_y - self.position[1])**2)
        # collision occurs if the distance is less than the sum of effective radii
        return distance < effective_radius + projectile.get_radius()
    
    def on_hit(self, projectile):
        # decrease the target's health by one per hit
        self.health -= 1
        # return True if health is depleted (target destroyed), else return False
        if self.health <= 0:
            return True
        return False

