# Changelog

## [Unreleased]

### Added
- New Spider Enemy
  - Spawns at night when snake is sleeping
  - Moves slowly with red glowing eyes
  - Hides in trees/bushes during day
  - Dies if caught in daylight without shelter
  - Death animation with flipping and blinking
  - Spiders only spawn if trees/bushes exist on map

- Spider Web Mechanics
  - Spiders leave web traps while moving
  - Webs slow down ants for 5 seconds
  - Ants jump while caught in webs
  - Webs are destroyed after trapping an ant
  - All webs disappear at mid-day from sunlight
  - Webs feature gentle wave animation and shimmer effects

- Ant-Spider Interactions
  - Groups of 3+ ants can attack spiders
  - 70% chance spider flees, 30% chance spider dies
  - Fleeing spiders leave more webs behind
  - Spiders avoid ant colonies

### Changed
- Improved Settings Icon Design
  - Simplified gear icon for better visibility
  - Reduced visual noise in icon pattern

### Fixed
- Spider movement speed adjustments
  - Reduced normal speed to 0.04 (was 0.08)
  - Reduced web creation frequency
  - Added cooldown between web placements
- Spider respawning logic
  - Now properly respawns each night when conditions are met
  - Better shelter-seeking behavior before daylight

### Technical
- Added spider-related sound effects
  - Web creation sound
  - Spider death sound
- Improved web animation system
  - Added phase shifts for organic movement
  - Added alpha variation for shimmer effect
- Added logging for web clearing events

