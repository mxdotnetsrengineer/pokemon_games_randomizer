import random
from helpers.consoles_helper import GBA_CHAR_TABLE, get_gba_offset
from settings import current_config

def get_map_name(game_file, map_header_offset):
    """
    Extracts and decrypts the map name string using the GBA character table.
    """
    # Root pointer array for map name text addresses in FireRed USA v1.0
    MAP_NAMES_TABLE_OFFSET = 0x3F1CAC
    
    # Byte 20 (0x14) contains the regionMapSectionId matching the game engine structure
    name_id = game_file[map_header_offset + 20]
        
    # FireRed string arrays are index-shifted; entry 0 matches index 0x58 (Pallet Town)
    if name_id < 0x58:
        return "UNKNOWN"
        
    adjusted_index = name_id - 0x58
        
    # Read the GBA text pointer pointing to the string memory block
    pointer_entry = MAP_NAMES_TABLE_OFFSET + (adjusted_index * 4)
    string_pointer = get_gba_offset(game_file, pointer_entry)
    
    if not string_pointer or string_pointer >= len(game_file):
        return "UNKNOWN"
        
    # Standard character array parser loop up to the 0xFF terminator
    map_name = ""
    offset = string_pointer
    while offset < len(game_file):
        char_byte = game_file[offset]
        if char_byte == 0xFF:
            break
        map_name += GBA_CHAR_TABLE.get(char_byte, "?")
        offset += 1
        
    return map_name if map_name else "UNKNOWN"

def get_item_name(game_file, item_id):
    """
    Extracts and decrypts the item name string directly from the embedded item structure.
    """
    # 0x1C8 is the exact pointer address from your HMA configuration
    # Read the base item table address from the GBA pointer at 0x1C8
    base_items_offset = get_gba_offset(game_file, current_config["ITEMS_POINTER_OFFSET"])
    
    if not base_items_offset or base_items_offset >= len(game_file):
        return "UNKNOWN"

    # Calculate the exact position of the target item structure
    target_item_offset = base_items_offset + (item_id * current_config["ITEM_STRUCT_SIZE"])
    
    if target_item_offset >= len(game_file):
        return "UNKNOWN"

    # Standard character array parser loop up to the 14-byte string limit or 0xFF terminator
    item_name = ""
    offset = target_item_offset
    max_string_end = target_item_offset + 14  # Item names have a strict 14-byte field limit
    
    while offset < max_string_end and offset < len(game_file):
        char_byte = game_file[offset]
        if char_byte == 0xFF:
            break
        item_name += GBA_CHAR_TABLE.get(char_byte, "?")
        offset += 1

    return item_name if item_name.strip() else "UNKNOWN"

def randomize_pokeballs_item(game_file, quantity = 1):
    item_name = ""
    random_new_item = -1;
    while True:
        # 1. Generate the random item ID (Example range for FireRed items)
        random_new_item = random.randint(1, current_config["MAX_ITEM_ID"])
        
        # 2. Get the item name using your memory-based function
        item_name = get_item_name(game_file, random_new_item)
        
        # 3. Validation: If it contains '???', skip it and reroll
        if "???" in item_name or item_name == "UNKNOWN":
            continue  # Rerolls and tries a new random_new_item
            
        # 4. If the name is valid, break the loop
        break

    new_script_bytes = bytearray([
        # copyvarifnotzero 0x8000 ANTIDOTE (ID del Ítem)
        0x1A, 0x00, 0x80, random_new_item & 0xFF, (random_new_item >> 8) & 0xFF,
        
        # copyvarifnotzero 0x8001 0x1 (Cantidad)
        0x1A, 0x01, 0x80, quantity & 0xFF, (quantity >> 8) & 0xFF,
        
        # callstd MSG_FIND (Opcode real 0x09 + Parámetro 0x01)
        0x09, 0x01,
        
        # end (Opcode real 0x02)
        0x02
    ])

    print(f"[POKEBALL REPOINTED] Given Item ID: {random_new_item} | Name: {item_name}")
    return new_script_bytes