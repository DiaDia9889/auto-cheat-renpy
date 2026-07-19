init python:
    import re
    import os
    import ast
    import sys
    import json
    import struct
    import pickle
    import zlib
    import subprocess

    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    DEBUG_MODE = True
    DISCOVER_USED_VARIABLES = False
    FONT_SIZE_MODIFIER = -4
    DECOMPILE_RPYC = True  # Включить декомпиляцию .rpyc файлов

    UNRPYC_PATH = os.environ.get('UNRPYC_PATH', None)
    UNRPA_PATH = os.environ.get('UNRPA_PATH', None)

    # Пакеты для установки через pip
    PIP_PACKAGES = ['unrpa', 'unrpyc']

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
    # COMPILED REGEX
    # =========================================================================
    CHOICE_PATTERN = re.compile(r'(?:"([^"]+)"|\'([^\']+)\')\s*(?:if\s+[^:]+)?\s*:')
    CALC_PATTERN = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*([\+\-]?)=\s*([0-9\.]+)')
    TAG_PATTERN = re.compile(r'\{[^}]*\}')

    # =========================================================================
    # PIP AUTO-INSTALLATION
    # =========================================================================
    def _get_python_candidates():
        """Возвращает список возможных команд Python в зависимости от ОС."""
        if sys.platform == 'win32':
            return [
                ['py', '-3'],      # Windows py launcher (предпочтительный)
                ['python'],
                ['python3'],
            ]
        else:
            return [
                ['python3'],
                ['python'],
            ]

    def find_working_python_cmd():
        """Находит первую рабочую команду Python через системный PATH.
        
        Возвращает список аргументов (например ['python3'] или ['py', '-3'])
        или None если ничего не найдено.
        """
        cache_attr = '_working_python_cmd'
        if hasattr(find_working_python_cmd, cache_attr):
            return getattr(find_working_python_cmd, cache_attr)
        
        for candidate in _get_python_candidates():
            try:
                result = subprocess.run(
                    candidate + ['--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    version = (result.stdout.strip() or result.stderr.strip())
                    write_discovery_log("[PYTHON] Working command: {} ({})".format(' '.join(candidate), version))
                    setattr(find_working_python_cmd, cache_attr, candidate)
                    return candidate
            except Exception as e:
                write_discovery_log("[PYTHON] {} failed: {}".format(' '.join(candidate), e))
                continue
        
        write_discovery_log("[PYTHON] No working python command found in PATH")
        setattr(find_working_python_cmd, cache_attr, None)
        return None

    def check_pip_available():
        """Проверяет наличие pip через системный PATH."""
        python_cmd = find_working_python_cmd()
        if not python_cmd:
            write_discovery_log("[PIP] No python command available")
            return False
        
        try:
            result = subprocess.run(
                python_cmd + ['-m', 'pip', '--version'],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                write_discovery_log("[PIP] pip available: {}".format(result.stdout.strip()))
                return True
            else:
                write_discovery_log("[PIP] pip check failed: {}".format(result.stderr.strip()[:200]))
                return False
        except subprocess.TimeoutExpired:
            write_discovery_log("[PIP] pip check timeout")
            return False
        except Exception as e:
            write_discovery_log("[PIP] Cannot check pip: {}".format(e))
            return False

    def install_packages_via_pip(packages):
        """Устанавливает пакеты через pip, используя системный PATH."""
        if not packages:
            return True
        
        python_cmd = find_working_python_cmd()
        if not python_cmd:
            write_discovery_log("[PIP] Cannot install: no python command")
            return False
        
        write_discovery_log("[PIP] Installing via {}: {}".format(' '.join(python_cmd), ', '.join(packages)))
        
        try:
            cmd = python_cmd + ['-m', 'pip', 'install', '--upgrade', '--no-warn-script-location'] + packages
            write_discovery_log("[PIP] Command: {}".format(' '.join(cmd)))
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                write_discovery_log("[PIP] Installation successful!")
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-5:]:
                        write_discovery_log("[PIP] " + line)
                return True
            else:
                write_discovery_log("[PIP] Installation failed (code {}):".format(result.returncode))
                if result.stderr:
                    write_discovery_log("[PIP] " + result.stderr[:500])
                return False
        
        except subprocess.TimeoutExpired:
            write_discovery_log("[PIP] Installation timeout (300s)")
            return False
        except Exception as e:
            write_discovery_log("[PIP] Error during installation: {}".format(e))
            return False

    def _cmd_available(cmd):
        """Проверяет, доступна ли команда через PATH."""
        try:
            result = subprocess.run(
                cmd + ['--help'],
                capture_output=True,
                text=True,
                timeout=15
            )
            # returncode 0 или наличие 'usage' в выводе = команда работает
            return result.returncode == 0 or 'usage' in (result.stdout + result.stderr).lower()
        except Exception:
            return False

    def find_installed_package(package_name):
        """Универсальный поиск установленного пакета через PATH.
        
        Проверяет два способа вызова:
        1. Команда напрямую: {package_name} --help
        2. Через python: python -m {package_name} --help
        
        Args:
            package_name: Имя пакета ('unrpa' или 'unrpyc')
            
        Returns:
            - '{package_name}' если доступна команда напрямую
            - '__python_module__' если доступен через python -m
            - None если ничего не найдено
        """
        pkg_upper = package_name.upper()
        
        # 1. Проверяем команду напрямую через PATH
        try:
            result = subprocess.run(
                [package_name, '--help'],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0 or 'usage' in (result.stdout + result.stderr).lower():
                write_discovery_log("[{}] Found {} in system PATH".format(pkg_upper, package_name))
                return package_name
        except Exception:
            pass
        
        # 2. Проверяем через python -m
        python_cmd = find_working_python_cmd()
        if python_cmd:
            try:
                result = subprocess.run(
                    python_cmd + ['-m', package_name, '--help'],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                if result.returncode == 0 or 'usage' in (result.stdout + result.stderr).lower():
                    write_discovery_log("[{}] {} available via {} -m {}".format(
                        pkg_upper, package_name, ' '.join(python_cmd), package_name))
                    return '__python_module__'
            except Exception:
                pass
        
        return None

    def find_installed_unrpa():
        """Ищет unrpa через системный PATH."""
        return find_installed_package('unrpa')

    def find_installed_unrpyc():
        """Ищет unrpyc через системный PATH."""
        return find_installed_package('unrpyc')

    def ensure_tools_installed():
        """Главная функция: обеспечивает наличие unrpa и unrpyc.
        
        Логика:
        1. Проверяет UNRPA_PATH и UNRPYC_PATH из env/констант
        2. Ищет утилиты в стандартных локациях
        3. Если не найдено — пытается установить через pip
        4. Если pip недоступен — выводит инструкции
        
        Возвращает кортеж (unrpa_path, unrpyc_path)
        """
        global UNRPA_PATH, UNRPYC_PATH
        
        unrpa_found = None
        unrpyc_found = None
        
        # 1. Проверяем env/константы
        if UNRPA_PATH and os.path.exists(UNRPA_PATH):
            write_discovery_log("[TOOLS] Using UNRPA_PATH: {}".format(UNRPA_PATH))
            unrpa_found = UNRPA_PATH
        
        if UNRPYC_PATH and os.path.exists(UNRPYC_PATH):
            write_discovery_log("[TOOLS] Using UNRPYC_PATH: {}".format(UNRPYC_PATH))
            unrpyc_found = UNRPYC_PATH
        
        # 2. Автопоиск в стандартных локациях
        if not unrpa_found:
            unrpa_found = find_unrpa()
        
        if not unrpyc_found:
            unrpyc_found = find_unrpyc()
        
        # 3. Если что-то не найдено — пытаемся установить через pip
        missing_tools = []
        if not unrpa_found:
            missing_tools.append('unrpa')
        if not unrpyc_found:
            missing_tools.append('unrpyc')
        
        if missing_tools:
            write_discovery_log("[TOOLS] Missing: {}".format(', '.join(missing_tools)))
            
            # Проверяем pip
            if not check_pip_available():
                write_discovery_log("[TOOLS] " + "="*60)
                write_discovery_log("[TOOLS] ERROR: pip is not available!")
                write_discovery_log("[TOOLS] Cannot auto-install unrpa/unrpyc.")
                write_discovery_log("[TOOLS] ")
                write_discovery_log("[TOOLS] To install required tools manually:")
                write_discovery_log("[TOOLS] ")
                write_discovery_log("[TOOLS] 1. Install Python 3 from https://www.python.org/downloads/")
                write_discovery_log("[TOOLS] 2. IMPORTANT: Check 'Add Python to PATH' during installation")
                write_discovery_log("[TOOLS] 3. Open CMD/PowerShell and run:")
                write_discovery_log("[TOOLS]      pip install unrpa unrpyc")
                write_discovery_log("[TOOLS] ")
                write_discovery_log("[TOOLS] Or download manually:")
                write_discovery_log("[TOOLS]   unrpa:   https://github.com/Lattyware/unrpa")
                write_discovery_log("[TOOLS]   unrpyc:  https://github.com/CensoredUsername/unrpyc")
                write_discovery_log("[TOOLS] ")
                write_discovery_log("[TOOLS] Or set UNRPA_PATH and UNRPYC_PATH in environment variables")
                write_discovery_log("[TOOLS] " + "="*60)
                return (unrpa_found, unrpyc_found)
            
            # Пытаемся установить недостающие пакеты
            write_discovery_log("[TOOLS] Attempting to install missing packages via pip...")
            
            if install_packages_via_pip(PIP_PACKAGES):
                write_discovery_log("[TOOLS] Packages installed, searching again...")
                
                # Повторный поиск после установки
                if not unrpa_found:
                    unrpa_found = find_installed_unrpa()
                
                if not unrpyc_found:
                    unrpyc_found = find_installed_unrpyc()
            else:
                write_discovery_log("[TOOLS] pip installation failed. Tools still missing.")
        
        # 4. Финальный отчёт
        if unrpa_found:
            write_discovery_log("[TOOLS] ✓ unrpa: {}".format(unrpa_found))
        else:
            write_discovery_log("[TOOLS] ✗ unrpa: NOT FOUND")
        
        if unrpyc_found:
            write_discovery_log("[TOOLS] ✓ unrpyc: {}".format(unrpyc_found))
        else:
            write_discovery_log("[TOOLS] ✗ unrpyc: NOT FOUND")
        
        return (unrpa_found, unrpyc_found)

    # =========================================================================
    # UNRPA EXTERNAL TOOL INTEGRATION
    # =========================================================================
    def find_unrpa():
        """Ищет CLI-утилиту unrpa в стандартных локациях.
        
        Возвращает полный путь к unrpa или None.
        """
        global UNRPA_PATH
        
        if UNRPA_PATH and os.path.exists(UNRPA_PATH):
            return UNRPA_PATH
        
        base_dir = os.path.dirname(config.gamedir)
        
        search_paths = [
            os.path.join(base_dir, 'unrpa.py'),
            os.path.join(base_dir, 'unrpa', 'unrpa.py'),
            os.path.join(base_dir, 'unrpa', 'src', 'unrpa.py'),
            os.path.join(base_dir, 'tools', 'unrpa.py'),
            os.path.join(base_dir, 'tools', 'unrpa', 'unrpa.py'),
        ]
        
        if sys.platform == 'win32':
            search_paths.extend([
                os.path.join(base_dir, 'unrpa.bat'),
                os.path.join(base_dir, 'unrpa', 'unrpa.bat'),
            ])
        else:
            search_paths.extend([
                os.path.join(base_dir, 'unrpa.sh'),
                os.path.join(base_dir, 'unrpa', 'unrpa.sh'),
            ])
        
        for path in search_paths:
            if os.path.exists(path):
                write_discovery_log("[UNRPA] Found unrpa CLI at: {}".format(path))
                UNRPA_PATH = path
                return path
        
        return None
    # =========================================================================
    # UNRPYC EXTERNAL TOOL INTEGRATION
    # =========================================================================
    def find_unrpyc():
        """Ищет утилиту unrpyc в стандартных локациях.
        
        Возвращает полный путь к unrpyc или None.
        """
        global UNRPYC_PATH
        
        if UNRPYC_PATH and os.path.exists(UNRPYC_PATH):
            return UNRPYC_PATH
        
        base_dir = os.path.dirname(config.gamedir)
        
        search_paths = [
            os.path.join(base_dir, 'unrpyc.py'),
            os.path.join(base_dir, 'unrpyc', 'unrpyc.py'),
            os.path.join(base_dir, 'unrpyc', 'src', 'unrpyc.py'),
            os.path.join(base_dir, 'tools', 'unrpyc.py'),
            os.path.join(base_dir, 'tools', 'unrpyc', 'unrpyc.py'),
        ]
        
        if sys.platform == 'win32':
            search_paths.extend([
                os.path.join(base_dir, 'unrpyc.bat'),
                os.path.join(base_dir, 'unrpyc', 'unrpyc.bat'),
            ])
        else:
            search_paths.extend([
                os.path.join(base_dir, 'unrpyc.sh'),
                os.path.join(base_dir, 'unrpyc', 'unrpyc.sh'),
            ])
        
        for path in search_paths:
            if os.path.exists(path):
                write_discovery_log("[UNRPYC] Found unrpyc at: {}".format(path))
                UNRPYC_PATH = path
                return path
        
        return None


    def build_unrpa_cmd(unrpa_path, extra_args):
        """Строит команду для запуска unrpa."""
        if unrpa_path == 'unrpa':
            # Команда из PATH
            return ['unrpa'] + extra_args
        elif unrpa_path == '__python_module__':
            python_cmd = find_working_python_cmd()
            return python_cmd + ['-m', 'unrpa'] + extra_args
        elif unrpa_path.endswith('.py'):
            return [sys.executable, unrpa_path] + extra_args
        else:
            return [unrpa_path] + extra_args

    def decompile_rpyc_external(rpyc_path, unrpyc_path=None):
        """Декомпилирует .rpyc файл используя unrpyc."""
        if not unrpyc_path:
            return False
        
        rpy_path = rpyc_path[:-1]  # .rpyc -> .rpy
        
        try:
            # Определяем команду
            if unrpyc_path == 'unrpyc':
                cmd = ['unrpyc', rpyc_path]
            elif unrpyc_path == '__python_module__':
                python_cmd = find_working_python_cmd()
                cmd = python_cmd + ['-m', 'unrpyc', rpyc_path]
            elif unrpyc_path.endswith('.py'):
                cmd = [sys.executable, unrpyc_path, rpyc_path]
            else:
                cmd = [unrpyc_path, rpyc_path]
            
            write_discovery_log("[RPYC] Decompiling: {} -> {}".format(
                os.path.basename(rpyc_path), os.path.basename(rpy_path)))
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                if os.path.exists(rpy_path):
                    write_discovery_log("[RPYC] Successfully decompiled: {}".format(os.path.basename(rpy_path)))
                    return True
                else:
                    write_discovery_log("[RPYC] unrpyc completed but .rpy not created")
                    return False
            else:
                write_discovery_log("[RPYC] unrpyc failed (code {}): {}".format(
                    result.returncode, result.stderr[:200]))
                return False
        
        except subprocess.TimeoutExpired:
            write_discovery_log("[RPYC] Decompilation timeout: {}".format(os.path.basename(rpyc_path)))
            return False
        except Exception as e:
            write_discovery_log("[RPYC] Error: {}".format(e))
            return False
    # =========================================================================
    # RPA ARCHIVE EXTRACTION (with external decompilation)
    # =========================================================================
    def extract_rpa_scripts_only():
        """Извлекает скрипты из .rpa архивов используя CLI-утилиту unrpa."""
        extracted_count = 0
        skipped_count = 0
        decompiled_count = 0
        
        unrpa_path, unrpyc_path = ensure_tools_installed()
        
        if not unrpa_path:
            write_discovery_log("[RPA] Cannot extract .rpa archives without unrpa")
            return 0
        
        if not unrpyc_path:
            write_discovery_log("[INIT] unrpyc not available - .rpyc files will not be decompiled")
                
        # Проходим по всем .rpa архивам
        for root, dirs, files in os.walk(config.gamedir):
            if 'tl' in root or 'cache' in root:
                continue
            
            for file in files:
                if not file.endswith('.rpa'):
                    continue
                    
                rpa_path = os.path.join(root, file)
                write_discovery_log("[RPA] Processing archive: {}".format(file))
                
                # ============================================================
                # ШАГ 1: Получаем список файлов через unrpa -l (list)
                # ============================================================
                file_list_output = None
                
                try:
                    cmd = build_unrpa_cmd(unrpa_path, ['-l', rpa_path])
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        file_list_output = result.stdout
                    else:
                        write_discovery_log("[RPA] unrpa -l failed (code {}): {}".format(result.returncode, result.stderr[:200]))
                        # Fallback на --list
                        cmd = build_unrpa_cmd(unrpa_path, ['--list', rpa_path])
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            file_list_output = result.stdout
                        else:
                            continue
                
                except Exception as e:
                    write_discovery_log("[RPA] Error running unrpa list: {}".format(e))
                    continue
                
                # ============================================================
                # ШАГ 2: Проверяем наличие .rpy/.rpyc файлов
                # ============================================================
                script_files = []
                
                if file_list_output:
                    for line in file_list_output.strip().split('\n'):
                        line = line.strip()
                        if not line: 
                            continue
                        
                        # В выводе может быть просто путь или путь с доп. инфо
                        if line.endswith('.rpy') or line.endswith('.rpyc'):
                            script_files.append(line)
                        elif ' ' in line:
                            parts = line.split()
                            if parts[-1].endswith('.rpy') or parts[-1].endswith('.rpyc'):
                                script_files.append(parts[-1])
                
                if not script_files:
                    write_discovery_log("[RPA] No .rpy/.rpyc files in {}, skipping".format(file))
                    continue
                
                write_discovery_log("[RPA] Found {} script files in {}".format(len(script_files), file))
                
                # ============================================================
                # ШАГ 3: Распаковываем архив во временную директорию
                # ============================================================
                temp_extract_dir = os.path.join(config.gamedir, '_temp_rpa_extract_' + file.replace('.rpa', ''))
                
                try:
                    if os.path.exists(temp_extract_dir):
                        import shutil
                        shutil.rmtree(temp_extract_dir, ignore_errors=True)
                    os.makedirs(temp_extract_dir, exist_ok=True)
                    
                    write_discovery_log("[RPA] Extracting {} to temporary directory...".format(file))
                    
                    # unrpa извлекает весь архив, поэтому используем временную папку
                    cmd = build_unrpa_cmd(unrpa_path, ['-mp', temp_extract_dir, rpa_path])
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode != 0:
                        write_discovery_log("[RPA] unrpa extraction failed: {}".format(result.stderr[:200]))
                        import shutil
                        shutil.rmtree(temp_extract_dir, ignore_errors=True)
                        continue
                    
                    write_discovery_log("[RPA] Extraction completed, filtering scripts...")
                    
                    # ============================================================
                    # ШАГ 4: Копируем только .rpy и .rpyc файлы в game/
                    # ============================================================
                    for temp_root, temp_dirs, temp_files in os.walk(temp_extract_dir):
                        for temp_file in temp_files:
                            if not (temp_file.endswith('.rpy') or temp_file.endswith('.rpyc')):
                                continue
                            
                            temp_path = os.path.join(temp_root, temp_file)
                            rel_path = os.path.relpath(temp_path, temp_extract_dir)
                            target_path = os.path.join(config.gamedir, rel_path)
                            
                            if os.path.exists(target_path):
                                skipped_count += 1
                                continue
                            
                            target_dir = os.path.dirname(target_path)
                            if target_dir:
                                os.makedirs(target_dir, exist_ok=True)
                            
                            try:
                                with open(temp_path, 'rb') as src:
                                    with open(target_path, 'wb') as dst:
                                        dst.write(src.read())
                                
                                size = os.path.getsize(target_path)
                                write_discovery_log("[RPA] Extracted: {} ({} bytes)".format(rel_path, size))
                                extracted_count += 1
                                
                                if temp_file.endswith('.rpyc') and DECOMPILE_RPYC and unrpyc_path:
                                    if decompile_rpyc_external(target_path, unrpyc_path):
                                        decompiled_count += 1
                            except Exception as e:
                                write_discovery_log("[RPA] Error copying {}: {}".format(rel_path, e))
                    
                    # Удаляем временную директорию
                    import shutil
                    shutil.rmtree(temp_extract_dir, ignore_errors=True)
                    write_discovery_log("[RPA] Archive {} processed".format(file))
                
                except Exception as e:
                    write_discovery_log("[RPA] Error processing {}: {}".format(file, e))
                    import shutil
                    if os.path.exists(temp_extract_dir):
                        shutil.rmtree(temp_extract_dir, ignore_errors=True)
        
        write_discovery_log("[RPA] Total: extracted {} scripts, skipped {}, decompiled {}".format(
            extracted_count, skipped_count, decompiled_count))
        
        return extracted_count

    # =========================================================================
    # AUTO-DISCOVERY FUNCTIONS
    # =========================================================================
    def get_all_rpy_files():
        """Собирает все .rpy файлы в game/ (включая распакованные и декомпилированные)."""
        rpy_files = []
        for root, dirs, files in os.walk(config.gamedir):
            if 'tl' in root or 'cache' in root:
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
        discovered_vars = {}
        assignment_pattern = re.compile(r'^\s*\$\s*([a-zA-Z_]\w*)\s*[\+\-]?=\s*', re.MULTILINE)
        
        write_discovery_log("\n[USED VAR DISCOVERY] Scanning for variables used in assignments...")
        
        for filepath in rpy_files:
            content = read_file_text(filepath)
            if content is None: continue
            
            matches = assignment_pattern.findall(content)
            for var_name in matches:
                if var_name not in discovered_vars:
                    discovered_vars[var_name] = 0
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
    # AST FUNCTION CALL PARSER
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
        text = text.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", '"').replace(u"\u201d", '"').replace(u"\u2013", "-").replace(u"\u2014", "-")
        return text.strip()

    # =========================================================================
    # DISCOVER LABEL CHANGES
    # =========================================================================
    def discover_label_changes(rpy_files):
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
                    
                    in_if_block = False
                    if_indent = None
                    
                    for j in range(i + 1, min(i + 31, len(lines))):
                        stripped = lines[j].strip()
                        if not stripped: continue
                        leading_spaces = len(lines[j]) - len(lines[j].lstrip())
                        
                        if leading_spaces <= label_indent and stripped:
                            break
                        
                        if in_if_block and leading_spaces <= if_indent:
                            in_if_block = False
                            if_indent = None
                        
                        if stripped.startswith('if ') or stripped.startswith('elif '):
                            in_if_block = True
                            if_indent = leading_spaces
                            continue
                        
                        if in_if_block:
                            continue
                        
                        if stripped.startswith('$') or '=' in stripped:
                            func_res = parse_function_call_args(stripped)
                            if func_res:
                                changes.append(list(func_res))
                            else:
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
        screen_choices = {}
        screen_pattern = re.compile(r'^screen\s+([a-zA-Z_]\w*)\s*\(')
        text_pattern = re.compile(r'text\s+(?:"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\')')
        
        jump_call_pattern = re.compile(r'action\s+(?:Jump|Call)\s*\(\s*["\']([^"\']+)["\']\s*\)')
        return_pattern = re.compile(r'action\s+Return\s*\(')
        
        write_discovery_log("\n[SCREEN DISCOVERY] Scanning for screens with imagebutton...")
        
        def unescape_text(text):
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
                    
                    current_button_action = None
                    current_button_text = None
                    
                    for j in range(i + 1, len(lines)):
                        stripped = lines[j].strip()
                        if not stripped: continue
                        leading_spaces = len(lines[j]) - len(lines[j].lstrip())
                        
                        if leading_spaces <= screen_indent and stripped:
                            break
                        
                        jump_match = jump_call_pattern.search(stripped)
                        if jump_match:
                            current_button_action = {
                                'type': 'jump',
                                'target': jump_match.group(1)
                            }
                        else:
                            return_match = return_pattern.search(stripped)
                            if return_match:
                                current_button_action = {
                                    'type': 'return',
                                    'target': None
                                }
                        
                        text_match = text_pattern.search(stripped)
                        if text_match:
                            raw_text = text_match.group(1) if text_match.group(1) is not None else text_match.group(2)
                            current_button_text = unescape_text(raw_text)
                        
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
    # INITIALIZATION & CONFIG LOADING
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
            try:
                os.remove(CONFIG_PATH)
            except:
                pass

    if not MENU_VARIABLE_NAMES:
        write_discovery_log("\n[INIT] No config found or empty. Starting full auto-discovery...")
        
        # Проверяем количество .rpy файлов
        test_files = get_all_rpy_files()
        
        # Если мало файлов, извлекаем из архивов
        if len(test_files) < 10:
            write_discovery_log("[INIT] Few .rpy files found ({}). Attempting RPA extraction...".format(len(test_files)))
            extracted = extract_rpa_scripts_only()
            if extracted > 0:
                write_discovery_log("[INIT] Extracted {} script files from .rpa archives".format(extracted))
        
        # Сканируем все файлы (включая только что распакованные)
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
        """Читает файл напрямую по пути. Кэширует результат."""
        try:
            if filepath in _file_cache:
                try:
                    file_mtime = os.path.getmtime(filepath)
                    if _cache_timestamps.get(filepath) == file_mtime:
                        return _file_cache[filepath]
                except:
                    return _file_cache[filepath]
            
            content = read_file_text(filepath)
            if content is None:
                return None
            
            lines = content.splitlines()
            _file_cache[filepath] = lines
            
            try:
                _cache_timestamps[filepath] = os.path.getmtime(filepath)
            except:
                pass
            
            return lines
        except:
            return None

    # =========================================================================
    # MAIN MENU PARSER
    # =========================================================================
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
    _current_choice_screen = None
    _original_show_screen = renpy.show_screen
    _original_hide_screen = renpy.hide_screen
    
    def tracked_show_screen(name, *args, **kwargs):
        global _current_choice_screen
        if name in SCREEN_CHOICES:
            _current_choice_screen = name
        return _original_show_screen(name, *args, **kwargs)
    
    def tracked_hide_screen(name, *args, **kwargs):
        global _current_choice_screen
        if name == _current_choice_screen:
            _current_choice_screen = None
        return _original_hide_screen(name, *args, **kwargs)
    
    renpy.show_screen = tracked_show_screen
    renpy.hide_screen = tracked_hide_screen

    # =========================================================================
    # IMAGEBUTTON OVERLAY SYSTEM
    # =========================================================================
    def create_imagebutton_overlay(screen_name):
        if screen_name not in SCREEN_CHOICES:
            return
        
        choices = SCREEN_CHOICES[screen_name]
        if not choices:
            return
        
        overlay_id = "imagebutton_overlay"
        
        try:
            renpy.hide_screen(overlay_id)
        except:
            pass
        
        renpy.show_screen(overlay_id, screen_name=screen_name, choices=choices)

    def imagebutton_overlay_tracker():
        global _current_choice_screen
        
        if not _current_choice_screen:
            try:
                if renpy.get_screen("imagebutton_overlay"):
                    renpy.hide_screen("imagebutton_overlay")
            except:
                pass
            return
        
        if _current_choice_screen not in SCREEN_CHOICES:
            try:
                if renpy.get_screen("imagebutton_overlay"):
                    renpy.hide_screen("imagebutton_overlay")
            except:
                pass
            return
        
        if not renpy.get_screen(_current_choice_screen):
            _current_choice_screen = None
            try:
                if renpy.get_screen("imagebutton_overlay"):
                    renpy.hide_screen("imagebutton_overlay")
            except:
                pass
            return
        
        try:
            choices = SCREEN_CHOICES[_current_choice_screen]
            if choices:
                if not renpy.get_screen("imagebutton_overlay"):
                    renpy.show_screen("imagebutton_overlay", screen_name=_current_choice_screen, choices=choices)
        except Exception as e:
            write_cheat_log("IMAGEBUTTON OVERLAY ERROR: {}".format(e))

    config.overlay_functions.append(imagebutton_overlay_tracker)

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