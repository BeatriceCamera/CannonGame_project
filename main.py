import random
import math

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

import cannon_constants as const
from cannon_logic import Cannon
from projectile import Projectile
from obstacle import Obstacle
from target import Target

# Main Module

class CanGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # initialize game state variables
        self.state = "enter_nickname"
        self.nickname = ""
        self.score = 0
        self.shots_left = 10
        self.projectiles = []
        self.obstacles = []
        self.selected_projectile = "bullet"
        self.level = 1
        self.angle = 45
        self.velocity = 50
        self.cannon = None 
        self.error_label = None
        self.game_over = False
        self.paused = False

        # schedule the main update loop
        Clock.schedule_interval(self.update, 1 / 120)

        # define level backgrounds
        self.lvl_bg = {
            1: "images/1_level.jpg",
            2: "images/cannon_africa.jpg",
            3: "images/cannon_america.jpg"
        }

        # initialize the default background
        with self.canvas.before:
            self.background = Rectangle(
                source="images/choice_background.png",
                pos=self.pos, size=self.size
            )
        # bind size and position changes to update the background
        self.bind(size=self.update_background, pos=self.update_background)

        # create and add the main layout
        self.layout = FloatLayout(size=self.size)
        self.bind(size=self.resize)
        self.add_widget(self.layout)

        # create the nickname input widget
        self.nickname_input = TextInput(
            hint_text="Enter your nickname",
            size_hint=(None, None),
            size=(400, 50),
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            multiline=False
        )
        # create the continue button for nickname entry
        self.bgbutton = Button(
            background_normal="images/buttons/immagine_continue.jpg",
            size_hint=(None, None),
            size=(230, 188),
            pos_hint={"center_x": 0.5, "center_y": 0.4}
        )
        self.bgbutton.bind(on_press=self.start)

        # add widgets to the layout
        self.layout.add_widget(self.nickname_input)
        self.layout.add_widget(self.bgbutton)

        # debug
        self.deb_wid("Nickname Input", self.nickname_input)
        self.deb_wid("background Button", self.bgbutton)

        if self.cannon:
            print(f"Cannon initialized at position: {self.cannon.position}")
        else:
            print("Cannon not initialized yet.")

    def resize(self, *args):
        # update the layout size when the widget size changes
        self.layout.size = self.size

    def update_background(self, *args):
        # ensure the background covers the full widget area
        self.background.pos = self.pos
        self.background.size = self.size

# FOR THE INITIALIZATION OF THE GAME

    def start(self, instance):
        # read the nickname and trim any extra spaces
        self.nickname = self.nickname_input.text.strip()
        
        # if no nickname is provided, show an error message
        if not self.nickname:
            error_label = Label(
                text="Please, insert your nickname!",
                size_hint=(None, None),
                size=(700, 87),
                pos_hint={"center_x": 0.5, "center_y": 0.67},
                color=(1, 0, 0, 1)  
            )
            if self.error_label and self.error_label in self.layout.children:
                self.layout.remove_widget(self.error_label)
            self.error_label = error_label
            self.layout.add_widget(error_label)
            return  # stop processing if nickname is missing
        else:
            # remove any existing error label
            if self.error_label and self.error_label in self.layout.children:
                self.layout.remove_widget(self.error_label)
                self.error_label = None

            # display a welcome message
            welcome_label = Label(
                text=f"Welcome {self.nickname}!",
                size_hint=(None, None),
                size=(700, 87),
                pos_hint={"center_x": 0.5, "center_y": 0.67},
                color=(1, 1, 1, 1)
            )
            self.layout.add_widget(welcome_label)
            # proceed to game setup after a 2-second delay
            Clock.schedule_once(lambda dt: self.proceed_after_welcome(welcome_label), 2)

    def proceed_after_welcome(self, welcome_label):
        # remove the welcome label
        if welcome_label.parent:
            self.layout.remove_widget(welcome_label)

        # set state and prepare for game start
        self.state = "background"
        if self.cannon:
            self.remove_widget(self.cannon)
            self.cannon = None 
        print("Layout children before clearing:", self.layout.children)

        # update background and display the main menu
        self.background.source = "images/homescreen_background.jpg"
        self.layout.clear_widgets()

        # create and bind the main menu buttons
        self.bgbutton = Button(
            background_normal="images/buttons/play_button.png",
            size_hint=(None, None),
            size=(350, 185),
            pos_hint={"center_x": 0.5, "center_y": 0.2}
        )
        self.bgbutton.bind(on_press=self.go_to_projectile_screen)

        self.hofbutton = Button(
            background_normal="images/buttons/immagine_hof copia 2.jpeg",
            size_hint=(None, None),
            size=(200, 54),
            pos_hint={"center_x": 0.9, "center_y": 0.9}
        )
        self.hofbutton.bind(on_press=self.show_hall_of_fame)

        self.help_button = Button(
            background_normal="images/buttons/help_button.jpeg",
            size_hint=(None, None),
            size=(200, 55),
            pos_hint={"center_x": 0.1, "center_y": 0.9}
        )
        self.help_button.bind(on_press=self.helpscreenshow)

        self.layout.add_widget(self.hofbutton)
        self.layout.add_widget(self.help_button)
        self.layout.add_widget(self.bgbutton)

    def init_game(self, instance=None):
        # initialize game level; update background and state accordingly
        print(f"backgrounding level {self.level}!")
        self.state = f"level_{self.level}"

        if hasattr(self, 'background'):
            self.background.source = self.lvl_bg.get(self.level, "")
        else:
            with self.canvas.before:
                self.background = Rectangle(
                    source=self.lvl_bg.get(self.level, ""),
                    pos=self.pos,
                    size=self.size
                )
            self.bind(size=self.update_background, pos=self.update_background)

        self.layout.clear_widgets()

        # initialize the cannon if not present
        if not self.cannon:
            self.cannon = Cannon(position=[100, 150], angle=45)
            self.add_widget(self.cannon)
            print(f"Cannon initialized at position: {self.cannon.position}")

        self.cannon.position = [100, 190]
        self.cannon.angle = 45

        # generate obstacles for the current level
        self.initialize_obstacles()

        # draw the score background and label
        with self.canvas.before:
            Color(0.74, 0.53, 0.33, 1)  
            self.score_background = Rectangle(
                size=(360, 50), 
                pos=(self.width * 0.005, self.height * 0.94)
            )

        self.score_text = f"Score: {self.score}   Shots Left: {self.shots_left}"
        self.score_label = Label(
            text=self.score_text,
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"x": 0.05, "top": 0.98},
            halign="left",
            valign="middle",
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.score_label)

        # display a label for current angle and velocity (color changes based on level)
        if self.level == 1:
            param_color = (1, 1, 1, 1)
        else:
            param_color = (0, 0, 0, 1)
        self.param_label = Label(
            text=f"Angle: {self.cannon.get_angle()}\nVelocity: {self.velocity}",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"center_x": 0.065, "top": 0.91},
            color=param_color,
        )
        self.layout.add_widget(self.param_label)

        # create and add pause and help buttons
        self.pause_button = Button(
            background_normal="images/buttons/immagine_select.jpg",
            size_hint=(None, None),
            size=(200, 55),
            pos_hint={"center_x": 0.9, "center_y": 0.89}
        ) 
        self.pause_button.bind(on_press=self.toggle_pause)
        self.layout.add_widget(self.pause_button)

        self.help_button = Button(
            background_normal="images/buttons/help_button.jpeg",
            size_hint=(None, None),
            size=(200, 55),
            pos_hint={"center_x": 0.9, "center_y": 0.96}
        )
        self.help_button.bind(on_press=self.helpscreenshow)
        self.layout.add_widget(self.help_button)

        # create reset and trajectory preview buttons
        self.reset_button = Button(
            background_normal="images/buttons/immagine_reset.jpg",
            size_hint=(None, None),
            size=(200, 55),
            pos_hint={"center_x": 0.9, "center_y": 0.82}
        )
        self.reset_button.bind(on_press=self.reset_level)
        self.layout.add_widget(self.reset_button)

        self.trajectory_button = Button(
            background_normal="images/buttons/Immagine_traj.jpeg",
            size_hint=(None, None),
            size=(200, 55),
            pos_hint={"center_x": 0.9, "center_y": 0.75}
        )
        self.trajectory_button.bind(on_press=lambda instance: self.show_trajectory())
        self.layout.add_widget(self.trajectory_button)

        # store the base score at level start for resets
        self.level_base_score = self.score

        Clock.schedule_interval(self.update, 1 / 120)

    def deb_wid(self, name, widget):
        # debug helper to print widget properties
        print(f"{name} - Size: {widget.size}, Pos: {widget.pos}, Size Hint: {widget.size_hint}, Pos Hint: {widget.pos_hint}")

# RESTART AND RESET METHODS

    def restart(self, popup):
        # dismiss the game over popup and restart the game completely.
        if popup:
            popup.dismiss()
            print("Game over popup dismissed.")
        else:
            print("No popup instance provided to restart().")

        if hasattr(self, 'last_proj_event') and self.last_proj_event is not None:
            self.last_proj_event.cancel()
            self.last_proj_event = None
        self.last_proj_check = False
        self.game_over = False
        
        # schedule the rest of the restart process after a short delay (0.1 seconds)
        Clock.schedule_once(lambda dt: self._do_restart(), 0.1)

    def reset_level(self, instance):
        # Reset positions for obstacles that are not "rock" or "target"
        for obstacle in self.obstacles:
            if obstacle.obstacle_type not in ["rock", "target"] and hasattr(obstacle, 'initial_pos'):
                obstacle.pos = obstacle.initial_pos[:]            
                obstacle.position = obstacle.initial_pos[:]         

        # remove and recreate obstacles of type "rock" (non-scoring obstacles)
        rocks_to_remove = [obs for obs in self.obstacles if obs.obstacle_type == "rock"]
        for rock in rocks_to_remove:
            if rock in self.obstacles:
                self.obstacles.remove(rock)
            if rock.parent:
                rock.parent.remove_widget(rock)
        if hasattr(self, 'initial_rock_data'):
            for pos, size in self.initial_rock_data:
                new_rock = Obstacle("rock", self, image="images/small_images/immagineghianda.png", pos=pos, size=size)
                new_rock.initial_pos = pos[:]      
                new_rock.position = pos[:]         
                new_rock.pos = (pos[0] - size[0] // 2, pos[1] - size[1] // 2)
                self.obstacles.append(new_rock)
                self.layout.add_widget(new_rock)
                if new_rock.parent is None:
                    self.layout.add_widget(new_rock)

        # remove and recreate obstacles of type "target" (scoring targets)
        targets_to_remove = [obs for obs in self.obstacles if obs.obstacle_type == "target"]
        for target in targets_to_remove:
            if target in self.obstacles:
                self.obstacles.remove(target)
            if target.parent:
                target.parent.remove_widget(target)
        if hasattr(self, 'initial_target_data'):
            for pos, size in self.initial_target_data:
                new_target = Target(self, image="images/small_images/cursor_image.png", pos=pos, size=size, movable=True)
                self.obstacles.append(new_target)
                self.layout.add_widget(new_target)
                if new_target.parent is None:
                    self.layout.add_widget(new_target)

        # reset projectiles and adjust score based on the level's base score minus penalty
        self.shots_left = 10
        self.score = self.level_base_score - 15
        self.level_base_score = self.score  
        self.score_label.text = f"Score: {self.score}   Shots Left: {self.shots_left}"

        # Display a temporary penalty label
        penalty_color = (0, 0, 0, 1) if self.level > 1 else (1, 1, 1, 1)
        penalty_label = Label(
            text="As a penalty, 15 points have been removed.",
            size_hint=(None, None),
            size=(400, 50),
            pos_hint={"center_x": 0.5, "top": 0.85},
            color=penalty_color,
            font_size='20sp'
        )
        self.layout.add_widget(penalty_label)
        Clock.schedule_once(lambda dt: self.layout.remove_widget(penalty_label), 3)

    def _do_restart(self):
        # reset game state (except nickname) and show a welcome message before returning to the main menu
        self.clear_widgets()
        self.canvas.before.clear()
        self.projectiles = []
        self.obstacles = []
        self.cannon = None
        self.score = 0
        self.shots_left = 10
        self.game_over = False  
        self.level = 1         
        self.state = "restart" 
        with self.canvas.before:
            self.background = Rectangle(
                source="images/choice_background.png",
                pos=self.pos,
                size=self.size
            )
        self.bind(size=self.update_background, pos=self.update_background)
        self.layout = FloatLayout(size=self.size)
        self.bind(size=self.resize)
        self.add_widget(self.layout)

        # create a welcome label using the stored nickname
        from kivy.uix.label import Label
        welcome_label = Label(
            text=f"Here we are again {self.nickname}, good luck!",
            size_hint=(None, None),
            size=(400, 100),
            pos_hint={"center_x": 0.5, "center_y": 0.30},
            font_size='28sp',
            color=(1, 1, 1, 1)
        )
        self.layout.add_widget(welcome_label)
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.proceed(welcome_label), 3)

    def proceed(self, welcome_label):
        # remove the welcome label and display the main menu
        if welcome_label.parent:
            self.layout.remove_widget(welcome_label)
        self.show_main_menu()

    def show_main_menu(self):
        # display the main menu with Play, Hall of Fame, and Help buttons
        self.background.source = "images/homescreen_background.jpg"
        self.layout.clear_widgets()

        # create the Play, Hall fo fame and Help buttons
        self.bgbutton = Button(
            background_normal="images/buttons/play_button.png",
            size_hint=(None, None),
            size=(350, 185),
            pos_hint={"center_x": 0.5, "center_y": 0.2}
        )
        self.bgbutton.bind(on_press=self.go_to_projectile_screen)

        self.hofbutton = Button(
            background_normal="images/buttons/immagine_hof copia 2.jpeg",
            size_hint=(None, None),
            size=(200, 54),
            pos_hint={"center_x": 0.9, "center_y": 0.9}
        )
        self.hofbutton.bind(on_press=self.show_hall_of_fame)

        self.help_button = Button(
            background_normal="images/buttons/help_button.jpeg",
            size_hint=(None, None),
            size=(200, 55),
            pos_hint={"center_x": 0.1, "center_y": 0.9}
        )
        self.help_button.bind(on_press=self.helpscreenshow)

        self.layout.add_widget(self.hofbutton)
        self.layout.add_widget(self.help_button)
        self.layout.add_widget(self.bgbutton)

# PROJECTILE SELECTION AND SHOOTING

    def go_to_projectile_screen(self, instance):
        # display the projectile selection screen
        self.state = "choose_projectile"
        self.layout.clear_widgets()
        self.background.source = "images/trajectory_choice.jpg"

        # create bullet, bomb and laser's selection buttons 
        self.bullet_button = Button(
            background_normal="images/buttons/immagine_bullet.jpeg",
            size_hint=(None, None),
            size=(350, 285),
            pos_hint={"center_x": 0.2, "center_y": 0.4}
        )
        self.bullet_button.bind(on_press=lambda x: self.sel_proj("bullet"))

        self.bombshell_button = Button(
            background_normal="images/buttons/immagine_bomb.jpg",
            size_hint=(None, None),
            size=(350, 285),
            pos_hint={"center_x": 0.5, "center_y": 0.4}
        )
        self.bombshell_button.bind(on_press=lambda x: self.sel_proj("bombshell"))

        self.laser_button = Button(
            background_normal="images/buttons/immagine_laser.jpeg",
            size_hint=(None, None),
            size=(350, 285),
            pos_hint={"center_x": 0.8, "center_y": 0.4}
        )
        self.laser_button.bind(on_press=lambda x: self.sel_proj("laser"))

        self.layout.add_widget(self.bullet_button)
        self.layout.add_widget(self.bombshell_button)
        self.layout.add_widget(self.laser_button)
        print("Projectile screen initialized with buttons for Bullet, Bombshell, and Laser.")

    def sel_proj(self, projectile_type):
        # set the selected projectile type and initialize or resume the game accordingly
        self.selected_projectile = projectile_type
        print("Projectile selected:", projectile_type, "in state:", self.state)
        if self.state.startswith("level_") and self.paused:
            self.resume_game()
        elif self.state == "choose_projectile":
            self.layout.clear_widgets()
            self.init_game()

    def resume_game(self):
        # resume the game from the pause state
        if self.paused:
            self.paused = False
            Clock.schedule_interval(self.update, 1/120)
            if hasattr(self, 'pause_overlay') and self.pause_overlay:
                self.remove_widget(self.pause_overlay)
                self.pause_overlay = None
            print("Game resumed with projectile:", self.selected_projectile)

    def shoot_projectile(self):
        # fire a projectile from the cannon if shots remain
        if self.shots_left <= 0:
            print("No shots left! Game over.")
            self.finished()
            return
        tip_position = self.cannon.get_tip_position()
        print(f"Launching projectile from {tip_position}")
        projectile = Projectile(
            projectile_type=self.selected_projectile,
            start_position=tip_position
        )
        projectile.launch(
            angle=self.cannon.get_angle(),
            power=self.velocity
        )
        self.projectiles.append(projectile)
        self.add_widget(projectile)
        self.shots_left -= 1
        print(f"Shots left: {self.shots_left}")
        if self.shots_left == 0:
            print("No shots remaining!")
    
# OBSTACLES GENERALIZATION AND COLLISION HANDLING

    def initialize_obstacles(self):
        # generate obstacles for the current level based on level-specific configuration
        self.obstacles = []
        self.projectiles = []

        if self.level == 1:
            num_targets = 4
            num_rocks = 3
            num_perpetio = 3
            num_mirrors = 0
            num_wormholes = 0
        elif self.level == 2:
            num_targets = 5
            num_rocks = 3
            num_perpetio = 3
            num_mirrors = 2
            num_wormholes = 0
        elif self.level == 3:
            num_targets = 6
            num_rocks = 3
            num_perpetio = 2
            num_mirrors = 2
            num_wormholes = 2  # One pair of wormholes
        else:
            num_rocks = 3
            num_targets = 6
            num_perpetio = 2
            num_mirrors = 2
            num_wormholes = 2

        screen_padding = 50

        def get_random_position():
            return [
                random.randint(screen_padding, const.SCREEN_WIDTH - screen_padding),
                random.randint(screen_padding, const.SCREEN_HEIGHT - screen_padding)
            ]
        
        def get_valid_target_position(self, min_distance=400, min_separation=200):
            while True:
                x = random.randint(100, const.SCREEN_WIDTH - 100)
                y = random.randint(100, const.SCREEN_HEIGHT - 100)
                distance = math.sqrt((x - 100) ** 2 + (y - 190) ** 2)
                if distance < min_distance:
                    continue
            
                too_close = any(math.sqrt((x - t.position[0]) ** 2 + (y - t.position[1]) ** 2) < min_separation for t in self.obstacles if isinstance(t, Target))
                if not too_close:
                    return [x, y]
        
        # create targets
        for _ in range(num_targets):
            target = Target(self, image="images/small_images/cursor_image.png", 
                            pos=get_valid_target_position(self), size=(80, 80), movable=True)
            if target.parent is None:
                self.layout.add_widget(target)
            self.obstacles.append(target)

        # create wormholes in pairs
        for _ in range(num_wormholes // 2):
            wormhole1 = Obstacle("wormhole", self, image="images/small_images/immagine_wormhole.png",
                                pos=get_random_position(), size=(50, 100))
            wormhole1.initial_pos = wormhole1.position[:]  
            wormhole2 = Obstacle("wormhole", self, image="images/small_images/immagine_wormhole.png",
                                pos=get_random_position(), size=(50, 100))
            wormhole2.initial_pos = wormhole2.position[:]
            self.obstacles.extend([wormhole1, wormhole2])

        # create mirrors
        for _ in range(num_mirrors):
            mirror = Obstacle("mirror", self, image="images/small_images/immaginespecchio.jpg",
                            pos=get_random_position(), size=(8, 100))
            mirror.initial_pos = mirror.position[:]
            self.obstacles.append(mirror)

        # create perpetio
        for _ in range(num_perpetio):
            perpetio = Obstacle("perpetio", self, image="images/small_images/immaginefarfalla.png",
                                pos=get_random_position(), size=(80, 80))
            perpetio.initial_pos = perpetio.position[:]
            self.obstacles.append(perpetio)

        # create rocks
        for _ in range(num_rocks):
            rock = Obstacle("rock", self, image="images/small_images/immagineghianda.png",
                            pos=get_random_position(), size=(80, 80))
            rock.initial_pos = rock.position[:]  
            self.obstacles.append(rock)

        # add every generated obstacle to the layout
        for obstacle in self.obstacles:
            if obstacle.parent is None:
                self.layout.add_widget(obstacle)

        # save initial rocks and target data for resets
        self.initial_rock_data = [(rock.initial_pos, rock.size)
                                for rock in self.obstacles if rock.obstacle_type == "rock"]
        self.initial_target_data = [(obs.initial_pos, obs.size) 
                                for obs in self.obstacles if obs.obstacle_type == "target"]

        print(f"Obstacles initialized for level {self.level}: {num_targets} targets, {num_rocks} rocks, {num_wormholes} wormholes, {num_mirrors} mirrors, {num_perpetio} perpetios.")

    def handle_collisions(self):
        # process collisions between projectiles and obstacles
        for obstacle in self.obstacles[:]:
            for projectile in self.projectiles[:]:
                if obstacle.collision(projectile):
                    # wormhole logic: teleport the projectile using the paired wormhole
                    if obstacle.obstacle_type == "wormhole" and not projectile.just_teleported:
                        paired_wormhole = next(
                            (o for o in self.obstacles if o.obstacle_type == "wormhole" and o != obstacle), None
                        )
                        if paired_wormhole:
                            print(f"Paired wormhole found: {paired_wormhole}")
                            offset = paired_wormhole.radius + 10
                            exit_position = [
                                paired_wormhole.position[0] + offset,
                                paired_wormhole.position[1] + offset
                            ]
                            projectile.position = exit_position
                            projectile.image_widget.pos = (
                                exit_position[0] - projectile.radius,
                                exit_position[1] - projectile.radius
                            )
                            projectile.just_teleported = True
                            projectile.teleport_cooldown = 0.5
                            print(f"Exit position calculated: {exit_position}")
                            print(f"Projectile velocity after teleport: {projectile.velocity}")

                    # mirror logic: reflect the projectile
                    elif obstacle.obstacle_type == "mirror":
                        obstacle.projectile_reflection(projectile)
                        if projectile.projectile_type in ["bullet", "bombshell"]:
                            self.remove_projectile(projectile)

                    # perpetio logic: destroy the projectile
                    elif obstacle.obstacle_type == "perpetio":
                        print(f"{projectile.projectile_type} destroyed upon hitting perpetio.")
                        if projectile in self.projectiles:
                            projectile.remove_widget(projectile.image_widget)
                            self.projectiles.remove(projectile)

                    # on-hit logic for obstacles 
                    elif obstacle.on_hit(projectile):
                        if projectile.projectile_type == "bombshell":
                            # bombshell penetration: remove obstacles within BOMB_RADIUS of impact
                            impact_point = projectile.position
                            for obs in self.obstacles[:]:
                                dist = math.sqrt((obs.position[0] - impact_point[0])**2 +
                                                (obs.position[1] - impact_point[1])**2)
                                if dist <= const.BOMB_RADIUS:
                                    if obs.obstacle_type == "target":
                                        self.score += 10
                                    if hasattr(obs, 'image_widget'):
                                        obs.remove_widget(obs.image_widget)
                                    if obs in self.obstacles:
                                        self.obstacles.remove(obs)
                        else:
                            if obstacle.obstacle_type == "target":
                                self.score += 10
                            if hasattr(obstacle, 'image_widget'):
                                obstacle.remove_widget(obstacle.image_widget)
                            if hasattr(projectile, 'image_widget'):
                                projectile.remove_widget(projectile.image_widget)
                            if obstacle in self.obstacles:
                                self.obstacles.remove(obstacle)
                            if projectile in self.projectiles:
                                self.projectiles.remove(projectile)

        # if no targets obstacles remain, trigger the congratulations popup
        if not any(o.obstacle_type == "target" for o in self.obstacles):
            print("Congratulations! All targets destroyed.")
            if self.state != "congratulations":
                self.congrat_sc()

    def remove_projectile(self, projectile):
        # remove the projectile widget and mark it as inactive
        if hasattr(projectile, 'image_widget') and projectile.image_widget.parent:
            projectile.image_widget.parent.remove_widget(projectile.image_widget)
        if projectile in self.projectiles:
            self.projectiles.remove(projectile)
        projectile.active = False

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        # handle key presses for shooting and cannon control
        print(f"Key pressed: {key}")
        if self.state.startswith("level_"):
            if key == 32:  # Spacebar to shoot
                print("Shooting projectile")
                self.shoot_projectile()
            elif key == 275:  # Right arrow to rotate down
                print("Rotating cannon down")
                self.cannon.rotate("down")
            elif key == 276:  # Left arrow to rotate up
                print("Rotating cannon up")
                self.cannon.rotate("up")
            elif key == 273:  # Up arrow key to increase velocity
                self.velocity = min(self.velocity + 10, 100)
                print(f"Velocity increased to {self.velocity}")
            elif key == 274:  # Down arrow key to decrease velocity
                self.velocity = max(self.velocity - 10, 10)
                print(f"Velocity decreased to {self.velocity}")

# HALL OF FAME AND HELP SCREEN 

    def show_hall_of_fame(self, instance):
        # display the Hall of Fame popup with sorted entries
        try:
            with open("hall_of_fame.txt", "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = ["No Hall of Fame data found."]
        if lines and "No Hall of Fame data found." not in lines[0]:
            entries = []
            for line in lines:
                line = line.strip()
                parts = line.split(',')
                if len(parts) >= 2:
                    try:
                        score = int(parts[1].split(':')[1].strip())
                    except (IndexError, ValueError):
                        score = 0
                    entries.append((line, score))
                else:
                    entries.append((line, 0))
            # sort the entries by score descending
            entries.sort(key=lambda x: x[1], reverse=True)
            sorted_hof_data = "\n".join(entry[0] for entry in entries)
        else:
            sorted_hof_data = lines[0] if lines else "No Hall of Fame data found."
        sorted_hof_data = "\n\n" + sorted_hof_data
        
        # create a label with white text
        popup_content = Label(
            text=sorted_hof_data,
            size_hint_y=None,
            color=(1, 1, 1, 1),
            font_size='16sp',
            halign="left",
            valign="top",
            padding=(0, 100)  
        )
        popup_content.text_size = (620, None)
        popup_content.bind(texture_size=popup_content.setter('size'))
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(popup_content)
        popup = Popup(
            title="",
            content=scroll_view,
            size_hint=(None, None),
            size=(750, 938),
            separator_height=0,
            background="images/immagine_halloffame.jpeg"
        )
        popup.open()

    def save_to_hall_of_fame(self):
        # save the current player's entry to the Hall of Fame if not already present
        entry = f"Nickname: {self.nickname}, Score: {self.score}, Level: {self.level}"
        try:
            with open("hall_of_fame.txt", "r") as f:
                lines = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            lines = []
        
        if entry in lines:
            print("Duplicate entry found. Not saving to Hall of Fame.")
            return
        try:
            with open("hall_of_fame.txt", "a") as f:
                f.write(entry + "\n")
            print("Player's score saved to Hall of Fame.")
        except IOError as e:
            print(f"Failed to save to Hall of Fame: {e}")

    def helpscreenshow(self, instance):
        # display the help screen popup
        background = Image(source="images/help.jpeg", size_hint=(1, 1), allow_stretch=True, keep_ratio=True)
        help_popup = Popup(
            title="",
            content=background,
            size_hint=(0.8, 0.8),
            auto_dismiss=True,
            separator_height=0
        )
        help_popup.open()

# TRAJECTORY PREVIEW

    def show_trajectory(self):
        # if a trajectory is already being shown, do nothing
        if hasattr(self, 'traj_event') and self.traj_event:
            print("Trajectory already active, returning.")
            return

        print("Showing trajectory for level", self.level)
        
        # deduct penalty points and update the score label
        self.score -= 10
        self.score_label.text = f"Score: {self.score}   Shots Left: {self.shots_left}"

        # display a temporary penalty label
        penalty_color = (0, 0, 0, 1) if self.level >= 2 else (1, 1, 1, 1)
        penalty_label = Label(
            text="As penalty, 10 points have been removed.",
            size_hint=(None, None),
            size=(400, 50),
            pos_hint={"center_x": 0.5, "top": 0.75},
            color=penalty_color,
            font_size='20sp'
        )
        self.layout.add_widget(penalty_label)
        Clock.schedule_once(lambda dt: self.layout.remove_widget(penalty_label), 3)

        # create a countdown label and add it to the layout
        countdown_label = Label(
            text="15",  # initial countdown: 15 seconds
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={"center_x": 0.5, "top": 0.85},
            color=(1, 0, 0, 1),
            font_size='30sp'
        )
        self.layout.add_widget(countdown_label)

        # compute initial trajectory parameters based on the cannon's tip and current angle
        start_pos = self.cannon.get_tip_position()
        angle_rad = math.radians(self.cannon.get_angle())
        if self.selected_projectile == "bombshell":
            multiplier = 2
        elif self.selected_projectile == "laser":
            multiplier = 1
        else:  # bullet
            multiplier = 5
        v0 = self.velocity * multiplier
        v0x = v0 * math.cos(angle_rad)
        v0y = v0 * math.sin(angle_rad)

        # calculate t_max depending on the projectile type
        if self.selected_projectile == "bombshell":
            t_natural = 0.0
            cumulative = 0.0
            prev_point = start_pos
            step = 0.1
            while cumulative < const.BOMB_DRILL and t_natural < 10.0:
                t_natural += step
                x = start_pos[0] + v0x * t_natural
                y = start_pos[1] + v0y * t_natural - 0.5 * 9.8 * t_natural * t_natural
                current_point = (x, y)
                cumulative += math.dist(prev_point, current_point)
                prev_point = current_point
            t_max = t_natural
        elif self.selected_projectile == "laser":
            t_max = const.LASER_DIST / const.LASER_VEL
        else:  # bullet
            t_max = 100000 / abs(v0x) if abs(v0x) > 0 else 15.0

        print("Computed t_max:", t_max)
        print("Cannon tip position:", start_pos)

        # set the countdown time
        self.trajectory_time = 15.0
        countdown_label.text = str(int(self.trajectory_time))

        # ensure the trajectory widget covers the entire layout
        if not hasattr(self, 'traj_widget'):
            self.traj_widget = Widget(size=self.layout.size, pos=self.layout.pos)
        else:
            self.traj_widget.canvas.clear()
            self.traj_widget.size = self.layout.size
            self.traj_widget.pos = self.layout.pos

        # remove and re-add the trajectory widget so it sits on top
        if self.traj_widget.parent:
            self.traj_widget.parent.remove_widget(self.traj_widget)
        self.layout.add_widget(self.traj_widget)

        self.traj_segments = []

        # define the function to update the trajectory preview
        def update_trajectory(dt):
            self.traj_widget.canvas.clear()
            self.traj_segments = []
            current_start = self.cannon.get_tip_position()
            current_angle = math.radians(self.cannon.get_angle())
            if self.selected_projectile == "bombshell":
                mult = 2
            elif self.selected_projectile == "laser":
                mult = 1
            else:
                mult = 5
            current_v0 = self.velocity * mult
            current_v0x = current_v0 * math.cos(current_angle)
            current_v0y = current_v0 * math.sin(current_angle)
            t = 0.0
            step = 0.1
            traj_points = []
            while t <= t_max:
                if self.selected_projectile != "laser":
                    x = current_start[0] + current_v0x * t
                    y = current_start[1] + current_v0y * t - 0.5 * 9.8 * t * t
                else:
                    x = current_start[0] + current_v0x * t
                    y = current_start[1] + current_v0y * t
                traj_points.append((x, y))
                t += step
            print("Trajectory points count:", len(traj_points))
            dash_length_points = 5
            gap_length_points = 3
            i = 0
            line_color = (1, 1, 1, 1)
            with self.traj_widget.canvas:
                Color(*line_color)
                while i < len(traj_points) - 1:
                    seg_points = []
                    for p in traj_points[i:min(i + dash_length_points, len(traj_points))]:
                        seg_points.extend(p)
                    seg_line = Line(points=seg_points, width=1.5)
                    self.traj_segments.append(seg_line)
                    i += dash_length_points + gap_length_points
            return True

        self.traj_event = Clock.schedule_interval(update_trajectory, 0.2)

        # define the countdown update function
        def update_countdown(dt):
            self.trajectory_time -= dt
            remaining = int(max(0, self.trajectory_time))
            countdown_label.text = str(remaining)
            if self.trajectory_time <= 0:
                if self.traj_event:
                    self.traj_event.cancel()
                    self.traj_event = None
                if hasattr(self, 'traj_widget'):
                    self.traj_widget.canvas.clear()
                if countdown_label.parent:
                    self.layout.remove_widget(countdown_label)
                return False
            return True

        Clock.schedule_interval(update_countdown, 1)

# LEVEL PROGRESSION

    def next_level(self, instance=None):
        if hasattr(self, 'last_proj_event') and self.last_proj_event is not None:
            self.last_proj_event.cancel()
            self.last_proj_event = None
        # advance to the next level and reset shots
        self.level += 1
        self.shots_left = 10
        if self.level > 3:
            self.final_screen()
        else:
            self.init_game()

    def toggle_pause(self, instance):
        # toggle the pause state of the game
        if self.paused:
            self.resume_game()
        else:
            self.paused = True
            Clock.unschedule(self.update)
            self.pause_overlay = FloatLayout(size=self.size)
            with self.pause_overlay.canvas.before:
                Color(0, 0, 0, 0.6)  # Black with 60% opacity
                self.dark_rect = Rectangle(size=self.pause_overlay.size, pos=self.pause_overlay.pos)
   
            def update_rect(instance, value):
                self.dark_rect.size = instance.size
                self.dark_rect.pos = instance.pos
            self.pause_overlay.bind(size=update_rect, pos=update_rect)
            
            # create projectile selection buttons
            bullet_button = Button(
                background_normal="images/buttons/immagine_bullet.jpeg",
                size_hint=(None, None),
                size=(350, 285),
                pos_hint={"center_x": 0.2, "center_y": 0.6}
            )
            bullet_button.bind(on_press=lambda x: self.sel_proj("bullet"))
            
            bombshell_button = Button(
                background_normal="images/buttons/immagine_bomb.jpg",
                size_hint=(None, None),
                size=(350, 285),
                pos_hint={"center_x": 0.5, "center_y": 0.6}
            )
            bombshell_button.bind(on_press=lambda x: self.sel_proj("bombshell"))
            
            laser_button = Button(
                background_normal="images/buttons/immagine_laser.jpeg",
                size_hint=(None, None),
                size=(350, 285),
                pos_hint={"center_x": 0.8, "center_y": 0.6}
            )
            laser_button.bind(on_press=lambda x: self.sel_proj("laser"))
            
            # Create a resume button that simply resumes the game without changing the projectile.
            resume_button = Button(
                background_normal="images/buttons/immagine_resume.jpg",
                size_hint=(None, None),
                size=(125, 40),
                pos_hint={"center_x": 0.5, "center_y": 0.2}
            )
            resume_button.bind(on_press=lambda instance: self.resume_game())
            
            self.pause_overlay.add_widget(bullet_button)
            self.pause_overlay.add_widget(bombshell_button)
            self.pause_overlay.add_widget(laser_button)
            self.pause_overlay.add_widget(resume_button)
            
            self.add_widget(self.pause_overlay)
            print("Game paused. Shots left:", self.shots_left)

    def update_score_text(self):
        # update the score display text
        self.score_text = f"Score: {self.score}   Shots Left: {self.shots_left}"

    def update(self, dt):
        # main update loop called on a fixed interval
        if not self.state.startswith("level_"):
            return

        for obstacle in self.obstacles:
            obstacle.update(dt)

        for projectile in self.projectiles[:]:
            projectile.update(dt)
            if not projectile.is_active():
                self.projectiles.remove(projectile)

        self.handle_collisions()

        # if no shots remain and no projectiles are in flight, schedule game over check
        if self.shots_left <= 0 and not self.game_over:
            if not hasattr(self, 'last_proj_event') or self.last_proj_event is None:
                self.last_proj_event = Clock.schedule_once(self.check_last_projectile, 3)

        self.update_score_text()
        self.score_label.text = self.score_text

        if self.state.startswith("level_") and self.cannon:
            self.param_label.text = f"Angle: {self.cannon.get_angle()}\nVelocity: {self.velocity}"

    def final_screen(self):
        # display the full-screen final screen with winner entry and navigation buttons
        print("Displaying Final Screen!")
        entry = f"Nickname: {self.nickname}, Score: {self.score}, WINNER"
        try:
            with open("hall_of_fame.txt", "a") as f:
                f.write(entry + "\n")
            print("Winner entry saved to Hall of Fame.")
        except IOError as e:
            print(f"Failed to save winner entry: {e}")

        popup_content = FloatLayout(size=self.size)

        buttons_layout = BoxLayout(
            orientation="horizontal",
            spacing=100,               
            size_hint=(None, None),
            size=(500, 60)           
        )
        buttons_layout.pos_hint = {"center_x": 0.5, "y": 0.15}

        hof_button = Button(
            background_normal="images/buttons/immagine_hof copia 2.jpeg",
            size_hint=(None, None),
            size=(200, 54)
        )
        hof_button.bind(on_press=self.show_hall_of_fame)
        
        shutdown_button = Button(
            background_normal="images/buttons/immagine_shutdown.jpg",
            size_hint=(None, None),
            size=(200, 51)
        )
        shutdown_button.bind(on_press=lambda instance: self.shutdown())
        
        buttons_layout.add_widget(hof_button)
        buttons_layout.add_widget(shutdown_button)
        popup_content.add_widget(buttons_layout)
        
        popup = Popup(
            title="",
            content=popup_content,
            size_hint=(1, 1),
            separator_height=0,
            background="images/final_image.jpg"
        )
        popup.open()

    def finished(self):
        # trigger the game over sequence and display the Game Over popup
        print("Game Over! You ran out of shots.")
        Clock.unschedule(self.update)
        self.save_to_hall_of_fame()
        popup_width, popup_height = 450, 468

        popup_content = FloatLayout(size=(popup_width, popup_height))

        buttons_layout = BoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint=(None, None),
            size=(200 * 3 + 10 * 2, 51)  
        )
        buttons_layout.pos_hint = {"center_x": 0.5, "y": 0.05}
        
        restart_button = Button(
            background_normal="images/buttons/immagine_restart copia.jpg",
            size_hint=(None, None),
            size=(200, 51)
        )
        restart_button.bind(on_press=lambda instance: self.restart(popup))
        
        shutdown_button = Button(
            background_normal="images/buttons/immagine_shutdown.jpg",
            size_hint=(None, None),
            size=(200, 51)
        )
        shutdown_button.bind(on_press=lambda instance: self.shutdown())
    
        hof_button = Button(
            background_normal="images/buttons/immagine_hof copia 2.jpeg",
            size_hint=(None, None),
            size=(200, 51)
        )
        hof_button.bind(on_press=self.show_hall_of_fame)
        
        buttons_layout.add_widget(restart_button)
        buttons_layout.add_widget(shutdown_button)
        buttons_layout.add_widget(hof_button)
        
        popup_content.add_widget(buttons_layout)

        popup = Popup(
            title="",
            content=popup_content,
            size_hint=(None, None),
            size=(popup_width, popup_height),
            separator_height=0,
            background="images/gameover.png"
        )
        popup.open()

    def check_last_projectile(self, dt):
        if self.state.startswith("level_") and len(self.projectiles) == 0 and any(o.obstacle_type == "target" for o in self.obstacles):
            self.game_over = True
            self.finished()
        self.last_proj_event = None

    def congrat_sc(self):
        # display the Congratulations popup and automatically proceed to the next level
        print("Displaying Congratulations Screen")
        self.state = "congratulations"
        # remove any residual projectiles
        for p in self.projectiles[:]:
            self.remove_projectile(p)
        self.projectiles = []
        popup_width, popup_height = 450, 468

        popup_content = FloatLayout(size=(popup_width, popup_height))

        next_button = Button(
            background_normal="images/buttons/hall_button.png",
            size_hint=(None, None),
            size=(90, 72),
            pos_hint={"center_x": 0.5, "y": 0.05}
        )
        def on_next(instance):
            popup.dismiss()         
            self.next_level()       
        next_button.bind(on_press=on_next)
        popup_content.add_widget(next_button)

        popup = Popup(
            title="",
            content=popup_content,
            size_hint=(None, None),
            size=(popup_width, popup_height),
            separator_height=0,
            background="images/congr.png"
        )
        popup.open()

class scores(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.size = (200, 50)
        self.pos_hint = {"x": 0, "y": 0.9}  
        self.padding = [10, 5, 10, 5]

        with self.canvas.before:
            Color(0, 0, 0, 0.5)  
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.label = Label(
            text=f"Score: 0   Shots Left: 10",  
            color=(1, 1, 1, 1),  
        )
        self.add_widget(self.label)

    def update_text(self, score, shots_left):
        # update the score and remaining shots display
        self.label.text = f"Score: {score}   Shots Left: {shots_left}"
        self.bg.size = self.size
        self.bg.pos = self.pos

   
class CannonApp(App):
    def build(self):
        game = CanGame()
        game.size = (const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        from kivy.core.window import Window
        Window.bind(on_key_down=game.on_key_down)  # bind key events globally
        return game

if __name__ == "__main__":
    print(" Cannon Game...")
    CannonApp().run()




