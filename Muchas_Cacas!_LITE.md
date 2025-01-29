### Detailed Implementation Document for Pixel Swarm: Basic Colony

#### Overview
This document provides detailed instructions and specifications for developing the "Pixel Swarm: Basic Colony" mini-version game. The coder will implement all described mechanics, visuals, and interactions to make the game functional and playable.

---

### Game Window
- **Resolution**: 480x800 pixels
- **Orientation**: Portrait mode
- **Grid System**:
  - Tile size: 16x16 pixels
  - Grid dimensions: 30x50 tiles

---

### Core Mechanics

#### 1. **Colony Mechanics**
- **Entity**:
  - Sprite: 16x16 pixels
  - Centered when placed by the player.
- **Spawning Ant Pixels**:
  - Requires 1 plant resource per Ant Pixel.
  - Max spawn rate: 1 Ant Pixel per second.
- **Spawning Additional Colonies**:
  - Requires 5 rock resources.
  - Colonies can be placed manually by the player within explored areas.

#### 2. **Ant Pixels**
- **Entity**:
  - Sprite: 8x8 pixels
  - Movement speed: 32 pixels/second.
- **Behavior**:
  - **Exploration**: Random walk within unexplored areas or toward nearest detected resource.
  - **Perception**: Detects resources within a radius of 64 pixels.
  - **Collection**: Carries 1 unit of resource (rock or plant).
  - **Return Logic**: Once a resource is collected, finds the shortest path back to the Colony using basic pathfinding (A* algorithm).

#### 3. **Resources**
- **Types**:
  - Rocks:
    - Sprite: 16x16 pixels
    - Regenerates every 10-20 seconds at random locations.
  - Plants:
    - Sprite: 16x16 pixels
    - Regenerates every 5-15 seconds at random locations.

#### 4. **Map and Fog of War**
- **Map Dimensions**:
  - Fixed-size grid (480x800 pixels).
  - Scrollable by dragging with the mouse or touchscreen.
- **Fog of War**:
  - Unexplored areas are obscured.
  - Visibility radius around:
    - Colonies: 96 pixels.
    - Ant Pixels: 64 pixels.

---

### User Interface (UI)
- **HUD Elements**:
  - Resource Counter:
    - Rocks and Plants, displayed with small icons and numbers.
    - Location: Top-left corner of the screen.
  - Colony Placement Indicator:
    - Shows a transparent sprite of the Colony when ready to place.
  - Ant Pixel Counter:
    - Displays the total number of active Ant Pixels.
    - Location: Top-right corner of the screen.
- **Interactive Elements**:
  - Drag to scroll the map.
  - Tap to place the Colony.
  - Visual feedback for successful or invalid actions.

---

### Visuals
- **Art Style**: Retro pixel-art.
- **Assets**:
  - **Colony**:
    - Static sprite with slight animation to indicate activity.
  - **Ant Pixel**:
    - Small, animated sprite with a simple movement effect.
  - **Resources**:
    - Rocks: Grayish sprite with subtle texture.
    - Plants: Green sprite with leaf details.
  - **Fog of War**:
    - Dark overlay with smooth edges that fades as areas are revealed.

---

### Audio
- **Background Music**:
  - Looping, ambient track.
- **Sound Effects**:
  - Resource collection.
  - Ant Pixel spawning.
  - Colony placement.

---

### Programming Details

#### 1. **Movement and Pathfinding**
- **Ant Pixels**:
  - Use random walk for exploration.
  - Implement A* pathfinding for returning to Colony.

#### 2. **Resource Management**
- **Resource Regeneration**:
  - Rocks and plants spawn at random unoccupied tiles.
  - Time intervals for regeneration are based on the above specifications.

#### 3. **Fog of War**
- **Implementation**:
  - Store explored tiles in a 2D boolean array.
  - Update visibility based on Colony and Ant Pixel positions.

#### 4. **Entity Handling**
- Use an object pool for Ant Pixels to optimize performance.

---

### Implementation Milestones

#### Phase 1: Basic Map and UI
- Implement the grid-based map.
- Create scrollable and fog-of-war mechanics.

#### Phase 2: Resource and Entity Setup
- Add rocks and plants with regeneration logic.
- Implement the Colony entity and placement system.

#### Phase 3: Ant Pixel Behavior
- Program Ant Pixel movement, resource detection, and collection.

#### Phase 4: Polishing
- Add sound, animations, and refine UI elements.

---

This document provides all the technical and artistic details necessary to build "Pixel Swarm: Basic Colony." Feel free to reach out for clarification or additional features.

