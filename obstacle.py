from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
import math
import random
import cannon_constants as const
from kivy.graphics import Color, Ellipse

# Obstacle Class: Manages obstacle properties, movement, collision detection, and interactions with projectiles

class Obstacle(Widget):
    def __init__(self, obstacle_type, game, image=None, movable=True, **kwargs):
        super().__init__(**kwargs)
        # initialize obstacle properties
        self.obstacle_type = obstacle_type
        self.radius = 30
        self.game = game
        self.movable = movable

        # compute the logical center position of the obstacle
        self.position = [
            random.randint(const.SCREEN_WIDTH // 2, const.SCREEN_WIDTH - self.radius * 2),
            random.randint(150, const.SCREEN_HEIGHT // 2)
        ]
        # save the initial position for later resets
        self.initial_pos = self.position[:] 

        # set initial velocity if the obstacle is mobile
        self.vx = random.uniform(-5, 5) if self.movable else 0
        self.vy = random.uniform(-5, 5) if self.movable else 0
        print(f"Obstacle initialized with velocity: vx={self.vx}, vy={self.vy}")

        # set health: rocks are destructible; perpetio are indestructible.
        if obstacle_type in ["target", "rock"]:
            self.health = 3
        else:
            self.health = None

        # Create and position the image widget so that its center aligns with the logical position
        self.image_widget = Image(
            source=image,
            size=self.size
        )
        self.image_widget.center = self.position
        self.add_widget(self.image_widget)

    def update(self, dt):
        # update the obstacle's logical position based on its velocity and re-center the image widget accordingly. Also handle bouncing off window edges
        # update logical position
        self.position[0] += self.vx * dt
        self.position[1] += self.vy * dt

        # bounce off window edges
        from kivy.core.window import Window
        if self.position[0] - self.radius <= 0 or self.position[0] + self.radius >= Window.width:
            self.vx = -self.vx
        if self.position[1] - self.radius <= 0 or self.position[1] + self.radius >= Window.height:
            self.vy = -self.vy

        # re-center the image widget on the updated position
        if hasattr(self, 'image_widget'):
            self.image_widget.center = self.position

    def collision(self, projectile):
        # Determine if a projectile collides with this obstacle. Uses an effective radius (larger for rocks) plus the projectile's radius.
        proj_x, proj_y = projectile.get_position()
        effective_radius = self.radius
        distance = math.sqrt((proj_x - self.position[0]) ** 2 + (proj_y - self.position[1]) ** 2)
        return distance < effective_radius + projectile.get_radius()

    def on_hit(self, projectile):
        # Process a hit on this obstacle. Rocks lose health and are removed when health reaches zero. Other types (like perpetio) cannot be destroyed.
        if self.obstacle_type == 'rock':
            self.health -= 1
            if self.health <= 0:
                return True
        return False

    def projectile_reflection(self, projectile):
        # Reflect a projectile when it hits a mirror. Bullets and bombshells are removed upon impact; lasers are reflected by inverting their velocity.
        if self.obstacle_type == "mirror":
            if projectile.projectile_type in ["bullet", "bombshell"]:
                if hasattr(projectile, 'image_widget') and projectile.image_widget.parent:
                    projectile.image_widget.parent.remove_widget(projectile.image_widget)
                projectile.active = False  # Mark as inactive to remove from updates
                print(f"{projectile.projectile_type.capitalize()} disappeared upon hitting the mirror!")
            elif projectile.projectile_type == "laser":
                projectile.velocity[0] = -projectile.velocity[0]
                projectile.velocity[1] = -projectile.velocity[1]
                print("Laser reflected by the mirror!")

