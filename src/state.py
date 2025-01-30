import pygame
import math
from constants import Economy

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
    
    # ... (rest of GameState implementation) 