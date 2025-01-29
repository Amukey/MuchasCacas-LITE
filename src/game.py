import pygame
import random
import logging
import math
import noise  # We'll need to add 'noise' to requirements.txt
from entities import Colony, Ant, Snake, COLONY_MAX_SIZE, COLONY_MIN_SIZE, COLOR_COLONY
from resources import Rock, Plant, Bush
from ui import HUD, SettingsWindow
from utils import load_assets
from sounds import GameSounds
from constants import Economy, Animation, Background, WINDOW_WIDTH, WINDOW_HEIGHT, FPS

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Muchas Cacas! Lite")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load logo
        self.logo = pygame.image.load('assets/images/amuke_games_logo.png').convert_alpha()
        logo_width = 300
        logo_height = int(logo_width * self.logo.get_height() / self.logo.get_width())
        self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
        
        # Intro sequence states and timings
        self.intro_state = 'logo_fade_in'
        self.fade_start_time = pygame.time.get_ticks()
        self.fade_durations = {
            'logo_fade_in': Animation.LOGO_FADE_IN,
            'logo_stay': Animation.LOGO_STAY,
            'logo_fade_out': Animation.LOGO_FADE_OUT,
            'map_fade_in': Animation.MAP_FADE_IN,
            'trees_fade_in': Animation.TREES_FADE_IN,
            'rocks_fade_in': Animation.ROCKS_FADE_IN,
            'snake_fade_in': Animation.SNAKE_FADE_IN
        }
        
        # Initialize game objects with alpha
        self.alpha = 0
        self.assets = load_assets()
        self.sounds = GameSounds()
        self.hud = HUD()
        
        # Game state
        self.placing_colony = False
        self.colonies = []
        self.ants = []
        self.rocks = []
        self.plants = []
        self.bushes = []
        self.snake = Snake((random.randint(0, 480), random.randint(0, 800)), self)
        
        # Resource spawn settings
        self.resource_spawn_timer = pygame.time.get_ticks()
        self.resource_spawn_interval = Economy.Generation.RESOURCE_SPAWN_INTERVAL
        self.max_resources = {
            'rocks': Economy.Generation.MAX_ROCKS,
            'plants': Economy.Generation.MAX_PLANTS,
            'bushes': Economy.Generation.MAX_BUSHES
        }
        
        # Background settings
        self.TILE_SIZE = Background.TILE_SIZE
        self.noise_scale = Background.NOISE_SCALE
        self.grass_patches = []
        self.generate_grass_patches()
        self.background = self.generate_background()
        
        # Initialize resources
        self.initialize_resources()
        
        self.settings_window = SettingsWindow(WINDOW_WIDTH, WINDOW_HEIGHT)

    def initialize_resources(self):
        """Initialize rocks, plants and bushes on the map"""
        for _ in range(10):
            self.rocks.append(Rock((
                random.randint(20, self.screen.get_width() - 20),
                random.randint(20, self.screen.get_height() - 20)
            )))
            self.plants.append(Plant((
                random.randint(20, self.screen.get_width() - 20),
                random.randint(20, self.screen.get_height() - 20)
            )))
            # Initialize with more bushes
            for _ in range(2):  # Double the amount of bushes
                self.bushes.append(Bush((
                    random.randint(20, self.screen.get_width() - 20),
                    random.randint(20, self.screen.get_height() - 20)
                )))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if settings icon was clicked
                settings_icon_rect = pygame.Rect(WINDOW_WIDTH - 45, 15, 32, 32)
                if settings_icon_rect.collidepoint(mouse_pos):
                    self.settings_window.is_visible = not self.settings_window.is_visible
                    if self.settings_window.is_visible:
                        self.pixel_icons['settings'].current_frame = 1  # Show hover state
                    continue
                
                # Handle settings window interaction
                if self.settings_window.is_visible:
                    if self.settings_window.handle_click(mouse_pos):
                        # Update volumes
                        self.sounds.set_volumes(
                            self.settings_window.sound_volume,
                            self.settings_window.music_volume
                        )
                    continue
                
                if not self.colonies:  # First colony placement
                    first_colony = Colony(mouse_pos, self.ants, self, is_main=True)
                    self.colonies.append(first_colony)
                elif self.placing_colony:  # Place new colony
                    new_colony = Colony(mouse_pos, self.ants, self, is_main=False)
                    self.colonies.append(new_colony)
                    self.colonies[0].resources['minerals'] -= 200
                    self.colonies[0].resources['plants'] -= 400
                    self.sounds.play_colony_create()
                    self.placing_colony = False
                else:  # Check for indicator clicks
                    for colony in self.colonies:
                        action = colony.handle_click(mouse_pos)
                        if action == 'spawn_ant':
                            colony.spawn_ant(self.ants)
                            break
                        elif action == 'new_colony':
                            self.placing_colony = True
                            break

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Update resources
        self.update_resources(current_time)
        
        # Update plant growth animations
        for plant in self.plants:
            plant.update()
        
        # Get obstacles for collision detection
        obstacles = self.rocks + self.plants + self.bushes
        
        # Update snake and check for kills
        killed = self.snake.update(pygame.mouse.get_pos(), self.ants, self.colonies)
        if killed:
            self.hud.increment_kills()
        
        # Update ants
        for ant in self.ants:
            ant.update(pygame.mouse.get_pos(), 
                      self.snake.position, 
                      obstacles,
                      self.rocks + self.plants + self.bushes,  # All resources
                      self.colonies)

        # Remove depleted resources
        self.rocks = [rock for rock in self.rocks if rock.minerals > 0]
        self.plants = [plant for plant in self.plants if plant.resources > 0]
        self.bushes = [bush for bush in self.bushes if bush.resources > 0]

        # Update colonies
        for colony in self.colonies:
            colony.update(current_time, self.ants)

        # Update HUD tooltips
        self.hud.update(pygame.mouse.get_pos())

        # Update music system with game state
        try:
            game_state = {
                'ants': self.ants,
                'snake_nearby': self.is_snake_nearby(),
                'resources_low': self.are_resources_low()
            }
            self.sounds.update_music(game_state)
        except Exception as e:
            print(f"Error updating music state: {e}")

    def update_resources(self, current_time):
        """Spawn new resources periodically with improved logic"""
        if current_time - self.resource_spawn_timer >= self.resource_spawn_interval:
            self.resource_spawn_timer = current_time
            
            # Calculate resource needs
            rocks_needed = self.max_resources['rocks'] - len(self.rocks)
            plants_needed = self.max_resources['plants'] - len(self.plants)
            bushes_needed = self.max_resources['bushes'] - len(self.bushes)
            
            # Spawn multiple resources at once if needed
            for _ in range(min(3, rocks_needed)):  # Spawn up to 3 rocks at once
                if rocks_needed > 0:
                    position = self.find_valid_resource_position()
                    self.rocks.append(Rock(position))
            
            for _ in range(min(3, plants_needed)):  # Spawn up to 3 plants at once
                if plants_needed > 0:
                    position = self.find_valid_resource_position()
                    self.plants.append(Plant(position))
            
            for _ in range(min(4, bushes_needed)):  # Spawn up to 4 bushes at once
                if bushes_needed > 0:
                    position = self.find_valid_resource_position()
                    self.bushes.append(Bush(position))

    def find_valid_resource_position(self):
        """Find a valid position for a new resource"""
        attempts = 0
        min_distance = 30  # Minimum distance from other resources
        
        while attempts < 10:
            position = (
                random.randint(20, self.screen.get_width() - 20),
                random.randint(20, self.screen.get_height() - 20)
            )
            
            # Check distance from other resources
            too_close = False
            for resource in self.rocks + self.plants + self.bushes:
                dx = position[0] - resource.position[0]
                dy = position[1] - resource.position[1]
                if (dx * dx + dy * dy) < min_distance * min_distance:
                    too_close = True
                    break
            
            if not too_close:
                return position
            
            attempts += 1
        
        # If no good position found after 10 attempts, just return a random position
        return (
            random.randint(20, self.screen.get_width() - 20),
            random.randint(20, self.screen.get_height() - 20)
        )

    def generate_grass_patches(self):
        """Generate positions for grass patches"""
        width, height = self.screen.get_width(), self.screen.get_height()
        for _ in range(100):  # Number of grass patches
            self.grass_patches.append({
                'pos': (random.randint(0, width), random.randint(0, height)),
                'offset': random.random() * 6.28,
                'size': random.randint(2, 4)
            })

    def generate_background(self):
        """Generate a textured forest floor background with fine lines"""
        width, height = self.screen.get_width(), self.screen.get_height()
        background = pygame.Surface((width, height))
        
        # Forest floor colors (earthier tones)
        colors = {
            'dark': (65, 42, 25),     # Dark earth
            'base': (82, 53, 31),     # Medium earth
            'light': (98, 63, 37),    # Light earth
            'detail': (73, 47, 28)    # Detail earth
        }
        
        # Generate base noise map
        for y in range(0, height, self.TILE_SIZE):
            for x in range(0, width, self.TILE_SIZE):
                # Generate two different noise values for more texture
                noise_val = noise.pnoise2(x/self.noise_scale, 
                                        y/self.noise_scale, 
                                        octaves=4,
                                        persistence=0.6,
                                        lacunarity=2.5,
                                        repeatx=width, 
                                        repeaty=height, 
                                        base=42)
                
                # Second noise for line pattern
                line_noise = noise.pnoise2(x/10, y/10, 
                                         octaves=1,
                                         persistence=0.5,
                                         lacunarity=2.0,
                                         repeatx=width,
                                         repeaty=height,
                                         base=17)
                
                # Create fine line pattern with noise
                for px in range(self.TILE_SIZE):
                    for py in range(self.TILE_SIZE):
                        pixel_x = x + px
                        pixel_y = y + py
                        
                        if pixel_x >= width or pixel_y >= height:
                            continue
                        
                        # Base color selection
                        if noise_val > 0.2:
                            color = colors['light']
                        elif noise_val < -0.2:
                            color = colors['dark']
                        else:
                            color = colors['base']
                        
                        # Add line pattern
                        line_val = (line_noise + 1) / 2  # Normalize to 0-1
                        if (pixel_y + int(line_val * 4)) % 4 == 0:  # Create fine lines
                            color = tuple(max(0, c - 12) for c in color)
                        
                        # Add subtle noise variation
                        if random.random() < 0.1:  # 10% chance for noise detail
                            color = tuple(max(0, min(255, c + random.randint(-5, 5))) 
                                        for c in color)
                        
                        background.set_at((pixel_x, pixel_y), color)
        
        return background

    def draw_grass_patches(self, surface):
        """Draw animated grass patches"""
        time = pygame.time.get_ticks() / 1000
        grass_colors = [
            (67, 100, 18),  # Dark green
            (85, 125, 23),  # Medium green
            (103, 148, 28)  # Light green
        ]
        
        for patch in self.grass_patches:
            x, y = patch['pos']
            size = patch['size']
            sway = math.sin(time * 2 + patch['offset']) * 2
            
            # Draw each blade of grass in the patch
            for i in range(size):
                color = random.choice(grass_colors)
                blade_height = random.randint(3, 6)
                
                # Calculate swaying position
                sway_offset = sway * (blade_height / 6)  # Taller grass sways more
                
                # Draw grass blade
                pygame.draw.line(surface,
                               color,
                               (x + i * 2, y),
                               (x + i * 2 + sway_offset, y - blade_height),
                               1)

    def draw(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw animated grass patches
        self.draw_grass_patches(self.screen)
        
        # Draw all game objects
        for rock in self.rocks:
            rock.draw(self.screen, 255)  # Full opacity after intro
        for plant in self.plants:
            plant.draw(self.screen, 255)
        for bush in self.bushes:
            bush.draw(self.screen, 255)
        for colony in self.colonies:
            colony.draw(self.screen)
        for ant in self.ants:
            ant.draw(self.screen)
        self.snake.draw(self.screen, 255)
        
        # Draw colony preview when placing
        if self.placing_colony:
            mouse_pos = pygame.mouse.get_pos()
            preview_rect = pygame.Rect(
                mouse_pos[0] - COLONY_MIN_SIZE // 2,
                mouse_pos[1] - COLONY_MIN_SIZE // 2,
                COLONY_MIN_SIZE,
                COLONY_MIN_SIZE
            )
            preview_color = (COLOR_COLONY[0], COLOR_COLONY[1], COLOR_COLONY[2], 128)
            pygame.draw.rect(self.screen, preview_color, preview_rect)
        
        self.hud.draw(self.screen, self.colonies, self.ants)
        
        # Draw settings window if visible
        if self.settings_window.is_visible:
            self.settings_window.draw(self.screen)

    def update_intro_sequence(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.fade_start_time
        
        if self.intro_state == 'logo_fade_in':
            # Play sound at the very start of the sequence
            if not hasattr(self, 'sound_played'):  # Check if we've played the sound
                self.sounds.play_startup()
                self.sound_played = True  # Mark sound as played
            
            self.alpha = min(255, (elapsed * 255) // self.fade_durations['logo_fade_in'])
            if elapsed >= self.fade_durations['logo_fade_in']:
                self.intro_state = 'logo_stay'
                self.fade_start_time = current_time
                
        elif self.intro_state == 'logo_stay':
            if elapsed >= self.fade_durations['logo_stay']:
                self.intro_state = 'logo_fade_out'
                self.fade_start_time = current_time
                
        elif self.intro_state == 'logo_fade_out':
            # Reset sound flag when sequence ends
            if hasattr(self, 'sound_played'):
                delattr(self, 'sound_played')
            self.alpha = max(0, 255 - (elapsed * 255) // self.fade_durations['logo_fade_out'])
            if elapsed >= self.fade_durations['logo_fade_out']:
                self.intro_state = 'map_fade_in'
                self.fade_start_time = current_time
                
            # Start background music as logo fades out
            if not hasattr(self, 'music_started'):
                self.sounds.start_background_music()
                self.music_started = True
                
        elif self.intro_state == 'map_fade_in':
            self.alpha = min(255, (elapsed * 255) // self.fade_durations['map_fade_in'])
            if elapsed >= self.fade_durations['map_fade_in']:
                self.intro_state = 'trees_fade_in'
                self.fade_start_time = current_time
                
        elif self.intro_state == 'trees_fade_in':
            self.alpha = min(255, (elapsed * 255) // self.fade_durations['trees_fade_in'])
            if elapsed >= self.fade_durations['trees_fade_in']:
                self.intro_state = 'rocks_fade_in'
                self.fade_start_time = current_time
                
        elif self.intro_state == 'rocks_fade_in':
            self.alpha = min(255, (elapsed * 255) // self.fade_durations['rocks_fade_in'])
            if elapsed >= self.fade_durations['rocks_fade_in']:
                self.intro_state = 'snake_fade_in'
                self.fade_start_time = current_time
                
        elif self.intro_state == 'snake_fade_in':
            self.alpha = min(255, (elapsed * 255) // self.fade_durations['snake_fade_in'])
            if elapsed >= self.fade_durations['snake_fade_in']:
                self.intro_state = 'game_running'

    def draw_intro_sequence(self):
        self.screen.fill((0, 0, 0))  # Black background
        
        if self.intro_state in ['logo_fade_in', 'logo_stay', 'logo_fade_out']:
            # Draw logo with current alpha
            logo_surface = self.logo.copy()
            logo_surface.set_alpha(self.alpha)
            logo_x = (self.screen.get_width() - self.logo.get_width()) // 2
            logo_y = (self.screen.get_height() - self.logo.get_height()) // 2
            self.screen.blit(logo_surface, (logo_x, logo_y))
            
        else:
            # Draw game elements with fade effects
            if self.intro_state in ['map_fade_in', 'trees_fade_in', 'rocks_fade_in', 'snake_fade_in', 'game_running']:
                background_surface = self.background.copy()
                background_surface.set_alpha(255 if self.intro_state != 'map_fade_in' else self.alpha)
                self.screen.blit(background_surface, (0, 0))
                
            if self.intro_state in ['trees_fade_in', 'rocks_fade_in', 'snake_fade_in', 'game_running']:
                for plant in self.plants:
                    plant.draw(self.screen, self.alpha if self.intro_state == 'trees_fade_in' else 255)
                    
            if self.intro_state in ['rocks_fade_in', 'snake_fade_in', 'game_running']:
                for rock in self.rocks:
                    rock.draw(self.screen, self.alpha if self.intro_state == 'rocks_fade_in' else 255)
                    
            if self.intro_state in ['snake_fade_in', 'game_running']:
                self.snake.draw(self.screen, self.alpha if self.intro_state == 'snake_fade_in' else 255)

    def run(self):
        while self.running:
            if self.intro_state != 'game_running':
                # Handle quit events during intro
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        return
                
                self.update_intro_sequence()
                self.draw_intro_sequence()
            else:
                self.handle_events()
                self.update()
                self.draw()
            
            pygame.display.flip()
            self.clock.tick(60)

    def spawn_ant(self, position):
        new_ant = Ant(position, self)  # Pass self (game) to ant
        self.ants.append(new_ant) 

    def show_splash_screen(self):
        """Show splash screen with logo"""
        # Create surfaces
        logo_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        fade_surface.fill((0, 0, 0))
        
        # Load and scale logo
        logo = pygame.image.load("assets/logo.png").convert_alpha()
        logo_rect = logo.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        
        # Animation timings from constants
        timings = Animation
        start_time = pygame.time.get_ticks()
        
        # Play startup sound at beginning of fade-in
        self.sounds.play_startup()
        
        # Splash screen loop
        while True:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - start_time
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    return True
            
            # Clear screen
            self.screen.fill((0, 0, 0))
            
            # Calculate alpha based on animation phase
            if elapsed < timings.LOGO_FADE_IN:
                # Fade in
                alpha = int(255 * (elapsed / timings.LOGO_FADE_IN))
            elif elapsed < timings.LOGO_FADE_IN + timings.LOGO_STAY:
                # Stay visible
                alpha = 255
            elif elapsed < timings.LOGO_FADE_IN + timings.LOGO_STAY + timings.LOGO_FADE_OUT:
                # Fade out
                fade_progress = (elapsed - (timings.LOGO_FADE_IN + timings.LOGO_STAY)) / timings.LOGO_FADE_OUT
                alpha = int(255 * (1 - fade_progress))
            else:
                # Animation complete
                return True
            
            # Draw logo with current alpha
            logo_surface.fill((0, 0, 0, 0))
            logo_surface.blit(logo, logo_rect)
            logo_surface.set_alpha(alpha)
            self.screen.blit(logo_surface, (0, 0))
            
            pygame.display.flip() 

    def is_snake_nearby(self):
        """Check if snake is near any colony"""
        if not self.colonies:
            return False
        for colony in self.colonies:
            dx = self.snake.position[0] - colony.position[0]
            dy = self.snake.position[1] - colony.position[1]
            if (dx * dx + dy * dy) < 200 * 200:  # 200 pixel radius
                return True
        return False

    def are_resources_low(self):
        """Check if resources are running low"""
        if not self.colonies:
            return False
        main_colony = self.colonies[0]
        return (main_colony.resources['minerals'] < 50 or 
                main_colony.resources['plants'] < 50) 