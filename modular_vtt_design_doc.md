Virtual Tabletop (VTT) Design Document

Project Name: Modular Virtual Tabletop (VTT)
Author: [Your Name]
Date: 2025-08-28

---

1. Overview

The Modular VTT is a platform for playing tabletop RPGs that supports multiple game systems (e.g., D&D 5e, Traveller, Shadowrun) and homebrew / expansion modules. The system is designed to be strict enough to enforce consistency, yet flexible enough to handle wildly different game mechanics.

Goals:
- Support any RPG system via a standardized module format.
- Allow homebrew content and expansions to extend or override core rules safely.
- Provide conflict detection and resolution.
- Maintain a clear structure for developers with a DevKit.

---

2. Core Engine

The core engine provides universal services for all modules:
- Dice API: Rolling, modifiers, success/failure evaluation.
- Entity API: Characters, NPCs, starships, or other units.
- Action API: Registering and executing actions (spells, attacks, skills).
- Event System: Hooks for custom behaviors.
- Sheet/UI Renderer: Renders character sheets and tabs dynamically from JSON.
- Map/Token System: Display and control game map, tokens, and assets.
- Persistence System: Save/load game state.

The engine is system-agnostic, relying on modules to define rules, sheets, scripts, and assets.

---

3. Module System

3.1 Module Types
- System Module: Full ruleset for a game (D&D 5e, Traveller). Contains core rules, dice mechanics, sheets, scripts, and assets.
- Mini-Module / Homebrew: Adds or overrides specific elements (classes, ships, monsters). Declares dependencies on a base system module.

3.2 Module Structure

Folder layout (DevKit standard):
```
module_name/
├── module.json
├── metadata.json
├── rules.json
├── sheets.json
├── scripts/
│   └── action_scripts.js
└── assets/
    ├── tokens/
    └── icons/
```

3.3 Manifest Fields
- id: Unique system identifier
- name: Display name
- version: Module version
- author: Creator(s)
- description: Short text
- entry: File paths for rules, sheets, scripts, assets
- dependencies: Modules required before loading
- engine: Supported engine versions
- tags: Metadata for search/filter

---

4. Character Sheets & Rules
- Sheets defined in sheets.json with tabs and fields (label, key, type).
- Rules in rules.json define dice expressions, success mechanics, and system logic.
- Scripts register actions using Action API with unique IDs and optional hooks.

Example: Psionic Blast action (D&D Psion module)
```js
registerAction("psionic_blast", {
    label: "Psionic Blast",
    formula: "2d8 + @int_mod",
    onSuccess: (result, actor, target) => {
        updateAttribute(target.id, "hp", -result.total);
    }
});
```

---

5. Assets
- Tokens and icons stored under assets/
- Recommended naming: moduleid.type.name.ext (e.g., dnd5e.token.goblin.png)

---

6. Conflict Management
6.1 Detection
- Duplicate field keys in sheets
- Duplicate dice/mechanics keys in rules
- Duplicate action IDs in scripts
- Duplicate asset filenames

6.2 Resolution
- Automatic merge if safe
- Warn GM if manual choice required
- Apply overrides/extensions per module declaration
- Save decisions in conflict_resolutions.json

6.3 Load Order
1. Core system modules
2. Official expansions
3. Homebrew / mini-modules (user can reorder manually)

---

7. DevKit
Provides developers with:
- Templates for system and mini-modules
- Documentation: guide.md, conflict_management.md, dice_syntax.md, sheet_layout_guide.md
- Examples: Traveller core module, D&D Psion module
- Validator script: checks for schema errors and duplicate IDs
- Preview tool: test modules in sandbox
- Packager: compress modules into distributable format

---

8. Module Load Sequence
1. Start engine → initialize core APIs
2. Read installed modules → sort by type (system, expansion, homebrew)
3. Load system modules → register rules, sheets, scripts, assets
4. Load expansions → merge with system modules
5. Load homebrew modules → check dependencies, merge, detect conflicts
6. Resolve conflicts → automatic merge or GM choice
7. Finalize merged session → all content available
8. Start game session → players interact via UI

---

9. Example Modules
- D&D Psion Module: Adds Psion class tab, psionic_attack, psionic_damage, Psionic Blast action, Psi Points tracking, token & icon.
- Traveller Starship Module: Adds Starship tabs (Systems & Crew), starship_initiative, laser_attack, scripts, starship token & laser cannon icon.

---

10. Visual Architecture
```
[Core Engine]
     │
     ▼
[System Modules] → D&D, Traveller
     │
     ▼
[Mini-Modules/Homebrew] → Psion, Starships
     │
     ▼
[Conflict Manager] → auto/GM resolution
     │
     ▼
[Game Session] → final merged sheets, rules, actions, assets
```

---

This design document provides a complete blueprint for building a modular VTT, supporting multiple systems, homebrew modules, conflict management, and a developer-friendly structure.

