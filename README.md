# Objective
This script (or gui in the future) wants to be a randomizer for all the possible pokemon games. Allow any developer to add a pokemon game/fan game randomizer with only a config file.

# Pokémon Games Randomizer & Decryptor

This project is a Python-based tool designed to parse, decrypt, and randomize binary structures, I am starting with Generation III Pokémon GBA Games. It features initial optimized support for Pokémon FireRed and 1 fan game.

---

## 🚀 Quick Start Guide

To ensure maximum performance and speed when managing Python dependencies, this project utilizes **`uv`**

### 1. Create the Virtual Environment
Navigate to the root directory of the project and spin up an isolated virtual environment:
```bash
python -m uv venv 
```

### 2. Activate the Environment

Activate the virtual environment depending on your operating system:
* **macOS / Linux:**
  ```bash
  source .venv/bin/activate
  ```
* **Windows:**
  ```powershell
  .venv\Scripts\activate
  ```

### Execution
Once the JSON configuration files are tailored and your clean ROM is placed in the root folder, launch the process by executing:
```bash
python main.py
```

---

## ⚙️ Configuration Properties

The system dynamically unifies global configurations, game-specific layouts, and randomizer flags at runtime. Hexadecimal string values (properties starting with `0x`) are automatically processed and converted into integers internally to streamline raw binary operations.

### 1. Game JSON Properties (e.g., `games/fire-red.json`)
Maps the static physical offsets, pointers, and structural metrics embedded inside the original target ROM.

* **`GAME_NAME`**: A descriptive title for the game you are randomizing (e.g., `"My Pokemon FireRed"`).
* **`ORIGINAL_GAME`**: The exact file name of the game you are randomizing, must be located in the root directory.
* **`MODIFIED_GAME`**: The designated output name for the game that cointains randomized data.
* **`GAME_START`**: The specific entry offset highlighting the start of the executable header or game configuration.
* **`MAX_ROM_SIZE`**: The file size limit in bytes allocation for the Game (e.g., `0x1000000` for 16MB).
* **`FREE_SPACE_START`**: The memory pointer index where unused padding (bytes filled with `0xFF`) is safe to overwrite with injected data.
* **`BANK_TABLE_OFFSET`**: The hardcoded offset pointing directly to the root master map bank table.
* **`BANK_TABLE_BANKS_POSITION`**: Position or index boundary flag controlling sequential map bank parsing.
* **`MAP_NAMES_TABLE_OFFSET`**: The internal pointer mapping out the textual data table for location/area names.
* **`REGION_MAP_BYTE`**: Specific byte size parameter configured for region maps parsing.
* **`BANKS_TO_PRINT`**: The upper limit of map banks the script will iterate through for debugger terminal logs.
* **`MAPS_PER_BANK_TO_PRINT`**: The limit of individual maps per bank evaluated sequentially during decoding logs.
* **`MAX_ITEM_ID`**: The maximum upper index boundary for valid item IDs in the game configuration data.
* **`POKEBALL_SPRITE_ID`**: The visual graphic sprite index assigned to items sitting on the overworld floor maps.
* **`ITEMS_POINTER_OFFSET`**: The offset mapping the global layout structure array containing all item assets.
* **`ITEM_STRUCT_SIZE`**: The structural size in bytes occupied by an item item array entry inside the GBA memory layout.

### 2. Global / Randomizer Config Properties (e.g., `games/global_config.json`)
Establishes logical rules and evaluation switches that the randomizer engine enforces upon the target binaries.

* **`RANDOMIZE_POKEBALLS_ITEMS`**: A boolean switch (`true`/`false`) toggling whether items lying visibly inside Pokéballs on the ground should be randomized.

---

## 🛠️ Custom Dynamic Values

During the initialization routines handled by `init_global_config()`, the system injects and modifies transient keys inside the unified operational state dictionary. These values do not live in the static files:

* **`game_file`**: Instantiated as an empty array structure designed to cache the ongoing modified game byte sequence prior to dumping to the physical file.
* **`current_free_space`**: Initially shadows the address provided in `FREE_SPACE_START`. As custom routines inject randomized content, pointers, or tables, this field updates as a **self-incrementing dynamic pointer** to ensure consecutive binary injections never overlap or overwrite data corruptively.
