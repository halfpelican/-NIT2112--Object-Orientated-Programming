# OzZoo GUI Player Guide

This guide explains how to play OzZoo through the current GUI implementation.

## Getting started

1. Open a terminal in the project folder.
2. Run:

```powershell
python .\ozzoo\main.py
```

You can also run:

```powershell
python -m ozzoo.main
```

At launch, you see the **Main Menu** with:

- **🌿 New Game**
- **📂 Load Game**
- **🚪 Quit**

Starting a new game creates a mission-based starter zoo, then opens the Dashboard.

## Main screen overview

### Global layout

- **Top header**: navigation buttons, current day, and budget.
- **Bottom status bar**: short feedback messages for recent actions.

### Main Menu

- Start a new game.
- Load an existing save file (`.json`).
- Quit the app.

### Dashboard (📊)

- **Active Missions** panel with progress bars and reward text.
- **Stat cards**: Budget, Animals, Diversity, Visitors, Sick, Enclosures, Welfare, Reputation.
- **Alerts**: hunger, sickness, dirty enclosures, low stock, low budget, and risk warnings.
- **Quick Actions**:
  - **⏭️ Advance Day**
  - **🍖 Feed Hungry**
  - **🧹 Clean Dirty**
  - **💾 Save Game**
- **Resources** summary for food and medicine stock.

Advancing day opens a day summary popup with visitors, finances, events, births/deaths, and reviews.

### Animals (🦘)

- Filter animals by **All / Hungry / Sick / Healthy**.
- Select an animal to view detailed stats and condition.
- Actions available:
  - **Feed**
  - **Heal**
  - **Treat** (only relevant when sick)
  - **Make Sound**
  - **Feeding Frenzy** mini-game

### Enclosures (🏕️)

- View each enclosure’s capacity, cleanliness, habitat, and risk state.
- Detail panel shows compatible species and all animals inside.
- Actions available:
  - **Clean Enclosure**
  - **Reinforce Barrier** (costs money)
  - **Emergency Relocate Platypus** (billabong only, costs money)

### Map (🗺️)

- 10x10 grid for building and placement.
- Click a tile, then choose an item from the **Build Menu**:
  - Enclosures
  - Scenery
  - Facilities
- Enclosures require a clear 3x3 area and consume budget.
- **Clear Tile** removes placed content from the selected tile.

### Shop (🛒)

- Tabs for **Food**, **Medicine**, and **Animals**.
- Food and medicine purchases increase stock.
- Animal purchase flow asks for:
  - name
  - age
  - gender
  - target enclosure
- Wrong-habitat enclosure choices are shown and blocked from purchase.

### Settings (⚙️)

- Start new game.
- Save / load game.
- View current game info.
- Return to main menu or quit.

## Core gameplay loop

1. Review missions, alerts, welfare, and reputation on the Dashboard.
2. Buy supplies and animals in the Shop.
3. Build and expand on the Map.
4. Manage care in Animals and Enclosures tabs.
5. Advance the day from Dashboard.
6. Read day results and adjust your plan for the next day.

## Animals: purchasing and care

Each animal has key stats:

- **Health** (0–100)
- **Hunger** (0–100, higher means hungrier)
- **Happiness** (0–100)

Daily updates increase hunger and decrease happiness. Starvation, sickness, dirty enclosures, and predation pressure can reduce health.  
If health reaches 0, the animal dies.

Care tools:

- Feed with the correct diet type.
- Use medicine to heal.
- Treat sickness with appropriate medicine stock.

## Visitors

Daily visitors are generated from:

- a base amount
- welfare bonus
- species diversity bonus
- penalties for sick animals

Visitors view animals, affecting satisfaction. Satisfied visitors can donate.  
At day end, visitor reviews are generated (when visitors exist), including star ratings such as:

**⭐️⭐️⭐️⭐️ 4 out of 5 stars**

Reputation is recalculated from review history and shown on the Dashboard.

## Missions

Missions are shown in the Dashboard mission widget and can run in parallel.

Implemented mission types:

- `KEEP_HAPPY`
- `VISITOR_COUNT`
- `PROFIT_TARGET`
- `BUILD_ENCLOSURES`
- `BREED_ANIMALS`

Mission progress updates when days advance.  
Timed missions lose days remaining at day end.  
Completed missions pay rewards and are removed.  
Failed missions are marked failed and removed.  
New missions are added every 3 in-game days.

## Win and lose conditions

There is no global win screen or hard game-over screen in the current GUI flow.  
The simulation continues while you manage your zoo, with success/failure represented through mission outcomes, finances, welfare, reputation, and animal outcomes.

## Mini-games and special mechanics

### Feeding Frenzy mini-game

Trigger from **Animals** by selecting an animal and clicking **🎮 Feeding Frenzy**.

- Uses a shared daily toss-attempt pool tied to current visitors.
- Each toss consumes one food unit.
- Correct food + good timing improves score and happiness gain.
- Misses can injure animals.
- Session summary shows attempts, success ratio, star rating, and stat impact.

### Predation risk system

Predation risk can escalate for configured predator/prey pairings when species are in the same or adjacent enclosures.  
Implemented risk families include:

- Saltwater Crocodile ↔ Platypus
- Goanna ↔ Ringtail Possum
- Snake predator systems (Carpet Python / Eastern Brown Snake with configured prey)
- Tasmanian Devil pressure in mixed-species outback enclosures

At higher risk, animals can lose health/happiness and suffer mishap events, including possible deaths.  
Players can respond by separating species, reinforcing barriers, and using emergency relocation options where available.

### Other day events

Random day events can modify mood, visitors, and finances (for example heatwaves, VIP/grant-style events, or school excursions).  
Mission reward breeding can also create newborns, followed by naming prompts in the day report flow.
