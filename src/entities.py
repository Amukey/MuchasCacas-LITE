import pygame
import random
import logging
import math
from resources import Rock, Plant, Bush
from constants import (
    Economy, Behavior, COLONY_MIN_SIZE, COLONY_MAX_SIZE, 
    ANT_SIZE, UI, COLORS, RESOURCE_EFFECTS, PERCEPTION_RADIUS, VISUALS,
    DAY_NIGHT, WINDOW_WIDTH, WINDOW_HEIGHT  # Added DAY_NIGHT and window dimensions
)
import noise

# Constants for entity sizes and colors
PERCEPTION_RADIUS = 40

# Colors
COLOR_GLOW_BLUE = (0, 0, 255) # Blue glow
COLOR_GLOW_YELLOW = (255, 255, 0) # Yellow glow
COLOR_COLONY_OUTLINE = (173, 216, 230)  # Baby blue

class Colony:
    def __init__(self, position, ants, game, is_main=True):
        self.position = position
        self.sprite = pygame.Surface((COLONY_MIN_SIZE, COLONY_MIN_SIZE))
        self.is_main = is_main
        self.resources = {
            'minerals': Economy.COLONY_INITIAL_MINERALS if is_main else 0,
            'plants': Economy.COLONY_INITIAL_PLANTS if is_main else 0
        }
        self.ant_count = 0
        self.max_ants = Economy.COLONY_MAX_ANTS
        self.game = game  # Store game reference
        self.spawn_timer = 0
        self.spawn_interval = 5000  # Check for spawning every 5 seconds
        self.flash_timer = 0
        self.flash_interval = 500  # Flash every 500ms
        self.flash_state = False  # For toggling flash
        self.ant_indicator_rect = None
        self.colony_indicator_rect = None

        # Add factory animation properties
        self.factory_noise = self.generate_factory_pattern()
        self.gear_rotation = 0
        self.conveyor_offset = 0
        self.light_flash_timer = 0
        self.working_parts = []  # Store animated machinery parts
        self.generate_working_parts()

        # Spawn initial ants if this is the main colony
        if is_main:
            self.spawn_initial_ants(ants)

    def spawn_initial_ants(self, ants):
        """Spawn 2 initial ants for the main colony"""
        for _ in range(2):
            if self.ant_count < self.max_ants:
                ant_position = (
                    self.position[0] + random.randint(-10, 10),
                    self.position[1] + random.randint(-10, 10)
                )
                new_ant = Ant(ant_position, self.game)
                new_ant.home_colony = self
                ants.append(new_ant)
                self.ant_count += 1

    def can_spawn_ant(self):
        """Check if colony can spawn a new ant"""
        return (self.ant_count < self.max_ants and 
                self.resources['minerals'] >= Economy.Costs.ANT_MINERALS and 
                self.resources['plants'] >= Economy.Costs.ANT_PLANTS)

    def can_create_colony(self):
        """Check if colony has enough resources to create a new colony"""
        return (self.resources['minerals'] >= Economy.Costs.NEW_COLONY_MINERALS and 
                self.resources['plants'] >= Economy.Costs.NEW_COLONY_PLANTS and 
                self.is_main)  # Only main colony can create new colonies

    def spawn_ant(self, ants):
        """Spawn a new ant if resources are available"""
        if self.can_spawn_ant():
            ant_position = (
                self.position[0] + random.randint(-10, 10),
                self.position[1] + random.randint(-10, 10)
            )
            new_ant = Ant(ant_position, self.game)
            new_ant.home_colony = self
            ants.append(new_ant)
            self.ant_count += 1
            self.resources['minerals'] -= Economy.Costs.ANT_MINERALS
            self.resources['plants'] -= Economy.Costs.ANT_PLANTS
            self.game.sounds.play_ant_spawn()

    def update(self, current_time, ants):
        """Automatically decide when to spawn ants based on resources"""
        if current_time - self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = current_time
            
            # More aggressive spawning when ant count is low
            if self.ant_count < self.max_ants and self.can_spawn_ant():
                # Higher priority to spawn when fewer ants
                spawn_priority = (self.max_ants - self.ant_count) / self.max_ants
                
                if random.random() < spawn_priority:
                    self.spawn_ant(ants)
                    logging.debug(f"Colony auto-spawned ant. Current count: {self.ant_count}/{self.max_ants}")

    def generate_factory_pattern(self):
        """Generate a noise-based factory texture"""
        size = COLONY_MAX_SIZE
        pattern = pygame.Surface((size, size))
        
        # Create base metallic texture using noise
        for x in range(size):
            for y in range(size):
                noise_val = noise.pnoise2(x/10, y/10, octaves=3, persistence=0.5)
                # Create metallic look with darker and lighter pixels
                color_val = int(128 + noise_val * 64)
                pattern.set_at((x, y), (color_val, color_val, color_val))
        
        # Add "circuit" lines
        for _ in range(5):
            start = random.randint(0, size-1)
            pygame.draw.line(pattern, (50, 50, 50), 
                           (0, start), (size, start), 1)
            pygame.draw.line(pattern, (50, 50, 50), 
                           (start, 0), (start, size), 1)
        
        return pattern

    def generate_working_parts(self):
        """Generate animated machinery parts"""
        size = COLONY_MAX_SIZE
        center = size // 2
        
        # Add gears
        self.working_parts.append({
            'type': 'gear',
            'pos': (center - 5, center - 5),
            'size': 6,
            'speed': 2
        })
        
        # Add conveyor belts
        self.working_parts.append({
            'type': 'conveyor',
            'pos': (5, center),
            'width': size - 10,
            'height': 4,
            'speed': 1
        })
        
        # Add blinking lights
        for _ in range(3):
            self.working_parts.append({
                'type': 'light',
                'pos': (random.randint(2, size-2), random.randint(2, size-2)),
                'size': 2,
                'state': random.random() < 0.5
            })

    def draw(self, surface):
        current_time = pygame.time.get_ticks()
        size = COLONY_MAX_SIZE
        
        # Create colony surface with factory pattern
        colony_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        colony_surface.blit(self.factory_noise, (0, 0))
        
        # Update and draw working parts
        self.gear_rotation += 2
        self.conveyor_offset = (self.conveyor_offset + 1) % 8
        
        for part in self.working_parts:
            if part['type'] == 'gear':
                self.draw_gear(colony_surface, part)
            elif part['type'] == 'conveyor':
                self.draw_conveyor(colony_surface, part)
            elif part['type'] == 'light':
                if current_time % 1000 < 500:  # Blink every half second
                    part['state'] = not part['state']
                self.draw_light(colony_surface, part)
        
        # Draw outline for secondary colonies
        if not self.is_main:
            pygame.draw.rect(colony_surface, COLORS['COLONY_OUTLINE'], 
                           (0, 0, size, size), 2)
        
        # Draw to main surface
        surface.blit(colony_surface, 
                    (self.position[0] - size // 2,
                     self.position[1] - size // 2))
        
        # Update flash state
        if current_time - self.flash_timer > self.flash_interval:
            self.flash_timer = current_time
            self.flash_state = not self.flash_state
        
        # Draw resource bars and indicators
        self.draw_resource_bars(surface)
        self.draw_indicators(surface)

    def draw_gear(self, surface, gear):
        """Draw a rotating gear"""
        center = (gear['pos'][0] + gear['size'], gear['pos'][1] + gear['size'])
        teeth = 8
        inner_radius = gear['size'] - 2
        outer_radius = gear['size']
        
        for i in range(teeth):
            angle = self.gear_rotation + (i * 360 / teeth)
            rad = math.radians(angle)
            
            # Draw gear tooth
            start = (center[0] + inner_radius * math.cos(rad),
                    center[1] + inner_radius * math.sin(rad))
            end = (center[0] + outer_radius * math.cos(rad),
                   center[1] + outer_radius * math.sin(rad))
            pygame.draw.line(surface, (100, 100, 100), start, end, 2)

    def draw_conveyor(self, surface, conveyor):
        """Draw an animated conveyor belt"""
        rect = pygame.Rect(conveyor['pos'][0], conveyor['pos'][1],
                          conveyor['width'], conveyor['height'])
        pygame.draw.rect(surface, (80, 80, 80), rect)
        
        # Draw moving segments
        for x in range(conveyor['pos'][0], conveyor['pos'][0] + conveyor['width'], 4):
            pos = (x + self.conveyor_offset) % (conveyor['width'] + 4)
            pygame.draw.line(surface, (60, 60, 60),
                           (pos, conveyor['pos'][1]),
                           (pos, conveyor['pos'][1] + conveyor['height']))

    def draw_light(self, surface, light):
        """Draw a blinking indicator light"""
        color = (0, 255, 0) if light['state'] else (0, 100, 0)
        pygame.draw.circle(surface, color,
                         light['pos'], light['size'])

    def draw_resource_bars(self, surface):
        """Draw minimal resource indicators near colony"""
        # Small dots or thin bars below colony
        bar_width = 20
        bar_height = 2
        spacing = 4
        
        # Minerals bar (brown)
        mineral_percent = min(1, self.resources['minerals'] / UI.Bars.MAX_MINERAL_VALUE)
        pygame.draw.rect(surface, UI.Bars.BACKGROUND,
                        (self.position[0] - bar_width - spacing, 
                         self.position[1] + COLONY_MAX_SIZE//2 + 2,
                         bar_width, bar_height))
        pygame.draw.rect(surface, UI.Bars.MINERAL,
                        (self.position[0] - bar_width - spacing,
                         self.position[1] + COLONY_MAX_SIZE//2 + 2,
                         bar_width * mineral_percent, bar_height))
        
        # Plants bar (green)
        plant_percent = min(1, self.resources['plants'] / UI.Bars.MAX_PLANT_VALUE)
        pygame.draw.rect(surface, UI.Bars.BACKGROUND,
                        (self.position[0] + spacing,
                         self.position[1] + COLONY_MAX_SIZE//2 + 2,
                         bar_width, bar_height))
        pygame.draw.rect(surface, UI.Bars.PLANT,
                        (self.position[0] + spacing,
                         self.position[1] + COLONY_MAX_SIZE//2 + 2,
                         bar_width * plant_percent, bar_height))

    def draw_indicators(self, surface):
        """Draw ant spawn and colony creation indicators"""
        # Draw ant spawn indicator
        if self.can_spawn_ant():
            self.ant_indicator_rect = pygame.Rect(
                self.position[0] - UI.Indicators.SIZE // 2,
                self.position[1] + UI.Indicators.VERTICAL_OFFSET,
                UI.Indicators.SIZE,
                UI.Indicators.SIZE
            )
            pygame.draw.rect(surface, COLOR_GLOW_BLUE, self.ant_indicator_rect)
        else:
            self.ant_indicator_rect = None

        # Draw colony creation indicator
        if self.can_create_colony():
            self.colony_indicator_rect = pygame.Rect(
                self.position[0] + UI.Indicators.SIZE + UI.Indicators.SPACING,
                self.position[1] + UI.Indicators.VERTICAL_OFFSET,
                UI.Indicators.SIZE,
                UI.Indicators.SIZE
            )
            pygame.draw.rect(surface, COLOR_GLOW_YELLOW, self.colony_indicator_rect)
        else:
            self.colony_indicator_rect = None

    def handle_click(self, mouse_pos):
        """Handle clicks on colony indicators"""
        if self.ant_indicator_rect and self.ant_indicator_rect.collidepoint(mouse_pos):
            return 'spawn_ant'
        elif self.colony_indicator_rect and self.colony_indicator_rect.collidepoint(mouse_pos):
            return 'new_colony'
        return None

class Ant:
    def __init__(self, position, game):
        self.position = position
        self.sprite = pygame.Surface((ANT_SIZE, ANT_SIZE))
        self.resources = {'minerals': 0, 'plants': 0}
        self.carry_capacity = 10
        self.speed = 1.0  # Slower speed for better control
        self.perception_radius = PERCEPTION_RADIUS
        self.jump_height = 0
        self.jump_count = 0
        self.is_jumping = False
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]
        self.window_width = 480  # Game window width
        self.window_height = 800  # Game window height
        self.edge_buffer = 20  # Distance from edge to trigger turn around
        self.home_colony = None  # Reference to the colony this ant belongs to
        self.state = 'exploring'  # States: 'exploring', 'collecting', 'returning'
        self.target_resource = None
        self.scuttle_offset = 0  # For scuttling animation
        self.game = game  # Store game reference
        self.web_slow_timer = 0  # Timer for web slowdown effect

    def draw(self, surface):
        try:
            # Calculate position with jump offset and scuttle animation
            draw_y = self.position[1] - self.jump_height + math.sin(self.scuttle_offset) * 2
            
            # Update scuttle animation
            self.scuttle_offset += 0.2
            
            # Draw resource-specific effects
            if self.resources['minerals'] > 0 or self.resources['plants'] > 0:
                # Calculate pulsing intensity for particles
                pulse = (RESOURCE_EFFECTS['PULSE_MIN'] + 
                        (RESOURCE_EFFECTS['PULSE_MAX'] - RESOURCE_EFFECTS['PULSE_MIN']) * 
                        (math.sin(pygame.time.get_ticks() * RESOURCE_EFFECTS['PULSE_SPEED']) * 0.5 + 0.5))
                
                if self.resources['minerals'] > 0:
                    # Draw mineral sparkles
                    if random.random() < RESOURCE_EFFECTS['PARTICLE_CHANCE']['MINERAL']:
                        sparkle_color = VISUALS['ENTITIES']['ANT']['CARRYING']['MINERAL']['SPARKLE']
                        for _ in range(RESOURCE_EFFECTS['PARTICLES_PER_SPAWN']):
                            particle_pos = (
                                self.position[0] + random.randint(-ANT_SIZE, ANT_SIZE),
                                draw_y + random.randint(-ANT_SIZE, ANT_SIZE)
                            )
                            pygame.draw.circle(surface, sparkle_color, 
                                            particle_pos, RESOURCE_EFFECTS['PARTICLE_SIZE']['MINERAL'])
                else:  # Plants
                    # Draw plant particles
                    if random.random() < RESOURCE_EFFECTS['PARTICLE_CHANCE']['PLANT']:
                        particle_color = VISUALS['ENTITIES']['ANT']['CARRYING']['PLANT']['PARTICLE']
                        for _ in range(RESOURCE_EFFECTS['PARTICLES_PER_SPAWN']):
                            particle_pos = (
                                self.position[0] + random.randint(-ANT_SIZE, ANT_SIZE),
                                draw_y + random.randint(-ANT_SIZE, ANT_SIZE)
                            )
                            min_size, max_size = RESOURCE_EFFECTS['PARTICLE_SIZE']['PLANT']
                            particle_size = random.randint(min_size, max_size)
                            pygame.draw.circle(surface, particle_color, particle_pos, particle_size)
            
            # Draw the ant
            ant_rect = pygame.Rect(
                self.position[0] - ANT_SIZE // 2,
                draw_y - ANT_SIZE // 2,
                ANT_SIZE,
                ANT_SIZE
            )
            pygame.draw.rect(surface, COLORS['ANT'], ant_rect)
            
        except Exception as e:
            print(f"Error in ant draw method: {e}")
            # Fallback to basic ant drawing
            pygame.draw.rect(surface, COLORS['ANT'], 
                           (self.position[0] - ANT_SIZE//2, 
                            self.position[1] - ANT_SIZE//2,
                            ANT_SIZE, ANT_SIZE))

    def update(self, cursor_pos, snake_pos, obstacles, resources, colonies):
        # Update web effect
        if self.web_slow_timer > 0:
            self.web_slow_timer -= self.game.clock.get_time()
            # Ant moves at half speed while in web and jumps
            current_speed = self.speed * 0.5
            if not self.is_jumping:
                self.start_jump()
        else:
            current_speed = self.speed
            
        # Handle threats first
        threat_detected = False
        
        if self.perceive_threat(cursor_pos):
            self.flee()
            self.start_jump()
            threat_detected = True
        
        if self.perceive_threat(snake_pos):
            self.flee()
            self.start_jump()
            threat_detected = True

        # Update jump animation
        self.update_jump()

        # Move ant and handle boundaries
        self.move(obstacles, current_speed)

        # Only continue with resource collection if no threats were detected
        if not threat_detected:
            # Update based on current state
            if self.state == 'exploring':
                self.explore(resources)
            elif self.state == 'collecting':
                self.collect_resources()
            elif self.state == 'returning':
                self.return_to_colony(colonies)

    def perceive_threat(self, threat_pos):
        """Check if a threat is within perception radius"""
        return math.hypot(self.position[0] - threat_pos[0],
                         self.position[1] - threat_pos[1]) < self.perception_radius

    def flee(self):
        """Choose a random direction when fleeing from threats"""
        # Generate random angle between 0 and 2π
        flee_angle = random.uniform(0, 2 * math.pi)
        
        # Convert angle to direction vector
        self.direction = [
            math.cos(flee_angle),
            math.sin(flee_angle)
        ]
        
        # Normalize direction vector
        total = math.sqrt(self.direction[0]**2 + self.direction[1]**2)
        if total != 0:
            self.direction = [
                self.direction[0]/total,
                self.direction[1]/total
            ]

    def start_jump(self):
        """Start a jump animation"""
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_count = 0

    def update_jump(self):
        """Update jump animation"""
        if self.is_jumping:
            if self.jump_count < 2:  # Two jumps as per documentation
                self.jump_height = 5 * math.sin(self.jump_count * math.pi)
                self.jump_count += 0.1
            else:
                self.is_jumping = False
                self.jump_height = 0

    def check_boundaries(self):
        """Check if ant is near window boundaries and respond accordingly"""
        near_edge = False
        # Check horizontal boundaries
        if self.position[0] <= self.edge_buffer:  # Near left edge
            self.direction[0] = abs(self.direction[0])  # Force movement right
            near_edge = True
        elif self.position[0] >= self.window_width - self.edge_buffer:  # Near right edge
            self.direction[0] = -abs(self.direction[0])  # Force movement left
            near_edge = True

        # Check vertical boundaries
        if self.position[1] <= self.edge_buffer:  # Near top edge
            self.direction[1] = abs(self.direction[1])  # Force movement down
            near_edge = True
        elif self.position[1] >= self.window_height - self.edge_buffer:  # Near bottom edge
            self.direction[1] = -abs(self.direction[1])  # Force movement up
            near_edge = True

        if near_edge:
            self.start_jump()  # Start the double jump animation
            logging.debug(f"Ant hit boundary at {self.position}, new direction: {self.direction}")

    def move(self, obstacles, speed):
        """Move the ant while staying in bounds"""
        # Check boundaries before moving
        self.check_boundaries()

        # Calculate new position
        new_pos = (
            self.position[0] + self.direction[0] * speed,
            self.position[1] + self.direction[1] * speed
        )

        # Ensure the new position stays within bounds
        new_pos = (
            max(0, min(new_pos[0], self.window_width)),
            max(0, min(new_pos[1], self.window_height))
        )

        self.position = new_pos

    def explore(self, resources):
        """Look for resources while exploring"""
        if self.resources['minerals'] >= self.carry_capacity or self.resources['plants'] >= self.carry_capacity:
            self.state = 'returning'
            return

        # Check for nearby resources (including bushes)
        for resource in resources:
            distance = math.hypot(self.position[0] - resource.position[0],
                                self.position[1] - resource.position[1])
            
            if distance < self.perception_radius:
                self.target_resource = resource
                self.state = 'collecting'
                self.start_jump()
                # Move towards resource
                dx = resource.position[0] - self.position[0]
                dy = resource.position[1] - self.position[1]
                total = abs(dx) + abs(dy)
                if total != 0:
                    self.direction = [dx/total, dy/total]
                break

    def collect_resources(self):
        """Collect resources when near them"""
        if not self.target_resource:
            self.state = 'exploring'
            return

        # Check if target resource still exists (hasn't been depleted)
        if ((isinstance(self.target_resource, Rock) and self.target_resource.minerals <= 0) or
            (isinstance(self.target_resource, (Plant, Bush)) and self.target_resource.resources <= 0)):
            self.target_resource = None
            self.state = 'exploring'
            return

        distance = math.hypot(self.position[0] - self.target_resource.position[0],
                            self.position[1] - self.target_resource.position[1])

        if distance < ANT_SIZE + self.target_resource.size:
            # Collect minerals from rocks
            if isinstance(self.target_resource, Rock) and self.target_resource.minerals > 0:
                collect_amount = min(
                    self.carry_capacity - self.resources['minerals'],
                    self.target_resource.minerals
                )
                self.resources['minerals'] += collect_amount
                self.target_resource.minerals -= collect_amount
                logging.debug(f"Ant collected {collect_amount} minerals")
                self.game.sounds.play_mineral_collect()
                self.game.hud.trigger_icon_animation('mineral')

            # Collect from plants or bushes
            elif isinstance(self.target_resource, (Plant, Bush)) and self.target_resource.resources > 0:
                collect_amount = min(
                    self.carry_capacity - self.resources['plants'],
                    self.target_resource.resources
                )
                self.resources['plants'] += collect_amount
                self.target_resource.resources -= collect_amount
                logging.debug(f"Ant collected {collect_amount} plant resources")
                self.game.sounds.play_plant_collect()
                self.game.hud.trigger_icon_animation('plant')

            self.start_jump()  # Jump after collecting
            
            # Always move to returning state after collecting
            if self.resources['minerals'] > 0 or self.resources['plants'] > 0:
                self.state = 'returning'
                self.target_resource = None
            else:
                self.state = 'exploring'
                self.target_resource = None

    def return_to_colony(self, colonies):
        """Return to nearest colony when carrying resources"""
        if not colonies:
            return

        # Find nearest colony
        nearest_colony = min(colonies, 
                           key=lambda c: math.hypot(self.position[0] - c.position[0],
                                                  self.position[1] - c.position[1]))
        
        distance = math.hypot(self.position[0] - nearest_colony.position[0],
                            self.position[1] - nearest_colony.position[1])

        # Move towards colony
        if distance > ANT_SIZE + COLONY_MIN_SIZE:
            dx = nearest_colony.position[0] - self.position[0]
            dy = nearest_colony.position[1] - self.position[1]
            total = abs(dx) + abs(dy)
            if total != 0:
                self.direction = [dx/total, dy/total]
        else:
            # Deposit resources
            nearest_colony.resources['minerals'] += self.resources['minerals']
            nearest_colony.resources['plants'] += self.resources['plants']
            self.resources = {'minerals': 0, 'plants': 0}
            self.state = 'exploring'
            self.start_jump()  # Jump after depositing resources
            self.game.sounds.play_resource_deposit()

class Snake:
    def __init__(self, position, game):
        self.position = position
        self.body = [position]  # Head is at index 0
        self.size = 4
        self.length = 15  # Initial length
        self.speed = 1  # Reduced from 2 to 1 for slower movement
        self.perception_radius = 10  # Reduced perception radius
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]
        self.wave_offset = 0  # For wave animation
        self.game = game
        self.is_sleeping = False
        self.sleep_center = position  # Initialize sleep_center
        self.sleep_coil = []
        self.sleep_zs = []  # List to track sleeping Z particles
        self.z_spawn_timer = 0
        self.z_spawn_interval = 1000  # Spawn new Z every second

    def update(self, mouse_pos, ants, colonies):
        # Don't update position or chase ants if sleeping
        if self.is_sleeping:
            return False
        
        # Move towards nearest ant within perception radius (from head position)
        nearest_ant = None
        nearest_distance = float('inf')
        
        # Only check for ants near the snake's head
        for ant in ants:
            distance = math.hypot(self.position[0] - ant.position[0],
                                self.position[1] - ant.position[1])
            if distance < self.perception_radius and distance < nearest_distance:
                # Check if ant is not in a colony
                in_colony = False
                for colony in colonies:
                    colony_distance = math.hypot(ant.position[0] - colony.position[0],
                                              ant.position[1] - colony.position[1])
                    if colony_distance < COLONY_MIN_SIZE:
                        in_colony = True
                        break
                
                if not in_colony:
                    nearest_ant = ant
                    nearest_distance = distance

        # Update direction based on nearest ant or random movement
        if nearest_ant:
            # Move towards ant
            dx = nearest_ant.position[0] - self.position[0]
            dy = nearest_ant.position[1] - self.position[1]
            total = abs(dx) + abs(dy)
            if total != 0:
                self.direction = [dx/total, dy/total]

            # Check if snake caught the ant
            if nearest_distance < self.size:
                if nearest_ant.home_colony:
                    nearest_ant.home_colony.ant_count -= 1
                ants.remove(nearest_ant)
                self.length += 1
                logging.debug(f"Snake ate ant! Total eaten: {self.length - 15}")
                self.game.sounds.play_snake_eat()
                return True  # Return True when kill happens
        else:
            # Random movement if no ants nearby
            if random.random() < 0.02:  # 2% chance to change direction
                self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]

        # Update position
        new_x = self.position[0] + self.direction[0] * self.speed
        new_y = self.position[1] + self.direction[1] * self.speed
        
        # Keep snake in bounds
        new_x = max(0, min(new_x, 480))
        new_y = max(0, min(new_y, 800))
        
        # Update body positions
        self.body.insert(0, (new_x, new_y))
        if len(self.body) > self.length:
            self.body.pop()
        
        self.position = (new_x, new_y)
        self.wave_offset += 0.2  # Update wave animation

    def draw(self, surface, alpha=255):
        if self.is_sleeping:
            # Draw coiled sleeping snake first
            for i, pos in enumerate(self.sleep_coil):
                segment_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.rect(segment_surface, VISUALS['ENTITIES']['SNAKE']['SLEEP'], 
                               (0, 0, self.size, self.size))
                surface.blit(segment_surface, 
                           (pos[0] - self.size // 2,
                            pos[1] - self.size // 2))
            
            # Update and draw sleeping Zs
            current_time = pygame.time.get_ticks()
            
            # Spawn new Z more frequently
            if current_time - self.z_spawn_timer > 500:  # Every 0.5 seconds
                self.z_spawn_timer = current_time
                # Use stored sleep center position
                spawn_x = self.position[0] + random.uniform(-5, 5)  # Small random offset
                spawn_y = self.position[1]  # Start from center of coil
                
                self.sleep_zs.append({
                    'pos': (spawn_x, spawn_y),
                    'size': 14,
                    'alpha': 255,
                    'offset': random.uniform(-0.5, 0.5),
                    'birth_time': current_time
                })
            
            # Update and draw each Z
            new_zs = []
            for z in self.sleep_zs:
                age = current_time - z['birth_time']
                if age < 800:  # Live for 0.8 seconds
                    # Gentler upward movement
                    x = z['pos'][0] + math.sin((age * 0.008) + z['offset']) * 2
                    y = z['pos'][1] - age * 0.015  # Slower upward movement
                    
                    # Calculate size and alpha
                    size = 14 + math.sin(age * 0.01) * 2  # Slight size variation
                    alpha = max(0, 255 - (age / 800) * 255)  # Fade out
                    
                    # Draw Z with shadow
                    z_font = pygame.font.Font(None, int(size))
                    shadow_surface = z_font.render("Z", True, (0, 0, 0))
                    shadow_surface.set_alpha(alpha * 0.5)
                    surface.blit(shadow_surface, (x - shadow_surface.get_width()//2 + 1, y + 1))
                    
                    z_surface = z_font.render("Z", True, VISUALS['ENTITIES']['SNAKE']['SLEEP_Z']['COLOR'])
                    z_surface.set_alpha(alpha)
                    surface.blit(z_surface, (x - z_surface.get_width()//2, y))
                    
                    z['pos'] = (x, y)
                    z['alpha'] = alpha
                    new_zs.append(z)
            
            self.sleep_zs = new_zs
        else:
            # Draw normal moving snake
            for i, pos in enumerate(self.body):
                wave_y = math.sin(self.wave_offset + i * 0.3) * 3
                segment_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.rect(segment_surface, COLORS['SNAKE'], 
                               (0, 0, self.size, self.size))
                surface.blit(segment_surface, 
                           (pos[0] - self.size // 2,
                            pos[1] - self.size // 2 + wave_y))

    def start_sleeping(self):
        """Coil the snake into sleeping position"""
        self.is_sleeping = True
        self.sleep_center = self.position  # Store the center position for sleeping
        segments = len(self.body)
        coil_radius = self.size * 3
        
        # Update all body positions to the coiled position
        self.sleep_coil = []
        for i in range(segments):
            angle = i * 0.5  # Controls how tight the coil is
            radius = coil_radius - (i * self.size / 4)  # Spiral inward
            x = self.sleep_center[0] + math.cos(angle) * radius
            y = self.sleep_center[1] + math.sin(angle) * radius
            self.sleep_coil.append((x, y))
        
        # Update body positions to match coiled state
        self.body = self.sleep_coil.copy()
        self.position = self.sleep_center  # Update head position

    def wake_up(self):
        """Return to normal state"""
        self.is_sleeping = False
        # Keep the last position when waking up
        last_pos = self.position
        self.body = [last_pos for _ in range(self.length)]  # Reset body to straight
        self.sleep_coil = []
        self.sleep_zs = []
        self.z_spawn_timer = 0

class Spider:
    def __init__(self, position, game):
        self.position = position
        self.game = game
        self.size = 18  # Slightly bigger than ant
        self.speed = 0.04  # Even slower (was 0.08)
        self.state = 'wandering'
        self.home_plant = None
        self.death_animation_timer = 0
        self.death_blinks = 0
        self.web_cooldown = 2000  # Longer cooldown between webs (was 1000)
        self.web_chance = 0.005  # Much lower chance (was 0.02)
        self.leg_animation_offset = 0
        self.flee_timer = 0
        self.flee_direction = [0, 0]
        self.daylight_death_timer = 0
        self.edge_buffer = 20  # Buffer from screen edges
        
        # Spider pixel art pattern
        self.spider_pattern = [
            "  XXXX  ",
            " XXXXXX ",
            "XXXXXXXX",
            "XXX  XXX",
            " X XX X ",
            "X X  X X"
        ]
        
        # Colors for spider
        self.colors = {
            'body': (40, 40, 40),      # Dark grey
            'legs': (20, 20, 20),      # Almost black
            'eyes': (255, 0, 0),       # Bright red (glowing effect)
            'death': (80, 0, 0)        # Blood red for death animation
        }
        
    def update(self, dt, plants, bushes, colonies, ants):
        if self.state == 'dying':
            self._update_death_animation(dt)
            return
            
        if self.state == 'fleeing':
            self._update_fleeing(dt)
            return
            
        # Check for daylight death
        current_time = pygame.time.get_ticks()
        cycle_time = (current_time - self.game.cycle_start_time) % DAY_NIGHT['CYCLE_DURATION']
        is_day = cycle_time < DAY_NIGHT['CYCLE_DURATION'] / 2
        
        if is_day and self.state != 'sleeping':
            if not self._find_shelter(plants, bushes):
                self.state = 'dying'
                self.daylight_death_timer = 2000  # 2 seconds to die
                self.speed *= 2  # Double speed for final run
                self.flee_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
                return
                
        # Update web placement
        if self.web_cooldown > 0:
            self.web_cooldown -= dt
        elif random.random() < self.web_chance:
            self.game.webs.append(SpiderWeb(self.position, self.game))
            self.web_cooldown = 1000
            self.game.sounds.play_spider_web()
            
        # Update movement
        if self.state == 'wandering':
            self._update_wandering(dt, colonies)
            
        # Update leg animation
        self.leg_animation_offset += dt * 0.01
        
    def _update_wandering(self, dt, colonies):
        # Check for nearby colonies
        for colony in colonies:
            dx = colony.position[0] - self.position[0]
            dy = colony.position[1] - self.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < COLONY_MAX_SIZE * 2:
                # Count nearby ants
                nearby_ants = sum(1 for ant in self.game.ants 
                                if math.hypot(ant.position[0] - self.position[0],
                                            ant.position[1] - self.position[1]) < 50)
                
                if nearby_ants >= 3:  # At least 3 ants needed to challenge spider
                    if random.random() < 0.7:  # 70% chance to flee
                        self.state = 'fleeing'
                        self.flee_timer = 3000  # 3 seconds of fleeing
                        # Flee direction away from colony
                        self.flee_direction = [-dx/distance, -dy/distance]
                        # Place more webs while fleeing
                        self.web_chance = 0.1
                    else:
                        self.state = 'dying'
                        self.game.sounds.play_spider_death()
                    return
                    
        # Random movement
        if random.random() < 0.02:
            angle = random.uniform(0, 2 * math.pi)
            self.flee_direction = [math.cos(angle), math.sin(angle)]
            
        # Update position with boundary checking
        new_x = self.position[0] + self.flee_direction[0] * self.speed * dt
        new_y = self.position[1] + self.flee_direction[1] * self.speed * dt
        
        # Keep in bounds with edge buffer
        if new_x < self.edge_buffer:
            new_x = self.edge_buffer
            self.flee_direction[0] *= -1  # Reverse x direction
        elif new_x > WINDOW_WIDTH - self.edge_buffer:
            new_x = WINDOW_WIDTH - self.edge_buffer
            self.flee_direction[0] *= -1  # Reverse x direction
            
        if new_y < self.edge_buffer:
            new_y = self.edge_buffer
            self.flee_direction[1] *= -1  # Reverse y direction
        elif new_y > WINDOW_HEIGHT - self.edge_buffer:
            new_y = WINDOW_HEIGHT - self.edge_buffer
            self.flee_direction[1] *= -1  # Reverse y direction
        
        self.position = (new_x, new_y)
        
    def _update_fleeing(self, dt):
        self.flee_timer -= dt
        if self.flee_timer <= 0:
            self.state = 'wandering'
            self.web_chance = 0.02
            return
            
        # Place more webs while fleeing, but not too many
        if random.random() < 0.05:  # Reduced from 0.2
            self.game.webs.append(SpiderWeb(self.position, self.game))
            self.web_cooldown = 1500  # Added cooldown for fleeing webs
            self.game.sounds.play_spider_web()
            
        # Update position with boundary checking
        new_x = self.position[0] + self.flee_direction[0] * self.speed * dt
        new_y = self.position[1] + self.flee_direction[1] * self.speed * dt
        
        # Keep in bounds with edge buffer
        if new_x < self.edge_buffer:
            new_x = self.edge_buffer
            self.flee_direction[0] *= -1
        elif new_x > WINDOW_WIDTH - self.edge_buffer:
            new_x = WINDOW_WIDTH - self.edge_buffer
            self.flee_direction[0] *= -1
            
        if new_y < self.edge_buffer:
            new_y = self.edge_buffer
            self.flee_direction[1] *= -1
        elif new_y > WINDOW_HEIGHT - self.edge_buffer:
            new_y = WINDOW_HEIGHT - self.edge_buffer
            self.flee_direction[1] *= -1
        
        self.position = (new_x, new_y)
        
    def _update_death_animation(self, dt):
        if self.daylight_death_timer > 0:
            self.daylight_death_timer -= dt
            # Move in flee direction
            new_x = self.position[0] + self.flee_direction[0] * self.speed * dt
            new_y = self.position[1] + self.flee_direction[1] * self.speed * dt
            self.position = (new_x, new_y)
            return
            
        self.death_animation_timer += dt
        if self.death_animation_timer >= 500:  # Blink every 0.5 seconds
            self.death_animation_timer = 0
            self.death_blinks += 1
            if self.death_blinks >= 3:
                self.game.spider = None  # Remove spider from game
                
    def _find_shelter(self, plants, bushes):
        """Find nearest plant or bush to hide in"""
        shelter_spots = plants + bushes
        if not shelter_spots:
            return False
            
        # Find nearest shelter
        nearest = min(shelter_spots, 
                     key=lambda x: math.hypot(x.position[0] - self.position[0],
                                            x.position[1] - self.position[1]))
        
        # Clear previous shelter if exists
        if self.home_plant and hasattr(self.home_plant, 'has_spider'):
            self.home_plant.has_spider = False
            
        self.home_plant = nearest
        if hasattr(nearest, 'has_spider'):
            nearest.has_spider = True  # Mark the shelter as occupied
        self.state = 'sleeping'
        return True
        
    def draw(self, surface):
        if self.state == 'sleeping':
            return

        pixel_size = 2
        flip_y = 1
        
        if self.state == 'dying':
            # Flip upside down when dying
            flip_y = -1
            
        # Draw spider body
        for row_idx, row in enumerate(self.spider_pattern):
            for col_idx, pixel in enumerate(row):
                if pixel == 'X':
                    x = self.position[0] + (col_idx - len(row)/2) * pixel_size
                    y = self.position[1] + (row_idx * flip_y - len(self.spider_pattern)/2) * pixel_size
                    
                    color = self.colors['body']
                    if self.state == 'dying':
                        if self.death_blinks % 2 == 0:
                            color = self.colors['death']
                    
                    pygame.draw.rect(surface, color, (x, y, pixel_size, pixel_size))
                    
        # Draw glowing red eyes
        if self.state != 'dying' or self.death_blinks % 2 == 0:
            eye_positions = [(2, 3), (5, 3)]  # Eye positions in pattern
            for ex, ey in eye_positions:
                x = self.position[0] + (ex - len(row)/2) * pixel_size
                y = self.position[1] + (ey * flip_y - len(self.spider_pattern)/2) * pixel_size
                pygame.draw.rect(surface, self.colors['eyes'], (x, y, pixel_size, pixel_size))

class SpiderWeb:
    def __init__(self, position, game):
        self.position = position
        self.game = game
        self.size = 16
        self.affected_ants = set()
        self.destroyed = False
        self.ant_jump_timer = {}
        self.wave_offset = random.random() * 6.28  # Random starting phase
        self.wave_speed = 0.001  # Slightly slower for more gentle movement
        self.wave_amplitude = 1.2  # Control the amount of movement
        
        # Web pattern (9x15 pixels)
        self.web_pattern = [
            "  X  X X X  X ",
            "   X   X   X  ",
            "  X X  X  X X ",
            " X   X X X   X",
            "X X X X X X X X",
            " X   X X X   X",
            "  X X  X  X X ",
            "   X   X   X  ",
            "  X  X X X  X "
        ]
        
        self.colors = {
            'primary': (200, 200, 200, 180),
            'secondary': (150, 150, 150, 140)
        }
        
    def affects_ant(self, ant):
        """Check if ant is caught in web and handle effects"""
        if ant in self.affected_ants:
            # Update jump timer for this ant
            self.ant_jump_timer[ant] += self.game.clock.get_time()
            
            # Make ant jump while in web
            ant.start_jump()
            
            # After 5 seconds, destroy web and free ant
            if self.ant_jump_timer[ant] >= 5000:  # 5 seconds
                self.destroyed = True
                self.affected_ants.remove(ant)
                ant.web_slow_timer = 0
            return True
            
        distance = math.hypot(self.position[0] - ant.position[0],
                            self.position[1] - ant.position[1])
                            
        if distance < self.size/2:
            self.affected_ants.add(ant)
            self.ant_jump_timer[ant] = 0  # Start timer for this ant
            ant.web_slow_timer = 5000  # 5 seconds of slowdown
            return True
        return False
        
    def draw(self, surface):
        current_time = pygame.time.get_ticks()
        pixel_size = 2
        
        # Calculate wave offsets with more natural movement
        wave_x = math.sin(current_time * self.wave_speed + self.wave_offset) * self.wave_amplitude
        wave_y = math.cos(current_time * self.wave_speed * 0.7 + self.wave_offset) * self.wave_amplitude
        
        for row_idx, row in enumerate(self.web_pattern):
            for col_idx, pixel in enumerate(row):
                if pixel == 'X':
                    # Calculate distance from center for wave intensity
                    center_x = len(row) / 2
                    center_y = len(self.web_pattern) / 2
                    dist_from_center = math.sqrt((col_idx - center_x)**2 + (row_idx - center_y)**2)
                    wave_intensity = max(0.3, 1 - (dist_from_center / max(center_x, center_y)))
                    
                    # Add slight phase shift based on position for more organic movement
                    phase_shift = (col_idx + row_idx) * 0.1
                    
                    # Apply wave effect with phase shift
                    offset_x = wave_x * wave_intensity * (1 + dist_from_center/5) * math.sin(phase_shift)
                    offset_y = wave_y * wave_intensity * (1 + dist_from_center/5) * math.cos(phase_shift)
                    
                    x = self.position[0] + (col_idx - len(row)/2) * pixel_size + offset_x
                    y = self.position[1] + (row_idx - len(self.web_pattern)/2) * pixel_size + offset_y
                    
                    # Add slight alpha variation for shimmer effect
                    alpha_shift = int(20 * math.sin(current_time * 0.001 + phase_shift))
                    color = list(self.colors['primary' if (row_idx + col_idx) % 2 == 0 else 'secondary'])
                    color[3] = max(100, min(255, color[3] + alpha_shift))
                    
                    pygame.draw.rect(surface, tuple(color), (x, y, pixel_size, pixel_size))

