import pygame
import random
import time
import logging
import math

# Initialize pygame
pygame.init()

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ============================
# Constants (Easily Tweakable)
# ============================

# Screen dimensions
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 1024

# Map dimensions
MAP_WIDTH = 1024
MAP_HEIGHT = 1024

# Colors
COLOR_MAIN_PIXEL = (0, 0, 0)          # Black for main pixel (heart)
COLOR_ANT_PIXEL = (0, 0, 0)           # Black for pixel ants
COLOR_ROCK = (128, 128, 128)          # Gray
COLOR_GRASS = (0, 255, 0)             # Green
COLOR_BREADCRUMB = (255, 255, 0)      # Yellow
COLOR_BACKGROUND = (255, 255, 255)    # White

# Main Pixel Size Constraints
MAIN_PIXEL_SIZE = 10                 # Size for main pixel square
MIN_MAIN_PIXEL_SIZE = 5              # Minimum size for main pixel
MAX_MAIN_PIXEL_SIZE = 10             # Maximum size for main pixel

# Game settings
NUM_INITIAL_ANTS = 4
NUM_ROCKS = 100
NUM_GRASS_CLUSTERS = 50
ANT_PIXEL_SIZE = 4                    # Size for pixel ants
RESOURCES_NEEDED_FOR_ANT = {'minerals': 15, 'plants': 10}
ENERGY_CONSUMPTION_RATE = 1           # Energy consumed per minute
BREADCRUMB_LIFETIME = 20              # Breadcrumb lifetime in seconds
AWARENESS_RADIUS = 50                 # Radius for detecting resources and cursor

# Upgrade settings
UPGRADE_COST = {
    'storage': {'minerals': 100},
    'speed_boost': {'minerals': 100, 'plants': 50},
    'energy_efficiency': {'minerals': 100, 'plants': 100},
    'energy_storage': {'minerals': 100, 'plants': 100},
    'carry_capacity': {'minerals': 50},
    'durability': {'plants': 50}
}
UPGRADE_EFFECTS = {
    'storage': 10,              # Increase storage by 10
    'speed_boost': 1.2,         # Increase speed by 20%
    'energy_efficiency': 0.8,   # Reduce energy consumption by 20%
    'energy_storage': 10,       # Increase battery capacity by 10 units
    'carry_capacity': 5,        # Increase carry capacity by 5
    'durability': 1.5           # Increase durability by 50%
}

# Node creation cost
NODE_CREATION_COST = {'minerals': 200, 'plants': 400}

# Resource contents
ROCK_MINERAL_CONTENT = 10          # Amount of minerals in each rock
PLANT_RESOURCE_CONTENT = 15        # Amount of resources in each plant

# Add this constant to control the initial placement
MAX_INITIAL_PIXELS = 1  # Only one main pixel node can be placed initially

# ======================================
# Initialize Screen and Clock
# ======================================

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Muchas Cacas! Pixel Exploration Game")

clock = pygame.time.Clock()

# ======================================
# Helper Functions
# ======================================

def distance(pos1, pos2):
    """Calculate Euclidean distance between two positions."""
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

def update_breadcrumbs(breadcrumbs):
    """Remove breadcrumbs that have exceeded their lifetime."""
    current_time = pygame.time.get_ticks()
    return [breadcrumb for breadcrumb in breadcrumbs if current_time - breadcrumb.creation_time < BREADCRUMB_LIFETIME * 1000]

# ======================================
# GameObject and Derived Classes
# ======================================

class GameObject:
    def __init__(self, position, size, color):
        self.position = position
        self.size = size
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, pygame.Rect(self.position[0] - self.size // 2, self.position[1] - self.size // 2, self.size, self.size))

class Rock(GameObject):
    def __init__(self, position):
        super().__init__(position, 10, COLOR_ROCK)
        self.minerals = ROCK_MINERAL_CONTENT

class Plant(GameObject):
    def __init__(self, position):
        super().__init__(position, 10, COLOR_GRASS)
        self.resources = PLANT_RESOURCE_CONTENT

    def grow(self, biome):
        growth_rate = 0.1 if biome != 'lake' else 0.2
        if self.resources < PLANT_RESOURCE_CONTENT:
            self.resources += growth_rate
            if self.resources > PLANT_RESOURCE_CONTENT:
                self.resources = PLANT_RESOURCE_CONTENT
            logging.debug(f"Plant at {self.position} grew to {self.resources} resources")

class Breadcrumb(GameObject):
    def __init__(self, position):
        super().__init__(position, 2, COLOR_BREADCRUMB)
        self.creation_time = pygame.time.get_ticks()

class MainPixelNode(GameObject):
    def __init__(self, position):
        super().__init__(position, MAIN_PIXEL_SIZE, COLOR_MAIN_PIXEL)
        self.energy = 50
        self.battery_capacity = 50
        self.resources = {'minerals': 0, 'plants': 0}
        self.upgrades = {'storage': False, 'energy_efficiency': False}
        self.spawned_ants = 0  # Track the number of ants spawned

    def draw(self, surface):
        pulse_size = MAIN_PIXEL_SIZE + int(5 * math.sin(pygame.time.get_ticks() / 500))
        pygame.draw.rect(surface, self.color, pygame.Rect(self.position[0] - pulse_size // 2, self.position[1] - pulse_size // 2, pulse_size, pulse_size))

        if self.upgrades['storage']:
            pygame.draw.rect(surface, (0, 255, 0), pygame.Rect(self.position[0] - 5, self.position[1] - 5, 10, 10))
        if self.upgrades['energy_efficiency']:
            pygame.draw.rect(surface, (255, 255, 0), pygame.Rect(self.position[0] + 5, self.position[1] + 5, 10, 10))

    def has_sufficient_resources(self):
        return self.resources['minerals'] >= RESOURCES_NEEDED_FOR_ANT['minerals'] and self.resources['plants'] >= RESOURCES_NEEDED_FOR_ANT['plants']

    def spawn_ants(self, pixels, num_ants=4):
        max_ants = 10  # Maximum number of ants this node can spawn
        ants_to_spawn = min(num_ants, max_ants - self.spawned_ants)
        for _ in range(ants_to_spawn):
            ant_position = (
                self.position[0] + random.randint(-10, 10),
                self.position[1] + random.randint(-10, 10)
            )
            pixels.append(Ant(ant_position))
            self.spawned_ants += 1
            logging.debug(f"Spawned pixel ant at {ant_position}")

    def update_energy(self, time_of_day):
        if time_of_day == 'day':
            self.energy += 10
        else:
            self.energy -= ENERGY_CONSUMPTION_RATE
        self.energy = min(self.energy, self.battery_capacity)

    def upgrade(self, upgrade_type):
        if upgrade_type == 'storage':
            self.resources['minerals'] += UPGRADE_EFFECTS['storage']
        elif upgrade_type == 'energy_efficiency':
            self.energy *= UPGRADE_EFFECTS['energy_efficiency']
        elif upgrade_type == 'energy_storage':
            self.battery_capacity += UPGRADE_EFFECTS['energy_storage']

class Ant(GameObject):
    def __init__(self, position, direction=None, size=ANT_PIXEL_SIZE):
        super().__init__(position, size, COLOR_ANT_PIXEL)
        self.direction = direction if direction else (random.choice([-1, 1]), random.choice([-1, 1]))
        self.resources = {'minerals': 0, 'plants': 0}
        self.carry_capacity = 10
        self.speed = 2.0
        self.health_points = 10

    def draw(self, surface):
        # Draw the ant with a glowing effect if carrying resources
        glow_color = (0, 0, 255) if self.resources['minerals'] > 0 or self.resources['plants'] > 0 else self.color
        pygame.draw.rect(surface, glow_color, pygame.Rect(self.position[0] - self.size // 2, self.position[1] - self.size // 2, self.size, self.size))

    def perceive(self, cursor_position, snake_position):
        # Flee from the cursor or snake if within perception radius
        if distance(self.position, cursor_position) < AWARENESS_RADIUS or distance(self.position, snake_position) < AWARENESS_RADIUS:
            self.direction = (-self.direction[0], -self.direction[1])  # Reverse direction

    def leave_breadcrumb(self, breadcrumbs):
        # Leave a breadcrumb if carrying resources
        if self.resources['minerals'] > 0 or self.resources['plants'] > 0:
            breadcrumbs.append(Breadcrumb(self.position))

    def heal(self):
        """Heal the ant by consuming plants."""
        while self.resources['plants'] >= 2 and self.health_points < 10:
            self.resources['plants'] -= 2  # Consume 2 plant units
            self.health_points += 1  # Restore 1 health point
            logging.debug(f"Ant at {self.position} healed to {self.health_points} HP")

    def upgrade(self, upgrade_type):
        if upgrade_type == 'carry_capacity':
            self.carry_capacity += UPGRADE_EFFECTS['carry_capacity']
        elif upgrade_type == 'health_points':
            self.health_points += UPGRADE_EFFECTS['durability']
        elif upgrade_type == 'speed_boost':
            self.speed *= UPGRADE_EFFECTS['speed_boost']

class Snake(GameObject):
    def __init__(self, position):
        super().__init__(position, 20, (255, 0, 0))  # Red color for the snake
        self.direction = (1, 0)  # Initial direction

    def move(self):
        # Move the snake in its current direction
        self.position = (
            (self.position[0] + self.direction[0]) % MAP_WIDTH,
            (self.position[1] + self.direction[1]) % MAP_HEIGHT
        )
        logging.debug(f"Snake moved to {self.position}")

    def detect_and_attack(self, pixels):
        # Logic for detecting and attacking pixels
        # This is a placeholder for actual logic
        return {}, self.position

    def update_danger_zones(self):
        # Logic to update danger zones around the snake
        pass

# ======================================
# Main Game Loop
# ======================================

def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT, screen

    # Define biomes
    BIOMES = {
        'forest': {
            'color_palette': {
                'background': (34, 139, 34),  # Forest green
                'rock': COLOR_ROCK,
                'plant': COLOR_GRASS
            },
            'effects': 'forest'
        },
        'desert': {
            'color_palette': {
                'background': (210, 180, 140),  # Tan
                'rock': COLOR_ROCK,
                'plant': (189, 183, 107)  # Dark khaki
            },
            'effects': 'desert'
        },
        'rocky': {
            'color_palette': {
                'background': (112, 128, 144),  # Slate gray
                'rock': COLOR_ROCK,
                'plant': COLOR_GRASS
            },
            'effects': 'rocky'
        },
        'lake': {
            'color_palette': {
                'background': (0, 191, 255),   # Deep sky blue
                'rock': COLOR_ROCK,
                'plant': (34, 139, 34)         # Forest green
            },
            'effects': 'lake'
        }
    }

    # Select a random biome
    selected_biome = random.choice(list(BIOMES.keys()))
    biome = BIOMES[selected_biome]
    logging.debug(f"Selected biome: {selected_biome}")

    # Initialize game objects
    rocks = [Rock((random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT))) for _ in range(NUM_ROCKS)]
    grass = [Plant((random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT))) for _ in range(NUM_GRASS_CLUSTERS)]
    breadcrumbs = []
    pixels = []
    resource_piles = []
    resources_collected = {'minerals': 0, 'plants': 0}

    # Define the snake
    snake = Snake((random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT)))

    main_pixel_position = None
    placing_main_pixel = True
    initial_pixel_count = 0

    running = True

    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                logging.debug(f"Window resized to {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    if placing_main_pixel and initial_pixel_count < MAX_INITIAL_PIXELS:
                        main_pixel_position = (
                            mouse_pos[0],
                            mouse_pos[1]
                        )
                        main_pixel_node = MainPixelNode(main_pixel_position)
                        pixels.append(main_pixel_node)
                        main_pixel_node.spawn_ants(pixels)  # Spawn ants immediately after placement
                        initial_pixel_count += 1
                        logging.debug(f"Placed main pixel at {main_pixel_position} with size {MAIN_PIXEL_SIZE}")
                        placing_main_pixel = False

        screen.fill(biome['color_palette']['background'])

        snake.move()
        collected_resources, drop_position = snake.detect_and_attack(pixels)
        if collected_resources:
            for resource_type, amount in collected_resources.items():
                if amount > 0:
                    resource_color = COLOR_ROCK if resource_type == 'minerals' else COLOR_GRASS
                    resource_piles.append(GameObject(drop_position, 5, resource_color))
                    logging.debug(f"Dropped {amount} {resource_type} at {drop_position}")

        snake.update_danger_zones()

        for rock in rocks[:]:
            rock.draw(screen)
            if rock.minerals <= 0:
                rocks.remove(rock)
                logging.debug(f"Rock at {rock.position} depleted and removed")

        for plant in grass[:]:
            if plant.resources > 0:
                plant.grow(selected_biome)
                plant.draw(screen)
            else:
                grass.remove(plant)
                logging.debug(f"Plant at {plant.position} depleted and removed")

        for breadcrumb in breadcrumbs:
            breadcrumb.draw(screen)

        for pixel in pixels:
            if isinstance(pixel, Ant):
                pixel.perceive(pygame.mouse.get_pos(), snake.position)
                pixel.leave_breadcrumb(breadcrumbs)
                pixel.heal()  # Heal if possible
                pixel.draw(screen)  # Ensure ants are drawn on the screen

        for resource in resource_piles:
            resource.draw(screen)

        snake.draw(screen)

        if main_pixel_position:
            main_pixel_node.spawn_ants(pixels)
            main_pixel_node.update_energy('day' if current_time % 120000 < 60000 else 'night')

        breadcrumbs = update_breadcrumbs(breadcrumbs)

        adapt_to_environment(pixels, rocks, grass, selected_biome)

        handle_upgrades_and_exchanges(pixels, resources_collected)

        # Ensure ants are moving
        move_pixel_ants(pixels, breadcrumbs, main_pixel_position, rocks, grass, resources_collected, snake)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def adapt_to_environment(pixels, rocks, grass, biome):
    """Adapt the environment by regenerating resources."""
    for plant in grass:
        plant.grow(biome)  # Grow plants based on biome effects

    # Example: Regenerate minerals in rocks over time
    for rock in rocks:
        if rock.minerals < ROCK_MINERAL_CONTENT:
            rock.minerals += 0.01  # Slowly regenerate minerals
            if rock.minerals > ROCK_MINERAL_CONTENT:
                rock.minerals = ROCK_MINERAL_CONTENT

def handle_upgrades_and_exchanges(pixels, resources_collected):
    """Handle upgrades and exchanges for the main pixel node and ants."""
    for pixel in pixels:
        if isinstance(pixel, MainPixelNode):
            # Check for possible upgrades for the main pixel node
            if pixel.resources['minerals'] >= UPGRADE_COST['storage']['minerals']:
                pixel.upgrade('storage')
            if pixel.resources['minerals'] >= UPGRADE_COST['speed_boost']['minerals'] and pixel.resources['plants'] >= UPGRADE_COST['speed_boost']['plants']:
                pixel.upgrade('speed_boost')
            if pixel.resources['minerals'] >= UPGRADE_COST['energy_efficiency']['minerals'] and pixel.resources['plants'] >= UPGRADE_COST['energy_efficiency']['plants']:
                pixel.upgrade('energy_efficiency')
            if pixel.resources['minerals'] >= UPGRADE_COST['energy_storage']['minerals'] and pixel.resources['plants'] >= UPGRADE_COST['energy_storage']['plants']:
                pixel.upgrade('energy_storage')
        elif isinstance(pixel, Ant):
            # Check for possible upgrades for ants
            if resources_collected['minerals'] >= UPGRADE_COST['carry_capacity']['minerals']:
                pixel.upgrade('carry_capacity')
                resources_collected['minerals'] -= UPGRADE_COST['carry_capacity']['minerals']
            if resources_collected['plants'] >= UPGRADE_COST['durability']['plants']:
                pixel.upgrade('durability')
                resources_collected['plants'] -= UPGRADE_COST['durability']['plants']

def move_pixel_ants(pixels, breadcrumbs, main_pixel_position, rocks, grass, resources_collected, snake):
    """Move pixel ants and handle their interactions."""
    for pixel in pixels:
        if isinstance(pixel, Ant):
            # Move the ant in its current direction
            new_position = (
                pixel.position[0] + pixel.direction[0] * pixel.speed,
                pixel.position[1] + pixel.direction[1] * pixel.speed
            )

            # Ensure the ant stays within the map boundaries
            new_position = (
                max(0, min(new_position[0], MAP_WIDTH)),
                max(0, min(new_position[1], MAP_HEIGHT))
            )

            # Update the ant's position
            pixel.position = new_position

            # Check for resource collection
            for rock in rocks:
                if distance(pixel.position, rock.position) < AWARENESS_RADIUS and rock.minerals > 0:
                    collected = min(rock.minerals, pixel.carry_capacity - pixel.resources['minerals'])
                    pixel.resources['minerals'] += collected
                    rock.minerals -= collected
                    logging.debug(f"Pixel ant at {pixel.position} collected {collected} minerals from rock at {rock.position}")

            for plant in grass:
                if distance(pixel.position, plant.position) < AWARENESS_RADIUS and plant.resources > 0:
                    collected = min(plant.resources, pixel.carry_capacity - pixel.resources['plants'])
                    pixel.resources['plants'] += collected
                    plant.resources -= collected
                    logging.debug(f"Pixel ant at {pixel.position} collected {collected} plant resources from plant at {plant.position}")

            # Return to main pixel node if carrying resources
            if pixel.resources['minerals'] > 0 or pixel.resources['plants'] > 0:
                if distance(pixel.position, main_pixel_position) < AWARENESS_RADIUS:
                    resources_collected['minerals'] += pixel.resources['minerals']
                    resources_collected['plants'] += pixel.resources['plants']
                    logging.debug(f"Pixel ant at {pixel.position} returned resources to main pixel node")
                    pixel.resources['minerals'] = 0
                    pixel.resources['plants'] = 0

            # Leave breadcrumbs
            if random.random() < 0.1:  # Random chance to leave a breadcrumb
                breadcrumbs.append(Breadcrumb(pixel.position))

if __name__ == "__main__":
    main()
