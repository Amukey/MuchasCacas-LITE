import pygame
import random
import logging
import math
import noise
import numpy as np  # Add this import
from entities import Colony, Ant, Snake, Spider, SpiderWeb, COLONY_MAX_SIZE, COLONY_MIN_SIZE
from resources import Rock, Plant, Bush
from ui import HUD, SettingsWindow, SettingsMenu, SettingsIcon
from utils import load_assets
from sounds import GameSounds
from constants import (
    Economy, Animation, Background, WINDOW_WIDTH, WINDOW_HEIGHT, 
    FPS, DAY_NIGHT, Behavior, COLORS, VISUALS, UI
)
from state import GameState  # Update import
from amuke_games_logo_code import AmukeGamesLogo  # Add this

class GameState:
    """Manages game state and musical progression"""
    def __init__(self):
        self.intensity = 0.0        # 0.0 to 1.0
        self.danger_level = 0.0     # 0.0 to 1.0
        self.resource_abundance = 1.0  # 0.0 to 1.0
        self.time_of_day = 'day'    # 'day' or 'night'
        self.current_biome = 'peaceful'
        
        # Musical state
        self.current_mood = 'peaceful'  # peaceful, ambient, floating, dreamy
        self.transition_requested = False
        self.last_state_update = pygame.time.get_ticks()
        
    def update(self, game_objects):
        """Update game state based on game objects"""
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_state_update < 1000:  # Update every second
            return
            
        self.last_state_update = current_time
        
        # Calculate intensity based on ant activity and threats
        active_ants = sum(1 for ant in game_objects['ants'] if hasattr(ant, 'resources') and 
                         (ant.resources['minerals'] > 0 or ant.resources['plants'] > 0))
        self.intensity = min(1.0, (active_ants / max(len(game_objects['ants']), 1)) * 0.5)
        
        # Calculate danger level
        snake_distances = []
        if game_objects['colonies']:
            for colony in game_objects['colonies']:
                dx = game_objects['snake'].position[0] - colony.position[0]
                dy = game_objects['snake'].position[1] - colony.position[1]
                snake_distances.append(math.sqrt(dx*dx + dy*dy))
            
            closest_snake = min(snake_distances) if snake_distances else float('inf')
            self.danger_level = max(0.0, min(1.0, 1.0 - (closest_snake / 300)))
        
        # Calculate resource abundance
        total_resources = (
            sum(rock.minerals for rock in game_objects['resources']['rocks']) +
            sum(plant.resources for plant in game_objects['resources']['plants']) +
            sum(bush.resources for bush in game_objects['resources']['bushes'])
        )
        max_resources = (
            len(game_objects['resources']['rocks']) * Economy.Capacity.ROCK_MINERAL_CAPACITY +
            len(game_objects['resources']['plants']) * Economy.Capacity.TREE_RESOURCE_CAPACITY +
            len(game_objects['resources']['bushes']) * Economy.Capacity.BUSH_RESOURCE_CAPACITY
        )
        
        self.resource_abundance = total_resources / max_resources if max_resources > 0 else 1.0
        
        # Update time of day (cycle every 2 minutes)
        self.time_of_day = 'day' if (current_time // 120000) % 2 == 0 else 'night'
        
        # Update musical mood
        self._update_mood()
    
    def _update_mood(self):
        """Update musical mood based on game state"""
        if self.danger_level > 0.7:
            new_mood = 'ambient'
        elif self.intensity > 0.6:
            new_mood = 'floating'
        elif self.resource_abundance < 0.3:
            new_mood = 'dreamy'
        else:
            new_mood = 'peaceful'
            
        if new_mood != self.current_mood:
            self.current_mood = new_mood
            self.transition_requested = True
    
    def _calculate_nearest_distance(self, pos1, objects):
        """Calculate nearest distance between position and objects"""
        if not objects:
            return float('inf')
        
        return min(
            np.sqrt((pos1[0] - obj.position[0])**2 + (pos1[1] - obj.position[1])**2)
            for obj in objects
        )

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Muchas Cacas! Lite")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create animated logo instead of loading image
        logo_width = 300
        self.logo = AmukeGamesLogo(logo_width)
        
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
        
        # Initialize game state
        self.game_state = GameState()
        
        # Day/Night cycle state
        self.cycle_start_time = pygame.time.get_ticks()
        self.current_time_of_day = 'day'
        self.day_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.night_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.night_overlay.fill(DAY_NIGHT['NIGHT_TINT'])
        
        # Snake sleep position (set when night begins)
        self.snake_sleep_position = None
        
        # Initialize UI elements
        self.settings_menu = SettingsMenu(self.screen, self.sounds)
        
        # Initialize pixel icons including settings
        self.pixel_icons = {
            'settings': SettingsIcon(32)  # Create settings icon
        }
        
        self.spider = None  # Current spider
        self.webs = []  # List of active spider webs

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
            
            # Handle settings menu events
            self.settings_menu.handle_event(event)
            
            # Handle settings icon hover
            mouse_pos = pygame.mouse.get_pos()
            if self.settings_menu.settings_button.collidepoint(mouse_pos):
                self.pixel_icons['settings'].current_frame = 1  # Show hover state
            else:
                self.pixel_icons['settings'].current_frame = 0  # Normal state

    def update(self):
        current_time = pygame.time.get_ticks()
        cycle_time = (current_time - self.cycle_start_time) % DAY_NIGHT['CYCLE_DURATION']
        
        # Calculate day/night state
        is_night = cycle_time >= DAY_NIGHT['CYCLE_DURATION'] / 2
        
        # Spider handling
        if is_night:
            # Spider spawning at night
            if not self.spider and (self.plants or self.bushes) and self.snake.is_sleeping:
                if random.random() < 0.1:  # 10% chance each update to spawn spider
                    spawn_point = random.choice(self.plants + self.bushes)
                    self.spider = Spider(spawn_point.position, self)
                    spawn_point.has_spider = True
        else:
            # Day time - make sure spider seeks shelter or dies
            if self.spider and self.spider.state not in ['sleeping', 'dying']:
                if not self.spider._find_shelter(self.plants, self.bushes):
                    self.spider.state = 'dying'
                    self.spider.daylight_death_timer = 2000
                    self.spider.speed *= 2
                    self.spider.flee_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]

        # Update spider if it exists
        if self.spider:
            self.spider.update(self.clock.get_time(), self.plants, self.bushes,
                             self.colonies, self.ants)
            
            # Clean up dead spider
            if self.spider.state == 'dying' and self.spider.death_blinks >= 3:
                self.spider = None  # Allow new spider to spawn next night
        
        # Calculate if it's mid-day (when sun is highest)
        is_mid_day = (cycle_time >= DAY_NIGHT['CYCLE_DURATION'] / 4 and 
                     cycle_time <= DAY_NIGHT['CYCLE_DURATION'] / 4 + 1000)
        
        # Destroy all webs at mid-day
        if is_mid_day and self.webs:
            self.webs.clear()
            logging.debug("Mid-day: Clearing all spider webs")
        
        # Update webs and remove destroyed ones
        self.webs = [web for web in self.webs if not web.destroyed]
        
        # Check for web effects on ants
        for ant in self.ants:
            for web in self.webs:
                web.affects_ant(ant)
        
        # Calculate day/night state
        is_transitioning = (
            cycle_time < DAY_NIGHT['DAWN_DURATION'] or  # Dawn
            abs(cycle_time - DAY_NIGHT['CYCLE_DURATION'] / 2) < DAY_NIGHT['DUSK_DURATION']  # Dusk
        )
        
        # Update time of day
        new_time = 'night' if is_night else 'day'
        if new_time != self.current_time_of_day:
            self.handle_time_change(new_time)
        self.current_time_of_day = new_time
        
        # Update entity behaviors based on time of day
        self.update_day_night_behaviors(is_night, is_transitioning)
        
        # Update game state first
        self.game_state.update({
            'ants': self.ants,
            'colonies': self.colonies,
            'snake': self.snake,
            'resources': {
                'rocks': self.rocks,
                'plants': self.plants,
                'bushes': self.bushes
            },
            'time': current_time
        })
        
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

        # Update music system with game state object
        try:
            self.sounds.update_music(self.game_state)
        except Exception as e:
            print(f"Error updating music state: {e}")

        # Update display
        pygame.display.flip()

    def update_resources(self, current_time):
        """Spawn new resources periodically with improved balance"""
        if current_time - self.resource_spawn_timer >= self.resource_spawn_interval:
            self.resource_spawn_timer = current_time
            
            # Calculate current resource percentages
            rocks_percent = len(self.rocks) / self.max_resources['rocks']
            plants_percent = len(self.plants) / self.max_resources['plants']
            bushes_percent = len(self.bushes) / self.max_resources['bushes']
            
            # Calculate resource needs
            rocks_needed = self.max_resources['rocks'] - len(self.rocks)
            plants_needed = self.max_resources['plants'] - len(self.plants)
            bushes_needed = self.max_resources['bushes'] - len(self.bushes)
            
            # Adjust spawn rates based on current amounts
            spawn_chances = {
                'rocks': 0.8 if rocks_percent < 0.3 else 0.4,    # Higher chance when low
                'plants': 0.9 if plants_percent < 0.4 else 0.5,  # Plants spawn more frequently
                'bushes': 0.7 if bushes_percent < 0.3 else 0.3   # Bushes are rarer
            }
            
            # Spawn multiple resources at once if needed
            for _ in range(min(2, rocks_needed)):  # Max 2 rocks at once
                if rocks_needed > 0 and random.random() < spawn_chances['rocks']:
                    position = self.find_valid_resource_position()
                    self.rocks.append(Rock(position))
            
            for _ in range(min(3, plants_needed)):  # Max 3 plants at once
                if plants_needed > 0 and random.random() < spawn_chances['plants']:
                    position = self.find_valid_resource_position()
                    self.plants.append(Plant(position))
            
            for _ in range(min(2, bushes_needed)):  # Max 2 bushes at once
                if bushes_needed > 0 and random.random() < spawn_chances['bushes']:
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
        """Draw game state"""
        self.screen.fill((0, 0, 0))  # Black background
        
        if self.intro_state.startswith('logo'):
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.fade_start_time
            
            # Update logo animation
            dt = self.clock.get_time()  # Get time since last frame
            self.logo.update(dt)
            
            # Draw logo with appropriate fade
            logo_surface = self.logo.draw()
            logo_rect = logo_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            
            if self.intro_state == 'logo_fade_in':
                alpha = int(255 * (elapsed / self.fade_durations['logo_fade_in']))
            elif self.intro_state == 'logo_fade_out':
                alpha = int(255 * (1 - elapsed / self.fade_durations['logo_fade_out']))
            else:  # logo_stay
                alpha = 255
                
            # Create a surface for alpha blending
            fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, 255 - alpha))
            
            # Draw logo and fade overlay
            self.screen.blit(logo_surface, logo_rect)
            self.screen.blit(fade_surface, (0, 0))
            
        else:
            # Draw background
            self.screen.blit(self.background, (0, 0))
            
            # Draw animated grass patches
            self.draw_grass_patches(self.screen)
            
            # Draw all game objects
            for rock in self.rocks:
                rock.draw(self.screen, 255)
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
                preview_color = (*COLORS['COLONY'], 128)
                pygame.draw.rect(self.screen, preview_color, preview_rect)
            
            self.hud.draw(self.screen, self.colonies, self.ants)
            
            # Draw settings menu and icon
            self.settings_menu.draw()
            settings_icon = self.pixel_icons['settings'].get_current_frame()
            self.screen.blit(settings_icon, self.settings_menu.settings_button)
            
            # Draw day/night overlay
            self.draw_day_night_effects()
            
            # Draw webs
            for web in self.webs:
                web.draw(self.screen)
            
            # Draw spider
            if self.spider:
                self.spider.draw(self.screen)
            
            # Update display
            pygame.display.flip()

    def update_intro_sequence(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.fade_start_time
        
        if self.intro_state == 'logo_fade_in':
            # Play sound at the very start of the sequence
            if not hasattr(self, 'sound_played'):
                self.sounds.play_startup()
                self.sound_played = True
            
            self.alpha = min(255, (elapsed * 255) // self.fade_durations['logo_fade_in'])
            if elapsed >= self.fade_durations['logo_fade_in']:
                self.intro_state = 'logo_stay'
                self.fade_start_time = current_time
                
        elif self.intro_state == 'logo_stay':
            self.alpha = 255  # Keep fully visible
            if elapsed >= self.fade_durations['logo_stay']:
                self.intro_state = 'logo_fade_out'
                self.fade_start_time = current_time
                
        elif self.intro_state == 'logo_fade_out':
            self.alpha = max(0, 255 - (elapsed * 255) // self.fade_durations['logo_fade_out'])
            if elapsed >= self.fade_durations['logo_fade_out']:
                self.intro_state = 'game_running'  # Go directly to game
                self.fade_start_time = current_time
                
                # Start background music as logo fades out
                if not hasattr(self, 'music_started'):
                    self.sounds.start_background_music()
                    self.music_started = True
        
        # Update logo animation
        dt = self.clock.get_time()
        self.logo.update(dt)

    def draw_intro_sequence(self):
        self.screen.fill((0, 0, 0))  # Black background
        
        if self.intro_state in ['logo_fade_in', 'logo_stay', 'logo_fade_out']:
            # Draw animated logo
            logo_surface = self.logo.draw()
            logo_rect = logo_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            
            # Create fade surface for alpha blending
            fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, 255 - self.alpha))
            
            # Draw logo and fade overlay
            self.screen.blit(logo_surface, logo_rect)
            self.screen.blit(fade_surface, (0, 0))
        else:
            # Draw game elements
            self.screen.blit(self.background, (0, 0))
            # ... rest of game drawing code ...

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

    def handle_time_change(self, new_time):
        """Handle transition between day and night"""
        try:
            logging.info(f"Time changing to: {new_time}")
            if new_time == 'night':
                logging.debug("Night time: Snake going to sleep")
                self.snake.start_sleeping()
                
                # Reduce ant perception radius
                for ant in self.ants:
                    ant.perception_radius = Behavior.DAY_NIGHT['ANT_NIGHT_PERCEPTION']
                
            else:
                logging.debug("Day time: Snake waking up")
                self.snake.wake_up()
                
                # Restore ant perception radius
                for ant in self.ants:
                    ant.perception_radius = Behavior.DAY_NIGHT['ANT_DAY_PERCEPTION']
                
        except Exception as e:
            logging.error(f"Error in handle_time_change: {e}")
            raise

    def update_day_night_behaviors(self, is_night, is_transitioning):
        """Update entity behaviors based on time of day"""
        try:
            # Update ant behavior with special night actions
            for ant in self.ants:
                if is_night:
                    ant.speed = Behavior.DAY_NIGHT['ANT_NIGHT_SPEED']
                    ant.perception_radius = Behavior.DAY_NIGHT['ANT_NIGHT_PERCEPTION']
                    
                    # Special night behavior: ants stay closer to colony
                    if hasattr(ant, 'home_colony') and ant.home_colony:
                        distance_to_colony = math.hypot(
                            ant.position[0] - ant.home_colony.position[0],
                            ant.position[1] - ant.home_colony.position[1]
                        )
                        if distance_to_colony > DAY_NIGHT['NIGHT_VISIBILITY']:
                            # Move back towards colony
                            dx = ant.home_colony.position[0] - ant.position[0]
                            dy = ant.home_colony.position[1] - ant.position[1]
                            total = math.sqrt(dx*dx + dy*dy)
                            if total > 0:
                                ant.direction = [dx/total, dy/total]
                else:
                    ant.speed = Behavior.DAY_NIGHT['ANT_DAY_SPEED']
                    ant.perception_radius = Behavior.DAY_NIGHT['ANT_DAY_PERCEPTION']
            
            # Update snake behavior with sleep animation
            if is_night and self.snake_sleep_position:
                self.snake.speed = Behavior.DAY_NIGHT['SNAKE_NIGHT_SPEED']
                # Gradually move snake to sleep position
                dx = self.snake_sleep_position[0] - self.snake.position[0]
                dy = self.snake_sleep_position[1] - self.snake.position[1]
                if abs(dx) > 1 or abs(dy) > 1:
                    self.snake.position = (
                        self.snake.position[0] + dx * 0.1,
                        self.snake.position[1] + dy * 0.1
                    )
                else:
                    self.snake.position = self.snake_sleep_position
                    # Add sleep animation (Z's)
                    if hasattr(self, 'sleep_animation_time'):
                        if pygame.time.get_ticks() - self.sleep_animation_time > 1000:
                            self.sleep_animation_time = pygame.time.get_ticks()
                    else:
                        self.sleep_animation_time = pygame.time.get_ticks()
            else:
                self.snake.speed = Behavior.DAY_NIGHT['SNAKE_DAY_SPEED']
                if hasattr(self, 'sleep_animation_time'):
                    delattr(self, 'sleep_animation_time')
                
        except Exception as e:
            logging.error(f"Error in update_day_night_behaviors: {e}")

    def draw_day_night_effects(self):
        """Draw enhanced day/night visual effects with smooth celestial transitions"""
        current_time = pygame.time.get_ticks()
        cycle_time = (current_time - self.cycle_start_time) % DAY_NIGHT['CYCLE_DURATION']
        
        # Calculate base overlay alpha
        max_alpha = DAY_NIGHT['MAX_NIGHT_ALPHA']
        
        # Calculate cycle progress (0 to 1 for full day/night cycle)
        cycle_progress = cycle_time / DAY_NIGHT['CYCLE_DURATION']
        
        # Constants for path calculation
        base_height = WINDOW_HEIGHT * 0.4
        path_height = WINDOW_HEIGHT * 0.15
        
        # Determine if it's night time and calculate specific progress
        is_night = cycle_progress >= 0.5
        if is_night:
            # Moon movement (0 to 1 for night only)
            body_progress = (cycle_progress - 0.5) * 2
            celestial_x = -WINDOW_WIDTH * 0.1 + (WINDOW_WIDTH * 1.2) * body_progress
            celestial_y = base_height + path_height * math.sin(body_progress * math.pi)
        else:
            # Sun movement (0 to 1 for day only)
            body_progress = cycle_progress * 2
            celestial_x = -WINDOW_WIDTH * 0.1 + (WINDOW_WIDTH * 1.2) * body_progress
            celestial_y = base_height - path_height * math.sin(body_progress * math.pi)
        
        # Draw celestial body and effects
        if is_night:
            # Draw moon and glow
            pygame.draw.circle(self.screen, VISUALS['TIME']['NIGHT']['MOON'],
                             (int(celestial_x), int(celestial_y)), 20)
            for radius in range(30, 20, -2):
                glow_color = (*VISUALS['TIME']['NIGHT']['MOON_GLOW'][:3], 
                             int(255 * (30-radius)/10))
                pygame.draw.circle(self.screen, glow_color,
                                 (int(celestial_x), int(celestial_y)), radius)
        else:
            # Draw animated sun
            self._draw_sun((celestial_x, celestial_y), body_progress)
        
        # Check for mouse hover over visible celestial body
        if 0 <= celestial_x <= WINDOW_WIDTH:
            mouse_pos = pygame.mouse.get_pos()
            celestial_pos = (int(celestial_x), int(celestial_y))
            celestial_radius = 25 if not is_night else 20
            distance_to_mouse = math.hypot(mouse_pos[0] - celestial_pos[0], 
                                         mouse_pos[1] - celestial_pos[1])
            
            # Draw tooltip on hover
            if distance_to_mouse <= celestial_radius:
                minutes_in_cycle = DAY_NIGHT['CYCLE_DURATION'] / 1000 / 60
                current_minutes = (cycle_time / 1000 / 60)
                time_left = minutes_in_cycle/2 - current_minutes if not is_night else \
                           minutes_in_cycle - current_minutes
                
                if is_night:
                    time_str = f"Night Time - {time_left:.1f} minutes until dawn"
                else:
                    time_str = f"Day Time - {time_left:.1f} minutes until dusk"
                
                # Draw tooltip using UI style
                tooltip_font = pygame.font.Font(None, UI.Tooltips.FONT_SIZE)
                tooltip_surface = tooltip_font.render(time_str, True, UI.Tooltips.TEXT_COLOR)
                tooltip_rect = tooltip_surface.get_rect()
                tooltip_rect.centerx = int(celestial_x)
                tooltip_rect.bottom = int(celestial_y) - UI.Tooltips.OFFSET_Y
                
                background_rect = tooltip_rect.inflate(UI.Tooltips.PADDING * 2, UI.Tooltips.PADDING * 2)
                pygame.draw.rect(self.screen, UI.Tooltips.BACKGROUND, background_rect)
                pygame.draw.rect(self.screen, UI.Tooltips.BORDER_COLOR, background_rect, 
                               UI.Tooltips.BORDER_WIDTH)
                self.screen.blit(tooltip_surface, tooltip_rect)
        
        # Handle transitions and overlays
        if cycle_time < DAY_NIGHT['DAWN_DURATION']:
            # Dawn transition
            progress = cycle_time / DAY_NIGHT['DAWN_DURATION']
            alpha = int(max_alpha * (1 - progress))
            dawn_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            dawn_overlay.fill((*VISUALS['TIME']['TRANSITIONS']['DAWN']['TINT'], 
                              VISUALS['TIME']['TRANSITIONS']['DAWN']['ALPHA']))
            self.screen.blit(dawn_overlay, (0, 0))
        
        elif cycle_time < DAY_NIGHT['CYCLE_DURATION'] / 2:
            # Day
            alpha = 0
            
        elif cycle_time < DAY_NIGHT['CYCLE_DURATION'] / 2 + DAY_NIGHT['DUSK_DURATION']:
            # Dusk transition
            transition_time = cycle_time - DAY_NIGHT['CYCLE_DURATION'] / 2
            progress = transition_time / DAY_NIGHT['DUSK_DURATION']
            alpha = int(max_alpha * progress)
            dusk_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            dusk_overlay.fill((*VISUALS['TIME']['TRANSITIONS']['DUSK']['TINT'], 
                              VISUALS['TIME']['TRANSITIONS']['DUSK']['ALPHA']))
            self.screen.blit(dusk_overlay, (0, 0))
        else:
            # Night
            alpha = max_alpha
            if random.random() < 0.05:
                star_pos = (random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))
                star_size = random.randint(1, 3)
                pygame.draw.circle(self.screen, VISUALS['TIME']['NIGHT']['STARS'], 
                                 star_pos, star_size)
        
        # Apply base night overlay
        night_color = list(VISUALS['TIME']['NIGHT']['SKY'])
        night_color[3] = alpha
        self.night_overlay.fill(night_color)
        self.screen.blit(self.night_overlay, (0, 0)) 

    def _draw_sun(self, pos, cycle_progress):
        """Draw a pixelated sun with dynamic rays and warm gradients"""
        x, y = int(pos[0]), int(pos[1])
        current_time = pygame.time.get_ticks()
        
        # Core sun colors
        sun_colors = [
            (255, 247, 184),  # Bright yellow
            (255, 222, 123),  # Golden yellow
            (255, 198, 93),   # Orange yellow
            (255, 170, 66)    # Deep orange
        ]
        
        # Create larger pixel pattern for circular shape
        pixel_pattern = [
            "   XXXXX   ",
            "  XXXXXXX  ",
            " XXXXXXXXX ",
            "XXXXXXXXXXX",
            "XXXXXXXXXXX",
            "XXXXXXXXXXX",
            "XXXXXXXXXXX",
            "XXXXXXXXXXX",
            " XXXXXXXXX ",
            "  XXXXXXX  ",
            "   XXXXX   "
        ]
        
        # Calculate sun dimensions
        pixel_size = 3
        pattern_width = len(pixel_pattern[0])
        sun_radius = (pattern_width * pixel_size) // 2
        
        # Draw rays first (behind the sun)
        num_rays = 12
        max_ray_length = sun_radius * 0.5  # Ray length relative to sun size
        ray_width_base = 3
        
        ray_colors = [
            (255, 247, 184, 255),  # Bright yellow
            (255, 222, 123, 255),  # Golden yellow
        ]
        
        # Draw rays from center
        for i in range(num_rays):
            angle = (i * (360 / num_rays) + current_time * 0.02) % 360
            ray_length = max_ray_length * (0.7 + 0.3 * math.sin(current_time * 0.003 + i * 0.5))
            
            # Start from center of sun
            start_x = x
            start_y = y
            end_x = x + math.cos(math.radians(angle)) * (sun_radius + ray_length)
            end_y = y + math.sin(math.radians(angle)) * (sun_radius + ray_length)
            
            # Draw ray with gradient
            points = []
            ray_width = ray_width_base
            for t in range(8):
                progress = t / 7
                current_x = start_x + (end_x - start_x) * progress
                current_y = start_y + (end_y - start_y) * progress
                
                # Reduced wobble effect
                wobble = math.sin(current_time * 0.004 + i * 0.5) * 0.5
                current_x += math.cos(math.radians(angle + 90)) * wobble
                current_y += math.sin(math.radians(angle + 90)) * wobble
                
                points.append((current_x, current_y))
                
                color = ray_colors[0] if t < 4 else ray_colors[1]
                alpha = int(255 * (1 - progress))
                color = (*color[:3], alpha)
                
                if len(points) > 1:
                    pygame.draw.line(self.screen, color, points[-2], points[-1], 
                                   max(1, int(ray_width * (1 - progress * 0.5))))
        
        # Draw pixelated sun disc over the rays
        for row_idx, row in enumerate(pixel_pattern):
            for col_idx, cell in enumerate(row):
                if cell == 'X':
                    pixel_x = x - (len(row) * pixel_size // 2) + col_idx * pixel_size
                    pixel_y = y - (len(pixel_pattern) * pixel_size // 2) + row_idx * pixel_size
                    
                    noise_val = noise.pnoise2(col_idx * 0.5 + current_time * 0.001,
                                            row_idx * 0.5,
                                            octaves=2,
                                            persistence=0.5)
                    
                    dist_from_center = math.sqrt(
                        (row_idx - len(pixel_pattern)//2)**2 + 
                        (col_idx - len(row)//2)**2
                    )
                    color_index = min(3, int(dist_from_center/2))
                    color = list(sun_colors[color_index])
                    
                    color = [min(255, max(0, c + int(noise_val * 15))) for c in color]
                    
                    pygame.draw.rect(self.screen, color, 
                                   (pixel_x, pixel_y, pixel_size, pixel_size)) 