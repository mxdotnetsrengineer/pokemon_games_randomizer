from helpers.consoles_helper import GBA_CHAR_TABLE, get_gba_offset 

def parse_ground_item_script(game_file, script_pointer):
    """
    Advanced multi-tier engine scanner for FireRed ground items.
    Follows script jumps (goto/call) and extracts item structures dynamically.
    """
    if not script_pointer or script_pointer >= len(game_file):
        return None

    # Step 1: Follow immediate script redirections (goto 0x05 or call 0x06)
    # This prevents raw redirection wrappers from hiding the true byte content
    for _ in range(3):  # Follow up to 3 nested jumps safely
        if script_pointer + 5 < len(game_file):
            opcode = game_file[script_pointer]
            if opcode in [0x05, 0x06]:  # goto or call commands
                redirected_ptr = get_gba_offset(game_file, script_pointer + 1)
                if redirected_ptr and redirected_ptr < len(game_file):
                    script_pointer = redirected_ptr
                else:
                    break

    # Step 2: Thoroughly scan a wider execution window (up to 24 bytes lookahead)
    for offset_shift in range(24):
        current_pc = script_pointer + offset_shift
        if current_pc + 5 >= len(game_file):
            break
            
        command_byte = game_file[current_pc]
        
        # --- PATTERN 1: Native Engine Variable Loading (setvar 0x8000 ItemID) ---
        # Opcode layout: 0x16 [2 bytes Variable 0x8000] [2 bytes Item ID]
        if command_byte == 0x16:
            target_var = int.from_bytes(game_file[current_pc + 1 : current_pc + 3], byteorder='little')
            if target_var == 0x8000:
                item_id = int.from_bytes(game_file[current_pc + 3 : current_pc + 5], byteorder='little')
                
                # Check for item quantity setup right after (often setvar 0x8001 Qty)
                quantity = 1
                qty_pc = current_pc + 5
                if qty_pc + 5 < len(game_file) and game_file[qty_pc] == 0x16:
                    target_var_qty = int.from_bytes(game_file[qty_pc + 1 : qty_pc + 3], byteorder='little')
                    if target_var_qty == 0x8001:
                        quantity = int.from_bytes(game_file[qty_pc + 3 : qty_pc + 5], byteorder='little')
                        
                return item_id, quantity, current_pc + 3

        # --- PATTERN 2: XSE Standard Macro (copyvarifnotzero 0x8000 ItemID) ---
        # Opcode layout: 0x19 [2 bytes Variable 0x8000] [2 bytes Item ID]
        elif command_byte == 0x19:
            target_var = int.from_bytes(game_file[current_pc + 1 : current_pc + 3], byteorder='little')
            if target_var == 0x8000:
                item_id = int.from_bytes(game_file[current_pc + 3 : current_pc + 5], byteorder='little')
                
                quantity = 1
                qty_pc = current_pc + 5
                if qty_pc + 5 < len(game_file) and game_file[qty_pc] == 0x19:
                    quantity = int.from_bytes(game_file[qty_pc + 3 : qty_pc + 5], byteorder='little')
                return item_id, quantity, current_pc + 3
                
        # --- PATTERN 3: Direct Core Engine Command (giveitem ItemID Qty Type) ---
        # Opcode layout: 0x1A [2 bytes Item ID] [2 bytes Quantity]
        elif command_byte == 0x1A:
            item_id = int.from_bytes(game_file[current_pc + 1 : current_pc + 3], byteorder='little')
            quantity = int.from_bytes(game_file[current_pc + 3 : current_pc + 5], byteorder='little')
            return item_id, quantity, current_pc + 1
                
    return None