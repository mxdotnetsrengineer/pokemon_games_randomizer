import random
import settings
from settings import current_config 
from helpers.pointers_helper import allocate_banks,save_new_game_file,get_all_items

def randomize_game():
    if allocate_banks():
        save_new_game_file()

def get_items():
    get_all_items()

def main():
    if not os.path.exists(ORIGINAL_GAME):
        print(f"❌ Error: Please place your clean FireRed ROM as '{ORIGINAL_GAME}' in this folder.")
        return

    with open(ORIGINAL_GAME, "rb") as f:
        game_file = bytearray(f.read())

    print("=" * 80)
    print(f"🛰️  PURE DECRYPTION START: Root Map Bank Table at {hex(MAP_BANK_TABLE_OFFSET)}")
    print("=" * 80)

    # STEP 1: Loop through all 42 Map Banks sequentially
    for bank_id in range(BANKS_TO_PRINT):
        # Each entry in the table is a 4-byte pointer to that bank's map list
        bank_entry_offset = MAP_BANK_TABLE_OFFSET + (bank_id * 4)
        map_list_offset = get_gba_offset(game_file, bank_entry_offset)
        
        if map_list_offset is None or map_list_offset == 0:
            # Bank 0 and Bank 1 are empty or structurally restricted in FireRed
            #print(f"📁 Bank {bank_id}: [Empty or Reserved]")
            continue
            
        print(f"\n📁 Bank {bank_id} -> Map List pointer points to PC offset: {hex(map_list_offset)}")
        print("-" * 80)

    print("=" * 80)
    print("🔍 Pure manual binary decryption complete!")

if __name__ == "__main__":
    settings.init_global_config(settings.GAMES[int(settings.AvailableGames.RADICAL_FIRE_RED.value[0])])
    randomize_game()