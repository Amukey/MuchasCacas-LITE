"""Game-wide constants and configuration"""

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

# Colors and Visual Effects
VISUALS = {
    'ENTITIES': {
        'COLONY': {
            'PRIMARY': (0, 0, 0),        # Black
            'OUTLINE': (173, 216, 230),  # Baby blue
            'PREVIEW': (0, 0, 0, 128)    # Semi-transparent
        },
        'ANT': {
            'PRIMARY': (0, 0, 0),        # Black
            'CARRYING': {
                'MINERAL': {
                    'GLOW': (180, 180, 180),  # Grey
                    'SPARKLE': (255, 255, 255),  # White
                    'SHAPE': (160, 160, 160)   # Light grey
                },
                'PLANT': {
                    'GLOW': (100, 255, 100),    # Bright green
                    'PARTICLE': (150, 255, 150), # Light green
                    'SHAPE': (80, 200, 80)      # Dark green
                }
            }
        },
        'SNAKE': {
            'PRIMARY': (0, 255, 0),      # Green
            'SLEEP': (0, 200, 0),        # Darker green when sleeping
            'SLEEP_Z': {
                'COLOR': (255, 255, 255), # White Zs
                'MIN_SIZE': 8,
                'MAX_SIZE': 12,
                'FLOAT_SPEED': 0.03,
                'WAVE_SPEED': 0.01,
                'WAVE_AMPLITUDE': 5
            }
        }
    },
    'UI': {
        'BARS': {
            'BACKGROUND': (64, 64, 64),     # Dark gray
            'MINERAL': (139, 69, 19),       # Brown
            'PLANT': (34, 139, 34),         # Forest Green
            'BORDER': (200, 200, 200)       # Light gray
        },
        'TEXT': {
            'PRIMARY': (255, 255, 255),     # White
            'SECONDARY': (200, 200, 200)    # Light gray
        },
        'TOOLTIP': {
            'BACKGROUND': (0, 0, 0, 180),   # Semi-transparent black
            'BORDER': (255, 255, 255, 100)  # Semi-transparent white
        },
        'INDICATORS': {
            'ACTIVE': (255, 255, 255),      # White
            'INACTIVE': (100, 100, 100)     # Dark gray
        }
    },
    'TIME': {
        'DAY': {
            'SKY': (135, 206, 235),      # Sky blue
            'SUN': (255, 240, 100),      # Yellow
            'SUN_GLOW': (255, 200, 50)   # Orange glow
        },
        'NIGHT': {
            'SKY': (20, 20, 50, 100),    # Dark blue, semi-transparent
            'MOON': (220, 220, 240),     # Pale blue
            'MOON_GLOW': (180, 180, 200), # Pale blue glow
            'STARS': (255, 255, 220)      # Warm white
        },
        'TRANSITIONS': {
            'DAWN': {
                'TINT': (255, 200, 100),  # Warm sunrise
                'ALPHA': 30               # Subtle transition
            },
            'DUSK': {
                'TINT': (100, 50, 150),   # Purple sunset
                'ALPHA': 30               # Subtle transition
            }
        }
    }
}

# Colors (Legacy support - maps to VISUALS)
COLORS = {
    'COLONY': VISUALS['ENTITIES']['COLONY']['PRIMARY'],
    'ANT': VISUALS['ENTITIES']['ANT']['PRIMARY'],
    'SNAKE': VISUALS['ENTITIES']['SNAKE']['PRIMARY'],
    'GLOW': {
        'MINERAL': VISUALS['ENTITIES']['ANT']['CARRYING']['MINERAL']['GLOW'],
        'PLANT': VISUALS['ENTITIES']['ANT']['CARRYING']['PLANT']['GLOW'],
        'SPARKLE': VISUALS['ENTITIES']['ANT']['CARRYING']['MINERAL']['SPARKLE'],
        'LEAF': VISUALS['ENTITIES']['ANT']['CARRYING']['PLANT']['PARTICLE']
    },
    'COLONY_OUTLINE': VISUALS['ENTITIES']['COLONY']['OUTLINE']
}

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

    # Day/Night specific behaviors
    DAY_NIGHT = {
        'ANT_DAY_SPEED': 0.8,
        'ANT_NIGHT_SPEED': 0.6,
        'ANT_DAY_PERCEPTION': 40,
        'ANT_NIGHT_PERCEPTION': 25,
        'SNAKE_DAY_SPEED': 0.5,
        'SNAKE_NIGHT_SPEED': 0.0  # Snake doesn't move at night
    }

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
        OFFSET_Y = 20
        TEXT_COLOR = (255, 255, 255)  # White text
        BACKGROUND = (0, 0, 0, 180)   # Semi-transparent black
        BORDER_COLOR = (255, 255, 255, 100)  # Semi-transparent white
        BORDER_WIDTH = 1

    # Colony Preview
    class Preview:
        OPACITY = 128
        BORDER_WIDTH = 2
        BORDER_COLOR = (255, 255, 255, 128)  # Semi-transparent white

    # Resource Icons
    class Icons:
        SIZE = 24
        SPACING = 4
        MINERAL_EMOJI = "💎"
        PLANT_EMOJI = "🌿"
        ANT_EMOJI = "🐜"
        COLONY_EMOJI = "🏠"

# Audio Constants
SAMPLE_RATE = 44100
BUFFER_SIZE = 4096
QUEUE_LENGTH = 12
SEGMENT_DURATION = 0.5
CROSSFADE_DURATION = 0.15

BASE_FREQUENCIES = {
    'day': [220.0, 277.2, 329.6, 440.0, 554.4],  # A3 major pentatonic
    'night': [220.0, 261.6, 329.6, 392.0, 440.0]  # A3 minor pentatonic
}

# Volume levels
VOLUMES = {
    'MASTER': 0.8,
    'MUSIC': 0.6,
    'EFFECTS': 0.7
}

# Synthesis parameters
SOUND_PARAMS = {
    'REVERB_TIME': 0.3,
    'DELAY_TIME': 0.2,
    'PAD_DETUNE': 0.1,
    'FILTER_CUTOFF': 0.7
}

# Music Pattern Durations (in seconds)
PATTERN_DURATIONS = {
    'PEACEFUL': 32,    # Multiple of 8
    'AMBIENT': 48,     # Multiple of 16
    'FLOATING': 24,    # Multiple of 8
    'DREAMY': 40      # Multiple of 8
}

# Musical Constants
PHRASE_LENGTH = 8     # Beats per phrase
BAR_LENGTH = 4        # Beats per bar
MIN_PATTERN_TIME = 16 # Minimum time before pattern change

# Envelope Settings
ENVELOPE = {
    'BASS': {
        'ATTACK': 0.2,
        'DECAY': 0.3,
        'SUSTAIN': 0.6,
        'RELEASE': 0.8
    },
    'MELODY': {
        'ATTACK': 0.1,
        'DECAY': 0.2,
        'SUSTAIN': 0.7,
        'RELEASE': 0.4
    },
    'BEATS': {
        'ATTACK': 0.05,
        'DECAY': 0.1,
        'SUSTAIN': 0.8,
        'RELEASE': 0.3
    }
}

# Pattern Types
PATTERN_TYPES = {
    'REST': -1,
    'KICK': 1,
    'HIHAT': 2,
    'SNARE': 3,
    'SHAKER': 4
}

# Timing Variations
TIMING = {
    'PHRASE_SWING': 0.008,
    'BAR_SWING': 0.004,
    'MICRO_TIMING': 0.005
}

# Music State Constants
MUSIC_STATE = {
    'INTENSITY_TEMPO_FACTOR': 0.2,
    'DANGER_VOLUME_FACTOR': 0.3,
    'RESOURCE_VOLUME_FACTOR': 0.2,
    'MIN_QUEUE_LENGTH': 8,
    'MAX_QUEUE_LENGTH': 16,
    'TEMPO_SMOOTHING': 0.05
}

# Musical Moods
MOODS = {
    'PEACEFUL': {
        'tempo_mult': 0.75,
        'bass_prominence': 0.8,
        'melody_prominence': 1.0,
        'beat_sparsity': 1
    },
    'AMBIENT': {
        'tempo_mult': 0.7,
        'bass_prominence': 1.2,
        'melody_prominence': 0.6,
        'beat_sparsity': 0.5
    },
    'FLOATING': {
        'tempo_mult': 0.8,
        'bass_prominence': 0.9,
        'melody_prominence': 1.1,
        'beat_sparsity': 0.6
    },
    'DREAMY': {
        'tempo_mult': 0.65,
        'bass_prominence': 1.0,
        'melody_prominence': 0.8,
        'beat_sparsity': 1
    }
}

# Day/Night Cycle
DAY_NIGHT = {
    'CYCLE_DURATION': 180000,  # 3 minutes in milliseconds
    'DAWN_DURATION': 15000,    # 15 seconds transition
    'DUSK_DURATION': 15000,    # 15 seconds transition
    'NIGHT_TINT': (20, 20, 50, 100),  # Bluish night overlay with much less opacity (was 0)
    'DAY_VISIBILITY': 100,     # Day visibility radius
    'NIGHT_VISIBILITY': 40,    # Night visibility radius
    'MAX_NIGHT_ALPHA': 130,    # Maximum darkness (was 255)
    'SNAKE_SLEEP_SPOT': {
        'COLOR': (50, 50, 50), # Snake sleep spot marker
        'SIZE': 20             # Size of sleep spot
    }
}

# Resource Effects
RESOURCE_EFFECTS = {
    'GLOW_SIZE': 4,           # Pixels to add to base size
    'PULSE_SPEED': 0.01,      # Speed of pulsing
    'PULSE_MIN': 0.7,         # Minimum pulse intensity
    'PULSE_MAX': 1.0,         # Maximum pulse intensity
    'PARTICLE_CHANCE': {
        'MINERAL': 0.3,       # Chance to spawn mineral particles
        'PLANT': 0.2         # Chance to spawn plant particles
    },
    'PARTICLES_PER_SPAWN': 2,  # Number of particles to spawn
    'PARTICLE_SIZE': {
        'MINERAL': 1,         # Size of mineral sparkles
        'PLANT': (1, 1)       # Range of plant particle sizes (reduced from (1, 2))
    },
    'SHAPE_SIZE_MULT': 1.5    # Multiplier for resource shape size
} 