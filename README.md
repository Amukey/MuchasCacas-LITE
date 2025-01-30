# Muchas Cacas! LITE

A pixel art Idle strategy game where you manage ant colonies while avoiding threats.

## Recent Updates
- Added sophisticated pixelated sun animation
- Improved resource spawning balance
- Enhanced day/night cycle visuals
- Refined visual effects and transitions
- Added dynamic ray effects to sun

## Features
- Dynamic ant colony management
- Day/night cycle with sophisticated visual effects:
  - Pixelated sun with dynamic rays
  - Glowing moon with smooth transitions
  - Time-of-day tooltips
  - Dynamic lighting effects
- Strategic resource gathering with balanced spawning
- Custom animated pixel art graphics and effects
- Adaptive music system that responds to gameplay
- Customizable settings with volume controls
- Threat avoidance mechanics
- Enhanced visual polish:
  - Animated logo with sparkle effects
  - Smooth transitions
  - Particle effects

## Installation
1. Clone the repository
2. Install requirements:
```bash
pip install -r requirements.txt
```
3. Run the game:
```bash
python src/main.py
```

## Dependencies
- Python 3.8+
- Pygame 2.5.0+
- Noise (for terrain generation)

## Controls
- Left click to place colonies and spawn ants
- Left Click: Place first colony
- Left Click on Colony: Spawn new ant (costs resources)
- Right Click on Colony: Create new colony (costs resources)
- Mouse Movement: Guide ants to resources
- Settings icon in top right for volume controls
- Mouse hover over sun/moon for time information
- Settings Icon (Top Right): Adjust sound/music volume
- Mouse Hover on Sun/Moon: Check day/night cycle time

## Development
The game is in active development. Latest changes focus on:
- Visual polish and animations
- Game state management
- Performance optimizations
- UI/UX improvements

## Credits
Created by Guillermo Federico Heinze

## 🎨 Credits

- Game Design & Development: Guillermo F Heinze
- Pixel Art: Guillermo F Heinze
- Sound Design: Custom synthesized using Python

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues

- Snake movement could be smoother
- Resource respawn might need balancing
- Performance optimization needed for large number of ants
- UI could be more intuitive for new players
- Sound effects volume needs adjustment options
- Day/night cycle timing might need adjustment
- Colony placement needs better visual feedback
- Resource collection radius could be clearer

## 📞 Contact

Guillermo F Heinze - [@amukey](https://github.com/Amukey)
Project Link: [https://github.com/Amukey/MuchasCacas-LITE](https://github.com/Amukey/MuchasCacas-LITE)

## Project Structure
```
MuchasCacas!_LITE/
├── src/
│   ├── main.py              # Game entry point
│   ├── game.py             # Main game logic
│   ├── amuke_games_logo_code.py  # Logo animation
│   ├── utils.py            # Utility functions
│   ├── entities/           # Game entities
│   ├── resources/          # Game resources
│   ├── ui/                 # User interface components
│   └── sounds/             # Sound management
├── assets/                 # Game assets (images, sounds)
├── requirements.txt        # Project dependencies
├── README.md              # Project documentation
└── CHANGELOG.md           # Version history
```

## Game Features

### Colony Management
- Create and grow ant colonies
- Collect resources (minerals and plants)
- Manage resource distribution
- Expand territory strategically

### Day/Night Cycle
- Dynamic lighting system
- Different gameplay mechanics for day and night
- Visual transitions at dawn and dusk
- Sun and moon cycle affects creature behavior

### Predators & Threats
#### Snake
- Hunts ants during the day
- Sleeps at night in a coiled position
- Can be avoided with proper ant management

#### Spider (New!)
- Emerges at night when the snake sleeps
- Creates web traps to catch ants
- Hides in trees and bushes during day
- Can be defeated by groups of ants
- Webs disappear in mid-day sun

### Environment
- Procedurally generated resources
- Dynamic resource respawning
- Interactive plants and bushes
- Mineral deposits
- Spider webs with physics animations

### Visual Effects
- Pixel art graphics
- Particle effects
- Day/night transitions
- Animated creatures
- Dynamic web animations
- Death animations

### Audio
- Procedurally generated background music
- Dynamic sound effects
- Volume controls
- Environmental audio

## Controls
- Left Click: Create new colony (when possible)
- Mouse Movement: Guide snake
- ESC: Settings menu
- Volume controls in settings

## Strategy Tips
1. Build colonies near resources
2. Watch out for the snake during day
3. Beware of spider webs at night
4. Use groups of ants to defend against spiders
5. Keep colonies away from predator paths

## Technical Requirements
- Python 3.x
- Pygame 2.x
- NumPy (for sound generation)
- Additional dependencies in requirements.txt

## Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python src/main.py`

## Credits
Created by Guillermo F Heinze @ Amuke Games Studio