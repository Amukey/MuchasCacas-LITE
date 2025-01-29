# Game Window
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 800
FPS = 60

# Entity Sizes
COLONY_MIN_SIZE = 10
COLONY_MAX_SIZE = 25
ANT_SIZE = 3
SNAKE_SIZE = 4
PERCEPTION_RADIUS = 40

# Colors
COLOR_COLONY = (0, 0, 0)      # Black
COLOR_ANT = (0, 0, 0)         # Black
COLOR_SNAKE = (0, 255, 0)     # Green
COLOR_GLOW_BLUE = (0, 0, 255) # Blue glow
COLOR_GLOW_YELLOW = (255, 255, 0) # Yellow glow
COLOR_COLONY_OUTLINE = (173, 216, 230)  # Baby blue

# Game Economy
class Economy:
    # Colony Settings
    COLONY_INITIAL_MINERALS = 200
    COLONY_INITIAL_PLANTS = 100
    COLONY_MAX_ANTS = 12
    COLONY_SPAWN_INTERVAL = 8000
    
    # Resource Costs
    class Costs:
        # Colony Creation
        NEW_COLONY_MINERALS = 200
        NEW_COLONY_PLANTS = 400
        
        # Ant Creation
        ANT_MINERALS = 8
        ANT_PLANTS = 15
    
    # Resource Capacities
    class Capacity:
        ANT_MINERAL_CAPACITY = 15
        ANT_PLANT_CAPACITY = 15
        ROCK_MINERAL_CAPACITY = 150
        TREE_RESOURCE_CAPACITY = 100
        BUSH_RESOURCE_CAPACITY = 50

    # Resource Generation
    class Generation:
        RESOURCE_SPAWN_INTERVAL = 4000
        MAX_ROCKS = 25
        MAX_PLANTS = 25
        MAX_BUSHES = 45

# Entity Behavior
class Behavior:
    # Snake
    SNAKE_SPEED = 0.5
    SNAKE_PERCEPTION_RADIUS = 10
    SNAKE_INITIAL_LENGTH = 15
    SNAKE_WAVE_SPEED = 0.2
    
    # Ant
    ANT_SPEED = 0.8
    ANT_PERCEPTION_RADIUS = 40
    ANT_FLEE_DISTANCE = 100
    
    # Colony
    COLONY_PULSE_SPEED = 500  # milliseconds

# Animation Timings
class Animation:
    # Intro Sequence
    LOGO_FADE_IN = 500
    LOGO_STAY = 1000
    LOGO_FADE_OUT = 500
    MAP_FADE_IN = 800
    TREES_FADE_IN = 600
    ROCKS_FADE_IN = 600
    SNAKE_FADE_IN = 400

# Background Settings
class Background:
    TILE_SIZE = 4
    NOISE_SCALE = 25.0

# UI Settings
class UI:
    # Resource Bars
    class Bars:
        WIDTH = 30
        HEIGHT = 12
        VERTICAL_SPACING = 5
        MINERAL_OFFSET_Y = 20
        PLANT_OFFSET_Y = 25
        HORIZONTAL_OFFSET = 15
        
        # Colors
        BACKGROUND = (100, 100, 100)  # Gray
        MINERAL = (139, 69, 19)       # Brown
        PLANT = (0, 255, 0)           # Green
        
        # Max Values (for percentage calculation)
        MAX_MINERAL_VALUE = 400
        MAX_PLANT_VALUE = 800

    # Colony Indicators
    class Indicators:
        SIZE = 10
        SPACING = 2
        VERTICAL_OFFSET = 0  # From colony center
        
        # Colors are already defined in main colors section
        OPACITY = {
            'NORMAL': 255,
            'PREVIEW': 128
        }

    # Tooltips
    class Tooltips:
        FONT_SIZE = 14
        PADDING = 5
        BACKGROUND = (0, 0, 0, 180)  # Semi-transparent black
        TEXT_COLOR = (255, 255, 0)  # Yellow
        BORDER_COLOR = (200, 200, 200)
        BORDER_WIDTH = 1
        MAX_WIDTH = 200
        OFFSET_Y = -20  # Distance above element

    # Colony Preview
    class Preview:
        OPACITY = 128
        BORDER_WIDTH = 2
        BORDER_COLOR = (255, 255, 255, 128)  # Semi-transparent white

    # Resource Icons
    class Icons:
        SIZE = 16
        SPACING = 4
        MINERAL_EMOJI = "💎"
        PLANT_EMOJI = "🌿"
        ANT_EMOJI = "🐜"
        COLONY_EMOJI = "🏠" 