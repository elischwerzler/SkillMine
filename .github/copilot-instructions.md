# Copilot Instructions for SkillMine

## Project Overview
SkillMine is a 3D roleplay game built with **Ursina** (a Python game engine wrapping Panda3D). It features dungeons, multiple biomes, combat systems, inventory management, and skill progression.

## Key Technologies
- **Engine**: Ursina 8.3.0+ / Panda3D 1.10.15+
- **Language**: Python 3.10+
- **Graphics**: 3D entities, shaders, particle effects
- **UI**: Ursina UI components (buttons, panels, text)

## Project Structure
```
src/
├── ai/              # NPC and creature AI (companions, pets)
├── combat/          # Combat system, enemy definitions
├── dialogue/        # NPC dialogue and interactions
├── player/          # Character class, inventory, controller
├── quests/          # Quest system
├── ui/              # UI screens (login, menu, HUD, character creator)
└── world/           # World/dungeon generation
```

## Development Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints where practical
- Docstrings for classes and public methods
- Clear variable names
- Keep functions focused and modular

### Ursina-Specific Guidelines
- **Entity naming**: Use descriptive names for game entities
- **Collision detection**: Use colliders for all interactive objects
- **Shaders**: Reference `Entity.default_shader` for consistency
- **UI positioning**: Use relative positioning and proper parent assignments
- **Task scheduling**: Use `invoke()` and `destroy()` for timed events
- **Input handling**: Attach input methods to entities when possible

### Adding New Features
1. Follow the existing module structure
2. Create corresponding UI components if needed
3. Update `FEATURE_ROADMAP.md` with progress
4. Test with the game running (use `python main.py`)

### Feature Priorities
See `FEATURE_ROADMAP.md` for current priorities:
- Enemy loot drops
- Crafting minigame
- Skill tree system
- Boss improvements
- Dragon abilities
- Fairy Queen enhancements

### Testing & Debugging
- **Run the game**: `python main.py` from workspace root
- **Check imports**: Ensure all module paths match the src/ structure
- **Entity cleanup**: Properly destroy entities to prevent memory leaks
- **UI layer**: Use `z=10` for UI elements to ensure they appear on top

### Common Patterns
- Use config.py for all game constants
- Import from relative modules (e.g., `from src.combat.system import CombatSystem`)
- Attach event handlers to entities using methods
- Use `invoke()` for delayed actions
- Handle collisions with `collision_handler` or direct input

## Commit Guidelines
- Keep commits focused and descriptive
- Reference feature names from FEATURE_ROADMAP.md when applicable
- Test before committing to main branch

## Questions & Support
When uncertain about:
- **Ursina API**: Reference the entity structure and built-in methods
- **Game logic**: Check existing similar systems (e.g., combat.py for combat patterns)
- **Architecture**: Maintain the modular structure in src/
