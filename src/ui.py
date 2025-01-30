import pygame
from constants import (
    UI, WINDOW_WIDTH, WINDOW_HEIGHT, Economy,
    COLORS
)
import random

# UI Constants
UI_FONT_SIZE = UI.Tooltips.FONT_SIZE
UI_PADDING = UI.Tooltips.PADDING
UI_MARGIN = 10

# HUD Layout Constants
HUD_TOP_MARGIN = 10
HUD_RIGHT_MARGIN = 45  # For colony count in top right
HUD_LEFT_MARGIN = 10

# Resource Bar Constants
BAR_HEIGHT = 12
BAR_WIDTH = 400
BAR_MAX_MINERALS = 400  # Maximum minerals for bar display
BAR_MAX_PLANTS = 800    # Maximum plants for bar display

# Pip Constants (for ant counter)
PIP_SIZE = 2
PIP_SPACING = 4
PIP_COUNT = 20  # Maximum number of pips to show

# Colony Icon Constants
COLONY_ICON_SIZE = 15
SMALL_ANT_ICON_SIZE = 3

# Resource Icon Constants
RESOURCE_ICON_SIZE = 12  # New constant for resource icons

# Tooltip texts with unicode symbols
TOOLTIP_TEXTS = {
    'minerals': "◆ Minerals: {}/{}\nUsed for creating ants ({}) and colonies ({})".format(
        "{}", BAR_MAX_MINERALS, Economy.Costs.ANT_MINERALS, Economy.Costs.NEW_COLONY_MINERALS),
    'plants': "✿ Plants: {}/{}\nUsed for creating ants ({}) and colonies ({})".format(
        "{}", BAR_MAX_PLANTS, Economy.Costs.ANT_PLANTS, Economy.Costs.NEW_COLONY_PLANTS),
    'ants': "• Colony Ants: {}/{}\nClick colony to spawn new ant\nCost: {} minerals + {} plants",
    'colonies': "⌂ Total Colonies: {}\nCreate new colony\nCost: {} minerals + {} plants"
}

class PixelIcon:
    def __init__(self, size):
        self.size = size
        self.frames = []
        self.current_frame = 0
        self.animation_timer = 0
        self.is_animating = False
        self.frame_duration = 100  # milliseconds per frame
        self.generate_frames()
    
    def trigger_animation(self):
        self.is_animating = True
        self.current_frame = 0
        self.animation_timer = pygame.time.get_ticks()

    def update(self):
        if not self.is_animating:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > self.frame_duration:
            self.current_frame += 1
            self.animation_timer = current_time
            if self.current_frame >= len(self.frames):
                self.current_frame = 0
                self.is_animating = False

    def get_current_frame(self):
        return self.frames[self.current_frame]

class MineralIcon(PixelIcon):
    def generate_frames(self):
        # Crystal/diamond shape with sparkle animation
        base_frame = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        colors = [(139, 69, 19), (160, 82, 45), (205, 133, 63)]  # Brown shades
        
        # Frame 1 - Basic crystal
        crystal = [
            [0,0,1,1,0,0],
            [0,1,1,1,1,0],
            [1,1,1,1,1,1],
            [1,1,1,1,1,1],
            [0,1,1,1,1,0],
            [0,0,1,1,0,0]
        ]
        
        for frame_num in range(4):
            frame = base_frame.copy()
            for y, row in enumerate(crystal):
                for x, pixel in enumerate(row):
                    if pixel:
                        color = colors[(x + y + frame_num) % len(colors)]
                        frame.set_at((x, y), color)
            
            # Add sparkle at different positions
            sparkle_pos = [(1, 1), (4, 1), (2, 3), (3, 4)][frame_num]
            frame.set_at(sparkle_pos, (255, 255, 255))
            
            self.frames.append(frame)

class PlantIcon(PixelIcon):
    def generate_frames(self):
        # Sprouting plant animation
        base_frame = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        colors = [(34, 139, 34), (50, 205, 50), (0, 255, 0)]  # Green shades
        
        frames_data = [
            # Frame 1 - Small sprout
            [[0,0,0,1,0,0],
             [0,0,1,1,1,0],
             [0,0,0,1,0,0],
             [0,0,0,1,0,0],
             [0,0,0,1,0,0],
             [0,0,1,1,1,0]],
            
            # Frame 2 - Growing
            [[0,0,1,1,0,0],
             [0,1,1,1,1,0],
             [0,0,1,1,0,0],
             [0,0,1,1,0,0],
             [0,1,1,1,1,0],
             [1,1,1,1,1,1]],
            
            # Frame 3 - Blooming
            [[0,1,1,1,1,0],
             [1,1,1,1,1,1],
             [0,1,1,1,1,0],
             [0,0,1,1,0,0],
             [0,1,1,1,1,0],
             [1,1,1,1,1,1]],
            
            # Frame 4 - Full bloom with movement
            [[1,1,1,1,1,1],
             [1,1,1,1,1,1],
             [0,1,1,1,1,0],
             [0,0,1,1,0,0],
             [0,1,1,1,1,0],
             [1,1,1,1,1,1]]
        ]
        
        for frame_data in frames_data:
            frame = base_frame.copy()
            for y, row in enumerate(frame_data):
                for x, pixel in enumerate(row):
                    if pixel:
                        color = colors[(x + y) % len(colors)]
                        frame.set_at((x, y), color)
            self.frames.append(frame)

class ColonyIcon(PixelIcon):
    def generate_frames(self):
        # Factory-like icon with moving parts
        base_frame = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        colors = {
            'base': (100, 100, 100),  # Gray base
            'light': (0, 255, 0),     # Green light
            'dark': (50, 50, 50),     # Dark details
            'highlight': (150, 150, 150)  # Light gray highlights
        }
        
        frames_data = [
            # Frame 1 - Basic factory with lights off
            [[1,1,1,1,1,1],
             [1,2,1,2,1,1],
             [1,1,1,1,1,1],
             [0,1,2,1,0,0],
             [0,1,1,1,0,0],
             [1,1,1,1,1,1]],
            
            # Frame 2 - Lights on, gear position 1
            [[1,1,1,1,1,1],
             [1,3,1,3,1,1],
             [1,1,4,1,1,1],
             [0,1,2,1,0,0],
             [0,1,1,1,0,0],
             [1,1,1,1,1,1]],
            
            # Frame 3 - Lights blinking, gear position 2
            [[1,1,1,1,1,1],
             [1,2,1,3,1,1],
             [1,1,4,1,1,1],
             [0,1,4,1,0,0],
             [0,1,1,1,0,0],
             [1,1,1,1,1,1]],
            
            # Frame 4 - Different lights, gear position 3
            [[1,1,1,1,1,1],
             [1,3,1,2,1,1],
             [1,1,4,1,1,1],
             [0,1,2,1,0,0],
             [0,1,4,1,0,0],
             [1,1,1,1,1,1]]
        ]
        
        color_map = {
            0: (0, 0, 0, 0),        # Transparent
            1: colors['base'],       # Base structure
            2: colors['dark'],       # Dark details
            3: colors['light'],      # Active lights
            4: colors['highlight']   # Moving parts
        }
        
        for frame_data in frames_data:
            frame = base_frame.copy()
            for y, row in enumerate(frame_data):
                for x, pixel in enumerate(row):
                    if pixel:
                        frame.set_at((x, y), color_map[pixel])
            self.frames.append(frame)

class AntIcon(PixelIcon):
    def generate_frames(self):
        # Ant with moving legs and antennae
        base_frame = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        colors = {
            'body': (0, 0, 0),        # Black body
            'highlight': (40, 40, 40)  # Slight highlight
        }
        
        frames_data = [
            # Frame 1 - Basic position
            [[0,0,1,0,0,0],
             [0,0,1,1,0,0],
             [1,1,1,1,1,0],
             [0,1,1,1,0,0],
             [1,0,1,0,1,0],
             [0,1,0,1,0,0]],
            
            # Frame 2 - Legs position 2
            [[0,0,1,0,0,0],
             [0,1,1,1,0,0],
             [1,1,1,1,1,0],
             [0,1,1,1,0,0],
             [0,1,1,1,0,0],
             [1,0,0,0,1,0]],
            
            # Frame 3 - Legs position 3
            [[0,1,1,0,0,0],
             [0,0,1,1,0,0],
             [1,1,1,1,1,0],
             [0,1,1,1,0,0],
             [1,0,1,0,1,0],
             [0,1,0,1,0,0]],
            
            # Frame 4 - Legs position 4
            [[0,0,1,0,1,0],
             [0,0,1,1,0,0],
             [1,1,1,1,1,0],
             [0,1,1,1,0,0],
             [0,1,1,1,0,0],
             [1,0,0,0,1,0]]
        ]
        
        for frame_data in frames_data:
            frame = base_frame.copy()
            for y, row in enumerate(frame_data):
                for x, pixel in enumerate(row):
                    if pixel:
                        # Add some subtle variation to the black
                        color = colors['highlight'] if (x + y) % 3 == 0 else colors['body']
                        frame.set_at((x, y), color)
            self.frames.append(frame)

class SkullIcon(PixelIcon):
    def __init__(self, size):
        super().__init__(size)
        self.flash_duration = 500  # Flash duration in milliseconds
        self.flash_start = 0
        self.is_flashing = False

    def generate_frames(self):
        """Generate pixel art for skull icon"""
        base_frame = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Skull design (8x8 grid)
        skull_layout = [
            " XXXX ",  # Top
            "XXXXXX",  # Head
            "XX##XX",  # Eyes (# for dark spots)
            "XXXXXX",
            " XXXX ",
            "  XX  ",  # Jaw
            " XXXX "   # Base
        ]
        
        # Colors
        colors = {
            'X': (220, 220, 220),  # Bone white
            '#': (40, 40, 40)      # Dark for eyes
        }
        
        # Generate normal and flashing frames
        normal_frame = base_frame.copy()
        flash_frame = base_frame.copy()
        
        for y, row in enumerate(skull_layout):
            for x, char in enumerate(row):
                if char in colors:
                    # Normal color
                    normal_frame.set_at((x, y), colors[char])
                    # Red flash color
                    if char == 'X':
                        flash_frame.set_at((x, y), (255, 0, 0))
                    else:
                        flash_frame.set_at((x, y), colors[char])
        
        self.frames = [normal_frame, flash_frame]

    def trigger_flash(self):
        """Start the flash animation"""
        self.is_flashing = True
        self.flash_start = pygame.time.get_ticks()

    def update(self):
        """Update flash state"""
        if self.is_flashing:
            current_time = pygame.time.get_ticks()
            if current_time - self.flash_start > self.flash_duration:
                self.is_flashing = False
                self.current_frame = 0
            else:
                self.current_frame = 1

class SettingsIcon(PixelIcon):
    def __init__(self, size):
        super().__init__(size)
        self.is_open = False
        
    def generate_frames(self):
        """Generate pixel art for settings gear icon"""
        base_frame = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # More mechanical gear icon design (12x12 grid for better detail)
        gear_layout = [
            "     #      ",  # Outer teeth
            "   #    #   ",
            "     ##     ",  # Inner circle starts
            " #  ####  # ",
            "   ######   ",  # Core of gear
            "# ######## #",
            "   ######   ",
            " #  ####  # ",
            "     ##     ",  # Inner circle ends
            "   #    #   ",
            "      #     "   # Outer teeth
        ]
        
        # Colors
        normal_color = (180, 180, 180)  # Slightly darker gray for better contrast
        hover_color = (255, 255, 255)  # White
        
        # Scale factor for the 11x11 design to fit the icon size
        scale = self.size // 11
        
        # Generate normal and hover frames
        for color in [normal_color, hover_color]:
            frame = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            for y, row in enumerate(gear_layout):
                for x, pixel in enumerate(row):
                    if pixel == '#':
                        # Draw scaled pixel with slight offset to center
                        pygame.draw.rect(frame, color, 
                                       (x * scale + scale//2, 
                                        y * scale + scale//2, 
                                        scale, scale))
            
            self.frames.append(frame)

class SettingsWindow:
    def __init__(self, screen_width, screen_height):
        self.width = 200
        self.height = 150
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        self.sound_volume = 1.0
        self.music_volume = 0.5
        self.is_visible = False
        
        # Slider properties
        self.slider_width = 150
        self.slider_height = 8
        self.knob_size = 12
        self.sound_slider_y = 50
        self.music_slider_y = 90
        
        # Create window surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
    def draw(self, screen):
        if not self.is_visible:
            return
            
        # Draw window background
        pygame.draw.rect(self.surface, (40, 40, 40, 230), (0, 0, self.width, self.height))
        pygame.draw.rect(self.surface, (80, 80, 80, 255), (0, 0, self.width, self.height), 2)
        
        # Draw title
        font = pygame.font.Font(None, 24)
        title = font.render("Settings", True, (255, 255, 255))
        self.surface.blit(title, (self.width//2 - title.get_width()//2, 10))
        
        # Draw sliders
        self.draw_slider("Sound Effects", self.sound_volume, self.sound_slider_y)
        self.draw_slider("Music", self.music_volume, self.music_slider_y)
        
        screen.blit(self.surface, (self.x, self.y))
    
    def draw_slider(self, label, value, y):
        font = pygame.font.Font(None, 20)
        text = font.render(label, True, (255, 255, 255))
        self.surface.blit(text, (10, y - 20))
        
        # Draw slider track
        slider_x = (self.width - self.slider_width) // 2
        pygame.draw.rect(self.surface, (60, 60, 60), 
                        (slider_x, y, self.slider_width, self.slider_height))
        
        # Draw filled portion
        filled_width = int(self.slider_width * value)
        pygame.draw.rect(self.surface, (100, 100, 255), 
                        (slider_x, y, filled_width, self.slider_height))
        
        # Draw knob
        knob_x = slider_x + filled_width - self.knob_size//2
        pygame.draw.circle(self.surface, (255, 255, 255),
                         (knob_x + self.knob_size//2, y + self.slider_height//2),
                         self.knob_size//2)
    
    def handle_click(self, pos):
        if not self.is_visible:
            return False
            
        local_x = pos[0] - self.x
        local_y = pos[1] - self.y
        
        # Check if click is within window
        if 0 <= local_x <= self.width and 0 <= local_y <= self.height:
            # Handle sound slider
            if self.is_on_slider(local_x, local_y, self.sound_slider_y):
                self.sound_volume = self.get_slider_value(local_x)
                return True
            # Handle music slider
            elif self.is_on_slider(local_x, local_y, self.music_slider_y):
                self.music_volume = self.get_slider_value(local_x)
                return True
        return False
    
    def is_on_slider(self, x, y, slider_y):
        slider_x = (self.width - self.slider_width) // 2
        return (slider_x <= x <= slider_x + self.slider_width and
                slider_y - self.knob_size//2 <= y <= slider_y + self.knob_size//2)
    
    def get_slider_value(self, x):
        slider_x = (self.width - self.slider_width) // 2
        return max(0, min(1, (x - slider_x) / self.slider_width))

class SettingsMenu:
    def __init__(self, screen, game_sounds):
        self.screen = screen
        self.game_sounds = game_sounds
        self.visible = False
        
        # Settings window properties
        window_width = 300
        window_height = 200
        self.window_rect = pygame.Rect(
            screen.get_width() - window_width - 10,
            screen.get_height() - window_height - 10,
            window_width,
            window_height
        )
        
        # Slider properties
        self.slider_width = 200
        self.slider_height = 20
        self.music_slider_rect = pygame.Rect(
            self.window_rect.x + 50,
            self.window_rect.y + 50,
            self.slider_width,
            self.slider_height
        )
        self.sound_slider_rect = pygame.Rect(
            self.window_rect.x + 50,
            self.window_rect.y + 100,
            self.slider_width,
            self.slider_height
        )
        
        # Settings button (gear icon)
        self.button_size = 32
        self.settings_button = pygame.Rect(
            screen.get_width() - self.button_size - 10,
            screen.get_height() - self.button_size - 10,
            self.button_size,
            self.button_size
        )
        
        self.dragging_music = False
        self.dragging_sound = False
        
        # Add tooltip text
        self.tooltip_text = "Settings - Adjust music and sound effect volumes"
        self.tooltip_font = pygame.font.Font(None, UI.Tooltips.FONT_SIZE)
        
        # Initialize pixel icons
        self.pixel_icons = {
            'settings': SettingsIcon(self.button_size)
        }
        
        # Add tooltip corners
        self.tooltip_corners = self.generate_tooltip_corners()

    def draw(self):
        # Draw settings button and menu
        pygame.draw.rect(self.screen, (50, 50, 50), self.settings_button)
        settings_icon = self.pixel_icons['settings'].get_current_frame()
        self.screen.blit(settings_icon, self.settings_button)
        
        # Draw tooltip on hover
        mouse_pos = pygame.mouse.get_pos()
        if self.settings_button.collidepoint(mouse_pos):
            # Use HUD's tooltip drawing method
            HUD.draw_tooltip(self, self.screen, self.tooltip_text, self.settings_button, self.tooltip_font)
        
        # Draw settings window if visible
        if self.visible:
            # Draw settings window
            pygame.draw.rect(self.screen, (50, 50, 50), self.window_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), self.window_rect, 2)
            
            # Draw sliders
            pygame.draw.rect(self.screen, (150, 150, 150), self.music_slider_rect)
            pygame.draw.rect(self.screen, (150, 150, 150), self.sound_slider_rect)
            
            # Draw slider handles
            music_handle_x = self.music_slider_rect.x + (self.music_slider_rect.width * self.game_sounds.music_volume)
            sound_handle_x = self.sound_slider_rect.x + (self.sound_slider_rect.width * self.game_sounds.sound_volume)
            
            pygame.draw.rect(self.screen, (200, 200, 200), 
                           (music_handle_x - 5, self.music_slider_rect.y, 10, self.slider_height))
            pygame.draw.rect(self.screen, (200, 200, 200), 
                           (sound_handle_x - 5, self.sound_slider_rect.y, 10, self.slider_height))
            
            # Draw labels
            font = pygame.font.Font(None, 24)
            music_label = font.render("Music", True, (200, 200, 200))
            sound_label = font.render("Sound Effects", True, (200, 200, 200))
            
            self.screen.blit(music_label, (self.window_rect.x + 50, self.music_slider_rect.y - 25))
            self.screen.blit(sound_label, (self.window_rect.x + 50, self.sound_slider_rect.y - 25))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.settings_button.collidepoint(event.pos):
                self.visible = not self.visible
            elif self.visible:
                if self.music_slider_rect.collidepoint(event.pos):
                    self.dragging_music = True
                elif self.sound_slider_rect.collidepoint(event.pos):
                    self.dragging_sound = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_music = False
            self.dragging_sound = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_music:
                rel_x = (event.pos[0] - self.music_slider_rect.x) / self.slider_width
                self.game_sounds.music_volume = max(0, min(1, rel_x))
                self.game_sounds.set_volumes(self.game_sounds.sound_volume, self.game_sounds.music_volume)
            
            elif self.dragging_sound:
                rel_x = (event.pos[0] - self.sound_slider_rect.x) / self.slider_width
                self.game_sounds.sound_volume = max(0, min(1, rel_x))
                self.game_sounds.set_volumes(self.game_sounds.sound_volume, self.game_sounds.music_volume)

    def generate_tooltip_corners(self):
        """Generate pixel art corners for tooltips"""
        corner_design = [
            " ##",  # 3x3 corner piece
            "# #",
            "## "
        ]
        
        corners = {}
        corner_size = 3
        
        for position in ['tl', 'tr', 'bl', 'br']:
            corner = pygame.Surface((corner_size, corner_size), pygame.SRCALPHA)
            
            for y, row in enumerate(corner_design):
                for x, pixel in enumerate(row):
                    if pixel == '#':
                        color = UI.Tooltips.BORDER_COLOR
                        draw_x = x if 'l' in position else (corner_size - 1 - x)
                        draw_y = y if 't' in position else (corner_size - 1 - y)
                        corner.set_at((draw_x, draw_y), color)
            
            corners[position] = corner
            
        return corners

class PixelLogo:
    def __init__(self, width=300):
        """Create Amuke Games pixel logo"""
        # Base colors from the original logo
        self.colors = {
            'orange': (255, 140, 70),   # Top stripe
            'pink': (255, 80, 120),     # Middle stripe
            'blue': (70, 180, 255),     # Bottom stripe
            'plus': (255, 255, 255, 180)  # Plus symbols with transparency
        }
        
        # Calculate height based on original proportions
        height = int(width * 0.3)  # Thinner aspect ratio for the stripes
        
        # Create surface with alpha channel
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw the three stripes
        stripe_height = height // 3
        self.surface.fill(self.colors['orange'], (0, 0, width, stripe_height))
        self.surface.fill(self.colors['pink'], (0, stripe_height, width, stripe_height))
        self.surface.fill(self.colors['blue'], (0, stripe_height * 2, width, stripe_height))
        
        # Add floating plus symbols
        self._add_plus_symbols(width, height)
    
    def _add_plus_symbols(self, width, height):
        """Add floating plus symbols around stripes"""
        plus_sizes = [(4, 4), (6, 6)]  # Smaller plus sizes
        num_plus = 12  # Fewer plus symbols
        
        for _ in range(num_plus):
            size = random.choice(plus_sizes)
            x = random.randint(0, width - size[0])
            y = random.randint(0, height - size[1])
            
            # Draw plus
            self._draw_plus(x, y, size[0], self.colors['plus'])
    
    def _draw_plus(self, x, y, size, color):
        """Draw a single plus symbol"""
        thickness = max(1, size // 3)  # Thinner plus symbols
        
        # Horizontal line
        for i in range(size):
            for t in range(thickness):
                py = y + (size // 2) - (thickness // 2) + t
                if 0 <= py < self.surface.get_height():
                    self.surface.set_at((x + i, py), color)
        
        # Vertical line
        for i in range(size):
            for t in range(thickness):
                px = x + (size // 2) - (thickness // 2) + t
                if 0 <= px < self.surface.get_width():
                    self.surface.set_at((px, y + i), color)
    
    def get_surface(self):
        """Return the rendered logo surface"""
        return self.surface

class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, UI.Tooltips.FONT_SIZE)
        self.colors = COLORS
        self.tooltips = TOOLTIP_TEXTS
        self.tooltip_regions = {}
        self.active_tooltip = None
        self.frame_padding = 8
        
        # Create animated pixel icons
        self.pixel_icons = {
            'mineral': MineralIcon(32),
            'plant': PlantIcon(32),
            'colony': ColonyIcon(32),
            'ant': AntIcon(32),
            'skull': SkullIcon(32),  # Add skull icon
            'settings': SettingsIcon(32)  # Add settings icon
        }
        
        self.generate_pixel_frame()
        
        # Layout positions will be calculated when drawing
        self.colony_icon_pos = (0, 0)
        self.hover_element = None
        self.kills = 0  # Track snake kills
        
        # Add tooltip frame designs
        self.tooltip_corners = self.generate_tooltip_corners()

    def generate_pixel_frame(self):
        """Generate pixelated frame/bubble surface"""
        # Create single frame across the top - increased height for larger icons
        width = WINDOW_WIDTH - 10
        height = 90  # Increased from 70 to 90 for larger icons
        self.top_frame = self.create_pixel_frame(width, height)

    def create_pixel_frame(self, width, height):
        """Create a pixelated frame surface"""
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Frame colors
        border = (80, 80, 80, 230)  # Dark gray, semi-transparent
        fill = (40, 40, 40, 180)    # Darker fill, more transparent
        
        # Fill background
        pygame.draw.rect(frame, fill, (2, 2, width-4, height-4))
        
        # Draw pixelated border
        pixels = [
            # Top-left corner
            [(0,0), (1,0), (2,0), (0,1), (0,2)],
            # Top-right corner
            [(width-3,0), (width-2,0), (width-1,0), (width-1,1), (width-1,2)],
            # Bottom-left corner
            [(0,height-3), (0,height-2), (0,height-1), (1,height-1), (2,height-1)],
            # Bottom-right corner
            [(width-1,height-3), (width-1,height-2), (width-1,height-1), 
             (width-2,height-1), (width-3,height-1)]
        ]
        
        # Draw corner pixels and edges
        for corner in pixels:
            for x, y in corner:
                frame.set_at((x, y), border)
        
        # Draw edges
        for i in range(3, width-3):
            frame.set_at((i, 0), border)      # Top
            frame.set_at((i, height-1), border) # Bottom
        for i in range(3, height-3):
            frame.set_at((0, i), border)      # Left
            frame.set_at((width-1, i), border) # Right
            
        # Add subtle line divider in the middle
        mid_x = width // 2
        for y in range(4, height-4):
            frame.set_at((mid_x, y), (60, 60, 60, 100))
            
        return frame

    def calculate_layout(self, screen_width):
        """Calculate positions based on screen size"""
        # Calculate colony icon position (top right)
        self.colony_icon_pos = (
            screen_width - HUD_RIGHT_MARGIN,
            HUD_TOP_MARGIN
        )

    def draw_resource_bar(self, surface, x, y, value, max_value, color, tooltip_key):
        """Draw a resource bar with border and register tooltip region"""
        # Draw background
        pygame.draw.rect(surface, self.colors['background'], 
                        (x, y, BAR_WIDTH, BAR_HEIGHT))
        
        # Draw filled portion
        fill_width = int((value / max_value) * BAR_WIDTH)
        if fill_width > 0:
            pygame.draw.rect(surface, color, 
                           (x, y, fill_width, BAR_HEIGHT))
        
        # Draw border
        pygame.draw.rect(surface, self.colors['bar_border'], 
                        (x, y, BAR_WIDTH, BAR_HEIGHT), 1)

        # Register tooltip region
        self.tooltip_regions[tooltip_key] = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)

    def generate_tooltip_corners(self):
        """Generate pixel art corners for tooltips"""
        corner_design = [
            " ##",  # 3x3 corner piece
            "# #",
            "## "
        ]
        
        corners = {}
        corner_size = 3
        
        for position in ['tl', 'tr', 'bl', 'br']:
            corner = pygame.Surface((corner_size, corner_size), pygame.SRCALPHA)
            
            for y, row in enumerate(corner_design):
                for x, pixel in enumerate(row):
                    if pixel == '#':
                        color = UI.Tooltips.BORDER_COLOR
                        draw_x = x if 'l' in position else (corner_size - 1 - x)
                        draw_y = y if 't' in position else (corner_size - 1 - y)
                        corner.set_at((draw_x, draw_y), color)
            
            corners[position] = corner
            
        return corners

    def draw_tooltip(self, screen, text, anchor_rect, font=None):
        """Draw tooltip with decorative frame"""
        if font is None:
            font = self.font
            
        # Create tooltip surface
        tooltip_surface = font.render(text, True, UI.Tooltips.TEXT_COLOR)
        tooltip_rect = tooltip_surface.get_rect()
        
        # Calculate initial position (above the element)
        tooltip_rect.centerx = anchor_rect.centerx
        tooltip_rect.bottom = anchor_rect.top - UI.Tooltips.OFFSET_Y
        
        # Create background rect with extra padding for decoration
        padding = UI.Tooltips.PADDING + 3  # Extra space for corners
        background_rect = tooltip_rect.inflate(padding * 2, padding * 2)
        
        # Adjust position to keep within screen bounds
        if background_rect.left < 0:
            offset = -background_rect.left
            background_rect.left = 0
            tooltip_rect.left += offset
        elif background_rect.right > screen.get_width():
            offset = screen.get_width() - background_rect.right
            background_rect.right = screen.get_width()
            tooltip_rect.left += offset
            
        if background_rect.top < 0:
            tooltip_rect.top = anchor_rect.bottom + UI.Tooltips.OFFSET_Y
            background_rect = tooltip_rect.inflate(padding * 2, padding * 2)
        
        # Draw main background
        pygame.draw.rect(screen, UI.Tooltips.BACKGROUND, background_rect)
        
        # Draw decorative border
        border_rect = background_rect.inflate(-2, -2)
        pygame.draw.rect(screen, UI.Tooltips.BORDER_COLOR, border_rect, 1)
        
        # Draw corners
        corner_positions = {
            'tl': background_rect.topleft,
            'tr': (background_rect.right - 3, background_rect.top),
            'bl': (background_rect.left, background_rect.bottom - 3),
            'br': (background_rect.right - 3, background_rect.bottom - 3)
        }
        
        for position, pos in corner_positions.items():
            screen.blit(self.tooltip_corners[position], pos)
        
        # Draw text
        screen.blit(tooltip_surface, tooltip_rect)

    def update(self, mouse_pos):
        """Update tooltip state based on mouse position"""
        self.active_tooltip = None
        for key, rect in self.tooltip_regions.items():
            if rect.collidepoint(mouse_pos):
                self.active_tooltip = key
                break

    def draw(self, surface, colonies, ants):
        main_colony = colonies[0] if colonies else None
        if main_colony:
            # Draw single top frame
            surface.blit(self.top_frame, (5, 5))
            
            # Left side - Resources (adjusted positions)
            self.draw_resource_indicator(surface, 
                pos=(25, 15),
                icon_type='mineral',
                label="Minerals",
                value=main_colony.resources['minerals'],
                max_value=UI.Bars.MAX_MINERAL_VALUE,
                color=UI.Bars.MINERAL)
                
            self.draw_resource_indicator(surface,
                pos=(25, 50),
                icon_type='plant',
                label="Plants",
                value=main_colony.resources['plants'],
                max_value=UI.Bars.MAX_PLANT_VALUE,
                color=UI.Bars.PLANT)

            # Right side - Status (adjusted positions)
            right_section_x = WINDOW_WIDTH // 2 + 25
            self.draw_status_indicator(surface,
                pos=(right_section_x, 15),
                icon_type='colony',
                label="Colonies",
                value=len(colonies))
                
            self.draw_status_indicator(surface,
                pos=(right_section_x, 50),
                icon_type='ant',
                label="Ants",
                value=len(ants))

            # Draw kill counter with label
            self.draw_status_indicator(surface,
                pos=(right_section_x + 120, 15),
                icon_type='skull',
                label="Kills",
                value=self.kills)

            # Handle tooltips
            mouse_pos = pygame.mouse.get_pos()
            self.handle_tooltips(surface, mouse_pos, main_colony, colonies, ants)

            # Draw tooltips for hovered elements
            if self.hover_element:
                element_rect = self.tooltip_regions.get(self.hover_element)
                if element_rect:
                    tooltip_text = self.get_tooltip_text(self.hover_element, colonies, ants)
                    self.draw_tooltip(surface, tooltip_text, element_rect)

    def draw_status_indicator(self, surface, pos, icon_type, label, value):
        """Draw a status indicator with icon, label and value"""
        icon = self.pixel_icons[icon_type]
        icon.update()
        
        # Draw icon
        surface.blit(icon.get_current_frame(), pos)
        
        # Draw label with shadow
        label_shadow = self.font.render(label, True, (0, 0, 0, 128))
        label_text = self.font.render(label, True, (255, 255, 255))
        
        # Position label after icon
        surface.blit(label_shadow, (pos[0] + 45, pos[1] - 2))  # Slightly above center
        surface.blit(label_text, (pos[0] + 44, pos[1] - 3))
        
        # Draw value with shadow
        value_text = str(value)
        shadow_value = self.font.render(value_text, True, (0, 0, 0, 128))
        value_surface = self.font.render(value_text, True, (255, 255, 255))
        
        # Position value below label
        surface.blit(shadow_value, (pos[0] + 45, pos[1] + 12))
        surface.blit(value_surface, (pos[0] + 44, pos[1] + 11))

    def draw_resource_indicator(self, surface, pos, icon_type, label, value, max_value, color):
        """Draw a resource indicator with icon, label, bar and value"""
        icon = self.pixel_icons[icon_type]
        icon.update()
        
        # Draw icon
        surface.blit(icon.get_current_frame(), pos)
        
        # Draw label with shadow
        label_shadow = self.font.render(label, True, (0, 0, 0, 128))
        label_text = self.font.render(label, True, (255, 255, 255))
        
        # Position label after icon
        surface.blit(label_shadow, (pos[0] + 45, pos[1] - 2))  # Slightly above center
        surface.blit(label_text, (pos[0] + 44, pos[1] - 3))
        
        # Draw bar
        bar_rect = pygame.Rect(pos[0] + 44, pos[1] + 13, 80, 8)
        
        # Bar border
        pygame.draw.rect(surface, (60, 60, 60), 
                        (bar_rect.x-1, bar_rect.y-1, bar_rect.width+2, bar_rect.height+2))
        # Bar background
        pygame.draw.rect(surface, UI.Bars.BACKGROUND, bar_rect)
        # Bar fill
        fill_width = int((value / max_value) * 80)
        if fill_width > 0:
            pygame.draw.rect(surface, color, 
                           (bar_rect.x, bar_rect.y, min(fill_width, 80), bar_rect.height))
        
        # Draw value with shadow
        value_text = f"{value}"
        shadow_value = self.font.render(value_text, True, (0, 0, 0, 128))
        value_surface = self.font.render(value_text, True, (255, 255, 255))
        
        # Position value to the right of bar
        surface.blit(shadow_value, (pos[0] + 134, pos[1] + 12))
        surface.blit(value_surface, (pos[0] + 133, pos[1] + 11))

    def handle_tooltips(self, surface, mouse_pos, main_colony, colonies, ants):
        """Show detailed tooltips on hover"""
        tooltips = {
            'minerals': {
                'rect': pygame.Rect(10, 10, 90, 20),
                'text': f"Minerals: {main_colony.resources['minerals']}/{UI.Bars.MAX_MINERAL_VALUE}\n"
                       f"Used for:\n"
                       f"• New Ant ({Economy.Costs.ANT_MINERALS})\n"
                       f"• New Colony ({Economy.Costs.NEW_COLONY_MINERALS})"
            },
            'plants': {
                'rect': pygame.Rect(10, 35, 90, 20),
                'text': f"Plants: {main_colony.resources['plants']}/{UI.Bars.MAX_PLANT_VALUE}\n"
                       f"Used for:\n"
                       f"• New Ant ({Economy.Costs.ANT_PLANTS})\n"
                       f"• New Colony ({Economy.Costs.NEW_COLONY_PLANTS})"
            },
            'colonies': {
                'rect': pygame.Rect(WINDOW_WIDTH - 60, 10, 50, 20),
                'text': f"Colonies: {len(colonies)}\n"
                       f"Click colony + have resources\n"
                       f"to expand your network"
            },
            'ants': {
                'rect': pygame.Rect(WINDOW_WIDTH - 60, 35, 50, 20),
                'text': f"Ants: {len(ants)}\n"
                       f"Click blue indicator on colony\n"
                       f"to spawn new ants"
            }
        }

        # Check for hover and draw tooltip with new style
        for key, data in tooltips.items():
            if data['rect'].collidepoint(mouse_pos):
                self.draw_tooltip(surface, data['text'], data['rect'])
                break

    def trigger_icon_animation(self, icon_type):
        """Trigger animation for a specific icon"""
        if icon_type in self.pixel_icons:
            self.pixel_icons[icon_type].trigger_animation() 

    def increment_kills(self):
        """Increment kill counter and trigger skull flash"""
        self.kills += 1
        self.pixel_icons['skull'].trigger_flash() 