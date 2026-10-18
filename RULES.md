# KrckRP Rules Engine

## Default Stat Set

The engine uses a minimal but flexible core of stats that can be adapted to any world. These represent the fundamental capabilities of a character.

### Core Stats (Primary)
- **Strength** - Physical power, carrying capacity, melee combat effectiveness
- **Dexterity** - Agility, precision, reflexes, ranged combat accuracy
- **Constitution** - Health, endurance, resistance to damage and status effects  
- **Intelligence** - Knowledge, learning ability, problem-solving, spellcasting power
- **Wisdom** - Perception, intuition, insight, magical sensitivity
- **Charisma** - Persuasion, leadership, social influence, intimidation

### Secondary Stats (Derived)
- **Speed** - Movement rate and reaction time
- **Armor Class** - Defensive capability against attacks
- **Health Points** - Physical durability and survival capacity
- **Mana/Spell Points** - Magical energy for spellcasting and abilities

## Numeric Scales

All stats are represented as integers on a scale of 1-20, with the following typical ranges:
- **Base Range**: 1 to 20 (standard range)
- **Modifiable Range**: 1 to 30 (with significant modifiers possible)

### Stat Interpretation
- **1-5** - Very poor/weak
- **6-10** - Poor/average
- **11-15** - Good/above average  
- **16-20** - Excellent/high
- **21+** - Legendary/supernatural

## Resolution Formula

The core resolution engine determines outcome tier using this formula:

```
Outcome Tier = Capability Score + Context Modifiers + Random Factor 
               vs. Difficulty Score + Environmental Modifiers
```

### Detailed Calculation:
1. **Capability Score**: Primary stat value + relevant skill level (if applicable) + equipment bonuses
2. **Context Modifiers**: 
   - Preparation: +2 for well-prepared actions, -2 for rushed/impulsive
   - Terrain: +1/-1 based on environmental advantage/disadvantage  
   - Equipment: +1/-1 for quality/special features of gear used
3. **Random Factor** (deterministic): 
   - For non-critical actions: 0 (strictly deterministic)
   - For important decisions: ±1 to simulate narrative variation
4. **Difficulty Score**: Base difficulty value from the action being attempted
5. **Environmental Modifiers**: 
   - Time pressure: +1/-1 if urgent/relaxed
   - Status effects: -2 for severe debuffs, +1 for beneficial ones

### Outcome Tier Thresholds:

| Tier | Score Difference | Description |
|------|------------------|-------------|
| Critical Failure | < -5 | Complete disaster with significant consequences |
| Failure | -4 to -1 | Partially successful or completely failed |
| Mixed Success | 0 | Some benefits, some drawbacks |
| Success | 1-3 | Fully successful with minor improvements |
| Strong Success | 4+ | Exceptionally effective with notable benefits |

## Capability Modifiers

### Stat-based Bonuses:
- **Strength**: +1 per point to melee damage and carrying capacity
- **Dexterity**: +1 per point to ranged accuracy, initiative, armor class  
- **Constitution**: +1 per point to health points and resistance to status effects
- **Intelligence**: +1 per point to spell power and knowledge-based skill checks
- **Wisdom**: +1 per point to perception rolls and saving throws against magic
- **Charisma**: +1 per point to persuasion, intimidation, and social skill checks

### Contextual Modifiers:
- **Preparation** (for actions): +2 for well-planned actions, -2 for impulsive attempts
- **Terrain** (for combat/physical tasks): 
  - Advantage: +1 bonus  
  - Disadvantage: -1 penalty
- **Equipment**: 
  - Superior quality: +1 bonus
  - Inferior quality: -1 penalty
- **Status Effects**:
  - Severe debuff (-2 or more): -2 to capability score
  - Mild beneficial effect (+1 to +2): +1 to capability score

## Rule System Principles

The resolution system is designed for narrative-driven gameplay where:
1. Outcomes are primarily based on capability vs difficulty with context modifiers 
2. Randomness is kept minimal and mostly used for flavor rather than core mechanics
3. The engine produces outcome tiers that the narrator describes, not dice rolls
4. Player approach matters in terms of preparation and cleverness (though this is deterministic)
5. Actions that are clearly impossible or nonsensical are rejected before resolution

## Default World Configuration

The default world ruleset follows a balanced fantasy setting with these key characteristics:
- Combat uses traditional hit/armor systems
- Spellcasting requires mana points with scaling based on Intelligence/Wisdom
- Skills are represented as stat-based modifiers to relevant actions  
- All abilities have clear costs and limitations in the ability group system

This configuration can be customized per world through data-driven rule definitions.