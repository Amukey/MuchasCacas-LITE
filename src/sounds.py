"""
Sound and Music Generation System for Muchas Cacas! LITE

This module handles all audio generation and playback, including:
- Procedural sound effects generation
- Dynamic background music system
- Ambient music generation with mood transitions
- Volume control and audio mixing

The system uses pygame's audio mixer and numpy for sound synthesis.

Key Components:
- GameSounds: Main sound manager handling all audio playback
- MusicGenerator: Procedural music generation with dynamic moods
- Sound synthesis utilities for creating game sound effects

Requirements:
- pygame
- numpy
- math
- random

Author: Guillermo
License: MIT
"""

import pygame
import numpy as np
import pygame.sndarray
import random
import signal
import math
from constants import *
from state import GameState

# Initialize pygame mixer
pygame.mixer.init(44100, -16, 2, 512)

def create_synth_sound(frequency, duration, volume=0.5, waveform='sine'):
    """Create a synthesized sound with the given parameters"""
    sample_rate = 44100
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, False)
    
    if waveform == 'sine':
        wave = np.sin(2 * np.pi * frequency * t)
    elif waveform == 'square':
        wave = np.sign(np.sin(2 * np.pi * frequency * t))
    elif waveform == 'sawtooth':
        wave = 2 * (frequency * t - np.floor(0.5 + frequency * t))
    
    # Apply volume
    wave *= volume
    
    # Apply fade out (fixed the fade calculation)
    fade_samples = int(0.1 * sample_rate)
    if fade_samples > 0:
        fade = np.linspace(1.0, 0.0, min(fade_samples, len(wave)))
        wave[-len(fade):] *= fade
    
    # Convert to 16-bit integers
    wave = np.int16(wave * 32767)
    
    # Make stereo by duplicating the wave
    stereo = np.column_stack([wave, wave])
    
    return pygame.sndarray.make_sound(stereo)

# Create game sounds
class GameSounds:
    """
    Main sound manager for the game.
    
    Handles:
    - Sound effect playback
    - Background music generation and playback
    - Volume control for music and sound effects
    - Audio mixing and crossfading
    - Dynamic music transitions based on game state
    
    Usage:
        sounds = GameSounds()
        sounds.play_startup()  # Play startup sound
        sounds.start_background_music()  # Start dynamic music
        sounds.set_volumes(0.5, 0.5)  # Set sound/music volumes
    """
    def __init__(self):
        try:
            pygame.mixer.quit()
            pygame.mixer.init(44100, -16, 2, 1024)
            
            # Much quieter sound effects
            self.ant_spawn = create_synth_sound(880, 0.1, 0.15, 'sine')  # Halved volume
            
            # Resource collection sounds (very subtle)
            self.mineral_collect = create_synth_sound(440, 0.05, 0.1, 'square')
            self.plant_collect = create_synth_sound(550, 0.05, 0.1, 'sine')
            
            # Colony creation (gentler chord)
            base_freq = 220
            chord_duration = 0.5
            chord_samples = int(44100 * chord_duration)
            chord = np.zeros(chord_samples)
            
            for freq_mult in [1, 1.25, 1.5]:  # Major chord
                t = np.linspace(0, chord_duration, chord_samples, False)
                chord += np.sin(2 * np.pi * base_freq * freq_mult * t) * 0.1  # Reduced volume
            
            # Normalize and convert chord
            chord = np.int16(chord * 32767 / np.max(np.abs(chord)))
            self.colony_create = pygame.sndarray.make_sound(np.column_stack([chord, chord]))
            self.colony_create.set_volume(0.15)  # Set initial volume lower
            
            # Snake eating ant (softer thump)
            self.snake_eat = create_synth_sound(110, 0.2, 0.2, 'square')
            
            # Resource deposit sound (gentler chime)
            self.resource_deposit = create_synth_sound(660, 0.15, 0.15, 'sine')
            
            # Error sound (softer)
            self.error = create_synth_sound(220, 0.2, 0.15, 'sawtooth')
            
            # Startup sound (adjusted volume)
            self.startup_sound = self.create_gameboy_sound()
            self.startup_sound.set_volume(0.2)
            
            # Spider sounds (soft and creepy)
            self.spider_death = create_synth_sound(220, 0.3, 0.15, 'sawtooth')
            self.spider_web = create_synth_sound(440, 0.1, 0.1, 'sine')
            
            # Initialize volume controls
            self.sound_volume = 0.5  # Default sound effect volume
            self.music_volume = 0.5  # Default music volume
            
            # Better buffering settings for slower music
            self.music_generator = MusicGenerator()
            self.audio_queue = []
            self.queue_length = QUEUE_LENGTH
            self.segment_duration = SEGMENT_DURATION
            self.is_playing = False
            self.last_queue_time = 0
            self.crossfade_duration = CROSSFADE_DURATION
            
        except Exception as e:
            print(f"Error initializing sounds: {e}")
            self.music_generator = None
            self.audio_queue = []

    def create_gameboy_sound(self):
        """Create a GameBoy-style startup sound"""
        sample_rate = 44100
        duration = 1.2  # Slightly longer duration
        
        # Create time array
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Generate the characteristic "ping" frequencies (adjusted for more GameBoy-like sound)
        f1, f2, f3, f4 = 350, 700, 1400, 2100  # Higher frequencies for clearer sound
        
        # Create the four tones with timing offsets
        tone1 = np.sin(2 * np.pi * f1 * t) * np.exp(-2 * t)
        tone2 = np.sin(2 * np.pi * f2 * t) * np.exp(-2 * (t - 0.1)) * (t > 0.1)
        tone3 = np.sin(2 * np.pi * f3 * t) * np.exp(-2 * (t - 0.2)) * (t > 0.2)
        tone4 = np.sin(2 * np.pi * f4 * t) * np.exp(-2 * (t - 0.3)) * (t > 0.3)
        
        # Add slight pitch bend for more character
        bend = np.linspace(1.0, 1.02, len(t))
        tone4 *= bend
        
        # Combine tones with adjusted volumes
        audio_data = (
            tone1 * 0.4 + 
            tone2 * 0.35 + 
            tone3 * 0.3 + 
            tone4 * 0.25
        )
        
        # Add slight reverb effect
        reverb = np.zeros_like(audio_data)
        delay_samples = int(0.05 * sample_rate)
        reverb[delay_samples:] = audio_data[:-delay_samples] * 0.3
        audio_data += reverb
        
        # Normalize and convert to 16-bit integers
        audio_data = audio_data / np.max(np.abs(audio_data))
        audio_data = (audio_data * 32767 * 0.9).astype(np.int16)  # Increased volume to 90%
        
        # Create stereo audio
        stereo_data = np.column_stack([audio_data, audio_data])
        
        # Create pygame Sound object
        sound = pygame.sndarray.make_sound(stereo_data)
        return sound

    def update_music(self, game_state):
        """Update music based on game state with enhanced dynamics"""
        try:
            if not self.music_generator or not self.is_playing:
                return
            
            # Validate music generator state
            self.music_generator.validate_state()
            
            # Update music generator with game state
            self.music_generator.update_game_state(game_state)
            
            # Update audio queue
            current_time = pygame.time.get_ticks()
            samples_per_segment = int(self.segment_duration * 44100)
            crossfade_samples = int(self.crossfade_duration * 44100)
            
            # Dynamic queue length based on intensity and danger
            target_queue_length = max(
                MUSIC_STATE['MIN_QUEUE_LENGTH'],
                min(MUSIC_STATE['MAX_QUEUE_LENGTH'],
                    int(12 * (game_state.intensity + game_state.danger_level) / 2)
                )
            )
            
            while len(self.audio_queue) < target_queue_length:
                segment = self.music_generator.generate_segment(samples_per_segment + crossfade_samples)
                
                # Enhanced dynamic volume system
                base_volume = self.music_volume * (
                    0.8 +  # Base level
                    0.2 * game_state.resource_abundance * MUSIC_STATE['RESOURCE_VOLUME_FACTOR'] +  # Resource influence
                    0.3 * game_state.danger_level * MUSIC_STATE['DANGER_VOLUME_FACTOR'] +  # Danger boost
                    0.1 * game_state.intensity * MUSIC_STATE['INTENSITY_TEMPO_FACTOR']  # Activity boost
                )
                
                # Time of day influence
                if game_state.time_of_day == 'night':
                    base_volume *= 0.85  # Slightly quieter at night
                
                # Mood-based volume adjustments
                mood = game_state.current_mood.upper()
                if mood in MOODS:
                    base_volume *= (
                        MOODS[mood]['melody_prominence'] * 0.4 +
                        MOODS[mood]['bass_prominence'] * 0.4 +
                        0.2  # Minimum volume
                    )
                
                # Normalize and apply volume with smoother transitions
                max_val = np.max(np.abs(segment))
                if max_val > 0:
                    segment = segment * base_volume / max_val
                
                # Enhanced crossfade with mood-based timing
                fade_duration = crossfade_samples * (1.2 if mood == 'DREAMY' else 1.0)
                fade_in = (1 - np.cos(np.linspace(0, np.pi, int(fade_duration)))) / 2
                fade_out = (1 + np.cos(np.linspace(0, np.pi, int(fade_duration)))) / 2
                
                # Apply crossfade
                segment[:len(fade_in)] *= fade_in[:len(segment[:len(fade_in)])]
                segment[-len(fade_out):] *= fade_out[-len(segment[-len(fade_out):]):]
                
                # Convert to 16-bit integers with dithering for smoother sound
                dither = np.random.uniform(-0.5, 0.5, len(segment)) * 0.001
                audio_data = (segment * 32767 + dither).astype(np.int16)
                stereo_data = np.column_stack((audio_data, audio_data))
                
                sound = pygame.sndarray.make_sound(stereo_data)
                sound.set_volume(base_volume)
                self.audio_queue.append(sound)
            
            # Dynamic segment timing based on game state
            segment_duration = self.segment_duration * (
                1.1 - 0.2 * game_state.intensity +  # Speed up with intensity
                0.1 * game_state.danger_level       # Slight slowdown with danger
            )
            
            # Update playback timing
            if not pygame.mixer.get_busy():
                self.play_next_segment()
                self.last_queue_time = current_time
            elif current_time - self.last_queue_time >= (segment_duration * 1000 * 0.9):
                self.play_next_segment()
                self.last_queue_time = current_time
            
        except Exception as e:
            print(f"Error in update_music: {e}")
    
    def play_next_segment(self):
        """Play next segment with overlap"""
        try:
            if self.audio_queue:
                segment = self.audio_queue.pop(0)
                segment.play(fade_ms=50)  # Add small fade to smooth transition
                
        except Exception as e:
            print(f"Error playing segment: {e}")

    def set_volumes(self, sound_vol, music_vol):
        """Update volume levels"""
        self.sound_volume = sound_vol
        self.music_volume = music_vol
        
        # Update music volume for queued segments
        for segment in self.audio_queue:
            segment.set_volume(music_vol)
        
        # Update sound effects volumes
        self.ant_spawn.set_volume(sound_vol)
        self.mineral_collect.set_volume(sound_vol)
        self.plant_collect.set_volume(sound_vol)
        self.colony_create.set_volume(sound_vol)
        self.snake_eat.set_volume(sound_vol)
        self.resource_deposit.set_volume(sound_vol)
        self.error.set_volume(sound_vol)
        self.startup_sound.set_volume(sound_vol)
        self.spider_death.set_volume(sound_vol)
        self.spider_web.set_volume(sound_vol)
    
    def start_background_music(self):
        """Start background music with fade in"""
        try:
            self.is_playing = True
            self.music_volume = 0.0
            
            # Create initial game state for startup with error handling
            try:
                initial_state = GameState()
            except Exception as e:
                print(f"Error creating initial game state: {e}")
                initial_state = type('GameState', (), {
                    'intensity': 0.0,
                    'danger_level': 0.0,
                    'resource_abundance': 1.0,
                    'time_of_day': 'day'
                })
            
            # Begin playing
            self.update_music(initial_state)
            
            # Fade in over 2 seconds
            for vol in range(0, 11):
                self.music_volume = vol / 10.0
                pygame.time.wait(200)
                for segment in self.audio_queue:
                    segment.set_volume(self.music_volume)
                
        except Exception as e:
            print(f"Error starting background music: {e}")
    
    def stop_background_music(self):
        """Stop background music with fade out"""
        try:
            # Fade out over 2 seconds
            original_volume = self.music_volume
            for vol in range(10, -1, -1):
                self.music_volume = vol * original_volume / 10
                # Update volume of queued segments
                for segment in self.audio_queue:
                    segment.set_volume(self.music_volume)
                pygame.time.wait(200)
            
            # Stop playback
            self.is_playing = False
            pygame.mixer.stop()
            self.audio_queue.clear()
            
        except Exception as e:
            print(f"Error stopping background music: {e}")

    def play_ant_spawn(self):
        self.ant_spawn.play()
    
    def play_mineral_collect(self):
        self.mineral_collect.play()
    
    def play_plant_collect(self):
        self.plant_collect.play()
    
    def play_colony_create(self):
        self.colony_create.play()
    
    def play_snake_eat(self):
        self.snake_eat.play()
    
    def play_resource_deposit(self):
        self.resource_deposit.play()
    
    def play_error(self):
        self.error.play()

    def play_startup(self):
        """Play the startup sound"""
        self.startup_sound.play()

    def play_spider_death(self):
        """Play spider death sound"""
        try:
            self.spider_death.play()
        except:
            pass
            
    def play_spider_web(self):
        """Play web creation sound"""
        try:
            self.spider_web.play()
        except:
            pass

# Dummy sound class in case sound initialization fails
class DummySound:
    def play(self, loops=0):
        pass
    
    def stop(self):
        pass
    
    def set_volume(self, volume):
        pass
    
    def get_volume(self):
        return 0.0

class MusicGenerator:
    """
    Procedural music generator for ambient game soundtrack.
    
    Features:
    - Dynamic mood transitions
    - Day/night variations
    - Procedural melody generation
    - Chord progression system
    - Adaptive percussion patterns
    
    The generator creates ambient music that responds to:
    - Game intensity
    - Time of day
    - Current mood
    - Resource abundance
    - Danger levels
    
    Technical details:
    - Sample rate: 44100 Hz
    - Bit depth: 16-bit
    - Channels: Stereo
    - Buffer size: 1024 samples
    """
    def __init__(self):
        """Initialize the music generator"""
        self.is_night = False
        self.current_combination = 0
        self.sequence_position = 0
        self.transition_progress = 0.0
        self.is_transitioning = False
        self.current_beat_position = 0
        self.current_melody_position = 0
        self.current_bass_position = 0
        
        # Add progression sequence
        self.progression_sequence = [
            [0, 4, 5, 3],    # I - V - VI - IV progression
            [0, 5, 3, 4],    # I - VI - IV - V progression
            [3, 0, 4, 5],    # IV - I - V - VI progression
            [0, 3, 5, 4]     # I - IV - VI - V progression
        ]
        self.current_progression = 0
        self.progression_position = 0
        
        # Musical scales
        self.day_scale = [220.0, 247.5, 261.63, 293.66, 329.63, 349.23, 392.0]  # A3 major scale
        self.night_scale = [220.0, 261.63, 277.18, 329.63, 349.23]  # A3 minor pentatonic
        
        # Pattern combinations for different moods
        self.pattern_combinations = [
            {
                'name': 'peaceful',
                'patterns': ['floating', 'gentle', 'ambient']
            },
            {
                'name': 'dreamy',
                'patterns': ['dreamy', 'floating', 'ambient']
            }
        ]
        
        # Last played note for melodic continuity
        self.last_note = None

    def update_game_state(self, game_state):
        """Update generator state based on game state"""
        self.is_night = game_state.time_of_day == 'night'
        
        # Request mood transition if needed
        if game_state.current_mood != self.get_current_mood():
            self.request_transition(game_state.current_mood)

    def get_current_mood(self):
        """Get the current mood name"""
        if 0 <= self.current_combination < len(self.pattern_combinations):
            return self.pattern_combinations[self.current_combination]['name']
        return 'peaceful'  # Default mood

    def generate_segment(self, length):
        """Generate ambient segment with melodic focus
        
        Creates a musical segment with:
        - Sparse, gentle melodies
        - Occasional harmonies
        - Soft percussion elements
        - Dynamic mood transitions
        """
        segment = np.zeros(length)
        
        # Get current scale
        scale = self.night_scale if self.is_night else self.day_scale
        
        # Validate progression indices before using them
        if (not hasattr(self, 'progression_sequence') or 
            not self.progression_sequence or 
            not isinstance(self.progression_sequence, list)):
            self.progression_sequence = [
                [0, 4, 5, 3],    # I - V - VI - IV
                [0, 5, 3, 4],    # I - VI - IV - V
                [3, 0, 4, 5],    # IV - I - V - VI
                [0, 3, 5, 4]     # I - IV - VI - V
            ]
        
        # Ensure progression position is valid
        self.progression_position = getattr(self, 'progression_position', 0)
        self.sequence_position = getattr(self, 'sequence_position', 0)
        self.current_progression = getattr(self, 'current_progression', 0)
        
        # Ensure indices are within bounds
        self.current_progression %= len(self.progression_sequence)
        self.progression_position %= len(self.progression_sequence[0])
        
        # Melodic elements with plenty of space
        if random.random() < 0.15:  # Sparse melodic moments
            try:
                prog_index = (self.sequence_position // 4) % len(self.progression_sequence)
                chord_index = self.progression_sequence[prog_index][self.progression_position]
                
                # Ensure chord_index is within scale bounds
                chord_index %= len(scale)
                
                available_notes = [
                    scale[chord_index],
                    scale[chord_index] * 1.5,  # Fifth
                    scale[chord_index] * 2.0,  # Octave
                ]
                
                note = random.choice(available_notes)
                if self.last_note:
                    while abs(note - self.last_note) > scale[2] and random.random() < 0.9:
                        note = random.choice(available_notes)
                self.last_note = note
                
                # Very gentle melody
                melody_vol = 0.12 + 0.03 * math.sin(self.sequence_position * 0.1)
                segment += self.create_melody(note, length) * melody_vol
                
                # Occasional harmony
                if random.random() < 0.2:
                    harmony = note * 1.5  # Perfect fifth
                    segment += self.create_melody(harmony, length) * (melody_vol * 0.4)
            except Exception as e:
                print(f"Error in melody generation: {e}")
                # Continue without melody if there's an error
        
        # Update progression with bounds checking
        self.progression_position = (self.progression_position + 1) % len(self.progression_sequence[0])
        if self.progression_position == 0:
            self.current_progression = (self.current_progression + 1) % len(self.progression_sequence)
        
        # Very rare, soft percussion
        if random.random() < 0.08:
            try:
                drums = self.generate_drum_pattern(length, 
                                                'dreamy' if self.is_night else 'peaceful',
                                                self.sequence_position)
                segment += drums * 0.06
            except Exception as e:
                print(f"Error in drum generation: {e}")
        
        # Minimal compression
        segment = np.tanh(segment * 1.01)
        
        # Normalize with plenty of headroom
        max_val = np.max(np.abs(segment))
        if max_val > 0:
            segment = segment / max_val * 0.5
        
        # Update sequence position
        self.sequence_position += 1
        
        return segment

    def create_melody(self, frequency, length):
        """Create a soft, piano-like melody sound"""
        t = np.linspace(0, length/SAMPLE_RATE, length)
        
        # Gentle sine-based tone with subtle harmonics
        melody = (
            1.0 * np.sin(2 * np.pi * frequency * t) +
            0.2 * np.sin(4 * np.pi * frequency * t) * np.exp(-3 * t) +
            0.1 * np.sin(6 * np.pi * frequency * t) * np.exp(-4 * t)
        )
        
        # Piano-like envelope
        attack = int(0.01 * length)
        decay = int(0.2 * length)
        sustain = 0.6
        release = int(0.5 * length)
        
        envelope = np.ones(length) * sustain
        envelope[:attack] = np.linspace(0, 1, attack)**2
        envelope[attack:attack+decay] = np.linspace(1, sustain, decay)
        envelope[-release:] = np.linspace(sustain, 0, release)**2
        
        # Add very gentle chorus
        chorus = np.zeros_like(melody)
        chorus_delay = int(0.02 * SAMPLE_RATE)
        if chorus_delay < len(melody):
            chorus[chorus_delay:] = melody[:-chorus_delay] * 0.3
        
        return (melody + chorus * 0.1) * envelope

    def validate_state(self):
        """Validate and repair generator state if needed"""
        try:
            # Ensure progression indices are valid
            if not hasattr(self, 'progression_sequence'):
                self.progression_sequence = [
                    [0, 4, 5, 3],    # I - V - VI - IV
                    [0, 5, 3, 4],    # I - VI - IV - V
                    [3, 0, 4, 5],    # IV - I - V - VI
                    [0, 3, 5, 4]     # I - IV - VI - V
                ]
            
            if not hasattr(self, 'current_progression'):
                self.current_progression = 0
            
            if not hasattr(self, 'progression_position'):
                self.progression_position = 0
            
            # Ensure indices are within bounds
            self.current_progression %= len(self.progression_sequence)
            self.progression_position %= len(self.progression_sequence[0])
            
            # Validate other musical positions
            self.current_beat_position %= 16
            self.current_melody_position %= 16
            self.current_bass_position %= 16
            
            return True
            
        except Exception as e:
            print(f"Error in state validation: {e}")
            self._reset_to_defaults()
            return False

    def _reset_to_defaults(self):
        """Reset generator to safe default state"""
        self.current_combination = 0
        self.sequence_position = 0
        self.transition_progress = 0.0
        self.transition_time = 0
        self.is_transitioning = False
        self.current_beat_position = 0
        self.current_melody_position = 0
        self.current_bass_position = 0
        self.last_note = None

    def request_transition(self, target_mood):
        """Request a transition to a new mood"""
        try:
            # Find the pattern combination matching the target mood
            for i, combo in enumerate(self.pattern_combinations):
                if combo['name'].lower() == target_mood:
                    if i != self.current_combination:
                        self.is_transitioning = True
                        self.transition_progress = 0.0
                        self.current_combination = i
                        self.transition_time = 0
                    break
        except Exception as e:
            print(f"Error requesting transition: {e}")

    def create_kick(self, length):
        """Create an ultra-soft, minimal kick for ambient music"""
        t = np.linspace(0, length/SAMPLE_RATE, length)
        
        # Very gentle pitch envelope
        freq_start = 60   # Lower start
        freq_end = 58    # Minimal pitch drop
        
        # Minimal pitch envelope
        freq = freq_start * (np.exp(-12 * t) * 0.2 + 0.8)  # Very short drop, higher sustain
        freq = np.clip(freq, freq_end, freq_start)
        
        # Phase accumulation
        phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
        
        # Pure sine only
        kick = np.sin(phase)
        
        # Ultra short envelope
        attack = int(0.002 * length)  # Shorter attack
        decay = int(0.08 * length)    # Much shorter decay
        
        envelope = np.ones(length)
        envelope[:attack] = np.linspace(0, 1, attack)**2
        envelope[attack:] = np.exp(-8 * np.linspace(0, 1, len(envelope[attack:])))
        
        # Very gentle lowpass
        kick = np.convolve(kick, np.hanning(16), mode='same')
        
        # No room sound, just pure kick
        output = kick * envelope
        
        # Normalize and keep extremely quiet
        output = output / np.max(np.abs(output))
        return output * 0.15  # Even lower volume

    def create_snare(self, length):
        """Create a soft snare sound"""
        t = np.linspace(0, length/SAMPLE_RATE, length)
        
        # Mix of tone and noise
        tone_freq = 180
        tone = np.sin(2 * np.pi * tone_freq * t)
        noise = np.random.uniform(-1, 1, len(t))
        
        # Filter the noise
        noise = np.convolve(noise, np.hanning(32), mode='same')
        
        # Combine tone and noise
        snare = tone * 0.3 + noise * 0.7
        
        # Envelope
        attack = int(0.001 * length)
        decay = int(0.15 * length)
        envelope = np.ones(length)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[attack:] = np.exp(-7 * np.linspace(0, 1, len(envelope[attack:])))
        
        return snare * envelope * 0.2  # Quiet snare

    def create_hihat(self, length, is_open=False):
        """Create a gentle hi-hat sound"""
        t = np.linspace(0, length/SAMPLE_RATE, length)
        
        # Generate noise
        noise = np.random.uniform(-1, 1, len(t))
        
        # Bandpass filter (6-12kHz range)
        noise = np.convolve(noise, np.hanning(16), mode='same')
        
        # Envelope
        attack = int(0.001 * length)
        decay = int(0.3 * length if is_open else 0.05 * length)
        envelope = np.ones(length)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[attack:] = np.exp(-12 * np.linspace(0, 1, len(envelope[attack:])))
        
        return noise * envelope * 0.15  # Very quiet hi-hat

    def create_shaker(self, length, style='soft'):
        """Create a gentle shaker/tambourine sound"""
        t = np.linspace(0, length/SAMPLE_RATE, length)
        
        # Generate filtered noise
        noise = np.random.uniform(-1, 1, len(t))
        
        # Different filter characteristics for different styles
        if style == 'soft':
            # Gentle shaker sound
            noise = np.convolve(noise, np.hanning(8), mode='same')
        else:
            # More bright tambourine-like sound
            noise = np.convolve(noise, np.hamming(4), mode='same')
        
        # Add some metallic resonance for tambourine
        if style == 'bright':
            resonance = np.sin(2 * np.pi * 6000 * t) * 0.1
            noise += resonance * np.random.uniform(0, 1, len(t))
        
        # Envelope
        attack = int(0.001 * length)
        decay = int(0.08 * length if style == 'soft' else 0.15 * length)
        envelope = np.ones(length)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[attack:] = np.exp(-10 * np.linspace(0, 1, len(envelope[attack:])))
        
        return noise * envelope * (0.1 if style == 'soft' else 0.15)

    def generate_drum_pattern(self, length, mood='peaceful', position=0):
        """Generate ambient drum pattern with dynamic variations
        
        Args:
            length: Length of the pattern in samples
            mood: 'peaceful' or 'dreamy' - affects pattern style
            position: Sequence position for pattern variation
        
        Creates gentle percussion patterns with:
        - Soft kicks with minimal pitch movement
        - Variable timing based on mood
        - Subtle room ambience
        - Dynamic pattern evolution
        """
        pattern = np.zeros(length)
        
        # Calculate timing divisions for slower tempo (75-80 BPM)
        quarter_note = int(0.8 * SAMPLE_RATE)  # Slower tempo
        eighth_note = quarter_note // 2
        sixteenth_note = quarter_note // 4
        
        if mood == 'peaceful':
            # Variable kick pattern
            pattern_type = position % 3  # Three different basic patterns
            if pattern_type == 0:
                kick_positions = [0, int(quarter_note * 2.5)]
            elif pattern_type == 1:
                kick_positions = [0, int(quarter_note * 3)]
            else:
                kick_positions = [0, int(quarter_note * 2), int(quarter_note * 3.5)]
            
            for offset in kick_positions:
                if offset < length and random.random() < 0.8:
                    pattern[offset:] += self.create_kick(length-offset) * 0.5
                    
                    # Variable room sound
                    room = np.zeros_like(pattern)
                    room_delay = int((0.06 + 0.04 * math.sin(position * 0.2)) * SAMPLE_RATE)
                    if room_delay < len(pattern[offset:]):
                        room[offset+room_delay:] = pattern[offset:-room_delay] * 0.15
                        room = np.convolve(room, np.hanning(128), mode='same')
                        pattern += room
        
        elif mood == 'dreamy':
            # Dreamy variations
            if random.random() < 0.5:
                kick = self.create_kick(length) * (0.3 + 0.1 * math.sin(position * 0.3))
                pattern += kick
                
                # Evolving reverb
                reverb = np.zeros_like(pattern)
                base_delay = 0.15 + 0.1 * math.sin(position * 0.25)
                delays = [
                    (base_delay, 0.2),
                    (base_delay * 1.5, 0.15),
                    (base_delay * 2, 0.1)
                ]
                for delay_time, amplitude in delays:
                    delay = int(delay_time * SAMPLE_RATE)
                    if delay < length:
                        reverb[delay:] = pattern[:-delay] * amplitude
                        reverb = np.convolve(reverb, np.hanning(256), mode='same')
                pattern += reverb * 0.3
        
        return pattern * 0.4 