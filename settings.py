import json
import os

current_config = {}

GAMES = ["fire-red", "radical-red", "emerald"]

from enum import Enum
class AvailableGames(Enum):
    ORIGINAL_FIRE_RED = 0,
    RADICAL_FIRE_RED = 1,

def init_global_config(game_key):
    global current_config

    raw_data = {}
    global_path = "games/global_config.json"

    if os.path.exists(global_path):
        with open(global_path, "r", encoding="utf-8") as f:
            raw_data.update(json.load(f))
    else:
        print("⚠️ Warning: Shared global_config.json file not found.")

    game_path = f"games/{game_key}.json"
    if not os.path.exists(game_path):
        raise FileNotFoundError(f"❌ Game configuration not found at: {game_path}")
    with open(game_path, "r", encoding="utf-8") as f:
        game_data = json.load(f)
        raw_data.update(game_data)
    
    # 3. Process and convert hex values automatically for both layers
    processed_config = {}
    for key, value in raw_data.items():
        if isinstance(value, str) and value.startswith("0x"):
            processed_config[key] = int(value, 16)
        else:
            processed_config[key] = value
    
    #custom options
    processed_config["game_file"] = []
    processed_config["current_free_space"] = processed_config["FREE_SPACE_START"]        

    # 4. Clear old state and commit the new unifed configuration
    current_config.clear()
    current_config.update(processed_config)
    
    game_name = current_config.get('GAME_NAME', game_key)
    print(f"🛰️  Global configuration initialized for: {game_name}")