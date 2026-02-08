# SkillMine Feature Roadmap

## ✅ Completed
- Fixed dungeon wall collision by adding colliders
- Removed invisible world boundary walls for open exploration
- Set all bow ranges to 30 for balanced ranged combat

## 🚧 In Progress / High Priority

### Enemy Loot Drops System
- Enemies drop items/ores when defeated (% chance based on enemy type)
- Boss enemies drop rare ores and monster parts
- Implement drop tables for each enemy type

### Crafting Minigame
- Timing-based minigame when crafting items
- Hit button when ring is in target zone
- Successful hits increase item stats
- Multiple rounds (3 attempts) determine quality bonus
- Better timing = better stats on crafted item

### Skill Tree System
- Earn 1 skill point per level
- Randomly generated paths (procedural generation)
- Ultimate skills require unlocking all surrounding nodes
- Bosses also reward skill points

### Boss Improvements
- Add specific boss enemies to volcano/hellscape biome
- Boss respawn system (30-60 minute timers)
- Bosses drop rare loot, stat points, and skill points
- Make bosses significantly harder (10x HP, special abilities)

### Dragon Abilities
- Dragons shoot fireballs at player
- Fireball projectiles with AOE damage
- Fire damage over time effect

### Fairy Queen Enhancement
- Flying movement pattern
- Hover above ground with bobbing animation

### Secret Bases & Crafting Stations
- Hidden bases in each biome area
- Contains anvils for arrow/armor crafting
- Upgrade station for improving existing items

### Pendant System
- Fairy circles in Fantasy Land drop pendants
- Enchanting room to upgrade character stats
- Pendant-based upgrade tree (like secondary skill tree)

## 📋 Implementation Notes

### Enemy Loot System Structure
```python
ENEMY_LOOT_TABLES = {
    'Wolf': {'drop_chance': 0.15, 'items': ['Leather', 'Health Potion']},
    'Slime': {'drop_chance': 0.20, 'items': ['Slime Core', 'Mana Potion']},
    'Dragon': {'drop_chance': 0.80, 'items': ['Dragon Scale', 'Dragon Ingot', 'Fire Crystal']},
    # Bosses have 100% drop rate
    'Alpha Wolf': {'drop_chance': 1.0, 'items': ['Rare Leather', 'Wolf Fang', 'Swift Essence']},
}
```

### Crafting Minigame Flow
1. Player crafts item at anvil
2. Minigame starts with moving ring
3. Player presses SPACE when ring overlaps target
4. Success adds +% bonus to damage/defense
5. Three rounds total, each success stacks bonus
6. Final item gets quality multiplier based on successes

### Skill Tree Design
- Circular/radial layout around player
- Nodes: Stat boosts, new abilities, passive bonuses
- Ultimate skills at outer ring (require all adjacent unlocked)
- Example skills:
  - +10% Damage
  - +50 Max HP
  - Double Jump ability
  - Life Steal 5%
  - Critical Hit Chance +15%

### Boss Spawn Locations
- Volcano: Fire Drake (level 70, shoots meteors)
- Desert: Pharaoh King (level 65, summons mummies)
- Swamp: Swamp Beast (level 60, poison AOE)
- Tundra: Frost Giant (level 68, freezing attacks)
- Fantasy Land: Fairy Queen (level 75, charm + magic projectiles)

## 🔧 Technical Improvements Needed
- Refactor enemy defeat logic into single method
- Create LootManager class for drop handling
- MinigameController for crafting timing system
- SkillTree class with node graph structure
- Boss class inheriting from Enemy with special abilities

## 📝 Testing Checklist
- [ ] Enemies consistently drop loot
- [ ] Crafting minigame feels responsive
- [ ] Skill tree UI is readable and intuitive
- [ ] Bosses are challenging but fair
- [ ] Loot economy is balanced
- [ ] No collision issues in dungeons
- [ ] Bow range feels appropriate at 30

## 🎯 Priority Order
1. Enemy loot drops (quick win, high impact)
2. Craftsstaffs fixed (bug fix)
3. Boss loot tables (extends #1)
4. Skill tree framework
5. Crafting minigame
6. Boss abilities and respawning
7. Dragon fireballs
8. Secret bases
9. Fairy queen flying
10. Pendant system
