import math
from kivy.uix.widget import Widget
from kivy.uix.image import Image
import cannon_constants as const
from kivy.clock import Clock

# Projectile Class: Handles the behavior of different projectile types

class Projectile(Widget):
    def __init__(self, projectile_type, start_position, **kwargs):
        super().__init__(**kwargs)

        # initialize projectile type and state variables
        self.projectile_type = projectile_type
        self.position = list(start_position) 
        self.velocity = [0, 0]
        self.active = True
        self.just_teleported = False
        self.teleport_cooldown = 0.0

        # configure projectile parameters based on its type
        if self.projectile_type == "bullet":
            self.radius = const.BULLET_RADIUS
            self.image_source = "images/small_images/bullet_widget.png"
            self.size = (40, 70)
        elif self.projectile_type == "bombshell":
            # bombshell projectiles are heavier and penetrate obstacles
            self.radius = const.BOMB_RADIUS
            self.image_source = "images/small_images/bombshell_widget.png"
            self.size = (30, 42)
            self.bomb_mass = const.BOMB_MASS
            self.bomb_drill_remaining = const.BOMB_DRILL    # penetration distance remaining
        elif self.projectile_type == "laser":
            # laser projectiles ignore gravity and use constant speed
            self.size = (100, 100)
            self.radius = self.size[0] // 2     # center-based radius
            self.image_source = "images/small_images/laser_widget.png"
            self.laser_timer = const.LASER_IMPULSE      # duration for which the laser remains active
            self.laser_traveled_distance = 0
            self.laser_start_position = list(self.position)

        # create the image widget to represent the projectile and center it
        self.image_widget = Image(
            source=self.image_source,
            size=self.size,
            pos=(self.position[0] - self.size[0] // 2,
                 self.position[1] - self.size[1] // 2)
        )
        self.add_widget(self.image_widget)

    def launch(self, angle, power):
        radian_angle = math.radians(angle)
        if self.projectile_type == "laser":
            # for lasers, ignore 'power' and use a fixed speed
            self.velocity = [
                const.LASER_VEL * math.cos(radian_angle),
                const.LASER_VEL * math.sin(radian_angle)
            ]
        elif self.projectile_type == "bombshell":
            # bombshells use a lower multiplier to simulate greater mass
            self.velocity = [
                power * math.cos(radian_angle) * 2,  
                power * math.sin(radian_angle) * 2
            ]
        else:
            # bullets use the standard multiplier
            self.velocity = [
                power * math.cos(radian_angle) * 5,
                power * math.sin(radian_angle) * 5
            ]
        print(f"Projectile launched with velocity: {self.velocity}")

    def update(self, dt):
        # update the projectile's position and check for removal conditions
        if not self.active:
            return

        # process teleport cooldown
        if self.just_teleported:
            self.teleport_cooldown -= dt
            if self.teleport_cooldown <= 0:
                self.just_teleported = False

        # save current position for distance calculations
        old_position = list(self.position)

        # apply gravity to non-laser projectiles
        if self.projectile_type != "laser":
            gravity = 9.8
            self.velocity[1] -= gravity * dt
        else:
            self.laser_timer -= dt

        # update logical position based on velocity
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt

        # calculate distance traveled during this update
        dx = self.position[0] - old_position[0]
        dy = self.position[1] - old_position[1]
        distance_moved = math.sqrt(dx * dx + dy * dy)

        # for laser: update traveled distance and check if it should be removed
        if self.projectile_type == "laser":
            self.laser_traveled_distance += distance_moved
            if self.laser_timer <= 0 or self.laser_traveled_distance >= const.LASER_DIST:
                self.remove_projectile()
                return
        # for bombshell: decrement the penetration distance remaining
        elif self.projectile_type == "bombshell":
            self.bomb_drill_remaining -= distance_moved
            if self.bomb_drill_remaining <= 0:
                self.remove_projectile()
                return

        # remove projectile if it exits the extended game area
        extended_margin = 1000
        if (self.position[0] + self.radius < -extended_margin or 
            self.position[0] - self.radius > const.SCREEN_WIDTH + extended_margin or
            self.position[1] + self.radius < -extended_margin or 
            self.position[1] - self.radius > const.SCREEN_HEIGHT + extended_margin):
            self.remove_projectile()
            return

        # update the image widget's position to keep it centered on the logical position
        if self.active and hasattr(self, 'image_widget'):
            self.image_widget.pos = (
                self.position[0] - self.size[0] // 2,
                self.position[1] - self.size[1] // 2
            )

    def is_active(self):
        # return whether the projectile is currently active
        return self.active

    def get_position(self):
        # return the current logical position of the projectile
        return self.position

    def get_radius(self):
        # return the effective collision radius of the projectile
        return self.radius

    def remove_projectile(self):
        # remove the projectile widget from its parent and mark it as inactive
        if self.parent:
            self.parent.remove_widget(self)
        self.active = False
