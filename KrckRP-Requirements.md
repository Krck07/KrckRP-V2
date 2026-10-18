# KrckRP: Project Specification & Roadmap

> **For AI assistants:** This file is the single source of truth for what KrckRP is. You do not need to look up any external product or website. Read the whole file before writing code. If something is marked **[OPEN]**, propose options and ask before committing. If something is marked **[ASSUMPTION]**, follow it unless told otherwise.

---

## 0. Rules for AI assistants (read first)

1. **The database is the source of truth, not the LLM.** The narrator LLM never writes game state directly. It writes prose. State changes are *proposed*, validated and *committed* by the engine.
2. **Never rely on the narrator emitting special syntax** (tags, commands, markers) to update state. This is exactly what failed in the previous attempt.
3. **Everything runs locally.** No cloud APIs, no telemetry, no external services at runtime. Do not suggest them.
4. **Do not add features from the Non-goals list (section 2).**
5. **Prefer simple, boring, debuggable code** over clever abstractions. This is a single-user local application.
6. **Every state change must be logged as an event** (section 6) so it can be inspected, undone and corrected.
7. **Keep the world-specific parts data-driven.** Spells, abilities, combat flavour and NPC attitudes live in world data, not hard-coded in the engine.
8. When unsure about a design decision, check section 14 (Open decisions) before inventing an answer.

---

## 1. What KrckRP is

KrckRP is a **local, single-player, AI-narrated role-playing game platform** that runs entirely on the player's own machine.

The player creates (together with an AI) a **world**, creates a **character** in it, and then plays through an open-ended story by typing what they want to do in their own words. Nothing is scripted: no dialogue trees, no pre-written quests. The story is generated as the player plays.

### The central idea

Plain "AI chat roleplay" fails over long sessions because one language model is asked to *invent the story and remember the whole world at the same time*. KrckRP splits those jobs:

| Component | Job |
|---|---|
| **Engine** (normal code + database) | Simulates and remembers the world: locations, characters, inventory, stats, quests, relationships, history, rules. Decides what is allowed and what the consequences are. |
| **Narrator** (LLM) | Turns what the engine says happened into good prose and dialogue, in the world's tone. |
| **Extractor** (small LLM) | Reads the narration and turns it into structured change proposals for the engine. |
| **Memory** (database + vector store) | Gives the narrator only the relevant slice of the world each turn, so the game *feels* like it has an enormous context window. |

### What the player experiences

- Create a world by chatting with an AI, then refine it in a form editor.
- Create a character inside that world.
- Play by typing free-form actions. The world responds and remembers.
- NPCs remember what you did, including in earlier play sessions, and bring it up later.
- Quests appear and evolve from play instead of being predetermined.
- A sidebar always shows the character, inventory, location, nearby characters and active quests.
- If the engine gets something wrong, the player can fix it, either by asking an assistant in plain language or by editing the data directly.

### Genre scope

Any genre the player can describe: fantasy, sci-fi, horror, slice-of-life, historical, cozy, grimdark and so on. The engine must therefore stay generic. Genre lives in world data.

---

## 2. Non-goals

Do **not** build or suggest:

- Multiplayer or parties of any kind
- User accounts, login, authentication
- Cloud hosting, cloud LLM APIs, online sync
- Mobile apps
- Marketplaces, world sharing or publishing platforms
- Monetisation, subscriptions
- Telemetry or analytics
- Voice input/output (not in scope for now)

---

## 3. Decided technical choices

| Area | Decision |
|---|---|
| Backend language | **Python**, using **FastAPI** |
| Frontend | **Web UI in the browser**, served locally by the backend |
| LLM runtime | **KoboldCpp** (local server, HTTP API) |
| Hardware | **AMD Radeon RX 7900 XT, 20 GB VRAM**. KoboldCpp should be run with a backend appropriate for AMD (Vulkan, or ROCm if it works). **[OPEN: verify which is faster/stable]** |
| Models | **Two models**: a larger *narrator* and a small, fast *extractor*. Exact models are **[OPEN]** (see section 14). |
| Persistent storage | A local **relational database** (SQLite is the default candidate) |
| Semantic storage | A local **vector store** queried by similarity (embedded/local; candidates in section 14) |
| Privacy | Fully offline-capable. No network calls other than to localhost services. |

### Notes on running two models on 20 GB

- The narrator should get most of the VRAM (model weights plus KV cache for a long context).
- The extractor must be small enough to run alongside it, or be loaded only between turns. **[OPEN: benchmark; do not assume both fit with a large context]**
- KoboldCpp serves one model per instance, so expect **two KoboldCpp instances on different ports** (or one instance with model switching if that proves workable). The engine must treat each as a separate configurable endpoint.
- Embeddings should be generated by a small model that does **not** compete for VRAM (CPU is acceptable).

---

## 4. Architecture overview

```
Browser UI  <──HTTP/WebSocket──>  FastAPI backend
                                      │
                    ┌─────────────────┼───────────────────┐
                    │                 │                   │
                 ENGINE          STORAGE LAYER       LLM CLIENTS
          (rules, resolution,   - SQLite (facts,     - Narrator → KoboldCpp #1
           validation, quest      state, event log)  - Extractor → KoboldCpp #2
           logic, context       - Vector store       - Assistant (correction)
           assembly)              (episodic memory,    → either model
                                  lore, summaries)
```

The engine sits **between the player and the LLMs**. The frontend never talks to KoboldCpp directly.

---

## 5. The turn pipeline (the core loop)

Every player action goes through the same steps. Implement this explicitly and keep each step separately testable.

1. **Receive input.** The player types free text, which is stored as part of a new `Turn`.
2. **Interpret intent.** Classify what the player is trying to do (move, talk, attack, use item, cast, examine, craft, other). This may use the extractor model with a constrained schema, plus simple rules where possible.
3. **Resolve mechanics in code.** The engine checks feasibility and computes an **outcome tier** (see section 8). Movement updates location, item use updates inventory, and so on. The LLM does not decide whether an action succeeds.
4. **Assemble context.** Build the narrator prompt from:
   - World style/tone settings and rules summary
   - Current location, time, nearby characters (from SQL)
   - Player state (from SQL)
   - Active quests and relevant goals (from SQL)
   - Rolling summary of recent events
   - The last N turns of raw text
   - Relevant memories retrieved by semantic search (from the vector store)
   - The **resolved outcome**: what actually happened mechanically, which the narrator must respect
5. **Narrate.** The narrator LLM writes the response, streamed to the UI.
6. **Extract.** The extractor LLM reads the narration (plus the player's input) and outputs **schema-validated JSON** describing proposed changes: new characters, location changes, item changes, relationship changes, quest updates, notable events.
   - Use **grammar-constrained / JSON-schema output** (KoboldCpp supports grammar sampling) rather than free-form text.
7. **Validate and commit.** The engine checks each proposal against the rules and current state (does this entity exist, is it consistent, is it allowed?). Valid changes are committed to SQL and logged as events. Invalid ones are discarded or flagged for review. Narrative is embedded into the vector store.
8. **Update UI.** Sidebar and chat refresh from committed state, not from the narrator's text.

**Design rule:** if the narrator says something happened that the engine did not approve (for example it describes the player finding a sword), the engine decides whether to accept it as canon. The extractor proposes, the engine decides.

---

## 6. Data model

> Field lists are a starting point, not a final schema. Propose changes where needed.

### Core entities

- **World**: the reusable template. It has a name, premise, genre/tone settings, narration style, content settings, the rule/ability configuration, and seed locations/characters/factions.
- **Campaign (save slot)**: one playthrough of a World. A world can have **multiple campaigns**. All mutable state belongs to a campaign. **[ASSUMPTION]**
- **Character**: both player character and NPCs. Fields: name, description, role, personality, speech style, goals, location, stats, status, inventory, relationships, visibility/knowledge flags, optional portrait path.
- **Location**: name, description, parent/children, connections to other locations with distances/travel time, tags, who is present.
- **Item**: name, description, properties/tags, owner or location.
- **Ability**: a spell, skill or power, linked to an **ability group** (see section 8).
- **Faction**: name, goals, relationships to other factions and to the player.
- **Relationship**: directed link between two characters or factions, with an attitude value and tags (for example trusts, fears, owes a debt).
- **Quest**: see section 9.
- **Event**: an immutable record of something that happened (see below).
- **Turn**: one player input plus the resulting narration, with a link to the events it produced.
- **Session**: a continuous stretch of play, used for "NPCs remember past sessions" and for summaries.

### Event log (important)

All changes to campaign state are written as **events** in an append-only log, each tagged with:

- the turn that produced it
- its source (`engine`, `extractor`, `player_correction`, `assistant_correction`, `world_creation`)
- the before and after values where relevant

This enables inspection, correction, **undo/rewind**, and rebuilding derived data (summaries, vector entries) if needed.

### Memory tiers

| Tier | Contents | Storage | Loaded |
|---|---|---|---|
| Working | Last N raw turns | SQL | Always |
| Rolling summary | Compressed recent history | SQL | Always |
| Canonical facts | Entities, stats, inventory, locations, relationships, quests | SQL | Selectively by relevance (location, nearby characters, quests) |
| Episodic memory | Past scenes, events and conversations as embedded text with metadata (turn, session, characters involved, location) | Vector store | Retrieved by semantic similarity plus metadata filters |
| Lore | World background, rules text, descriptions | Vector store | Retrieved when relevant |

### NPC knowledge

An NPC should only refer to things they plausibly **witnessed, were told, or could know**. Store enough metadata (who was present, who was told) to filter memories per NPC when building context. Avoid NPCs knowing everything the player did.

---

## 7. The engine

Responsibilities:

- Track **locations, distances and travel**. The narrator is told where things are and how far apart, and the engine does not let the story teleport without cause.
- Track **time** (world clock, day/night, elapsed time per action). **[OPEN: how granular]**
- Track **character state**: stats, status effects, inventory, progression/power level.
- Track **ability availability and progression** within the world's rule configuration.
- Track **relationships and NPC attitudes** and update them from events.
- Track **quests** (section 9).
- Assemble **context** for the narrator (section 5, step 4).
- **Validate** extractor proposals.
- Maintain the **event log** and support undo.
- Retrieve memories from the vector store and write new ones to it.

The engine must work **without** the LLMs for everything deterministic. The LLMs add language, not truth.

---

## 8. Rule system (general, narrative-weighted)

Goals: a *general* rule system that relies **less on pure luck** and **more on narrative context**, and in which spells and abilities are **grouped** so they adapt easily between worlds.

### Principles

- Outcomes are driven mainly by **capability vs. difficulty, adjusted by narrative context**, with only a small random element (or none). Dice are optional flavour, not the main driver.
- The engine produces an **outcome tier** (for example *failure*, *partial success*, *success*, *strong success*) plus consequences, and hands that to the narrator as a fact to describe.
- Context modifiers come from stored state: preparation, terrain, equipment, relationships, status effects, time pressure, plus tags the world defines.
- The player's wording matters. A clever, well-set-up approach should help, but the engine should apply this through explicit, inspectable modifiers rather than hidden LLM judgement. **[OPEN: how to evaluate "cleverness" deterministically; may use the extractor model to tag the approach, with the engine mapping tags to bonuses.]**

### Generalised ability groups

Define a small, world-independent set of **ability categories** that every world's spells/skills/powers map into. Example starting set (adjust as needed):

- Offense (harm, strike, destroy)
- Defense (protect, resist, shield)
- Restoration (heal, cleanse, repair)
- Mobility (move, escape, travel)
- Perception (sense, detect, identify)
- Influence (persuade, deceive, intimidate, charm)
- Manipulation/Creation (craft, summon, alter, build)
- Utility/Knowledge (lore, tools, specialised know-how)

Each world then **skins** these groups (a fantasy world calls Offense *fire magic*, a sci-fi world calls it *plasma weapons*) and defines specific abilities inside them, with costs, requirements and progression. The engine reasons about groups, and the narrator receives the world-specific flavour.

### Per-world configuration

Each world can set: stat names and ranges, resource types (mana, stamina, sanity, none), how combat feels (lethal/forgiving, detailed/abstract), how progression works (levels, milestones, narrative growth), and the relationship/attitude model. All stored as **data**.

**[OPEN]** Exact stat set, numeric scales and tier thresholds. Propose a minimal default world ruleset and make it editable.

---

## 9. Quests

Quests are **not predetermined**. They emerge and update during play.

- **Creation sources**: (a) the extractor detects a new objective, request or goal in the narration, (b) the engine generates one from an NPC/faction goal or an unresolved consequence, (c) the player or correction assistant adds one manually.
- **Quest fields**: title, summary, giver/related characters, location(s), objectives (each with status), state, hooks/consequences, origin turn.
- **States**: `proposed → active → (completed | failed | abandoned | expired)`. **[ASSUMPTION]**
- **Updates**: objectives change status from committed events, not from the narrator's claim alone.
- **Consequences**: completing, failing or ignoring a quest can create events that change relationships, faction standing and the world.
- Quests are always visible in the sidebar and are included in narrator context when relevant.

---

## 10. World creation

**Hybrid flow: chat first, then form editor.**

1. **Chat phase.** The player talks with an AI about the world they want. The AI asks questions and proposes content. Its output is turned into **structured world data** (via the same schema-validated approach as extraction), not left as loose text.
2. **Generated content may include**: setting description and tone, factions, key locations (with connections and distances), key characters, the rule configuration (ability groups skinned for this world), starting situation.
3. **Player controls**: the attitude of NPCs and locations (friendly, hostile, secretive and so on), relationship systems, combat feel, content settings, narration style.
4. **Form editor phase.** The player reviews and edits everything in a structured editor: add/remove/modify locations, characters, factions, abilities, rules.
5. **Character creation** happens inside a world: name, background, stats, starting abilities and items, appearance.
6. On confirm, the world is stored as a template, and a new campaign can be started from it.

The engine must be able to **remember the world and enforce world-specific systems** from this stored data on every turn.

---

## 11. Frontend

A local web UI served by the FastAPI backend.

### Main play screen

- **Chat/story pane** with streamed narration and the player's input box.
- **Sidebar** showing: character stats, inventory, current location (and nearby/connected places), nearby characters, active quests, time.
- **Turn controls**:
  - **Regenerate** the last response
  - **Undo/rewind** to a previous turn (game state rolls back too, using the event log)
  - **Edit** a past message (the player's or the AI's)
- **Save slots**: multiple campaigns per world, selectable from a menu.

### Correction tools (engine failures happen)

Both, as required:

1. **Assistant-driven correction.** A separate panel where the player says in plain language what is wrong ("my sword should be in my inventory", "Mira isn't in this town"). The assistant AI turns that into **structured edit operations** using a defined set of tools, which the engine validates and applies. All edits are logged as events with source `assistant_correction`. The assistant never writes to the database directly.
2. **Manual data editor.** Direct editing of characters, locations, items, quests, relationships and stats through forms. Logged as `player_correction`.

### Other screens

- World creation chat plus form editor (section 10)
- Settings: model endpoints, context sizes, sampler settings, narration style, content settings
- World/campaign library

### Behavioural notes on edit and rewind

- **Undo/rewind** removes the events (and associated vector entries and summaries) from the chosen turn onward.
- **Editing a past player message** rewinds to that turn and replays from the edited input. **[ASSUMPTION]**
- **Editing a past AI message** re-runs extraction for that turn and flags later turns as possibly inconsistent. **[OPEN: confirm behaviour]**

---

## 12. Visuals (late, optional)

- **One generated portrait per character**, created once and stored, shown in the chat/sidebar.
- This is a **separate optional phase**. The rest of the system must work fully without it.
- Needs an image-generation backend that works on AMD hardware locally. **[OPEN: evaluate options; consider VRAM contention with the narrator model, for example generating between turns or offloading]**
- Store the generation prompt/seed with the character so portraits are reproducible.

---

## 13. Content policy

- The application applies **no content filtering of its own**.
- It is **not built around explicit content**, but it also **must not refuse or sanitise** explicit or graphic content when the player asks for it. What the narrator writes is determined by the **chosen local model and the player's world/settings**, not by the app.
- World settings may include tone and content preferences (for example "graphic violence: yes/no") that are passed to the narrator as instructions.

---

## 14. Open decisions

These need proposals and a choice before or during implementation. Propose options with trade-offs. Do not silently decide.

1. **Narrator model** (roughly 20–30B class quantised for 20 GB VRAM) and **extractor model** (small, fast, good at JSON). Benchmark candidates.
2. **KoboldCpp backend** on the 7900 XT: Vulkan vs. ROCm.
3. **Vector store**: candidates include ChromaDB, LanceDB, or SQLite-based options such as sqlite-vec. Prefer the simplest local option.
4. **Embedding model**: small, local, ideally CPU-friendly.
5. **Frontend framework**: plain HTML/JS, or a light framework (for example Svelte or React). Prefer minimal build complexity.
6. **Realtime transport**: streaming via WebSocket or Server-Sent Events.
7. **Time model**: how granular in-world time is.
8. **Cleverness/approach evaluation** for the rule system (section 8).
9. **Behaviour of editing AI messages** (section 11).
10. **Default minimal ruleset**: stat set, scales, outcome tier thresholds.
11. **Image-generation backend** for portraits (section 12).
12. **Context budget**: how many tokens go to each part of the narrator prompt.

---

## 15. Lessons from the previous attempt

> **[TO FILL IN by the project owner]**: briefly list what failed in the earlier RAG-based version. Examples to consider: irrelevant memories retrieved, state drifting out of sync with the story, the AI forgetting or contradicting established facts, syntax-based state updates breaking over time, context filling up. Assistants should use this to avoid repeating the mistakes.

Already known from the owner:

- A RAG-supported system that relied on the AI generating special syntax to update state **failed in key areas**. This is why the engine is separate from the AI and the extractor outputs schema-validated JSON that the engine validates.

---

## 16. Roadmap and acceptance criteria

Build in order. Each phase should work end to end before the next begins.

### Phase 1: Skeleton and chat loop
- FastAPI backend, local web UI with chat, KoboldCpp narrator connected with streaming.
- SQLite with World, Campaign, Character (player), Location, Item.
- Player stats, inventory and current location stored in SQL and shown in the sidebar.
- **Done when:** you can play a basic scene; sidebar values come from the database.

### Phase 2: Engine, extraction and event log
- Implement the full turn pipeline (section 5) with a constrained-output extractor.
- Validation and commit logic, event log, turn records.
- Undo/rewind and regenerate working.
- **Done when:** moving locations, picking up or using items and stat changes in the story reliably update the database, and undoing a turn restores the previous state exactly.

### Phase 3: Memory
- Vector store, embeddings, rolling summaries, context assembly with budgets.
- NPC creation and memory, NPC knowledge filtering.
- **Done when:** an NPC met in an earlier session correctly refers to a specific earlier event, and irrelevant memories are not injected. Include a long-session test (for example 50+ turns across multiple sessions).

### Phase 4: Rules and quests
- Ability groups, per-world rule configuration, outcome tiers, context modifiers.
- Emergent quest system with lifecycle and consequences.
- **Done when:** the same action yields different, explainable outcomes depending on context, and quests appear and resolve from play.

### Phase 5: World creation
- Chat-based world builder producing structured data, then the form editor.
- Character creation flow, save slots, world/campaign library.
- **Done when:** a new world can be created from scratch in the UI and played immediately, and different worlds use different ability skins.

### Phase 6: Correction tools
- Assistant-driven correction with tool-based edits, manual data editor, edit past messages.
- **Done when:** a deliberate engine error can be fixed both ways and the fix is visible in the event log.

### Phase 7 (optional): Portraits
- One generated portrait per character, stored and displayed.
- **Done when:** characters show consistent stored portraits without breaking play.

---

## 17. Glossary

- **Engine**: the deterministic Python layer that owns game state, rules and context assembly.
- **Narrator**: the main LLM that writes story text.
- **Extractor**: the small LLM that converts narration into structured change proposals.
- **Assistant**: the LLM used for world creation help and for correction requests.
- **World**: reusable template (setting, rules, seed content).
- **Campaign**: one playthrough/save of a world.
- **Session**: a continuous period of play within a campaign.
- **Turn**: one player input plus the resulting narration and state changes.
- **Event**: an immutable log record of a state change.
- **Fact**: canonical state stored in SQL.
- **Memory**: episodic or lore text stored in the vector store.
- **Outcome tier**: the engine's resolved result of an action (for example failure, partial success, success), given to the narrator as ground truth.
- **Ability group**: a world-independent category (for example Offense, Restoration) into which world-specific spells and skills are mapped.
