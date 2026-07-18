# =========================================================================
# AUTO CHEAT - UNIVERSAL EDITION (AUTO-DISCOVERY v6.0)
# =========================================================================
# v6.0 - Screen Choice Tracking:
#      - Tracks active screens via show_screen/hide_screen interception
#      - Auto-discovers labels and their variable changes
#      - Auto-discovers screens with imagebutton + Jump actions
#      - Shows indicator overlay on screens with choices
#      - Detailed popup with all button effects
#      - Full Python 2.7 (Ren'Py 6.99/7.x) & Python 3 (Ren'Py 8.x) support
# =========================================================================

init python:
    import re
    import os
    import ast
    import sys
    import json

    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    DEBUG_MODE = True
    DISCOVER_USED_VARIABLES = False  # Set to True to discover variables from $ assignments
    FONT_SIZE_MODIFIER = -4

    # =========================================================================
    # COLOR CONSTANTS
    # =========================================================================
    COLOR_PLUS = "#2ecc71"
    COLOR_MINUS = "#e74c3c"
    COLOR_EQUAL = "#3498db"
    COLOR_DEBUG = "#f1c40f"

    # =========================================================================
    # LOGGING SYSTEMS
    # =========================================================================
    LOGGING_MODE = True
    LOG_FILE_PATH = os.path.join(config.gamedir, "auto_cheat.log")
    MAX_LOG_SIZE = 5 * 1024 * 1024

    DISCOVERY_LOG_PATH = os.path.join(config.gamedir, "auto_cheat_parsing.log")

    def read_file_text(filepath):
        try:
            if sys.version_info[0] < 3:
                with open(filepath, 'rb') as f:
                    return f.read().decode('utf-8')
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        except:
            return None

    def write_file_text(filepath, content):
        try:
            if sys.version_info[0] < 3:
                with open(filepath, 'wb') as f:
                    if isinstance(content, unicode):
                        content = content.encode('utf-8')
                    f.write(content)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
        except:
            pass

    def write_cheat_log(message):
        if not LOGGING_MODE: return
        try:
            if os.path.exists(LOG_FILE_PATH) and os.path.getsize(LOG_FILE_PATH) > MAX_LOG_SIZE:
                os.rename(LOG_FILE_PATH, LOG_FILE_PATH + ".bak")
            
            if sys.version_info[0] < 3 and isinstance(message, unicode):
                message = message.encode("utf-8")
            
            with open(LOG_FILE_PATH, "ab" if sys.version_info[0] < 3 else "a") as f:
                f.write(str(message) + "\n")
        except Exception as e:
            try:
                with open(DISCOVERY_LOG_PATH, "ab" if sys.version_info[0] < 3 else "a") as f:
                    f.write("LOG ERROR: {}\n".format(e))
            except:
                pass

    def write_discovery_log(message):
        try:
            if sys.version_info[0] < 3 and isinstance(message, unicode):
                message = message.encode("utf-8")
                
            with open(DISCOVERY_LOG_PATH, "ab" if sys.version_info[0] < 3 else "a") as f:
                f.write(str(message) + "\n")
        except:
            pass

    try:
        if not os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, "w") as f:
                f.write("Auto Cheat Log initialized\n")
        if not os.path.exists(DISCOVERY_LOG_PATH):
            with open(DISCOVERY_LOG_PATH, "w") as f:
                f.write("Auto Discovery Log initialized\n")
    except:
        pass

    write_discovery_log("\n" + "="*50)
    write_discovery_log("AUTO-DISCOVERY SESSION STARTED")
    write_discovery_log("="*50)

    # =========================================================================
    # CONFIGURATION DICTIONARIES
    # =========================================================================
    MENU_VARIABLE_NAMES = {}
    FUNCTION_PARSER_PATTERNS = {}
    LABEL_CHANGES = {}
    SCREEN_CHOICES = {}
    
    CONFIG_PATH = os.path.join(config.gamedir, "auto_cheat_config.json")

    # =========================================================================
    # COMPILED REGEX (определены рано, т.к. используются в discover_*)
    # =========================================================================
    CHOICE_PATTERN = re.compile(r'(?:"([^"]+)"|\'([^\']+)\')\s*(?:if\s+[^:]+)?\s*:')
    CALC_PATTERN = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*([\+\-]?)=\s*([0-9\.]+)')
    TAG_PATTERN = re.compile(r'\{[^}]*\}')

    # =========================================================================
    # AUTO-DISCOVERY FUNCTIONS
    # =========================================================================
    def get_all_rpy_files():
        rpy_files = []
        for root, dirs, files in os.walk(config.gamedir):
            if 'tl' in root or 'cache' in root or 'game\\tl' in root or 'game/tl' in root:
                continue
            for file in files:
                if file.endswith('.rpy'):
                    rpy_files.append(os.path.join(root, file))
        return rpy_files

    def discover_global_variables(rpy_files):
        discovered_vars = {}
        var_pattern = re.compile(r'^\s*(?:default|define)\s+(?!persistent\.)([a-zA-Z_]\w*)\s*=\s*(-?\d+(?:\.\d+)?)', re.MULTILINE)

        write_discovery_log("\n[VAR DISCOVERY] Scanning {} files for global numeric variables...".format(len(rpy_files)))
        
        for filepath in rpy_files:
            content = read_file_text(filepath)
            if content is None: continue
            
            matches = var_pattern.findall(content)
            for var_name, val in matches:
                if var_name not in discovered_vars:
                    num_val = float(val) if '.' in val else int(val)
                    discovered_vars[var_name] = num_val
                    write_discovery_log("  [+] Found variable: '{}' = {} in {}".format(var_name, num_val, os.path.basename(filepath)))
                
        write_discovery_log("[VAR DISCOVERY] Finished. Found {} unique numeric variables.".format(len(discovered_vars)))
        return discovered_vars
    
    def discover_used_variables(rpy_files):
        """Находит переменные, которые используются в присваиваниях в коде игры."""
        discovered_vars = {}
        # Паттерн для поиска присваиваний: $ var = value, $ var += value, $ var -= value
        assignment_pattern = re.compile(r'^\s*\$\s*([a-zA-Z_]\w*)\s*[\+\-]?=\s*', re.MULTILINE)
        
        write_discovery_log("\n[USED VAR DISCOVERY] Scanning for variables used in assignments...")
        
        for filepath in rpy_files:
            content = read_file_text(filepath)
            if content is None: continue
            
            matches = assignment_pattern.findall(content)
            for var_name in matches:
                if var_name not in discovered_vars:
                    discovered_vars[var_name] = 0  # Значение по умолчанию
                    write_discovery_log("  [+] Found used variable: '{}' in {}".format(var_name, os.path.basename(filepath)))
                
        write_discovery_log("[USED VAR DISCOVERY] Finished. Found {} used variables.".format(len(discovered_vars)))
        return discovered_vars

    def discover_function_patterns(rpy_files, known_vars):
        discovered_patterns = {}
        write_discovery_log("\n[PATTERN DISCOVERY] Scanning ALL '$' lines in all files for function calls...")
        
        for filepath in rpy_files:
            content = read_file_text(filepath)
            if content is None: continue
            lines = content.splitlines()

            for i, line in enumerate(lines):
                stripped = line.strip()
                if not stripped.startswith('$'): 
                    continue
                
                py_code = stripped[1:].strip()
                try:
                    tree = ast.parse(py_code)
                    if not tree.body: continue
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            func_name = node.func.id if hasattr(node.func, 'id') else (node.func.attr if hasattr(node.func, 'attr') else None)
                            if not func_name or func_name in discovered_patterns: 
                                continue

                            var_idx = -1
                            val_idx = -1

                            for idx, arg in enumerate(node.args):
                                arg_str_val = None
                                if hasattr(ast, 'Constant') and isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                    arg_str_val = arg.value
                                elif hasattr(ast, 'Str') and isinstance(arg, ast.Str):
                                    arg_str_val = arg.s
                                
                                if arg_str_val and arg_str_val in known_vars:
                                    var_idx = idx

                                is_num = False
                                if hasattr(ast, 'Constant') and isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                                    is_num = True
                                elif hasattr(ast, 'Num') and isinstance(arg, ast.Num):
                                    is_num = True
                                
                                if is_num:
                                    val_idx = idx

                            if var_idx != -1 and val_idx != -1:
                                tokens = []
                                max_idx = max(var_idx, val_idx)
                                for k in range(max_idx + 1):
                                    if k == var_idx: tokens.append("VAR")
                                    elif k == val_idx: tokens.append("VAL")
                                    else: tokens.append("_")

                                pattern_str = ", ".join(tokens)
                                discovered_patterns[func_name] = pattern_str
                                write_discovery_log("  [+] Auto-pattern for '{}': {} (Line {} in {})".format(func_name, pattern_str, i+1, os.path.basename(filepath)))
                except Exception:
                    pass
                    
        write_discovery_log("[PATTERN DISCOVERY] Finished. Found {} function patterns.".format(len(discovered_patterns)))
        return discovered_patterns

    # =========================================================================
    # AST FUNCTION CALL PARSER (определён до discover_label_changes)
    # =========================================================================
    def parse_function_call_args(code_line):
        try:
            line_clean = code_line.strip()
            if line_clean.startswith("$"): line_clean = line_clean[1:].strip()
            tree = ast.parse(line_clean)
            if not tree.body: return None
            expr_node = tree.body[0]
            call_node = expr_node.value if (hasattr(ast, "Expr") and isinstance(expr_node, ast.Expr)) else expr_node
            if not isinstance(call_node, ast.Call): return None
            
            func_name = call_node.func.id if hasattr(call_node.func, "id") else (call_node.func.attr if hasattr(call_node.func, "attr") else "")
            if func_name not in FUNCTION_PARSER_PATTERNS: return None

            tokens = [t.strip() for t in FUNCTION_PARSER_PATTERNS[func_name].split(",")]
            var_name, val_num = None, None

            for i, arg in enumerate(call_node.args):
                if i >= len(tokens): break
                token = tokens[i]
                if token == "VAR":
                    if hasattr(ast, "Constant") and isinstance(arg, ast.Constant): var_name = arg.value
                    elif hasattr(ast, "Str") and isinstance(arg, ast.Str): var_name = arg.s
                    elif isinstance(arg, ast.Name): var_name = arg.id
                elif token == "VAL":
                    if hasattr(ast, "Constant") and isinstance(arg, ast.Constant): val_num = arg.value
                    elif hasattr(ast, "Num") and isinstance(arg, ast.Num): val_num = arg.n
                    elif isinstance(arg, ast.UnaryOp):
                        op_val = arg.operand.value if (hasattr(ast, "Constant") and isinstance(arg.operand, ast.Constant)) else (arg.operand.n if hasattr(ast, "Num") else 0)
                        val_num = -op_val if isinstance(arg.op, ast.USub) else op_val

            if var_name is not None and val_num is not None:
                return (str(var_name), "+" if int(val_num) >= 0 else "", str(val_num))
        except: pass
        return None

    def normalize_text(text):
        while '{' in text and '}' in text:
            new_text = TAG_PATTERN.sub('', text)
            if new_text == text:
                break
            text = new_text
        text = text.replace(u"’", "'").replace(u"‘", "'").replace(u"“", '"').replace(u"”", '"').replace(u"–", "-").replace(u"—", "-")
        return text.strip()

    # =========================================================================
    # DISCOVER LABEL CHANGES (использует parse_function_call_args)
    # =========================================================================
    def discover_label_changes(rpy_files):
        """Находит изменения переменных в начале каждого label."""
        label_changes = {}
        label_pattern = re.compile(r'^label\s+([a-zA-Z_]\w*)\s*:')
        
        write_discovery_log("\n[LABEL DISCOVERY] Scanning for label changes...")
        
        for filepath in rpy_files:
            content = read_file_text(filepath)
            if content is None: continue
            lines = content.splitlines()
            
            for i, line in enumerate(lines):
                match = label_pattern.match(line.strip())
                if match:
                    label_name = match.group(1)
                    changes = []
                    label_indent = len(line) - len(line.lstrip())
                    
                    # Отслеживаем вложенность if блоков
                    in_if_block = False
                    if_indent = None
                    
                    # Парсим следующие 30 строк label'а
                    for j in range(i + 1, min(i + 31, len(lines))):
                        stripped = lines[j].strip()
                        if not stripped: continue
                        leading_spaces = len(lines[j]) - len(lines[j].lstrip())
                        
                        # Вышли из label
                        if leading_spaces <= label_indent and stripped:
                            break
                        
                        # Проверяем, вышли ли мы из if блока
                        if in_if_block and leading_spaces <= if_indent:
                            in_if_block = False
                            if_indent = None
                        
                        # Проверяем, начинаем ли мы if блок
                        if stripped.startswith('if ') or stripped.startswith('elif '):
                            in_if_block = True
                            if_indent = leading_spaces
                            continue
                        
                        # Пропускаем строки внутри if блоков
                        if in_if_block:
                            continue
                        
                        if stripped.startswith('$') or '=' in stripped:
                            func_res = parse_function_call_args(stripped)
                            if func_res:
                                changes.append(list(func_res))
                            else:
                                # Расширенный regex для поддержки True/False
                                calc_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*([\+\-]?)=\s*([0-9\.]+|True|False)', stripped)
                                if calc_match:
                                    changes.append([
                                        calc_match.group(1),
                                        calc_match.group(2),
                                        calc_match.group(3)
                                    ])
                    
                    if changes:
                        label_changes[label_name] = changes
                        write_discovery_log("  [+] Label '{}': {} changes found".format(label_name, len(changes)))
        
        write_discovery_log("[LABEL DISCOVERY] Finished. Found {} labels with changes.".format(len(label_changes)))
        return label_changes

    def discover_screen_choices(rpy_files, label_changes):
        """Находит screen'ы с imagebutton и связывает их с label'ами."""
        screen_choices = {}
        screen_pattern = re.compile(r'^screen\s+([a-zA-Z_]\w*)\s*\(')
        # Улучшенный паттерн с поддержкой экранированных кавычек
        text_pattern = re.compile(r'text\s+(?:"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\')')
        
        # Паттерны для разных типов action'ов
        jump_call_pattern = re.compile(r'action\s+(?:Jump|Call)\s*\(\s*["\']([^"\']+)["\']\s*\)')
        return_pattern = re.compile(r'action\s+Return\s*\(')
        
        write_discovery_log("\n[SCREEN DISCOVERY] Scanning for screens with imagebutton...")
        
        def unescape_text(text):
            """Удаляет экранирование из текста."""
            if text is None:
                return None
            text = text.replace('\\"', '"').replace("\\'", "'")
            text = text.replace('\\n', '\n').replace('\\t', '\t')
            return text
        
        for filepath in rpy_files:
            content = read_file_text(filepath)
            if content is None: continue
            lines = content.splitlines()
            
            for i, line in enumerate(lines):
                screen_match = screen_pattern.match(line.strip())
                if screen_match:
                    screen_name = screen_match.group(1)
                    screen_indent = len(line) - len(line.lstrip())
                    buttons = []
                    
                    current_button_action = None  # {'type': 'jump'|'return', 'target': label_name|None}
                    current_button_text = None
                    
                    for j in range(i + 1, len(lines)):
                        stripped = lines[j].strip()
                        if not stripped: continue
                        leading_spaces = len(lines[j]) - len(lines[j].lstrip())
                        
                        if leading_spaces <= screen_indent and stripped:
                            break
                        
                        # Ищем imagebutton с action
                        # Сначала проверяем Jump/Call
                        jump_match = jump_call_pattern.search(stripped)
                        if jump_match:
                            current_button_action = {
                                'type': 'jump',
                                'target': jump_match.group(1)
                            }
                        else:
                            # Проверяем Return
                            return_match = return_pattern.search(stripped)
                            if return_match:
                                current_button_action = {
                                    'type': 'return',
                                    'target': None
                                }
                        
                        # Ищем text с поддержкой экранированных кавычек
                        text_match = text_pattern.search(stripped)
                        if text_match:
                            raw_text = text_match.group(1) if text_match.group(1) is not None else text_match.group(2)
                            current_button_text = unescape_text(raw_text)
                        
                        # Если нашли и текст, и action — связываем
                        if current_button_text and current_button_action:
                            changes = []
                            jump_target = ""
                            
                            if current_button_action['type'] == 'jump' and current_button_action['target']:
                                jump_target = current_button_action['target']
                                changes = label_changes.get(jump_target, [])
                            elif current_button_action['type'] == 'return':
                                jump_target = "__return__"
                                changes = []
                            
                            buttons.append({
                                'text': current_button_text,
                                'jump': jump_target,
                                'action_type': current_button_action['type'],
                                'changes': changes
                            })
                            current_button_text = None
                            current_button_action = None
                    
                    if buttons:
                        screen_choices[screen_name] = buttons
                        write_discovery_log("  [+] Screen '{}': {} buttons found".format(screen_name, len(buttons)))
        
        write_discovery_log("[SCREEN DISCOVERY] Finished. Found {} screens with choices.".format(len(screen_choices)))
        return screen_choices

    # =========================================================================
    # INITIALIZATION & CONFIG LOADING (вызывается после определения всех функций)
    # =========================================================================
    if os.path.exists(CONFIG_PATH):
        write_discovery_log("\n[INIT] Config file found at {}. Loading...".format(CONFIG_PATH))
        try:
            content = read_file_text(CONFIG_PATH)
            if content:
                config_data = json.loads(content)
                MENU_VARIABLE_NAMES = config_data.get("variables", {})
                FUNCTION_PARSER_PATTERNS = config_data.get("patterns", {})
                LABEL_CHANGES = config_data.get("label_changes", {})
                SCREEN_CHOICES = config_data.get("screen_choices", {})
                write_discovery_log("[INIT] Loaded {} variables, {} patterns, {} labels, {} screens from JSON.".format(
                    len(MENU_VARIABLE_NAMES), len(FUNCTION_PARSER_PATTERNS), len(LABEL_CHANGES), len(SCREEN_CHOICES)))
        except Exception as e:
            write_discovery_log("[INIT] Error loading JSON: {}. Falling back to auto-discovery.".format(e))
            os.remove(CONFIG_PATH)

    if not MENU_VARIABLE_NAMES:
        write_discovery_log("\n[INIT] No config found or empty. Starting full auto-discovery...")
        
        all_files = get_all_rpy_files()
        write_discovery_log("[INIT] Found {} .rpy files to scan.".format(len(all_files)))
        
        discovered_vars = discover_global_variables(all_files)
        for var_name in discovered_vars:
            MENU_VARIABLE_NAMES[var_name] = var_name
        
        if DISCOVER_USED_VARIABLES:
            used_vars = discover_used_variables(all_files)
            for var_name in used_vars:
                if var_name not in MENU_VARIABLE_NAMES:
                    MENU_VARIABLE_NAMES[var_name] = var_name
            
        discovered_patterns = discover_function_patterns(all_files, discovered_vars)
        FUNCTION_PARSER_PATTERNS.update(discovered_patterns)
        
        label_changes = discover_label_changes(all_files)
        LABEL_CHANGES.update(label_changes)
        
        screen_choices = discover_screen_choices(all_files, label_changes)
        SCREEN_CHOICES.update(screen_choices)
        
        write_discovery_log("\n[INIT] Saving discovered config to {}...".format(CONFIG_PATH))
        try:
            save_data = {
                "variables": MENU_VARIABLE_NAMES,
                "patterns": FUNCTION_PARSER_PATTERNS,
                "label_changes": LABEL_CHANGES,
                "screen_choices": SCREEN_CHOICES
            }
            json_str = json.dumps(save_data, indent=4, ensure_ascii=False)
            write_file_text(CONFIG_PATH, json_str)
            write_discovery_log("[INIT] Config saved successfully!")
        except Exception as e:
            write_discovery_log("[INIT] Error saving JSON: {}".format(e))

    write_discovery_log("="*50)
    write_discovery_log("AUTO-DISCOVERY SESSION FINISHED")
    write_discovery_log("="*50 + "\n")

    # =========================================================================
    # EXPORT TO RENPY STORE
    # =========================================================================
    renpy.store.MENU_VARIABLE_NAMES = MENU_VARIABLE_NAMES
    renpy.store.SCREEN_CHOICES = SCREEN_CHOICES
    renpy.store.DEBUG_MODE = DEBUG_MODE
    renpy.store.FONT_SIZE_MODIFIER = FONT_SIZE_MODIFIER

    # =========================================================================
    # CHEAT VARIABLE MANIPULATION
    # =========================================================================
    def cheat_change_var(var_name, val):
        current_val = getattr(renpy.store, var_name, 0)
        try: setattr(renpy.store, var_name, current_val + int(val))
        except: pass
        renpy.restart_interaction()

    def cheat_set_var(var_name, val_str):
        try: setattr(renpy.store, var_name, int(val_str))
        except: pass
        renpy.store.cheat_input_value = ""
        renpy.restart_interaction()

    renpy.store.cheat_change_var = cheat_change_var
    renpy.store.cheat_set_var = cheat_set_var

    # =========================================================================
    # CACHING
    # =========================================================================
    _file_cache = {}
    _cache_timestamps = {}
    _menu_parse_cache = {}

    def get_file_content(filepath):
        try:
            file_mtime = os.path.getmtime(filepath)
            if filepath in _file_cache and _cache_timestamps.get(filepath) == file_mtime:
                return _file_cache[filepath]
            content = read_file_text(filepath)
            if content is None: return None
            lines = content.splitlines()
            _file_cache[filepath] = lines
            _cache_timestamps[filepath] = file_mtime
            return lines
        except: return None

    def get_parsed_menu(filepath, menu_idx, lines):
        cache_key = "{}:{}".format(filepath, menu_idx)
        if cache_key in _menu_parse_cache: return _menu_parse_cache[cache_key]
        
        menu_indent = len(lines[menu_idx]) - len(lines[menu_idx].lstrip())
        current_blocks, current_choice, choice_indent = {}, None, None
        for i in range(menu_idx + 1, len(lines)):
            line, stripped = lines[i], lines[i].strip()
            if not stripped: continue
            leading_spaces = len(line) - len(line.lstrip())
            if leading_spaces <= menu_indent and stripped: break
            match_choice = CHOICE_PATTERN.search(stripped)
            if match_choice:
                if choice_indent is None: choice_indent = leading_spaces
                if leading_spaces == choice_indent:
                    current_choice = match_choice.group(1) if match_choice.group(1) else match_choice.group(2)
                    current_blocks[current_choice] = []
                    continue
            if current_choice and leading_spaces > choice_indent:
                current_blocks[current_choice].append(line)
        _menu_parse_cache[cache_key] = current_blocks
        return current_blocks

    # =========================================================================
    # MAIN MENU PARSER
    # =========================================================================
    def core_menu_parser(caption_clean):
        filename, _ = renpy.get_filename_line()
        if not filename: return caption_clean
        if filename.startswith("game/"): filename = filename[5:]
        elif filename.startswith("game\\"): filename = filename[5:]

        try:
            filepath = os.path.join(config.gamedir, filename)
            lines = get_file_content(filepath)
            if not lines: 
                write_cheat_log("ERROR: Could not load file: {}".format(filepath))
                return caption_clean

            lookup_caption = normalize_text(caption_clean)
            write_cheat_log("DEBUG: Looking for caption: '{}'".format(lookup_caption))
            
            menu_locations = [i for i, line in enumerate(lines) if not line.strip().startswith(('old', 'new')) and line.strip().split('#')[0].strip().startswith('menu') and ':' in line]
            if not menu_locations: 
                write_cheat_log("DEBUG: No menu: found in file")
                return caption_clean

            target_menu_idx, menu_blocks, original_key = -1, {}, None
            
            for menu_idx in menu_locations:
                current_blocks = get_parsed_menu(filepath, menu_idx, lines)
                for ct in current_blocks.keys():
                    ct_normalized = normalize_text(ct)
                    write_cheat_log("DEBUG: Comparing '{}' with '{}'".format(lookup_caption, ct_normalized))
                    if lookup_caption == ct_normalized or lookup_caption in ct_normalized or ct_normalized in lookup_caption:
                        target_menu_idx = menu_idx
                        menu_blocks = current_blocks
                        original_key = ct
                        write_cheat_log("DEBUG: Found menu at line {} with {} variants".format(menu_idx, len(current_blocks)))
                        break
                if target_menu_idx != -1:
                    break
                    
            if target_menu_idx == -1: 
                write_cheat_log("DEBUG: Caption '{}' not found in any menu".format(lookup_caption))
                return caption_clean

            var_changes = {}
            if original_key and original_key in menu_blocks:
                write_cheat_log("DEBUG: Processing {} code lines for '{}'".format(len(menu_blocks[original_key]), original_key))
                for code_line in menu_blocks[original_key]:
                    stripped_line = code_line.strip()
                    if not stripped_line.startswith('$') and '=' not in stripped_line: continue
                    if "if " in stripped_line or "==" in stripped_line: continue

                    var_name, modifier, value = None, None, None
                    func_res = parse_function_call_args(stripped_line)
                    if func_res: 
                        var_name, modifier, value = func_res
                        write_cheat_log("DEBUG: Function call parsed: {} {} {}".format(var_name, modifier, value))
                    else:
                        match_calc = CALC_PATTERN.search(stripped_line)
                        if match_calc:
                            var_name, modifier, value = match_calc.group(1), match_calc.group(2), match_calc.group(3)
                            if value.endswith('.0'): value = value[:-2]
                            write_cheat_log("DEBUG: Regex parsed: {} {} {}".format(var_name, modifier, value))

                    if var_name:
                        if modifier == '': op_str = " = "
                        elif modifier == '+': op_str = " +="
                        elif modifier == '-': op_str = " -="
                        else: op_str = " {}=".format(modifier)
                        
                        if var_name in MENU_VARIABLE_NAMES:
                            disp_name = MENU_VARIABLE_NAMES[var_name]
                            if modifier == '':
                                color = COLOR_EQUAL
                            elif modifier == '+':
                                color = COLOR_PLUS
                            else:
                                color = COLOR_MINUS
                        elif DEBUG_MODE: 
                            disp_name = "DEBUG:" + var_name
                            color = COLOR_DEBUG
                        else: continue
                        
                        if var_name not in var_changes: var_changes[var_name] = []
                        var_changes[var_name].append(("{}{}{}".format(disp_name, op_str, value), color))

            found_changes = ["{{color={0}}}{1}{{/color}}".format(c, s) for changes in var_changes.values() for s, c in changes]
            
            if found_changes:
                try:
                    trans_cap = renpy.substitute(caption_clean)
                    if not trans_cap or trans_cap == caption_clean: trans_cap = caption_clean
                except: trans_cap = caption_clean
                result = "{} {{size={}}}({}){{/size}}".format(trans_cap, FONT_SIZE_MODIFIER, ', '.join(found_changes))
                write_cheat_log("SUCCESS: {}".format(result))
                return result
            return caption_clean
        except Exception as e:
            write_cheat_log("PARSER ERROR: {}".format(e))
            import traceback
            write_cheat_log(traceback.format_exc())
            return caption_clean

     # =========================================================================
    # SCREEN TRACKING
    # =========================================================================
    _current_choice_screen = None  # Только один активный screen с выборами
    _original_show_screen = renpy.show_screen
    _original_hide_screen = renpy.hide_screen
    
    def tracked_show_screen(name, *args, **kwargs):
        """Перехватывает show_screen для отслеживания активного screen'а с выборами."""
        global _current_choice_screen
        # Если показывается screen с выборами, запоминаем его
        if name in SCREEN_CHOICES:
            _current_choice_screen = name
        return _original_show_screen(name, *args, **kwargs)
    
    def tracked_hide_screen(name, *args, **kwargs):
        """Перехватывает hide_screen для очистки активного screen'а."""
        global _current_choice_screen
        # Если скрывается текущий screen с выборами, очищаем
        if name == _current_choice_screen:
            _current_choice_screen = None
        return _original_hide_screen(name, *args, **kwargs)
    
    renpy.show_screen = tracked_show_screen
    renpy.hide_screen = tracked_hide_screen

    # =========================================================================
    # IMAGEBUTTON OVERLAY SYSTEM
    # =========================================================================
    def create_imagebutton_overlay(screen_name):
        """Создаёт overlay с подсказками для imagebutton'ов."""
        if screen_name not in SCREEN_CHOICES:
            return
        
        choices = SCREEN_CHOICES[screen_name]
        if not choices:
            return
        
        # Создаём универсальный overlay
        overlay_id = "imagebutton_overlay"
        
        try:
            renpy.hide_screen(overlay_id)
        except:
            pass
        
        renpy.show_screen(overlay_id, screen_name=screen_name, choices=choices)

    def imagebutton_overlay_tracker():
        """Отслеживает активные screen'ы и создаёт overlay'и."""
        global _current_choice_screen
        
        if not _current_choice_screen or _current_choice_screen not in SCREEN_CHOICES:
            return
        
        try:
            create_imagebutton_overlay(_current_choice_screen)
        except Exception as e:
            write_cheat_log("IMAGEBUTTON OVERLAY ERROR: {}".format(e))

    config.overlay_functions.append(imagebutton_overlay_tracker)
    # =========================================================================
    # SCREEN CHOICE OVERLAY
    # =========================================================================
    def screen_choice_indicator():
        """Показывает индикатор на экране с imagebutton."""
        if not SCREEN_CHOICES or not _current_choice_screen:
            return
        
        try:
            # Скрываем предыдущий индикатор, если есть
            if renpy.get_screen("screen_choice_indicator"):
                renpy.hide_screen("screen_choice_indicator")
            
            # Показываем индикатор только для текущего screen'а
            if renpy.has_screen("screen_choice_indicator"):
                renpy.show_screen("screen_choice_indicator", screens=[_current_choice_screen])
        except:
            pass

    config.overlay_functions.append(screen_choice_indicator)

    # =========================================================================
    # MENU PROXY & UI
    # =========================================================================
    def custom_cheat_menu_proxy(items, interact=True, screen="choice"):
        patched = []
        for item in items:
            if isinstance(item, tuple) and len(item) >= 2:
                patched.append((core_menu_parser(item[0]),) + item[1:])
            elif hasattr(item, "caption"):
                item.caption = core_menu_parser(item.caption)
                patched.append(item)
            else: patched.append(item)
        return renpy.display_menu(patched, interact=interact, screen=screen)

    menu = custom_cheat_menu_proxy

    def force_continuous_cheat_button():
        try:
            if not renpy.get_screen("cheat_manager_overlay"):
                if renpy.has_screen("cheat_launcher_btn"):
                    renpy.show_screen("cheat_launcher_btn")
        except:
            pass
    config.overlay_functions.append(force_continuous_cheat_button)