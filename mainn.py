import random
import math
import json
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Line
from math import radians, cos, sin
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.animation import Animation
from kivy.properties import NumericProperty

SCREEN_WIDTH = 1000             # pixels
SCREEN_HEIGHT = 700

BULLET_MASS = SCREEN_WIDTH/2     # Bullet parameter that affects the muzzle velocity range
BOMB_MASS  = SCREEN_WIDTH/3      # Bomb parameter that affects the muzzle velocity range
BULLET_MAX_VEL = BULLET_MASS      # Bullet maximum muzzle velocity
BOMB_MAX_VEL = BOMB_MASS        # Bombshell maximum muzzle velocity
LASER_VEL = SCREEN_WIDTH/1.5       # Laser muzzle velocity 
BULLET_RADIUS = SCREEN_WIDTH/70     # Range of the damage of bullet 
BOMB_RADIUS = SCREEN_WIDTH/50       # Range of the damage of bombshell
LASER_DIST = SCREEN_WIDTH/100      # Range of the damage of laser 
BOMB_DRILL = SCREEN_WIDTH/50       # Space travelled inside the obstacles
LASER_IMPULSE = 3

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):   # Initialize the Screen base class
        super(WelcomeScreen, self).__init__(**kwargs)

        # Create a full-window background image
        self.background = Image(
            source="background.jpg",  
            allow_stretch=True,  # Allows to scale the image to fit the widget size
            keep_ratio=False     # Ignores the original aspect ratio, filling the window entirely
        )
        self.background.size = Window.size  # Adapts image to the current window size
        self.add_widget(self.background)  # Add the background as the first widget (so everything else appears on top of it)
        
        # Title label: centered near the top of the window
        self.welcome_label = Label(         
            text="Welcome to Cannon Game!",
            font_size=62,
            color=(0, 0, 0, 1),     # Black text 
            size_hint=(None, None),    # Use absolute 'size' and 'pos' instead of layout hints
            size=(500, 100),
            pos=(Window.width // 2 - 250, Window.height - 200)    #  # Manually center horizontally and place near the top
        )
        self.add_widget(self.welcome_label)      

        # Username input
        self.username_input = TextInput(     
            hint_text="Enter your username",
            size_hint=(None, None),
            size=(300, 40),
            pos=(Window.width // 2 - 150, Window.height // 2)
        )
        self.add_widget(self.username_input)

        # Button that starts the game flow
        self.start_button = Button(   
            text="Start",
            size_hint=(None, None),
            size=(200, 50),   
            pos=(Window.width // 2 - 100, Window.height // 2 - 60)   # Slightly below the username input 
        )
        self.start_button.bind(on_press=self.start_game)    # When pressed, call self.start_game 
        self.add_widget(self.start_button)

        # Button that navigates to the Help Screen
        self.help_button = Button(     
            text="Help",
            size_hint=(None, None),
            size=(100, 50),
            pos=(Window.width - 100, Window.height - 60)    # Top-right corner
        )
        self.help_button.bind(on_press=self.show_help)
        self.add_widget(self.help_button)

        # Button that navigates to the Hall of Fame Screen 
        self.hof_button = Button(     
            text="Hall of Fame",
            size_hint=(None, None),
            size=(150, 50),
            pos=(Window.width - 150, Window.height - 110)
        )
        self.hof_button.bind(on_press=self.show_hof)
        self.add_widget(self.hof_button)

    def start_game(self, instance):
        # Get the username from the input 
        username = self.username_input.text.strip()
        if username == "":
            username = "Anonymous"
        # Store the username on the ScreenManager so other screens can access it
        self.manager.username = username
        print(f"Starting game for {username}")       
        
        # Move to the projectile selection screen
        self.manager.current = "projectile_select" 
        
        # Reset game state on the game screen 
        game_screen = self.manager.get_screen("game")
        game_screen.reset_game() 
        game_screen.current_round = 1  # Reset rounds
        game_screen.attempt_count = 0   # Reset attempts
        game_screen.status_label.text = f"Round: {game_screen.current_round} - Attempt: {game_screen.attempt_count}/{game_screen.max_attempts}"   # Refresh the status label
        game_screen.status_label.opacity = 1  # Make the status label visible again
        game_screen.new_round()  # Generate a new target
  
    def show_hof(self, instance):   # Switch to the Hall of Fame screen 
        self.manager.current = "hall_of_fame"
    
    def show_help(self, instance):   # Switch to Help Screen 
        self.manager.previous_screen = self.name   # Remembers where we came from
        self.manager.current = "help"   # ScreenManager controls which screen is visible via 'current'


class HallOfFameScreen(Screen):
    def __init__(self, **kwargs):
        super(HallOfFameScreen, self).__init__(**kwargs)   # Initialize the base Screen 
        
        # Background image that fills the entire screen 
        self.background = Image(
            source="background.jpg",
            allow_stretch=True,   # Image scales arbitrarily
            keep_ratio=False   # Ignores aspect ratio to fully cover the window
        )
        self.background.size = Window.size   # Match the current window size
        self.add_widget(self.background)   # Add the background first 

        # Title: big bold title centered near the top
        title_label = Label(
            text="HALL OF FAME",
            font_size=40,
            bold=True,
            color=(0, 0, 0, 1),  # Black Text
            size_hint=(None, None),
            size=(800, 60),
            pos=(Window.width//2 - 400, Window.height - 100),   # Center horizontally, near the top
            halign="center",   # Horizontal text alignment 
            valign="middle"    # Vertical text alignment 
        )
        title_label.text_size = title_label.size
        self.add_widget(title_label)

        # Scoreboard label: text filled from update_hof()
        self.hof_label = Label(
            text="",   # Keep it empty for now 
            font_size=20,
            color=(0, 0, 0, 1),   # Black
            size_hint=(None, None),
            size=(800, 400),
            pos=(Window.width//2 - 140, Window.height//2 - 150),
            halign="left",
            valign="top"
        )
        self.hof_label.text_size = self.hof_label.size
        self.add_widget(self.hof_label)
    
        # Back button: to return back to welcome screen
        back_button = Button(
            text="Back",
            size_hint=(None, None),
            size=(150, 50),
            pos=(Window.width - 200, 50)
        )
        back_button.bind(on_press=self.go_back)
        self.add_widget(back_button)


    def update_hof(self):
        # Load leaderboard data from disk, sort and render it into the label
        # Try to open the JSON file 
        try:
            with open("hall_of_fame.json", "r") as f:
                hof = json.load(f)    # Expecting a list of dicts: [{"username": ..., "score": ...}, ...]
        except FileNotFoundError:    # # If it doesn't exist, create a default leaderboard
            hof = [
                {"username": "Alice", "score": 50},
                {"username": "Bob", "score": 60},
                {"username": "Charlie", "score": 70}
            ]
            with open("hall_of_fame.json", "w") as f:
                json.dump(hof, f)

        hof.sort(key=lambda x: x["score"])  # Sort ascending by score
        # Build a simple multi-line string with ranks 
        text = ""
        rank = 1
        for entry in hof:
            text += f"{rank}. {entry['username']} - {entry['score']} shots\n"   # Each line: "1. Alice - 50 shots"
            rank += 1
        self.hof_label.text = text   # Update the label to show the formatted leaderboard

    def on_pre_enter(self):
        # Update the leaderboard each time the screen is about to be shown
        self.update_hof()  

    def go_back(self, instance):
        # Go back to the welcome screen
        self.manager.current = "welcome"


class HelpScreen(Screen):
    def __init__(self, **kwargs):
        super(HelpScreen, self).__init__(**kwargs)   # Initialize the base screen 
        
        # Full-window background image
        self.background = Image(
            source="background.jpg",
            allow_stretch=True,
            keep_ratio=False
        )
        self.background.size = Window.size
        self.add_widget(self.background)

        # Big title centered near the top
        title_label = Label(
            text="HELP: INSTRUCTIONS OF CANNON GAME",
            font_size=35,
            bold=True,
            color=(0, 0, 0, 1),   # Black text   
            size_hint=(None, None),
            size=(800, 50),
            pos=(Window.width // 2 - 400, Window.height - 100),
            halign="center",
            valign="middle"
        )
        title_label.text_size = title_label.size  # Enable text alignment within the box 
        self.add_widget(title_label)

        # Subtitles (text, y_pos): tells what to write and at what height to place it
        subtitles = [
            ("Game overview", Window.height - 180),
            ("How to select the projectile", Window.height - 360),
            ("Controls", Window.height - 550),
        ]
        for text, y_pos in subtitles:   # The cycle creates a label for each subtitle 
            label = Label(
                text=text,
                font_size=25,
                bold=True,
                color=(0, 0, 0, 1),  # Black text
                size_hint=(None, None),
                size=(800, 50),
                pos=(Window.width // 2 - 400, y_pos),
                halign="center",
                valign="middle"
            )
            label.text_size = label.size
            self.add_widget(label)

        # Three instruction paragraphs (text, y_position)
        instructions = [
            ("The game consists of ten rounds: in each round, you are allowed a maximum of five attempts \n to hit the target using a projectile. To successfully complete a round, you must hit the target \n within these five attempts. Failure to do so will immediately end the game, resulting in a loss. \n To win the game, you must successfully pass all ten rounds. \n Additionally, your objective is to complete the game using as few shots as possible.", Window.height - 300),
            ("Choose from Bullet, Bombshell, or Laser.\n BULLET: massive projectile subject to gravity. \n It follows a parabolic trajectory and has a limited impact radius. \n BOMBSHELL: massive projectile subject to gravity. \n It follows a parabolic trajectory, it has a larger explosion radius than bullet. \n LASER: massless, it is not affected by gravity \n and follows a linear trajectory with a limited duration.", Window.height - 500),
            ("- Use the spacebar to shoot.\n- Use the angle slider to adjust the launch angle.\n- Use the velocity slider to adjust the speed.", Window.height - 650)
        ]
        for text, y_pos in instructions:
            label = Label(
                text=text,
                font_size=18,
                bold=True,
                color=(0, 0, 0, 1),  # Black text
                size_hint=(None, None),
                size=(800, 150),
                pos=(Window.width // 2 - 400, y_pos),
                halign="center",
                valign="middle"
            )
            label.text_size = label.size
            self.add_widget(label)

        # Navigation button to go back 
        back_button = Button(
            text="Back",
            size_hint=(None, None),
            size=(100, 50),
            pos=(Window.width - 200, 50)
        )
        back_button.bind(on_press=self.go_back)
        self.add_widget(back_button)

    def go_back(self, instance):
        # Return to the screen we came from if known, otherwise go to 'welcome'
        if hasattr(self.manager, "previous_screen"):
            self.manager.current = self.manager.previous_screen
        else:
            self.manager.current = "welcome"  # Default


class ProjectileButton(ButtonBehavior, BoxLayout):
    def __init__(self, image_source, label_text, projectile_type, **kwargs):
        super(ProjectileButton, self).__init__(**kwargs)    # Initialize ButtonBehaviour and BoxLayout and process standard kwargs 
        # Vertical arrangement: image on top, label below
        self.orientation = 'vertical'
        self.padding = 10  # Inner margin between the layout border and children 
        self.spacing = 5  # Vertical gap between image and label
        # Store the semantic type this button represents (bullet, bomb, laser)
        self.projectile_type = projectile_type

        # Image widget: top area, 80% of height 
        self.image = Image(source=image_source, allow_stretch=True, keep_ratio=True, size_hint=(1, 0.8))
        # Label widget: bottom area, 20% of height 
        self.label = Label(text=label_text, size_hint=(1, 0.2), color=(0, 0, 0, 1))
        
        self.add_widget(self.image)
        self.add_widget(self.label)


class ProjectileSelectScreen(Screen):
    def __init__(self, **kwargs):
        super(ProjectileSelectScreen, self).__init__(**kwargs)

        # Full-window background image 
        self.background = Image(
            source="background.jpg",
            allow_stretch=True,
            keep_ratio=False
        )
        self.background.size = Window.size
        self.add_widget(self.background)

        # Title label centered horizontally near the top
        title_label = Label(
            text="Select your projectile",
            font_size=48,
            color=(0, 0, 0, 1),
            size_hint=(None, None),
            size=(600, 100),
            pos=(Window.width/2 - 300, Window.height - 150)
        )
        self.add_widget(title_label)
        
        # Horizontal layout for buttons: container that arranges widgets from left to right with a fixed gap
        buttons_layout = BoxLayout(orientation='horizontal', spacing=50, size_hint=(None, None))
        buttons_layout.size = (800, 300)
        buttons_layout.pos = (Window.width/2 - 400, Window.height/2 - 150)
        
       # Create the three selector buttons 
        bullet_button = ProjectileButton(
            image_source="bullet.png",
            label_text="Bullet",
            projectile_type="bullet",
            size_hint=(None, None),
            size=(200, 300)
        )
        bomb_button = ProjectileButton(
            image_source="bomb.png",
            label_text="Bombshell",
            projectile_type="bomb",
            size_hint=(None, None),
            size=(200, 300)
        )
        laser_button = ProjectileButton(
            image_source="laser.png",
            label_text="Laser",
            projectile_type="laser",
            size_hint=(None, None),
            size=(200, 300)
        )
        # Connets the on_press event for each button
        bullet_button.bind(on_press=lambda instance: self.select_projectile("bullet"))
        bomb_button.bind(on_press=lambda instance: self.select_projectile("bomb"))
        laser_button.bind(on_press=lambda instance: self.select_projectile("laser"))

        # Add buttons to the horizontal BoxLayout 
        buttons_layout.add_widget(bullet_button)
        buttons_layout.add_widget(bomb_button)
        buttons_layout.add_widget(laser_button)
        # Add the row layout to the screen
        self.add_widget(buttons_layout)
        
        # Help button in the top-right corner 
        self.help_button = Button(
            text="Help",
            size_hint=(None, None),
            size=(100, 50),
            pos=(Window.width - 100, Window.height - 60)  # Sotto il tasto Save
        )
        self.help_button.bind(on_press=self.show_help)
        self.add_widget(self.help_button)
        
        # Back button above the Help button 
        back_button = Button(
            text="Back",
            size_hint=(None, None),
            size=(100, 50),
            pos=(Window.width - 100, Window.height - 110)  
        )
        back_button.bind(on_press=self.go_back)  # When pressed, calls the function go_back
        self.add_widget(back_button)
        
        # Flag tracking whether a game session in already in progress
        self.game_in_progress = False  # Initially, no game is running
         
    def go_back(self, instance):   
        # Navigation Back: If a game is running, return to the game; otherwise go back to welcome 
        if self.game_in_progress:
            self.manager.current = "game"
        else:
            self.manager.current = "welcome"  

    def show_help(self, instance):
        # Navigation Help: save where we came from, then navigate to the Help screen
        self.manager.previous_screen = self.name
        self.manager.current = "help"
       
    def select_projectile(self, projectile_type):
        # Main action: select a projectile. Persist the selected one and switch to the Game screen
        print(f"Selected projectile: {projectile_type}")
        
        # Set the chosen projectile in the Game screen
        game_screen = self.manager.get_screen("game")
        game_screen.selected_projectile = projectile_type
 
        self.game_in_progress = True   # Mark that a game is now considered 'in progress'
        self.manager.current = "game"   # Navigate to the actual game



class Projectile(Image):
    def __init__(self, angle=45, velocity=BULLET_MAX_VEL, projectile_type="bullet", **kwargs):
        super(Projectile, self).__init__(**kwargs)   # Initialize the Kivy Image base class

        # Choose the image based on the projectile type 
        if projectile_type == "bullet":
            self.source = "bullet.png"
        elif projectile_type == "bomb":
            self.source = "bomb.png"
        elif projectile_type == "laser":
            self.source = "laser.png"
        else:
            self.source = "bullet.png"  # Default, in case of a unknown type
        
        self.size_hint = (None, None)
        if projectile_type == "laser":
            self.size = (200, 200)  # Bigger dimension for the laser (purely sìvisual)
        else:
            self.size = (40, 40)    # Dimensions for bullet/bombshell
        self.reflected = False

        # Kinematics setup
        self.velocity = velocity  # Initial speed (pixels per second)
        self.angle = math.radians(angle)  # Convert the input angle from degrees to radians
        # Decompose the initial velocity vector into horizontal and vertical components
        self.vx = self.velocity * math.cos(self.angle)  
        self.vy = self.velocity * math.sin(self.angle)  
        
        # Gravity setup 
        if projectile_type == "laser":
            self.gravity = 0   # laser is a massless projectile: no gravity
            # Canvas transform to visually rotate the laser sprite
            with self.canvas.before:
                PushMatrix()
                # Create a rotation instruction: "Rotate" rotates everything drawn after its definition in the canvas up to the "PopMatrix"
                self.rot = Rotate(angle=0, origin=self.center)  # origin=self.center is the center of rotation, also the center of the widget (will be constantly updated)
            with self.canvas.after:
                PopMatrix()
        else:   # Massive projectiles follow a parabolic trajectory (constant downward acceleration)
            self.gravity = 300   # pixels per second squared     
        
        self.time = 0    # Life timer (seconds since fired)
        self.projectile_type = projectile_type

    def move(self, dt):
        # Integrate motion for one frame (dt seconds) 
        self.time += dt   # count total time
        self.x += self.vx * dt  # position
        self.y += self.vy * dt   # position
        if self.projectile_type != "laser":    # Applies gravity only to massive projectiles (no laser)
            self.vy -= self.gravity * dt   # Reduce vertical velocity over time 
        if self.projectile_type == "laser":    # Keep the laser sprite visually aligned with its physical direction
            self.rot.origin = self.center    # Update the rotation pivot to the current center
            self.rot.angle = math.degrees(self.angle)    # Rotate the sprite to match the current motion angle


class RockObstacle(Image):
    def __init__(self, pos, **kwargs):
        super(RockObstacle, self).__init__(**kwargs)   # Image inizializer so Kivy can process common keyword args
        self.source = "rock.png"         # Rock image
        self.size_hint = (None, None)    # Disable layout-driven sizing (absolute size in pixels)
        self.size = (100, 100)           # Dimensions of the rock
        self.pos = (pos[0], 75)           # Position of the rock: fixed at ground height, only x varies

    def on_hit(self):  # Called when a projectile hits the rock
            self.parent.remove_widget(self)   # Remove itself if hit


class PerpetioObstacle(Image):
    def __init__(self, pos, **kwargs):
        super(PerpetioObstacle, self).__init__(**kwargs)
        self.source = "perpetio.png"  # Perpetio image
        self.size_hint = (None, None)
        self.size = (100, 100)        
        self.pos = (pos[0], 75)       

    def on_hit(self, projectile):   # Called when a projectile hits the perpetio
        if projectile.parent:
            projectile.parent.remove_widget(projectile)   # Remove the projectile that hit the obstacle 


class MirrorObstacle(Image):
    def __init__(self, pos, mirror_angle=0, moving=False, speed=0, **kwargs):
        super(MirrorObstacle, self).__init__(**kwargs)   # Initialize base Image widget
        self.source = "mirror.png"  
        self.size_hint = (None, None)   # Absolute sizing and positioning
        self.size = (50, 130) 

        # Define lower bounds to keep the mirror away from the cannon/ground area
        min_x = 300
        min_y = 140
        # Define upper bounds so the mirror remains fully on screen
        max_y = min(230, Window.height - int(self.size[1]))
        max_x = Window.width - int(self.size[0]) 
        # Pick a random position within those bounds
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        self.pos = (x, y)

        # Store the mirror's orientation (in degrees)
        self.mirror_angle = mirror_angle 
        # Assign a random orientation, if caller passed None
        if mirror_angle is None:
            self.mirror_angle = random.randint(0, 360)
        else:
            self.mirror_angle = mirror_angle
        # Movement parameters. When moving=True, the mirror slides horizontally
        self.moving = moving
        self.speed = speed
        self.direction = 1  # Initial direction (+1 moves right, -1 moves left)

    def update(self, dt):   # Advance one frame of motion if moving is enabled
        if self.moving:
            # Compute next x
            new_x = self.x + self.speed * self.direction
            # If the mirror reaches the limits it reverses direction
            if new_x < 200 or new_x > Window.width - self.width:
                self.direction *= -1  
            else:   # Otherwise, apply the horizontal movement
                self.x = new_x


class ElastonioObstacle(Image):
    scale_y = NumericProperty(1)

    def __init__(self, pos, elastonio_angle=0, moving_y=False, speed_y=0, y_min=None, y_max=None, **kwargs):
        super(ElastonioObstacle, self).__init__(**kwargs)   # Initialize the base widget
        self.source = "elastonio.png"   
        self.size_hint = (None, None)
        self.size = (150, 50)         
        self.pos = pos           # Position will be determined by the obstacle generator
        self.elastonio_angle = elastonio_angle    # Store the surface orientation in degrees
         
        # Vertical motion configuration 
        self.moving_y = moving_y
        self.speed_y = speed_y     # px/frame     
        self.direction_y = 1   # +1 moves up, -1 moves down
        # Fix band along Y, keep above the ground and within the window
        if y_min is None:
            y_min = 95                  
        if y_max is None:
            y_max = min(230, Window.height - int(self.size[1]))
        self.y_min = y_min
        self.y_max = y_max

    def on_hit(self, projectile):
        # Called when a massive projectile hits the elastic pad
        # Immediate visual feedback via a squash-and-stretch animation (shrink quickly, then restore)
        from kivy.animation import Animation
        anim = Animation(scale_x=0.8, scale_y=0.8, duration=0.1) + Animation(scale_x=1, scale_y=1, duration=0.1)
        anim.start(self)

    def update(self, dt):
        # Ping-pong vertical motion (within vertical bounds) when enabled
        if self.moving_y and self.speed_y > 0:
            new_y = self.y + self.speed_y * self.direction_y
            if new_y < self.y_min or new_y > self.y_max:
                self.direction_y *= -1
            else:
                self.y = new_y


class CannonGame(Screen):
    def __init__(self, **kwargs):
        super(CannonGame, self).__init__(**kwargs)   # Initialize the base Kivy Screen with any keyword args passed in

        # Full-screen background image
        self.background = Image(source="background.jpg", allow_stretch=True, keep_ratio=False)
        self.background.size = Window.size   # Force the background size to match the current window size
        self.add_widget(self.background)    # Add the background first so it is drawn behind everything else
        # Create the cannon sprite with absolute size and position
        self.cannon = Image(source="cannon.png", size_hint=(None, None), size=(400, 200), pos=(-100, 100))
        self.add_widget(self.cannon)   # Add the cannon on top of the background

        # Game state
        self.current_round = 1   # Current round number 
        self.attempt_count = 0   # Attempts used in the current round
        self.max_attempts = 5   # Maximum attempts allowed per round
        self.total_shots = 0    # Total shots fired across all rounds
        self.game_ended = False   # Flag to freeze the game loop when the game ends (win or game over)
        self.projectiles = []     # List of active projectiles currently flying on screen
        self.obstacles = []    # Obstacles currently present in the scene  
        self.add_rock_obstacle(pos=(500, 75))   # Add one initial rock on the ground  
        self.target = None    # No target yet; it will be created in new_round()
        self.new_round()    # Create the first target 
        self.launch_angle = 45   # Default launch angle in degrees
        self.load_progress()    # Try to load saved progress

        # Status label: "Round: X - Attempt: Y/Z"
        self.status_label = Label(
            text=f"Round: {self.current_round} - Attempt: {self.attempt_count}/{self.max_attempts}",
            size_hint=(None, None),
            size=(400, 50),
            pos=(-50, Window.height - 50),    # Neart top-left
            font_size=24,         
            color=(0, 0, 0, 1)    # Black text
        )
        self.add_widget(self.status_label)    # Add the status label above background/cannon

        # Navigation: button to go back to Welcome screen
        self.back_button = Button(
            text="Back",
            size_hint=(None, None),
            size=(100, 50),
            pos=(Window.width - 100, Window.height - 110)   # Top-right area
        )
        self.back_button.bind(on_press=self.go_back)   # Bind click to handler that navigates to welcome and saves
        self.add_widget(self.back_button)    # Add the button to the screen

        # Angle slider 
        self.angle_slider = Slider(min=-45, max=90, value=self.launch_angle,    # range to allow a bit of downward aim
                                   size_hint=(None, None), size=(300, 50),
                                   pos=(50, self.cannon.y - 60))    # Placed below the cannon
        self.angle_slider.bind(value=self.on_angle_change)    # When the slider value changes, update the angle and its label
        self.add_widget(self.angle_slider)    # Add the angle slider  
        # Label displaying the current angle value in degrees
        self.angle_label = Label(text=f"Angle: {self.launch_angle:.0f}°",
                                 size_hint=(None, None), size=(150, 50),
                                 pos=(120, self.cannon.y - 100 ))    # Just under angle slider 
        self.add_widget(self.angle_label)

        # Velocity slider 
        self.muzzle_velocity = BULLET_MAX_VEL    # Initial muzzle velocity
        # Compute position for the velocity slider
        velocity_slider_x = 50 + 300 + 20    # start_x + angle_slider_width + margin
        velocity_slider_y = self.cannon.y - 60
        # Slider to control muzzle velocity
        self.velocity_slider = Slider(min=100, max=1000, value=self.muzzle_velocity,
                                      size_hint=(None, None), size=(300, 50),
                                      pos=(velocity_slider_x, velocity_slider_y))
        # When the slider changes, update the muzzle velocity and label
        self.velocity_slider.bind(value=self.on_velocity_change)
        self.add_widget(self.velocity_slider)    # Add the velocity slider       
        # Label that displays the current muzzle velocity
        self.velocity_label = Label(text=f"Velocity: {self.muzzle_velocity:.0f}",
                                    size_hint=(None, None), size=(150, 50),
                                    pos=(430, self.cannon.y - 100 ))
        self.add_widget(self.velocity_label)    # Add the velocity label

        self.selected_projectile = "bullet"  # Default projectile type 
        self.spawn_obstacles()   # Spawn obstacles for the current round (clears previous and adds new)

        Clock.schedule_interval(self.update, 1/60)     # Let's start the game update
        Window.bind(on_key_down=self.on_key_down)  # Bind keyboard input (keycode 32 triggers fire_projectile())

        # Button to change projectile 
        self.change_button = Button(
            text="Change projectile",
            size_hint=(None, None),
            size=(170, 50),
            pos=(Window.width - 170, Window.height - 730)    # Bottom-right area
        )
        self.change_button.bind(on_press=self.change_projectile)   # Bind click to open the projectile selection screen
        self.add_widget(self.change_button)   # Add the button

        # Button to open the Help screen 
        self.help_button = Button(
            text="Help",
            size_hint=(None, None),
            size=(100, 50),
            pos=(Window.width - 100, Window.height - 60)  # Below the Save button 
        )
        self.help_button.bind(on_press=self.show_help)   # Bind click to show_help
        self.add_widget(self.help_button)   # Add the button

    def reset_game(self):
        self.game_ended = False   # Mark the game as active again
        # Reset core progression counters
        self.current_round = 1
        self.attempt_count = 0
        self.total_shots = 0

        # Remove any residual widget from the win/lose screen
        for attr in ['game_over_label', 'win_label', 'shots_label', 'restart_button']:
            if hasattr(self, attr):
                self.remove_widget(getattr(self, attr))   # remove widget from the screen
                delattr(self, attr)    # delete attribute from this object

        # Remove any remaining projectiles from the previous run
        for proj in self.projectiles[:]:
            self.remove_widget(proj)    # Visually remove the projectile
        self.projectiles = []    # clear logical list
        # Remove any remaining obstacles from the previous run
        for obs in self.obstacles[:]:   
            self.remove_widget(obs)
        self.obstacles = []
        # Remove the target if still present
        if self.target:
            self.remove_widget(self.target)
            self.target = None

        self.status_label.opacity = 1    # Ensure the status label is visible again

    def change_projectile(self, instance):
        # Allow the player to change the projectile type by navigating to the projectile selection screen
        self.manager.previous_screen = self.name  # Store the name of the current screen
        self.manager.current = "projectile_select"   # Switch to projectile selection screen

    def show_help(self, instance):
        # Navigate to Help screen
        self.manager.previous_screen = self.name
        self.manager.current = "help"      # Switch to Help screen  
    
    def save_progress(self, instance):
        # Save the level and game state to a file
        progress_data = {
            "level": self.current_round,
            "attempts": self.attempt_count,
            "selected_projectile": self.selected_projectile
        }
        with open("game_progress.json", "w") as f:   # Open the save file and overwrite it with the new JSON
            json.dump(progress_data, f)

    def load_progress(self):
        # Load previously saved game state from the JSON file, if present.
        # If the file does not exist, fall back to safe defaults.
        try:
            with open("game_progress.json", "r") as f:
                progress_data = json.load(f)
                self.current_round = progress_data.get("level", 1)  
                self.attempt_count = progress_data.get("attempts", 0) 
                self.selected_projectile = progress_data.get("selected_projectile", "bullet")  
        except FileNotFoundError:   # First run or save file deleted: initialize a clean state
            self.current_round = 1
            self.attempt_count = 0
            self.selected_projectile = "bullet" 

    def go_back(self, instance):
        # Navigate back to Welcome screen and persist progress first
        self.save_progress(instance)   # Save the progress before going back
        self.manager.current = "welcome"  # Go back to welcome screen 
    
    def update_status_label(self):
        # Refresh the label state that shows the current round and attempts used 
        current_attempt = self.attempt_count if self.attempt_count < self.max_attempts else self.max_attempts   # Limit the displayed attempt count to max_attempts 
        self.status_label.text = f"Round: {self.current_round} - Attempt: {current_attempt}/{self.max_attempts}"   # Update the label text 
    
    def on_angle_change(self, instance, value):
        #  When the angle slider moves, update the model (launch_angle) and the corresponding label
        self.launch_angle = value   # Store the new angle (degrees) used when firing
        self.angle_label.text = f"Angle: {value:.0f}°"   # Reflect the new angle in the label

    def on_velocity_change(self, instance, value):
        # When the velocity slider moves, update the model (muzzle_velocity) and the label
        self.muzzle_velocity = value   # Store the new muzzle velocity for the next shot
        self.velocity_label.text = f"Velocity: {value:.0f}"   # Update the label to show the current velocity

    def spawn_obstacles(self):
        # Clear previous obstacles 
        for obs in self.obstacles:
            self.remove_widget(obs)
        self.obstacles = []

        # Rock: amount grows with round
        num_rock = (self.current_round + 2) // 4 + 1   # Rounds: 1-2 -> 1 rock, 3-4 -> 2 rocks, 5-6 -> 3, 7-8 -> 4, 9-10 -> 5
        for _ in range(num_rock):
            # Random x position, but y fixed to ground (75)
            pos_x = random.randint(150, Window.width - 100)
            pos_y = random.randint(0, 150) 
            rock = RockObstacle(pos=(pos_x, 75))
            self.add_widget(rock)
            self.obstacles.append(rock)

        # Perpetio: from round 3
        if self.current_round >= 3:
            num_perpetio = 1 + (self.current_round - 4) // 3 
            for _ in range(num_perpetio):
                pos_x = random.randint(150, Window.width - 100)
                pos_y = 75   # Ground 
                perpetio = PerpetioObstacle(pos=(pos_x, pos_y))
                self.add_widget(perpetio)
                self.obstacles.append(perpetio)

        # Mirror: from round 4
        if self.current_round >= 4 and self.target:
            # Top edge of the target to keep mirror above it
            target_top = self.target.y + self.target.height
            # Keep mirror at least 50px above target, but not below 80px overall
            min_mirror_y = max(80, target_top + 50)
            max_mirror_y = 150   # Desired maximum limit 
            # If the min exceeds the maximum limit, clamp to maximum
            if min_mirror_y > max_mirror_y:
                min_mirror_y = max_mirror_y
            mirror_pos_y = random.randint(min_mirror_y, max_mirror_y)
            mirror_pos_x = random.randint(200, Window.width - 100)
            
            # Mirror speed increases with round 
            if self.current_round == 6:
                mirror_speed = 1
            elif self.current_round == 7:
                mirror_speed = 1.3
            elif self.current_round == 8:
                mirror_speed = 1.7
            elif self.current_round in [9, 10]:
                mirror_speed = 2.3
            else:
                mirror_speed = 0  # In round 4,5 the mirror doesn't move
        
            # Create the mirror with movement and a given speed
            mirror = MirrorObstacle(pos=(mirror_pos_x, mirror_pos_y), 
                                mirror_angle=random.randint(0, 360), 
                                moving=True, 
                                speed=mirror_speed)
            self.add_widget(mirror)
            self.obstacles.append(mirror)

        # Elastonio: from round 7
        if self.current_round >= 7:
            num_elastonio = 1  
            for _ in range(num_elastonio):
                pos_x = random.randint(200, Window.width - 100)  # x from 200 onward 
                pos_y = random.randint(95, 200)  # # avoids ground & top (to avoid interfere with target and obstacles)
                elastonio_angle = random.randint(0, 360)

                # Vertical motion only in rounds 9–10
                moving_y = self.current_round in [9, 10]
                speed_y = 0.4 if self.current_round == 9 else (0.7 if self.current_round == 10 else 0)
                # Small amplitude 
                if self.current_round == 9:
                    amp = 12  
                elif self.current_round == 10:
                    amp = 16  
                else:
                    amp = 0   # No movement in round 7,8

                elastonio = ElastonioObstacle(
                    pos=(pos_x, pos_y),
                    elastonio_angle=elastonio_angle,
                    moving_y=moving_y,
                    speed_y=speed_y,
                    y_min=95,
                    y_max=230
                )             
                self.add_widget(elastonio)
                self.obstacles.append(elastonio)
    
    def new_round(self):  # Create a new target in a random position
        if self.target:
            self.remove_widget(self.target)   # If a target from the previous round exists, remove it
        self.spawn_obstacles()   # Spawn obstacles for this round
        
        # Define a rectangle on the right half of the screen where the target is allowed to spawn
        x_min = Window.width // 2
        x_max = Window.width - 100
        y_min = 60
        y_max = Window.height - 100

        collision = True
        # Try random positions until one doesn't collide with any obstacle
        while collision:
            x_random = random.randint(x_min, x_max)
            y_random = random.randint(y_min, y_max)
            candidate = Image(source="target.png", size_hint=(None, None), size=(40, 40), pos=(x_random, y_random))
            collision = False
            for obstacle in self.obstacles:
                if self.collides(candidate, obstacle):
                    collision = True
                    break
        # Assign and add the final target
        self.target = candidate
        self.add_widget(self.target)
    
    def next_round(self):
        if not self.game_ended:  # Only if the game hasn't ended
            self.current_round += 1  # Advance round counter 
            self.attempt_count = 0   # Reset attempts 
            self.update_status_label()   # Update status label
            self.new_round()   # Generate the new layout + target 
 
    def game_over(self):   
        self.game_ended = True   # # Tell the rest of the game loop to stop updating gameplay
        self.status_label.opacity = 0  # Hide the label without removing it

        # Remove the target and the obstacles from the screen to block updates 
        if self.target:
            self.remove_widget(self.target)
            self.target = None
        for obs in self.obstacles[:]:
            self.remove_widget(obs)
        self.obstacles = []   # Reset the list

        # Create and display a 'GAME OVER' banner centered on the screen
        game_over_label = Label(
            text="GAME OVER",
            size_hint=(None, None),
            size=(300, 100),
            pos=(Window.width // 2 - 150, Window.height // 2 - 50),
            font_size=48,
            color=(1, 0, 0, 1)  # Red
        )
        self.add_widget(game_over_label)
        self.game_over_label = game_over_label   # Keep a reference so we can remove it later in reset_game()
        
        # Button to go back to Welcome and start a new game 
        restart_button = Button(
            text="Restart Game",
            size_hint=(None, None),
            size=(200, 50),
            pos=(Window.width // 2 - 100, Window.height // 2 - 100)
        )
        restart_button.bind(on_press=lambda instance: self.go_to_welcome(None))  # Bind the button press that calls go_to_welcome 
        self.add_widget(restart_button)
        self.restart_button = restart_button
    
    def go_to_welcome(self, dt):
        self.reset_game()
        self.status_label.opacity = 0 
        self.manager.current = "welcome"  # Switch the active screen to 'welcome' via the ScreenManager

    def fire_projectile(self):
        # If the player has already used all attempts for this round, do nothing
        if self.attempt_count >= self.max_attempts:
            return
        # Attempts within this round and total shots across the game
        self.attempt_count += 1
        self.total_shots += 1 
        self.update_status_label()
        # Spawn the projectile at the cannon's muzzle 
        cannon_x = self.cannon.x + self.cannon.width - 120 
        cannon_y = self.cannon.y + self.cannon.height // 2 + 50  

        # Instantiate the projectile with the current aiming parameters and selected type
        projectile = Projectile(
            angle=self.launch_angle,   # degrees  
            velocity=self.muzzle_velocity,   # initial speed from the slider
            pos=(cannon_x, cannon_y),    # spawn position near the muzzle
            projectile_type=self.selected_projectile
        )
        self.add_widget(projectile)   # Add to the screen 
        self.projectiles.append(projectile)   # Track it to the update() loop moves it 

    def check_collision(self, projectile):
        # Return True if `projectile` hits `self.target`, False otherwise 
        if projectile.projectile_type == "laser":
            # Treat the laser as a point at its image center
            center_x = projectile.x + projectile.width / 2
            center_y = projectile.y + projectile.height / 2
            # Check if the center is inside the target
            if (center_x >= self.target.x and center_x <= self.target.x + self.target.width and
                center_y >= self.target.y and center_y <= self.target.y + self.target.height):
                return True
            return False

        elif projectile.projectile_type == "bullet":
            # Compute distance between the centers 
            center_proj = (projectile.x + projectile.width / 2, projectile.y + projectile.height / 2)
            center_target = (self.target.x + self.target.width / 2, self.target.y + self.target.height / 2)
            dist = math.sqrt((center_proj[0] - center_target[0]) ** 2 + (center_proj[1] - center_target[1]) ** 2)
            if dist <= BULLET_RADIUS:
                return True
            return False

        elif projectile.projectile_type == "bomb":
            # Same logic but with BOMB_RADIUS
            center_proj = (projectile.x + projectile.width / 2, projectile.y + projectile.height / 2)
            center_target = (self.target.x + self.target.width / 2, self.target.y + self.target.height / 2)
            dist = math.sqrt((center_proj[0] - center_target[0]) ** 2 + (center_proj[1] - center_target[1]) ** 2)
            return dist <= BOMB_RADIUS
        else:
            if (projectile.x < self.target.x + self.target.width and
                projectile.x + projectile.width > self.target.x and
                projectile.y < self.target.y + self.target.height and
                projectile.y + projectile.height > self.target.y):
                return True
            return False
    
        
    def add_rock_obstacle(self, pos):
        # Create and add a Rock obstacle to the game screen 
        rock = RockObstacle(pos=pos)  # Create the instance at the desired position
        self.add_widget(rock)   # Add it on screen
        self.obstacles.append(rock)   # Keep track of it on the logic list

    def collides(self, widget1, widget2):
        # Return True if widget1 and widget2 collide (rectangular overlapping)
        return not (
            widget1.x + widget1.width < widget2.x or   #w1 completely to the left of w2
            widget1.x > widget2.x + widget2.width or    #w1 completely to the right of w2
            widget1.y + widget1.height < widget2.y or    #w1 completely under w2
            widget1.y > widget2.y + widget2.height    #w1 completely above of w2
        )

    def distance(p1, p2):   # Euclidean distance between two 2D points
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def update(self, dt):   # Per-frame game loop. Called around 60 times per second
        # If the game ended, don't update anything else.
        if self.game_ended:
            return  
        # Give moving obstacles a chance to update themselves
        for obs in self.obstacles:
            if hasattr(obs, "update"):
                obs.update(dt)

        # Move each projectile and handle lifecycle + collisions        
        for projectile in self.projectiles[:]:  
            projectile.move(dt)  # Advance projectile physics (position, velocity, gravity if any)
            # If projectile is laser, after LASER_IMPULSE seconds, remove it 
            if projectile.projectile_type == "laser" and projectile.time > LASER_IMPULSE:
                self.remove_widget(projectile)
                self.projectiles.remove(projectile)
                continue

            if projectile.y < 0:  # If it falls below the screen, remove the projectile
                self.remove_widget(projectile)
                self.projectiles.remove(projectile)
                continue
 
            if self.check_collision(projectile):   # Check hit on the TARGET first
                print("HIT! New Round!")
                # Show an explosion effect when the hitting projectile is a bomb
                if projectile.projectile_type == "bomb":
                    explosion = Image(
                        source="explosion.png",
                        size_hint=(None, None),
                        size=(100, 100),
                        pos=(projectile.x, projectile.y)
                    )
                    self.add_widget(explosion)
                    # Schedule removal of the explosion sprite after 0.5s
                    Clock.schedule_once(lambda dt: self.remove_widget(explosion), 0.5)               
                self.remove_widget(projectile)  # Remove the projectile that hit the target
                self.projectiles.remove(projectile)
                self.attempt_count = 0   # Reset attempt counter because target was hit
                self.update_status_label()  # Update status label

                if self.current_round == 10: # If this was round 10, the player WINS and we finalize the score
                    self.status_label.opacity = 0
                    username = self.manager.username if hasattr(self.manager, "username") else "Anonymous"
                    try:
                        with open("hall_of_fame.json", "r") as f:
                            hof = json.load(f)
                    except FileNotFoundError:
                        hof = []
                    # Save score 
                    hof.append({"username": username, "score": self.total_shots})
                    hof.sort(key=lambda x: x["score"])
                    with open("hall_of_fame.json", "w") as f:
                        json.dump(hof, f)
                    # Mark game as ended and show the label 'YOU WIN'
                    self.game_ended = True
                    win_label = Label(
                        text="YOU WIN!",
                        size_hint=(None, None),
                        size=(300, 100),
                        pos=(Window.width // 2 - 150, Window.height // 2 - 50),
                        font_size=60,
                        color=(0, 1, 0, 1)  # Green
                    )
                    self.add_widget(win_label)
                    self.win_label = win_label

                    # Show the number of total shots 
                    shots_label = Label(
                        text=f"Total Shots: {self.total_shots}",
                        size_hint=(None, None),
                        size=(300, 100),
                        pos=(Window.width // 2 - 150, Window.height // 2 - 100),
                        font_size=34,
                        color=(1, 1, 1, 1)  # White 
                    )
                    self.add_widget(shots_label)
                    self.shots_label = shots_label

                     # Offer a restart button that goes back to Welcome and reset
                    restart_button = Button(
                        text="Save your Score and Restart Game",
                        size_hint=(None, None),
                        size=(300, 50),
                        pos=(Window.width // 2 - 150, Window.height // 2 - 160)
                    )
                    restart_button.bind(on_press=lambda instance: self.go_to_welcome(None))
                    self.add_widget(restart_button)
                    self.restart_button = restart_button
                   
                else:   # Otherwise, progress to the next round
                    self.next_round()  
                break  
                
            # If the projectile didn't hit the target, check collisions with obstacles
            for obstacle in self.obstacles[:]:
                collision = False
                if projectile.projectile_type == "laser":
                    # Use the center of the laser to check the collision
                    center_x = projectile.x + projectile.width / 2
                    center_y = projectile.y + projectile.height / 2
                    if (center_x >= obstacle.x and center_x <= obstacle.x + obstacle.width and
                       center_y >= obstacle.y and center_y <= obstacle.y + obstacle.height):
                       collision = True
                else:  # Rect-rect overlap for massive projectiles 
                    collision = self.collides(projectile, obstacle)

                if collision:
                    # Special behavior: Bomb explosion on impact (except on Elastonio)
                    if projectile.projectile_type == "bomb" and not isinstance(obstacle, ElastonioObstacle):
                        explosion = Image(
                            source="explosion.png",
                            size_hint=(None, None),
                            size=(100, 100),
                            pos=(projectile.x, projectile.y)
                        )
                        self.add_widget(explosion)
                        Clock.schedule_once(lambda dt: self.remove_widget(explosion), 0.5)  # Removes the explosion image after 0.5 seconds
                        
                        # Bomb can destroy rocks
                        if isinstance(obstacle, RockObstacle):                      
                            obstacle.on_hit()
                            if obstacle in self.obstacles:
                                self.obstacles.remove(obstacle)
                        # Remove the bomb itself      
                        self.remove_widget(projectile)
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)
                        break  # Esci dal ciclo degli ostacoli

                    # Mirror: reflect lasers once; remove bombshell and bullet 
                    elif isinstance(obstacle, MirrorObstacle):                       
                        if projectile.projectile_type == "laser":
                            # If it hasn't already been reflected, reflect only once
                            if not getattr(projectile, "reflected", False):
                                # Compute mirror normal from its angle 
                                n_x = math.cos(math.radians(obstacle.mirror_angle + 90))
                                n_y = math.sin(math.radians(obstacle.mirror_angle + 90))
                                 # Reflect velocity vector
                                dot = projectile.vx * n_x + projectile.vy * n_y                                
                                projectile.vx = projectile.vx - 2 * dot * n_x
                                projectile.vy = projectile.vy - 2 * dot * n_y
                                projectile.angle = math.atan2(projectile.vy, projectile.vx)
                                # Update laser sprite rotation, if present
                                if hasattr(projectile, 'rot'):
                                    projectile.rot.angle = math.degrees(projectile.angle)
                                projectile.reflected = True
                        else:  # Bullets/bombs are absorbed/blocked by the mirror                            
                            self.remove_widget(projectile)
                            if projectile in self.projectiles:
                                self.projectiles.remove(projectile)
                        break  

                    # Elastonio: elastic reflection for bullet/bomb (+squash anim), absorb laser
                    elif isinstance(obstacle, ElastonioObstacle):
                        if projectile.projectile_type in ["bullet", "bomb"]:
                            # Visual squash animation
                            from kivy.animation import Animation
                            anim = Animation(scale_y=0.8, duration=0.1) + Animation(scale_y=1, duration=0.1)
                            anim.start(obstacle)

                            # Elastic reflection with restitution > 1 for extra bounce
                            restitution = 1.2  
                            n_x = math.cos(math.radians(obstacle.elastonio_angle + 90))
                            n_y = math.sin(math.radians(obstacle.elastonio_angle + 90))
                            dot = projectile.vx * n_x + projectile.vy * n_y
                            projectile.vx = restitution * (projectile.vx - 2 * dot * n_x)
                            projectile.vy = restitution * (projectile.vy - 2 * dot * n_y)
                            projectile.angle = math.atan2(projectile.vy, projectile.vx)
                            if hasattr(projectile, 'rot'):
                                projectile.rot.angle = math.degrees(projectile.angle)
                            projectile.reflected = True
                        else:   # Laser is absorbed by Elastonio
                            self.remove_widget(projectile)
                            if projectile in self.projectiles:
                                self.projectiles.remove(projectile)
                        break 

                    else:
                    # Rocks are destroyed; Perpetio survives; projectile removed.
                        if isinstance(obstacle, RockObstacle):
                            print("Projectile hit a rock!")
                            obstacle.on_hit()
                            self.obstacles.remove(obstacle)
                        elif isinstance(obstacle, PerpetioObstacle):
                            print("Projectile hit a Perpetio!")
                        self.remove_widget(projectile)
                        if projectile in self.projectiles:  # In any case for default branch, remove projectile
                            self.projectiles.remove(projectile)
                        break

        #  If attempts are exhausted and no projectiles are in flight, end the game
        if self.attempt_count >= self.max_attempts and not self.projectiles:
            print("Game over, new round!")
            self.game_over() 
            
    def on_key_down(self, window, key, *args):
        # Handle keyboard presses while game screen is active
        if key == 32:  # spacebar keycode: if pressed, fire a new projectile
            self.fire_projectile()

    def show_help(self, instance):  # Open Help screen from the game 
        self.manager.previous_screen = self.name   # Remember where we came from 
        self.manager.current = "help"  # Navigate to Help screen 


class CannonApp(App):
    def build(self):
        self.manager = ScreenManager()
        welcome_screen = WelcomeScreen(name="welcome")
        self.manager.add_widget(welcome_screen)
        projectile_select_screen = ProjectileSelectScreen(name="projectile_select")
        self.manager.add_widget(projectile_select_screen)
        game_screen = CannonGame(name="game")
        self.manager.add_widget(game_screen)
        help_screen = HelpScreen(name="help")
        self.manager.add_widget(help_screen)
        hof_screen = HallOfFameScreen(name="hall_of_fame")
        self.manager.add_widget(hof_screen)
        return self.manager

if __name__ == "__main__":
    CannonApp().run()