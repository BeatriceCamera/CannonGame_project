# Constants module for the Cannon game
BULLET_RADIUS = 10                   # Radius of the bullet projectile (in pixels)
BOMB_RADIUS = 15                     # Base radius for the bombshell projectile
LASER_DIST = 5                       # Base distance for the laser projectile (will be overridden)

# Game field dimensions (in pixels)
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

# Frame rate (in frames per second)
FPS = 20

# Mass parameters for projectiles
BULLET_MASS = SCREEN_WIDTH / 2       # Mass of the bullet
BOMB_MASS = SCREEN_WIDTH / 3         # Mass of the bombshell

# Maximum muzzle velocities (derived from mass)
BULLET_MAX_VEL = BULLET_MASS
BOMB_MAX_VEL = BOMB_MASS 

# Projectile damage and impulse parameters
BULLET_RADIUS = SCREEN_WIDTH / 100   # Effective damage radius for bullet
BOMB_RADIUS = 50                     # Effective damage radius for bombshell

# Additional parameters for bombshell
BOMB_DRILL = 900                     # Maximum penetration (drill) distance for bombshell

# Laser parameters
LASER_VEL = 325                      # Constant speed for the laser
LASER_IMPULSE = 3                    # Duration (in seconds) the laser remains active
LASER_DIST = 1000                    # Maximum distance the laser travels
