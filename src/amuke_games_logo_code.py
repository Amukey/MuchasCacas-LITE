import pygame
import random
import math

class AmukeGamesLogo:
    """Pixel art logo generator for Amuke Games
    
    Creates a pixel-perfect recreation of the Amuke Games logo with:
    - Three-color gradient stripes
    - Pixel art text
    - Floating plus symbols
    - Customizable size
    """
    def __init__(self, width=300):
        # Gradient colors for AMUKE
        self.amuke_colors = [
            (255, 140, 70),   # Orange
            (255, 80, 120),   # Red
            (180, 80, 180),   # Purple
            (70, 180, 255)    # Baby blue
        ]
        
        # Gradient colors for GAMES
        self.games_colors = [
            (255, 160, 60),   # Light orange
            (255, 200, 80),   # Golden yellow
            (255, 140, 70)    # Orange
        ]
        
        # Plus symbols colors with transparency
        self.plus_colors = [
            (255, 140, 70, 180),   # Orange plus
            (255, 80, 120, 180),   # Pink plus
            (180, 80, 180, 180),   # Purple plus
            (70, 180, 255, 180)    # Blue plus
        ]
        
        # Keep your custom text pixel maps
        self.amuke_pixels = [
            " XXX  X   X X  X X  X XXXX",
            "XX XX XX XX X  X X X  X   ",
            "X   X X X X X  X XX   XXXX",
            "XXXXX X   X X  X X X  X   ",
            "X   X X   X  XX  X  X XXXX"
        ]
        
        self.games_pixels = [
            "XXXX  XXX   X   X XXXX XXXX",
            "X    XX XX  XX XX X    X   ",
            "X XX X   X  X X X XXXX XXXX",
            "X  X XXXXX  X   X X       X ",
            "XXXX X   X  X   X XXXX XXXX"
        ]
        
        # Initialize animation properties first
        self.plus_symbols = []  # Store plus symbols for animation
        self.animation_timer = 0
        self.sparkle_interval = 100  # Milliseconds between sparkle updates
        
        # Calculate dimensions
        self.width = width
        amuke_pixel_size = max(1, width // 50)  # Bigger AMUKE text
        games_pixel_size = max(1, amuke_pixel_size * 0.7)  # Smaller GAMES text
        
        # Calculate total height needed
        text_spacing = amuke_pixel_size * 3  # Space between texts
        total_height = (
            len(self.amuke_pixels) * amuke_pixel_size +  # AMUKE height
            text_spacing +  # Spacing
            len(self.games_pixels) * games_pixel_size    # GAMES height
        )
        
        self.height = int(total_height * 1.2)  # Add some padding
        
        # Create surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw components
        self._draw_text(amuke_pixel_size, games_pixel_size)
        self._add_plus_symbols()
    
    def _draw_text(self, amuke_size, games_size):
        """Draw the text with gradients"""
        # Center AMUKE horizontally
        amuke_width = len(self.amuke_pixels[0]) * amuke_size
        amuke_x = (self.width - amuke_width) // 2
        amuke_y = self.height * 0.2  # Position from top
        
        # Draw AMUKE with vertical gradient
        for row_idx, row in enumerate(self.amuke_pixels):
            # Calculate gradient color for this row
            progress = row_idx / (len(self.amuke_pixels) - 1)
            color = self._get_gradient_color(progress, self.amuke_colors)
            
            self._draw_pixel_row(row, amuke_x, amuke_y + row_idx * amuke_size, amuke_size, color)
        
        # Center and position GAMES below AMUKE
        games_width = len(self.games_pixels[0]) * games_size
        games_x = (self.width - games_width) // 2
        games_y = amuke_y + len(self.amuke_pixels) * amuke_size + amuke_size * 2
        
        # Draw GAMES with orange/yellow gradient
        for row_idx, row in enumerate(self.games_pixels):
            progress = row_idx / (len(self.games_pixels) - 1)
            color = self._get_gradient_color(progress, self.games_colors)
            
            self._draw_pixel_row(row, games_x, games_y + row_idx * games_size, games_size, color)
    
    def _get_gradient_color(self, progress, colors):
        """Get color from gradient based on progress (0-1)"""
        if progress >= 1:
            return colors[-1]
            
        segment_size = 1 / (len(colors) - 1)
        segment = int(progress / segment_size)
        segment_progress = (progress - segment * segment_size) / segment_size
        
        color1 = colors[segment]
        color2 = colors[segment + 1]
        
        # Handle both RGB and RGBA colors
        if len(color1) == 4 and len(color2) == 4:
            # Both colors have alpha
            return tuple(
                int(c1 + (c2 - c1) * segment_progress)
                for c1, c2 in zip(color1, color2)
            )
        else:
            # RGB only - return RGB values
            rgb = tuple(
                int(c1 + (c2 - c1) * segment_progress)
                for c1, c2 in zip(color1[:3], color2[:3])
            )
            return rgb
    
    def _draw_pixel_row(self, row, x, y, size, color):
        """Draw a row of pixels with given color"""
        for col_idx, pixel in enumerate(row):
            if pixel == 'X':
                pygame.draw.rect(
                    self.surface,
                    color,
                    (x + col_idx * size, y, size, size)
                )
    
    def _add_plus_symbols(self):
        """Add decorative plus symbols clustered around text"""
        plus_sizes = [
            (2, 2),   # Tiny plus
            (4, 4),   # Small plus
            (6, 6),   # Medium plus
            (10, 10)  # Large plus
        ]
        size_weights = [8, 6, 3, 1]  # More tiny and small pluses
        
        num_plus = 80  # Even more symbols for better coverage
        
        # Get letter positions and text boundaries
        letter_positions = self._get_letter_positions()
        text_bounds = self._get_text_boundaries()
        
        # Create initial plus symbols
        for _ in range(num_plus):
            if random.random() < 0.7:  # 70% chance to cluster around letters
                letter_pos = random.choice(letter_positions)
                # Tighter clustering around letters
                offset_x = random.gauss(0, 5)
                offset_y = random.gauss(0, 5)
                x = letter_pos['x'] + offset_x
                y = letter_pos['y'] + offset_y
            else:  # 30% chance to spread around text area
                word = random.choice(['AMUKE', 'GAMES'])
                bounds = text_bounds[word]
                # Generate position around text boundaries
                x = random.uniform(bounds['x'] - 10, bounds['x'] + bounds['width'] + 10)
                if random.random() < 0.5:  # 50% chance for top/bottom area
                    # Position above or below text with more spread
                    y = bounds['y'] + (random.choice([-1, 1]) * 
                                     random.uniform(0, bounds['height'] * 0.5))
                else:
                    # Position within text height
                    y = random.uniform(bounds['y'], bounds['y'] + bounds['height'])
            
            # Create base color without alpha
            base_color = self._get_gradient_color(y / self.height, self.plus_colors)
            
            self.plus_symbols.append({
                'x': x,
                'y': y,
                'size': random.choices(plus_sizes, weights=size_weights)[0][0],
                'color': (*base_color[:3], 0),
                'rotation': random.uniform(-45, 45),
                'sparkle_timer': random.randint(0, 500),
                'life_timer': random.randint(0, 1000),
                'life_duration': random.randint(500, 1500),
                'alpha': 0,
                'state': 'fade_in'
            })
    
    def _get_letter_positions(self):
        """Get center positions of all letters in both words"""
        positions = []
        pixel_size_amuke = self.width // 50
        pixel_size_games = int(pixel_size_amuke * 0.7)
        
        # AMUKE positions
        amuke_width = len(self.amuke_pixels[0]) * pixel_size_amuke
        amuke_x = (self.width - amuke_width) // 2
        amuke_y = self.height * 0.2
        
        # GAMES positions
        games_width = len(self.games_pixels[0]) * pixel_size_games
        games_x = (self.width - games_width) // 2
        games_y = amuke_y + len(self.amuke_pixels) * pixel_size_amuke + pixel_size_amuke * 2
        
        # Add letter positions for AMUKE
        for row_idx, row in enumerate(self.amuke_pixels):
            for col_idx, pixel in enumerate(row):
                if pixel == 'X':
                    positions.append({
                        'x': amuke_x + col_idx * pixel_size_amuke + pixel_size_amuke/2,
                        'y': amuke_y + row_idx * pixel_size_amuke + pixel_size_amuke/2
                    })
        
        # Add letter positions for GAMES
        for row_idx, row in enumerate(self.games_pixels):
            for col_idx, pixel in enumerate(row):
                if pixel == 'X':
                    positions.append({
                        'x': games_x + col_idx * pixel_size_games + pixel_size_games/2,
                        'y': games_y + row_idx * pixel_size_games + pixel_size_games/2
                    })
        
        return positions

    def _get_text_boundaries(self):
        """Get the boundaries of each word for particle placement"""
        pixel_size_amuke = self.width // 50
        pixel_size_games = int(pixel_size_amuke * 0.7)
        
        # AMUKE boundaries
        amuke_width = len(self.amuke_pixels[0]) * pixel_size_amuke
        amuke_x = (self.width - amuke_width) // 2
        amuke_y = self.height * 0.2
        amuke_height = len(self.amuke_pixels) * pixel_size_amuke
        
        # GAMES boundaries
        games_width = len(self.games_pixels[0]) * pixel_size_games
        games_x = (self.width - games_width) // 2
        games_y = amuke_y + amuke_height + pixel_size_amuke * 2
        games_height = len(self.games_pixels) * pixel_size_games
        
        return {
            'AMUKE': {
                'x': amuke_x,
                'y': amuke_y,
                'width': amuke_width,
                'height': amuke_height
            },
            'GAMES': {
                'x': games_x,
                'y': games_y,
                'width': games_width,
                'height': games_height
            }
        }

    def update(self, dt):
        """Update sparkle animation"""
        self.animation_timer += dt
        letter_positions = self._get_letter_positions()
        
        for plus in self.plus_symbols[:]:
            plus['sparkle_timer'] += dt
            plus['life_timer'] += dt
            
            # Faster fade in/out
            if plus['state'] == 'fade_in':
                plus['alpha'] = min(180, plus['alpha'] + dt)  # Faster fade in
                if plus['alpha'] >= 180:
                    plus['state'] = 'visible'
            elif plus['state'] == 'visible':
                if plus['life_timer'] > plus['life_duration']:
                    plus['state'] = 'fade_out'
            elif plus['state'] == 'fade_out':
                plus['alpha'] = max(0, plus['alpha'] - dt)  # Faster fade out
                if plus['alpha'] <= 0:
                    self.plus_symbols.remove(plus)
                    # Create new plus with tighter clustering
                    letter_pos = random.choice(letter_positions)
                    base_color = self._get_gradient_color(letter_pos['y'] / self.height, self.plus_colors)
                    
                    self.plus_symbols.append({
                        'x': letter_pos['x'] + random.gauss(0, 5),  # Tighter spread
                        'y': letter_pos['y'] + random.gauss(0, 5),  # Tighter spread
                        'size': random.choices([(2, 2), (4, 4), (6, 6), (10, 10)], 
                                            weights=[8, 6, 3, 1])[0][0],
                        'color': (*base_color[:3], 0),
                        'rotation': random.uniform(-45, 45),
                        'sparkle_timer': 0,
                        'life_timer': 0,
                        'life_duration': random.randint(500, 1500),  # Faster lifecycle
                        'alpha': 0,
                        'state': 'fade_in'
                    })
                    continue
            
            # More dynamic sparkle effect
            base_color = plus['color'][:3]
            wave = math.sin(plus['sparkle_timer'] / 100)  # Faster sparkle
            alpha = int(plus['alpha'] + wave * 60)  # More alpha variation
            plus['color'] = (*base_color, max(0, min(255, alpha)))
            
            # Add gentle rotation during life
            if random.random() < 0.1:  # 10% chance each frame
                plus['rotation'] += random.uniform(-2, 2)
    
    def draw(self, surface=None):
        """Draw the logo with animated plus symbols"""
        if surface is None:
            surface = self.surface
            surface.fill((0, 0, 0, 0))  # Clear with transparency
        
        # Draw text
        self._draw_text(self.width // 50, int(self.width // 50 * 0.7))
        
        # Draw plus symbols
        for plus in self.plus_symbols:
            self._draw_plus(
                int(plus['x']), 
                int(plus['y']), 
                plus['size'], 
                plus['color'], 
                plus['rotation']
            )
        
        return surface
    
    def _draw_plus(self, x, y, size, color, rotation=0):
        """Draw a single plus symbol with rotation"""
        thickness = max(1, size // 4)
        
        # Create a surface for the rotated plus
        plus_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Ensure color has all 4 components (RGBA)
        if len(color) == 3:
            color = (*color, 255)  # Add alpha if missing
        
        # Draw the plus on the surface
        pygame.draw.rect(plus_surface, color, (0, size//2 - thickness//2, size, thickness))
        pygame.draw.rect(plus_surface, color, (size//2 - thickness//2, 0, thickness, size))
        
        # Rotate the surface if needed
        if rotation:
            plus_surface = pygame.transform.rotate(plus_surface, rotation)
        
        # Blit to main surface
        self.surface.blit(plus_surface, 
                         (x - plus_surface.get_width()//2, 
                          y - plus_surface.get_height()//2))
    
    def get_surface(self):
        """Return the rendered logo surface"""
        return self.surface

# Example usage:
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Amuke Games Logo Test")
    clock = pygame.time.Clock()
    
    # Create logo
    logo = AmukeGamesLogo(400)
    
    # Main loop
    running = True
    while running:
        dt = clock.tick(60)  # 60 FPS
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update and draw logo
        logo.update(dt)
        
        screen.fill((0, 0, 0))  # Black background
        logo_surface = logo.draw()
        
        # Center logo on screen
        logo_rect = logo_surface.get_rect(center=screen.get_rect().center)
        screen.blit(logo_surface, logo_rect)
        
        pygame.display.flip()
    
    pygame.quit() 