### Game Design Document

Game title: MuchasCacas!_Lite
Platform: Python
Genre: Idle Strategy, Idle Exploration, Idle Resource Management.



#### **1. Overview**
This game is a pixel-art-inspired exploration and resource management game set in an alien world.
 The player spawns and manages "pixel ants," autonomous units that explore, gather resources, and expand across
  distinct biomes. The game features dynamic environments, procedural elements, and a balanced economy to engage 
  players in strategic decision-making.

---

#### **2. Core Gameplay Mechanics**




##### **2.1. Colony**
-**Behavior**: 
  - A colony doesn´t move, it is stationary, placed by the player at game start by left clicking on the map first.
  - New colonies can be purchased when enough resources have been collected. 
  - Each colony decides when it is best to spawn more ants. The colony needs the ants to keep a constant flow of resources.
- **Functionality**:
  - The colony is the starting point set by the player at game start by left clicking on the map.
  - Acts as the central hub, collecting resources from the pixel ants and generating new pixel ants.
  - Each colony can spawn a maximum of 20 ants.
  - The colony is the starting point for the player.
  - The colony is the main storage for the player.
  - The first colony is free and spawns where the player left clicks on the map at the beginning of the game.
  -  The first colony automatically spawns 4 pixel ants when it is created.
  - Pulsates rhythmically to indicate activity. 

- **Looks**: 
  - A pulsating large black square of 10x10 pixels.
 - The pulsating animation of the colony and the additional colonies is a heartbeat represented by scaling the square in and out, while the minimum size is 50x50 pixels.
  - The colony will have a glowing effect of blue color in the center of the square when it has enough resources to spawn pixel ants or yellow color when it has enough resources to create a new colony.
- **Cost**: 
  - First colony is free and spawns where the player left clicks on the map at the beginning of the game.
  - 200 mineral units + 400 green plant units for each new colony.
  - 40 minerals + 20 plants for each ant.



##### **2.2. Ants**
- **Behavior**:
  - Ants have a perception radius of 50 pixels. 
  - Ants will flee from the players cursor in a random direction as soon as they see it.
  - Ants will flee from the snake in a random direction as soon as they see it.
  - Ants have a carrying capacity of 10 minerals and 10 plants.
  - Ants spawn from the colony and explore the map randomly, when they see resources, they gather them and look for more untill their pockets are full, and then return the collected resources to 
  the colony.
  - They collaborate, moving in networks resembling mushroom mycelium, 
  transporting nutrients.
  - They can touch rocks and trees to collect their resources.
  - They can walk through rocks and trees, they can walk on the ground. 
- **Creation**:
  - The player starts with 4 ants that spawn from the first colony.
  - Additional ants can be spawned at the colony by gathering resources:
    - Cost: 40 minerals + 20 plant green pixels each.
    - Activation: clicking on the colony with the left mouse button while having enough resources.
- **Looks**:
  - A small black square of 3x3 pixels.
  - The ants have a procedural walking animation that is a scuttling motion.
  - Every time they perceive something and take a decision, they will animate in a jump of a height of 5 pixels on the spot twice before they start walking again.
  - The ants have a glowing effect of blue color in the center of the square when they have enough resources to return to the colony.


##### **2.3. New Colonies**
- **Creation**:
  - Created by the player by left clicking on the map with the left mouse button while having enough resources.
  - Cost: 200 mineral units + 400 green plant units for each new colony.
- **Functionality**:
  - Act as another autonomous colony hub to extend resource collection efficiency in distant areas.
- **Looks**: 
  - Same as the main colony, but has a outline in baby blue around it.
  


##### **2.5. Plant types: 
- **Trees**:
  - Looks: A large green rectangle of 10x30 pixels.
- **Bushes**:
  -Looks: A small darker green square of 10x10 pixels.

#### **2.6. Predators**
- **Snake**:
  - Behavior:
  - The snake spawns in the map randomly after the player placed the first main pixel node.
  - The snake will move inside the boundaries of the map randomly and will chase and try to eat any pixel ant that it sees.
  - The snake has a perception radius of 50 pixels.
  - The snake will flee from the players cursor as soon as it sees it.
  - The snake will chase the pixel ants and kill them if it sees them.
  - The snake cannot eat ants that are in the colony. 
  - Looks: 
  - At first a smal long green rectangle of 5x15 pixels, moving in the ground animated like a snake.
  - After eating an ant, the tail of the snake grows 1 pixel in length per eaten ant. this will make it look bigger over time.



#### **3. Game Economy**

##### **3.1. Core Resources**
- **Minerals**:
  - Source: Rocks.
  - Behavior: Each rock provides 50 minerals. Shrink as minerals are harvested; provide minerals when harvested.
  - Use: Pixel ant creation, upgrades, and node establishment.
  - Looks: A small brown square of 20x30 pixels.
  - New rocks spawn in the map randomly in intervals of 1000 minerals.
  - Rocks can be harvested by pixel ants to provide minerals.

- **Plants**: 
  - Source: Trees.
    - Behavior: 
      - Each tree provides 30 green pixels when harvested. 
     -Trees shrink in size as green pixels are harvested.
    - Use: Pixel ant creation, plant growth acceleration by proximity to other plants. 
     - Looks: Green shapes defined by the plant type.
  - Source: Bushes.
    - Behavior: 
    - Each bush provides 10 green pixels when harvested. Bushes shrink in size as plants are harvested. 
    -Bushes spawn more ofthen than trees.
    - Use:  Ant creation, Colony creation, plant growth acceleration by proximity to other plants.
- Looks: Green shapes defined by the plant type.

##### **3.2. Resource Costs**
| Action                   | Cost                        |
|--------------------------|-----------------------------|
| Spawn Ant                 | 3 minerals + 1 plants |
| Create Colony             | 200 minerals + 400 plants |
| Main Colony Storage       | 100 minerals                |
| Main Colony Speed Boost   | 100 minerals + 50 plants |
| Main Colony Energy Efficiency | 100 minerals + 100 plants |
| Main Colony Energy Storage | 100 minerals + 100 green pixels |
| Ant Carry Capacity         | 50 minerals                 |
| Ant Durability             | 50 green pixels             |
| New Colony Storage         | 100 minerals + 200 green pixels |
| New Colony Speed Boost     | 100 minerals + 50 green pixels |
| New Colony Energy Efficiency | 100 minerals + 100 green pixels |
| New Colony Energy Storage   | 100 minerals + 100 green pixels |


##### **3.3. Economy Loop**
1. Spawn ants from the main colony and nodes to gather resources.
2. Transport resources back to the main colony or nodes.
3. Use resources to:
   - Create more ants to gather resources.
   - Expand to new areas via new colonies to gather and store more resources.
   - Create new colonies to extend the network.

---

#### **4. Interaction with Environment**

##### **4.1. Plants** 
- Type: Interactable.
- Economic Value: 15 green pixels.
- Behavior: Provide green pixels when harvested. Shrink as green pixels are harvested; regrows randomly every 40 seconds. Disappears when depleted.
- Looks: A large green rectangle of 10x60 pixels. 


##### **4.2. Rocks**
- Type: Interactable.
- Economic Value: 10 minerals.
- Behavior: Provide minerals when harvested. Shrink as minerals are extracted; disappear when depleted.
- Looks: A large black rectangle of 20x10 pixels.
- Ants can´t walk on it.
- Ants can´t walk through it.
- Ants can´t walk on the same spot as a rock on the ground.

##### **4.3. Ground**
- Type: Terrain.
- Effects: acts as a background for the game.
- Looks: gray like dark mode background.
- Behavior: Ants can walk on it, player can place the main colony and nodes on it.
- Ants can walk on it.
- Plants can grow on it.
- Rocks can be placed on it.
- Player can place the main colony and nodes on it. 


---

#### **5. Procedural Elements**
- Procedurally generated Ground backgrounds ensure unique gameplay each session.
- Resource placement, obstacles, and pathways vary per playthrough.

---

#### **6. Visual Design**

##### **6.1. Art Style**
- Detailed pixel art aesthetic with natural color palette
- Animated elements with smooth transitions
- Dynamic lighting and shimmer effects
- Fine-lined textured backgrounds
- Organic movement patterns

##### **6.2. Sprite Design**
1. **Ants**:
- Small black squares (3x3 pixels)
   - Jumping animation when making decisions
   - Scuttling motion for movement
   - Blue glow effect when carrying resources

2. **Main Colony**:
   - Pulsating black square (10-25 pixels)
   - Blue glow indicator for ant spawning
   - Yellow glow indicator for colony creation
   - Resource bars showing mineral and plant levels
   - Flashing yellow indicators when enough resources for new colony

3. **Ground**:
   - Fine-lined textured background with noise patterns
   - Earth-toned color palette (browns and grays)
   - Subtle line patterns for depth
   - Dynamic small details for visual interest
   - 4-pixel tile size for fine detail

4. **Rocks**:
   - Detailed pixel art with multiple shapes
   - Shimmering effect on surfaces
   - Gray color variations for depth
   - Size varies based on remaining minerals
   - Resource indicator bar
   - Multiple rock shapes:
     - Triangular
     - Round
     - Angular
     - Oval

5. **Plants**:
   - Trees with swaying animation
   - Detailed leaf patterns
   - Color variations for depth
   - Size changes based on resources
   - Gentle wind movement effect
   - Resource indicator bar

6. **Snake**:
   - Smooth wave-like movement
   - Green colored segments
   - Growing tail with each ant eaten
   - Fluid body animation
   - 4-pixel size per segment

7. **New Colonies**:
   - Similar to main colony but with baby blue outline
   - Same pulsating animation
   - Resource bars and indicators
   - Smaller maximum ant capacity

8. **Resource Indicators**:
   - Progress bars for all resources
   - Color-coded (brown for minerals, green for plants)
   - Flashing effects for available actions
   - Clear visual feedback for resource gathering

##### **6.3. Animation Details**
- Smooth fade-in sequence at game start:
  1. Amuke Games logo (0.5s fade in, 1s stay, 0.5s fade out)
  2. Background texture fade-in (0.8s)
  3. Trees and plants fade-in (0.6s)
  4. Rocks fade-in (0.6s)
  5. Snake fade-in (0.4s)

- Dynamic Animations:
  - Plant swaying in wind
  - Rock surface shimmer
  - Colony size pulsing
  - Snake wave motion
  - Ant jumping decisions
  - Resource collection effects
  

---


#### **7. Progression System**
- Scoring is based on:
  - Map coverage.
  - Resources gathered.
  - Efficiency in expansion.
- Objectives include:
  - Explore 80% of the map.
  - Establish a specific number of nodes: 100 nodes.
  - Gather a target amount of minerals and green pixels: 1000 minerals and 1000 green pixels.


---


**9. Game objectives**
- Victory: The player wins the game by achieving the following: 
  - The player has to gather 10000 minerals and 10000 green pixels to win the game.
  - The player has to explore and expand to an 80% of the map to win the game.
- Defeat: The player loses the game if he loses all the pixel ants and cannot buy new ones.


#### **10. Technical Details**

##### **10.1. Player Interaction and Controls**
- Mouse Controls:
  - Left Click: Select and place the main colony or new colonies on the map, spawn new ants from the clicked colony.
  - Right Click: Cancel the current action or deselect a colony.
  - Selected colonies are highlighted when selected. 



##### **10.2. User Interface (UI)**
- Resource Display: A tooltip shows when hovering over the main colony or nodes, showing the current amount of minerals, plants as emojis and numbers as a tooltip.
- Colony Management: Left clicking on a colony selects it and shows the current amount of pixel ants, the current amount of minerals, the current amount of plant pixels as a tooltip.
- Hovering over any of the elements of the game displays a tooltip with the name of the element and its current amounts and relevant information.
- Each tooltip is cleverly placed inside the boundaries of the game window, so that it doesn´t hang outside the game window.





##### **10.3. Frameworks**
- **Pygame**: For 2D game mechanics and rendering.
- **Procedural Generation**: Algorithm-based placement of resources.

##### **10.4. Optimization**
- Efficient handling of pixel ant behavior and pathfinding.
- Dynamic loading of resources and assets.


