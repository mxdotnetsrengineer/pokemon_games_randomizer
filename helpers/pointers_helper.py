import os
from settings import current_config
from helpers.consoles_helper import get_gba_offset
from helpers.instances_helper import get_map_name,randomize_pokeballs_item, get_item_name 

def open_game():
    if not os.path.exists(current_config["ORIGINAL_GAME"]):
        print(f"❌ Error: Please place your game '{current_config["ORIGINAL_GAME"]}' in this folder.")
        return False

    with open(current_config["ORIGINAL_GAME"], "rb") as f:
        current_config["game_file"] = bytearray(f.read())

    return True
def find_free_space(game_file, size, start_offset):
    """
    Scans the ROM bytearray to locate an empty block filled with 0xFF bytes.
    """
    search_bytes = b'\xFF' * size
    index = game_file.find(search_bytes, start_offset)
    if index != -1:
        return index
    return None

def save_new_game_file():
    print("=" * 80)
    print("🔍 Pure manual binary decryption complete!")
    with open(current_config["MODIFIED_GAME"], "wb") as f:
        f.write(current_config["game_file"])

def allocate_banks():
    banks_id = current_config["BANK_TABLE_BANKS_POSITION"]
    if not open_game():
        return False
    print("=" * 80)
    print(f"🛰️  PURE DECRYPTION START: Root Map Bank Table at {hex(current_config["BANK_TABLE_OFFSET"])}")
    print("=" * 80)
    
    bank_entry_offset = current_config["BANK_TABLE_OFFSET"] + (banks_id * 4)
    bank_list_offset = get_gba_offset(current_config["game_file"], bank_entry_offset)

    if bank_list_offset is None or bank_list_offset == 0:
        print(f"📁 Core Table Position {banks_id}: [Empty or Reserved]")
        
    print(f"\n📁 Core Table Position {banks_id} -> Bank List pointer points to PC offset: {hex(bank_list_offset)}")
    print("-" * 80)

    # STEP 2: Loop through maps inside this bank
    # In a clean ROM, we safely scan until the next pointer block or an invalid marker
    for bank_id in range(current_config["BANKS_TO_PRINT"]):  
        bank_entry_offset = bank_list_offset + (bank_id * 4)
        bank_header_offset = get_gba_offset(current_config["game_file"], bank_entry_offset) #Se presume es el puntero de la lista de mapas

        if bank_header_offset is None or bank_header_offset == 0 or bank_header_offset > 0x1D00000:
            break
        
        # --- CORRECCIÓN: Calcular el límite del banco actual leyendo dónde empieza el siguiente banco ---
        next_bank_entry_offset = bank_list_offset + ((bank_id + 1) * 4)
        next_bank_header_offset = get_gba_offset(current_config["game_file"], next_bank_entry_offset)
        
        # Si es el último banco de la lista, asignamos un límite arbitrario seguro
        if next_bank_header_offset is None or next_bank_header_offset == 0 or next_bank_header_offset > 0x1D00000:
            next_bank_header_offset = bank_header_offset + 0x2000

        # Eliminamos la lectura errónea de tamaño del banco raíz aquí arriba para evitar los números gigantes
        print(f"📁 Bank ID {bank_id:2d} | Map List Base: {hex(bank_header_offset)}")

        allocate_bank_maps(bank_header_offset)
    return True

def allocate_bank_maps(bank_header_offset):
    for map_id in range(current_config["MAPS_PER_BANK_TO_PRINT"]):
        map_entry_offset = bank_header_offset + (map_id * 4)        
        map_header_offset = get_gba_offset(current_config["game_file"], map_entry_offset)
        
        if map_header_offset is None or map_header_offset == 0 or map_header_offset > 0x1D00000:
            break

        map_name = get_map_name(current_config["game_file"], map_header_offset)
        # Map Heaer
        layout_pointer = get_gba_offset(current_config["game_file"], map_header_offset)
        events_pointer = get_gba_offset(current_config["game_file"], map_header_offset + 4) # Siguiente puntero para el Paso 3

        width, height = 0, 0
        if layout_pointer and layout_pointer < len(current_config["game_file"]):
            width = int.from_bytes(current_config["game_file"][layout_pointer : layout_pointer + 4], byteorder='little')
            height = int.from_bytes(current_config["game_file"][layout_pointer + 4 : layout_pointer + 8], byteorder='little')

        #Condition (No more Banks) 
        if width > 200 or height > 200 or width == 0 or height == 0:
            break

        print(f"📍 Map ID {map_id:2d} | Name: {map_name:<15s} | Header: {hex(map_header_offset)} | Size: {width:3d}x{height:3d}")
        
        if current_config["RANDOMIZE_POKEBALLS_ITEMS"]:
            allocate_event_npcs(events_pointer) 

def allocate_event_npcs(events_pointer):
    npc_count = 0
    if events_pointer and events_pointer < len(current_config["game_file"]):
        # Byte 0 stores the total count of NPCs / physical objects on the map
        npc_count = current_config["game_file"][events_pointer]
        # Bytes 4-7 store the pointer to the array holding these NPC structures
        npc_list_pointer = get_gba_offset(current_config["game_file"], events_pointer + 4)
    
    print(f" Total Npcs: {npc_count}")
    for npc_idx in range(npc_count):
        npc_base_offset = npc_list_pointer + (npc_idx * 24)
        
        if npc_base_offset + 20 < len(current_config["game_file"]):
            # Byte 1 stores the Sprite/Graphic ID
            sprite_id = current_config["game_file"][npc_base_offset + 1]
            npc_text = "Standard Event Layout"
        
            original_pointer_bytes = current_config["game_file"][npc_base_offset + 16 : npc_base_offset + 20]
            original_gba_address = int.from_bytes(original_pointer_bytes, byteorder='little')
            original_rom_offset = original_gba_address - 0x08000000
            
            if current_config["RANDOMIZE_POKEBALLS_ITEMS"]:
                allocate_event_pokeballs(sprite_id, original_pointer_bytes,original_gba_address,original_rom_offset, npc_base_offset)
                    
def allocate_event_pokeballs(sprite_id,original_pointer_bytes, original_gba_address, original_rom_offset, npc_base_offset):
    if sprite_id == current_config["POKEBALL_SPRITE_ID"]:
        # 1. Inspect a chunk of the current script destination to verify its opcodes
        if 0 <= original_rom_offset < len(current_config["game_file"]):
            original_script_bytes = current_config["game_file"][original_rom_offset : original_rom_offset + 20]
            
            # Check for copyvarifnotzero (0x1A) AND callstd MSG_FIND (0x09, 0x01)
            is_already_an_item = 0x1A in original_script_bytes and b"\x09\x01" in original_script_bytes
        else:
            is_already_an_item = False  # Safety fallback if offset points out of bounds

        #2. CRITICAL: ONLY replace if it is ALREADY an item script. Skip if it is a Pokémon starter.
        if is_already_an_item:
            new_script_bytes = randomize_pokeballs_item(current_config["game_file"])
            
            original_pointer_bytes = current_config["game_file"][npc_base_offset + 16 : npc_base_offset + 20]
            original_pointer_address = int.from_bytes(original_pointer_bytes, byteorder='little')

            # Scan for safe space ahead of our continuously updated tracking offset position
            allocated_offset = find_free_space(current_config["game_file"], len(new_script_bytes), current_config["current_free_space"])
            if allocated_offset:
                # Inject byte array into ROM matrix memory
                current_config["game_file"][allocated_offset : allocated_offset + len(new_script_bytes)] = new_script_bytes
                
                # Move the bookmark tracker index past our written payload
                current_config["current_free_space"] = allocated_offset + len(new_script_bytes)
                
                # Convert PC layout address to GBA offset address
                gba_pointer_address = allocated_offset + 0x08000000
                
                # Update the NPC block script reference with the newly allocated pointer address
                current_config["game_file"][npc_base_offset + 16 : npc_base_offset + 20] = gba_pointer_address.to_bytes(4, byteorder='little')
                print(f"New Script: {hex(allocated_offset)}")
            else:
                print("[POKEBALL FAILED] Out of allocation space boundaries")    

def get_all_items():
    if not open_game():
        return

    """
    Extracts and decrypts the item name string directly from the embedded item structure.
    """
    # 0x1C8 is the exact pointer address from your HMA configuration
    # Read the base item table address from the GBA pointer at 0x1C8
    base_items_offset = get_gba_offset(current_config["game_file"], current_config["ITEMS_POINTER_OFFSET"])
    
    if not base_items_offset or base_items_offset >= len(current_config["game_file"]):
        return "UNKNOWN"

    # Calculate the exact position of the target item structure
    currentId = 0
    while currentId < 1000:
        item_name = get_item_name(current_config["game_file"], currentId)
        print(f"Item ID {currentId} | Item Name {item_name}")
        currentId += 1