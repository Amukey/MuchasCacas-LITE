import pygame
import math
import random

class GameObject:
    def __init__(self, position, size, color):
        self.position = position
        self.size = size
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, pygame.Rect(
            self.position[0] - self.size // 2,
            self.position[1] - self.size // 2,
            self.size,
            self.size
        ))

class Rock(GameObject):
    # Rock colors
    ROCK_COLORS = {
        'base': [(139, 137, 137), (145, 142, 142), (131, 129, 129)],  # Gray variations
        'dark': [(101, 99, 99), (90, 88, 88)],  # Darker shades for depth
        'shine': [(255, 255, 255), (220, 220, 220)]  # Shimmer colors
    }
    
    # Different rock shapes (X for rock, S for shine position)
    ROCK_SHAPES = [
        # Triangular rock
        ["  X  ",
         " XXX ",
         "XXXSX",
         "XXXXX"],
        
        # Round rock
        [" XXX ",
         "XXXXX",
         "XXSXX",
         "XXXXX",
         " XXX "],
        
        # Angular rock
        ["  XX ",
         "XXXXX",
         "XXSXX",
         " XXX ",
         " XX  "],
        
        # Oval rock
        [" XXX ",
         "XXXSX",
         "XXXXX",
         " XXX "],
    ]

    def __init__(self, position):
        super().__init__(position, 20, (139, 69, 19))
        self.minerals = 50
        self.original_size = 40
        self.size = self.original_size
        self.shape = random.choice(self.ROCK_SHAPES)
        self.pixels = self.generate_rock_pixels()
        self.shine_offset = random.random() * 6.28  # Random start phase for shimmer

    def generate_rock_pixels(self):
        """Generate pixel art for rock"""
        pixels = []
        
        # Convert shape to colored pixels with positions
        for y, row in enumerate(self.shape):
            for x, char in enumerate(row):
                if char == 'X':
                    # Randomly choose between base and dark colors for variety
                    color = random.choice(self.ROCK_COLORS['base'] if random.random() > 0.3 
                                        else self.ROCK_COLORS['dark'])
                    pixels.append(((x, y), color, 'rock'))
                elif char == 'S':
                    # Mark shine position
                    pixels.append(((x, y), random.choice(self.ROCK_COLORS['shine']), 'shine'))
        
        return pixels

    def draw(self, surface, alpha=255):
        if self.minerals <= 0:
            return

        # Calculate size scale based on remaining minerals
        scale = self.minerals / 50
        current_size = int(self.original_size * scale)
        pixel_size = max(3, int(5 * scale))  # Slightly larger pixels for rocks

        # Calculate shimmer effect
        time = pygame.time.get_ticks() / 1000
        shine_intensity = (math.sin(time * 2 + self.shine_offset) + 1) / 2  # 0 to 1

        # Draw each pixel of the rock
        for (x, y), color, part in self.pixels:
            if part == 'shine':
                # Interpolate between rock color and shine color based on intensity
                base_color = self.ROCK_COLORS['base'][0]
                shine_color = self.ROCK_COLORS['shine'][0]
                current_color = [
                    int(base_color[i] + (shine_color[i] - base_color[i]) * shine_intensity)
                    for i in range(3)
                ]
            else:
                current_color = color

            current_color = (*current_color, alpha)  # Add alpha to color tuple

            pixel_rect = pygame.Rect(
                self.position[0] + (x * pixel_size) - (current_size // 2),
                self.position[1] + (y * pixel_size) - (current_size // 2),
                pixel_size,
                pixel_size
            )
            pygame.draw.rect(surface, current_color, pixel_rect)

        # Draw mineral indicator with alpha
        if self.minerals < 50:
            indicator_bg = (*((200, 200, 200)), alpha)  # Gray background with alpha
            indicator_fg = (*((139, 69, 19)), alpha)    # Brown with alpha
            
            pygame.draw.rect(surface, indicator_bg,
                           (self.position[0] - 10, self.position[1] + 20,
                            20, 4))
            pygame.draw.rect(surface, indicator_fg,
                           (self.position[0] - 10, self.position[1] + 20,
                            int(20 * (self.minerals / 50)), 4))

class Plant(GameObject):
    # Pine tree colors
    TREE_COLORS = {
        'leaves': [(34, 139, 34), (46, 139, 34), (40, 180, 40)],  # Different green shades
        'trunk': [(139, 69, 19), (160, 82, 45)]  # Brown shades
    }
    
    def __init__(self, position):
        super().__init__(position, 10, (0, 255, 0))
        self.resources = 30
        self.original_size = 120
        self.size = 0  # Start at size 0
        self.sway_offset = random.random() * 6.28
        self.pixels = self.generate_pine_pixels()
        
        # Growth animation properties
        self.is_growing = True
        self.growth_start = pygame.time.get_ticks()
        self.growth_duration = 1000  # 1 second to grow
        self.growth_scale = 0.0  # Start at 0%

    def generate_pine_pixels(self):
        """Generate pixel art for pine tree"""
        # Taller pine tree layout (8x12 pixels scaled up)
        pine_layout = [
            "   XX   ",  # Top
            "  XXXX  ",
            " XXXXXX ",
            "XXXXXXXX",
            "XXXXXXXX",  # Added more body
            " XXXXXX ",
            " XXXXXX ",
            "  XXXX  ",  # Bottom leaves
            "   ||   ",  # Trunk
            "   ||   ",
            "   ||   ",  # Extended trunk
            "   ||   "   # Base
        ]
        
        pixels = []
        pixel_size = 6  # Increased from 4 to 6
        
        # Convert layout to colored pixels with positions
        for y, row in enumerate(pine_layout):
            for x, char in enumerate(row):
                if char == 'X':
                    color = random.choice(self.TREE_COLORS['leaves'])
                    pixels.append(((x, y), color, 'leaf'))
                elif char == '|':
                    color = random.choice(self.TREE_COLORS['trunk'])
                    pixels.append(((x, y), color, 'trunk'))
        
        return pixels

    def update(self):
        if self.is_growing:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.growth_start
            
            if elapsed < self.growth_duration:
                # Smooth easing function for natural growth
                progress = elapsed / self.growth_duration
                self.growth_scale = self.ease_out_elastic(progress)
            else:
                self.is_growing = False
                self.growth_scale = 1.0

    def ease_out_elastic(self, x):
        """Elastic easing function for natural tree growth"""
        c4 = (2 * math.pi) / 3
        
        if x == 0:
            return 0
        elif x == 1:
            return 1
        else:
            return pow(2, -10 * x) * math.sin((x * 10 - 0.75) * c4) + 1

    def draw(self, surface, alpha=255):
        if self.resources <= 0:
            return

        # Update growth animation
        self.update()

        # Calculate current size based on growth animation
        current_size = int(self.original_size * self.growth_scale * (self.resources / 30))
        pixel_size = max(2, int(4 * self.growth_scale * (self.resources / 30)))

        # Calculate sway offset based on time
        time = pygame.time.get_ticks() / 1000
        sway = math.sin(time + self.sway_offset) * 2 * self.growth_scale  # Sway increases with growth

        # Draw each pixel of the tree
        for (x, y), color, part in self.pixels:
            # Apply sway only to leaves, not trunk
            sway_offset = sway if part == 'leaf' else 0
            
            # Add alpha to color
            current_color = (*color, alpha)
            
            pixel_rect = pygame.Rect(
                self.position[0] + (x * pixel_size) - (current_size // 2) + sway_offset,
                self.position[1] + (y * pixel_size) - (current_size // 2),
                pixel_size,
                pixel_size
            )
            pygame.draw.rect(surface, current_color, pixel_rect)

        # Draw resource indicator with alpha (only when fully grown)
        if not self.is_growing and self.resources < 30:
            indicator_bg = (*((200, 200, 200)), alpha)
            indicator_fg = (*(0, 255, 0), alpha)
            
            pygame.draw.rect(surface, indicator_bg,
                           (self.position[0] - 10, self.position[1] + 20,
                            20, 4))
            pygame.draw.rect(surface, indicator_fg,
                           (self.position[0] - 10, self.position[1] + 20,
                            int(20 * (self.resources / 30)), 4))

class Bush(GameObject):
    # Bush colors
    BUSH_COLORS = {
        'leaves': [(0, 100, 0), (34, 139, 34), (0, 128, 0)],  # Darker green shades for bush
        'berries': [(220, 20, 60), (178, 34, 34), (139, 0, 0)],  # Red berry colors
        'stem': [(101, 67, 33), (139, 69, 19)]  # Dark brown shades
    }
    
    def __init__(self, position):
        super().__init__(position, 15, (0, 200, 0))
        self.resources = 10  # As per documentation
        self.original_size = 40  # Smaller than trees
        self.size = self.original_size
        self.sway_offset = random.random() * 6.28
        self.has_berries = random.random() > 0.5  # 50% chance of having berries
        self.pixels = self.generate_bush_pixels()

    def generate_bush_pixels(self):
        """Generate pixel art for berry bush"""
        # Bush layout (6x6 pixels scaled up)
        bush_layout = [
            " XXXX ",  # Top
            "XXXXXX",
            "XXXXXX",  # Middle
            "XXXXXX",
            " /||\\",  # Stems (fixed escape sequence)
            "  ||  "   # Base
        ]
        
        # Berry positions (only if bush has berries)
        berry_positions = [(1, 1), (4, 1), (2, 2), (3, 3)] if self.has_berries else []
        
        pixels = []
        
        # Convert layout to colored pixels with positions
        for y, row in enumerate(bush_layout):
            for x, char in enumerate(row):
                if char == 'X':
                    # Check if this position should be a berry
                    if (x, y) in berry_positions:
                        color = random.choice(self.BUSH_COLORS['berries'])
                        pixels.append(((x, y), color, 'berry'))
                    else:
                        color = random.choice(self.BUSH_COLORS['leaves'])
                        pixels.append(((x, y), color, 'leaf'))
                elif char in ['/','\\','|']:
                    color = random.choice(self.BUSH_COLORS['stem'])
                    pixels.append(((x, y), color, 'stem'))
        
        return pixels

    def draw(self, surface, alpha=255):
        if self.resources <= 0:
            return

        # Calculate size scale based on remaining resources
        scale = self.resources / 10
        current_size = int(self.original_size * scale)
        pixel_size = max(2, int(4 * scale))

        # Calculate sway offset based on time
        time = pygame.time.get_ticks() / 1000
        sway = math.sin(time + self.sway_offset) * 1.5

        # Draw each pixel of the bush
        for (x, y), color, part in self.pixels:
            # Apply sway only to leaves and berries, not stems
            sway_offset = sway if part in ['leaf', 'berry'] else 0
            
            # Add subtle bounce to berries
            berry_bounce = 0
            if part == 'berry':
                berry_bounce = math.sin(time * 2 + x * 0.5) * 1
            
            # Add alpha to color
            current_color = (*color, alpha)
            
            pixel_rect = pygame.Rect(
                self.position[0] + (x * pixel_size) - (current_size // 2) + sway_offset,
                self.position[1] + (y * pixel_size) - (current_size // 2) + berry_bounce,
                pixel_size,
                pixel_size
            )
            pygame.draw.rect(surface, current_color, pixel_rect)

        # Draw resource indicator with alpha
        if self.resources < 10:
            indicator_bg = (*((200, 200, 200)), alpha)  # Gray background with alpha
            indicator_fg = (*(0, 255, 0), alpha)        # Green with alpha
            
            pygame.draw.rect(surface, indicator_bg,
                           (self.position[0] - 10, self.position[1] + 15,
                            20, 4))
            pygame.draw.rect(surface, indicator_fg,
                           (self.position[0] - 10, self.position[1] + 15,
                            int(20 * (self.resources / 10)), 4)) 