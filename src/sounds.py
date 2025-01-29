import pygame
import numpy as np
import pygame.sndarray
import random
import signal

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
    def __init__(self):
        try:
            pygame.mixer.quit()
            pygame.mixer.init(44100, -16, 2, 1024)
            
            # Ant spawning sound (high-pitched blip)
            self.ant_spawn = create_synth_sound(880, 0.1, 0.3, 'sine')
            
            # Resource collection sounds
            self.mineral_collect = create_synth_sound(440, 0.05, 0.2, 'square')
            self.plant_collect = create_synth_sound(550, 0.05, 0.2, 'sine')
            
            # Colony creation (majestic chord)
            base_freq = 220
            chord_duration = 0.5
            chord_samples = int(44100 * chord_duration)
            chord = np.zeros(chord_samples)
            
            for freq_mult in [1, 1.25, 1.5]:  # Major chord
                t = np.linspace(0, chord_duration, chord_samples, False)
                chord += np.sin(2 * np.pi * base_freq * freq_mult * t) * 0.2
            
            # Normalize and convert chord
            chord = np.int16(chord * 32767 / np.max(np.abs(chord)))
            self.colony_create = pygame.sndarray.make_sound(np.column_stack([chord, chord]))
            
            # Snake eating ant (low thump)
            self.snake_eat = create_synth_sound(110, 0.2, 0.4, 'square')
            
            # Resource deposit sound (success chime)
            self.resource_deposit = create_synth_sound(660, 0.15, 0.3, 'sine')
            
            # Error sound (for when actions can't be performed)
            self.error = create_synth_sound(220, 0.2, 0.3, 'sawtooth')
            
            # Create GameBoy startup sound
            self.startup_sound = self.create_gameboy_sound()
            
            # Better buffering settings
            self.music_generator = ChiptuneMusicGenerator()
            self.audio_queue = []
            self.queue_length = 16  # Increased for smoother playback
            self.segment_duration = 0.25  # Shorter segments for tighter sync
            self.music_volume = 0.5
            self.is_playing = False
            self.last_queue_time = 0
            self.crossfade_duration = 0.1  # 100ms crossfade
            
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

    def update_music(self, game_state=None):
        """Update background music with seamless playback"""
        try:
            if not self.music_generator or not self.is_playing:
                return
            
            current_time = pygame.time.get_ticks()
            samples_per_segment = int(self.segment_duration * 44100)
            crossfade_samples = int(self.crossfade_duration * 44100)
            
            # Keep buffer well-stocked
            while len(self.audio_queue) < self.queue_length:
                segment = self.music_generator.generate_segment(samples_per_segment + crossfade_samples)
                
                # Normalize before crossfade
                max_val = np.max(np.abs(segment))
                if max_val > 0:
                    segment = segment / max_val
                
                # Improved crossfade with half-cosine window
                fade_in = (1 - np.cos(np.linspace(0, np.pi, crossfade_samples))) / 2
                fade_out = (1 + np.cos(np.linspace(0, np.pi, crossfade_samples))) / 2
                
                segment[:crossfade_samples] *= fade_in
                segment[-crossfade_samples:] *= fade_out
                
                # Convert to 16-bit integers
                audio_data = (segment * 32767).astype(np.int16)
                stereo_data = np.column_stack((audio_data, audio_data))
                
                sound = pygame.sndarray.make_sound(stereo_data)
                sound.set_volume(self.music_volume)
                self.audio_queue.append(sound)
            
            # More precise playback timing
            if not pygame.mixer.get_busy():
                self.play_next_segment()
                self.last_queue_time = current_time
            elif current_time - self.last_queue_time >= (self.segment_duration * 1000 * 0.9):
                # Queue next segment earlier (90% through current segment)
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
    
    def start_background_music(self):
        """Start background music with fade in"""
        try:
            self.is_playing = True
            # Start with low volume
            self.music_volume = 0.0
            
            # Begin playing
            self.update_music()
            
            # Fade in over 2 seconds
            for vol in range(0, 11):
                self.music_volume = vol / 10.0
                pygame.time.wait(200)
                # Update volume of queued segments
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

class ChiptuneMusicGenerator:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.buffer_size = sample_rate * 2
        self.bpm = 90  # Slower tempo (90 beats per minute)
        
        # Calculate timing constants
        self.seconds_per_beat = 60.0 / self.bpm
        self.samples_per_beat = int(self.sample_rate * self.seconds_per_beat)
        
        # Pattern combinations (beat, bass, melody)
        self.pattern_combinations = [
            {
                'name': 'Peaceful',
                'beat': 0,      # Simple
                'bass': 0,      # Steady
                'melody': 0,    # Simple
                'tempo_mult': 1.0
            },
            {
                'name': 'Flowing',
                'beat': 1,      # With snare
                'bass': 1,      # Walking
                'melody': 2,    # Wide
                'tempo_mult': 0.95
            },
            {
                'name': 'Dreamy',
                'beat': 5,      # Sparse
                'bass': 6,      # Pulsing
                'melody': 7,    # Neighbor tones
                'tempo_mult': 0.9
            },
            {
                'name': 'Gentle Groove',
                'beat': 8,      # Shaker groove
                'bass': 5,      # Arpeggiated
                'melody': 3,    # Rising
                'tempo_mult': 1.05
            }
        ]
        
        # Current state
        self.current_combination = 0
        self.pattern_duration = 60  # 60 seconds per combination
        self.transition_time = 0
        self.is_transitioning = False
        self.transition_progress = 0.0
        
        # Simple pentatonic scale frequencies
        self.base_frequencies = [220.0, 261.6, 293.7, 329.6, 392.0]  # A minor pentatonic
        
        # More varied beat patterns (1=kick, 2=hihat, 3=snare, 4=shaker, 0=rest)
        self.beat_patterns = [
            # Basic patterns
            [1,2,0,2, 1,2,0,2, 1,2,0,2, 1,2,2,2],    # Simple
            [1,0,3,2, 0,2,1,2, 1,0,3,2, 0,2,2,2],    # With snare
            [1,4,3,2, 1,4,3,2, 1,4,3,2, 1,4,2,2],    # Full
            # Complex patterns
            [1,0,2,3, 4,2,1,0, 3,0,2,4, 1,2,3,2],    # Syncopated
            [1,2,3,4, 2,3,4,1, 3,4,1,2, 4,1,2,3],    # Rolling
            [1,0,3,0, 2,0,3,0, 1,0,3,0, 2,4,3,4],    # Sparse
            # Build-up patterns
            [1,2,1,2, 1,2,1,3, 1,2,1,2, 1,3,4,2],    # Growing
            [1,0,1,0, 1,2,1,0, 1,2,1,2, 1,2,3,4],    # Building
            # Groove patterns
            [1,4,2,4, 3,4,2,4, 1,4,2,4, 3,4,2,4],    # Shaker groove
            [1,3,2,0, 1,3,2,4, 1,3,2,0, 1,3,4,2],    # Funky
            [1,2,0,2, 3,2,0,2, 1,2,0,2, 3,2,4,2],    # Steady
            [1,0,3,0, 1,4,3,4, 1,0,3,0, 1,4,3,2]     # Complex groove
        ]
        
        # More bass patterns
        self.bass_patterns = [
            [0, 0, 0, 0],          # Steady
            [0, 2, 0, 3],          # Walking
            [0, 3, 2, 0],          # Descending
            [0, 0, 2, 3],          # Rising
            [0, 4, 2, 3],          # Complex
            [0, 2, 4, 2],          # Arpeggiated
            [0, 0, 3, 3],          # Pulsing
            [0, 4, 0, 4],          # Octave jump
            [0, 2, 3, 4],          # Scale run
            [0, 3, 0, 2]           # Syncopated
        ]
        
        # Melody patterns (relative to scale)
        self.melody_patterns = [
            [0, 1, 2, 1],          # Simple
            [2, 1, 0, 1],          # Descending
            [0, 2, 4, 2],          # Wide
            [0, 0, 1, 2],          # Rising
            [4, 2, 1, 0],          # Falling
            [0, 2, 1, 3],          # Complex
            [2, 4, 2, 0],          # High range
            [0, 1, 0, 2],          # Neighbor tones
            [0, 3, 1, 4],          # Jumping
            [2, 2, 3, 4]           # Building
        ]
        
        # Add state tracking for continuous generation
        self.current_beat_position = 0
        self.current_melody_position = 0
        self.current_bass_position = 0
        self.last_note = None  # For melody continuity
        
    def generate_segment(self, length):
        segment = np.zeros(length, dtype=np.float32)
        
        # Get current pattern combination
        combo = self.pattern_combinations[self.current_combination]
        tempo_adjusted_length = int(length * combo['tempo_mult'])
        
        # Generate layers with tempo adjustment
        melody = self.generate_melody(tempo_adjusted_length, combo['melody'])
        bass = self.generate_bass(tempo_adjusted_length, combo['bass'])
        beats = self.generate_beats(tempo_adjusted_length, combo['beat'])
        
        # Resample to original length if needed
        if tempo_adjusted_length != length:
            melody = self.resample(melody, length)
            bass = self.resample(bass, length)
            beats = self.resample(beats, length)
        
        # Mix layers with smooth transitions
        if self.is_transitioning:
            # Calculate crossfade
            old_combo = self.pattern_combinations[(self.current_combination - 1) % len(self.pattern_combinations)]
            fade_out = np.cos(self.transition_progress * np.pi / 2)
            fade_in = np.sin(self.transition_progress * np.pi / 2)
            
            # Mix old and new patterns
            segment += (melody * fade_in + self.last_melody * fade_out) * 0.3
            segment += (bass * fade_in + self.last_bass * fade_out) * 0.3
            segment += (beats * fade_in + self.last_beats * fade_out) * 0.4
            
            self.transition_progress += length / (self.sample_rate * 2)  # 2-second transition
            if self.transition_progress >= 1.0:
                self.is_transitioning = False
        else:
            segment += melody * 0.3 + bass * 0.3 + beats * 0.4
        
        # Store current layers for transitions
        self.last_melody = melody
        self.last_bass = bass
        self.last_beats = beats
        
        # Update pattern timing
        self.transition_time += length / self.sample_rate
        if self.transition_time >= self.pattern_duration:
            self.start_transition()
        
        return segment
    
    def start_transition(self):
        """Start transition to next pattern combination"""
        self.is_transitioning = True
        self.transition_progress = 0.0
        self.current_combination = (self.current_combination + 1) % len(self.pattern_combinations)
        self.transition_time = 0
    
    def resample(self, audio, target_length):
        """Resample audio to target length"""
        if len(audio) == target_length:
            return audio
        return np.interp(
            np.linspace(0, len(audio)-1, target_length),
            np.arange(len(audio)),
            audio
        )

    def generate_melody(self, length, melody_pattern):
        segment = np.zeros(length, dtype=np.float32)
        
        # Calculate positions for continuous playback
        melody_length = length // 2  # 2 melody notes per segment
        
        # Generate continuous melody
        for i in range(2):  # 2 melody notes per segment
            start = i * melody_length
            end = start + melody_length
            
            # Choose next note based on previous for continuity
            if self.last_note is None:
                self.current_note = random.randint(0, len(self.base_frequencies)-1)
            else:
                # Move by small intervals for smoother melody
                self.current_note = (self.last_note + random.choice([-1, 0, 1])) % len(self.base_frequencies)
            
            self.last_note = self.current_note
            freq = self.base_frequencies[self.current_note]
            
            # Generate note with smoother envelope
            t_note = np.linspace(0, 1, end-start)
            wave = np.sign(np.sin(2 * np.pi * freq * t_note))
            envelope = np.exp(-2 * t_note) * (1 - np.exp(-50 * t_note))
            segment[start:end] += wave * envelope * 0.2
        
        # Update positions for next segment
        self.current_melody_position = (self.current_melody_position + 2) % 8  # 8 melody positions
        
        return segment

    def generate_bass(self, length, bass_pattern):
        segment = np.zeros(length, dtype=np.float32)
        
        # Generate continuous bass
        bass_pattern = self.bass_patterns[bass_pattern]
        bass_step = length // len(bass_pattern)
        
        for i, bass_note in enumerate(bass_pattern):
            start = i * bass_step
            end = start + bass_step
            
            # Get bass frequency from scale
            bass_freq = self.base_frequencies[bass_note] / 2  # One octave down
            t_bass = np.linspace(0, 1, end-start)
            
            # Mix square and saw waves for richer bass
            square = np.sign(np.sin(2 * np.pi * bass_freq * t_bass))
            saw = 2 * (bass_freq * t_bass - np.floor(0.5 + bass_freq * t_bass))
            bass_wave = (square * 0.7 + saw * 0.3) * 0.2  # Mix waveforms
            
            # Add subtle pitch bend for movement
            bend = 1.0 + 0.01 * np.sin(2 * np.pi * 0.5 * t_bass)
            bass_wave *= bend
            
            # Apply envelope
            envelope = np.exp(-1 * t_bass) * (1 - np.exp(-20 * t_bass))
            segment[start:end] += bass_wave * envelope
        
        # Update positions for next segment
        self.current_bass_position = (self.current_bass_position + 2) % 4  # 4 bass positions
        
        return segment

    def generate_beats(self, length, beat_pattern):
        segment = np.zeros(length, dtype=np.float32)
        
        # Enhanced beat generation
        beat_pattern = self.beat_patterns[beat_pattern]
        beat_duration = length // len(beat_pattern)
        
        for i, beat_type in enumerate(beat_pattern):
            start = i * beat_duration
            
            if beat_type == 1:  # Kick drum
                end = start + min(1000, beat_duration)
                t_beat = np.linspace(0, 1, end-start)
                # Deeper kick with frequency sweep
                freq_sweep = 100 * np.exp(-10 * t_beat)
                kick = np.sin(2 * np.pi * freq_sweep * t_beat)
                envelope = np.exp(-5 * t_beat)
                segment[start:end] += kick * envelope * 0.4
                
            elif beat_type == 2:  # Hi-hat
                end = start + min(300, beat_duration)
                t_beat = np.linspace(0, 1, end-start)
                # Filtered noise hi-hat
                hat = np.random.uniform(-1, 1, len(t_beat))
                # Add some high frequency resonance
                hat += np.sin(2 * np.pi * 8000 * t_beat) * 0.2
                envelope = np.exp(-50 * t_beat)
                segment[start:end] += hat * envelope * 0.15
                
            elif beat_type == 3:  # Snare
                end = start + min(800, beat_duration)
                t_beat = np.linspace(0, 1, end-start)
                # Mix of noise and tone for snare
                noise = np.random.uniform(-1, 1, len(t_beat))
                tone = np.sin(2 * np.pi * 200 * t_beat)
                snare = noise * 0.5 + tone * 0.5
                envelope = np.exp(-8 * t_beat)
                segment[start:end] += snare * envelope * 0.3
                
            elif beat_type == 4:  # Shaker/Percussion
                end = start + min(200, beat_duration)
                t_beat = np.linspace(0, 1, end-start)
                # Filtered noise with band-pass characteristic
                shaker = np.random.uniform(-1, 1, len(t_beat))
                # Add some mid frequency resonance
                shaker += np.sin(2 * np.pi * 2000 * t_beat) * 0.1
                envelope = np.exp(-40 * t_beat)
                segment[start:end] += shaker * envelope * 0.1
        
        # Update positions for next segment
        self.current_beat_position = (self.current_beat_position + 4) % 16  # 16 steps in pattern
        
        return segment

    def update_game_state(self, game_state):
        """Handle game state updates"""
        pass  # We'll add this functionality later 