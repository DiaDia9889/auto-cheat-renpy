#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_cheat_resource_extractor.py
Внешний скрипт для распаковки .rpa архивов и декомпиляции .rpyc файлов.
Запускается из auto_cheat.rpy в среде Python 3.9+.
"""

import sys

# Проверка версии Python
if sys.version_info < (3, 9):
    print("ERROR: This script requires Python 3.9 or higher.")
    sys.exit(1)

import os
import argparse
import subprocess
import shutil
import urllib.request
import zipfile
import io

# =========================================================================
# CONFIGURATION & ARGUMENTS
# =========================================================================
parser = argparse.ArgumentParser(description="Ren'Py Resource Extractor")
parser.add_argument("--gamedir", required=True, help="Path to the game's 'game/' directory")
parser.add_argument("--basedir", required=True, help="Path to the game's base directory (parent of 'game/')")
parser.add_argument("--log-file", required=True, help="Path to the discovery log file")
args = parser.parse_args()

# ВАЖНО: Нормализуем пути, чтобы избежать проблем с os.path.exists
CONFIG_GAMEDIR = os.path.abspath(args.gamedir)
CONFIG_BASEDIR = os.path.abspath(args.basedir)
DISCOVERY_LOG_PATH = os.path.abspath(args.log_file)

UNRPYC_PATH = None
UNRPA_PATH = None
PIP_PACKAGES = ['unrpa']
DECOMPILE_RPYC = True

# =========================================================================
# LOGGING & UTILS
# =========================================================================
def write_discovery_log(message):
    msg = str(message)
    print(msg)  # Дублируем в консоль
    try:
        with open(DISCOVERY_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception as e:
        print("LOG ERROR:", e)

def find_working_python_cmd():
    """Возвращает команду для запуска Python 3."""
    return [sys.executable]

# =========================================================================
# PYTHON & PIP UTILS
# =========================================================================
def check_pip_available():
    python_cmd = find_working_python_cmd()
    try:
        result = subprocess.run(
            python_cmd + ['-m', 'pip', '--version'],
            capture_output=True, text=True, timeout=15
        )
        return result.returncode == 0
    except Exception:
        return False

def install_packages_via_pip(packages):
    if not packages: return True
    python_cmd = find_working_python_cmd()
    try:
        cmd = python_cmd + ['-m', 'pip', 'install', '--upgrade', '--no-warn-script-location'] + packages
        write_discovery_log("[PIP] Installing: {}".format(' '.join(cmd)))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            write_discovery_log("[PIP] Error: {}".format(result.stderr))
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        write_discovery_log("[PIP] Installation timeout")
        return False
    except Exception as e:
        write_discovery_log("[PIP] Exception: {}".format(e))
        return False

def find_installed_package(package_name):
    try:
        result = subprocess.run(
            [package_name, '--help'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 or 'usage' in (result.stdout + result.stderr).lower():
            return package_name
    except Exception:
        pass
    
    python_cmd = find_working_python_cmd()
    try:
        result = subprocess.run(
            python_cmd + ['-m', package_name, '--help'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 or 'usage' in (result.stdout + result.stderr).lower():
            return '__python_module__'
    except Exception:
        pass
    return None

def find_installed_unrpa(): return find_installed_package('unrpa')
def find_installed_unrpyc(): return find_installed_package('unrpyc')

# =========================================================================
# UNRPYC DOWNLOAD & TOOL DISCOVERY
# =========================================================================
def download_unrpyc_from_github():
    unrpyc_dir = os.path.join(CONFIG_BASEDIR, 'unrpyc')
    unrpyc_py = os.path.join(unrpyc_dir, 'unrpyc.py')
    if os.path.exists(unrpyc_py): return unrpyc_py
    
    write_discovery_log("[UNRPYC] Downloading from GitHub...")
    try:
        zip_url = 'https://github.com/CensoredUsername/unrpyc/archive/refs/heads/master.zip'
        with urllib.request.urlopen(zip_url, timeout=60) as response:
            zip_data = response.read()
        
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
            root_folder = zip_ref.namelist()[0].split('/')[0]
            zip_ref.extractall(CONFIG_BASEDIR)
            extracted_dir = os.path.join(CONFIG_BASEDIR, root_folder)
            if os.path.exists(extracted_dir):
                if os.path.exists(unrpyc_dir): shutil.rmtree(unrpyc_dir)
                os.rename(extracted_dir, unrpyc_dir)
        
        if os.path.exists(unrpyc_py): return unrpyc_py
        return None
    except Exception as e:
        write_discovery_log("[UNRPYC] Download failed: {}".format(e))
        return None

def find_unrpa():
    global UNRPA_PATH
    if UNRPA_PATH and os.path.exists(UNRPA_PATH): return UNRPA_PATH
    
    search_paths = [
        os.path.join(CONFIG_BASEDIR, 'unrpa.py'),
        os.path.join(CONFIG_BASEDIR, 'unrpa', 'unrpa.py'),
        os.path.join(CONFIG_BASEDIR, 'tools', 'unrpa.py'),
    ]
    if sys.platform == 'win32':
        search_paths.append(os.path.join(CONFIG_BASEDIR, 'unrpa.bat'))
        
    for path in search_paths:
        if os.path.exists(path):
            write_discovery_log("[DEBUG] Found local unrpa at: {}".format(path))
            UNRPA_PATH = path
            return path
            
    write_discovery_log("[DEBUG] Local unrpa not found. Checking system...")
    installed = find_installed_unrpa()
    if installed:
        write_discovery_log("[DEBUG] Found installed unrpa: {}".format(installed))
        UNRPA_PATH = installed
        return installed
        
    return None

def find_unrpyc():
    global UNRPYC_PATH
    if UNRPYC_PATH and os.path.exists(UNRPYC_PATH): return UNRPYC_PATH
    
    search_paths = [
        os.path.join(CONFIG_BASEDIR, 'unrpyc.py'),
        os.path.join(CONFIG_BASEDIR, 'unrpyc', 'unrpyc.py'),
        os.path.join(CONFIG_BASEDIR, 'tools', 'unrpyc.py'),
    ]
    if sys.platform == 'win32':
        search_paths.append(os.path.join(CONFIG_BASEDIR, 'unrpyc.bat'))
        
    for path in search_paths:
        if os.path.exists(path):
            write_discovery_log("[DEBUG] Found local unrpyc at: {}".format(path))
            UNRPYC_PATH = path
            return path
            
    write_discovery_log("[DEBUG] Local unrpyc not found. Checking system...")
    installed = find_installed_unrpyc()
    if installed:
        write_discovery_log("[DEBUG] Found installed unrpyc: {}".format(installed))
        UNRPYC_PATH = installed
        return installed
        
    return None

def ensure_tools_installed():
    global UNRPA_PATH, UNRPYC_PATH
    
    write_discovery_log("[TOOLS] Checking for tools...")
    
    unrpa_found = find_unrpa()
    unrpyc_found = find_unrpyc()
    
    missing_tools = []
    if not unrpa_found: missing_tools.append('unrpa')
    if not unrpyc_found: missing_tools.append('unrpyc')
    
    if missing_tools:
        if 'unrpa' in missing_tools and check_pip_available():
            write_discovery_log("[TOOLS] Installing unrpa via pip...")
            if install_packages_via_pip(PIP_PACKAGES):
                unrpa_found = find_installed_unrpa()
        
        if 'unrpyc' in missing_tools:
            write_discovery_log("[TOOLS] Downloading unrpyc from GitHub...")
            downloaded_unrpyc = download_unrpyc_from_github()
            if downloaded_unrpyc:
                unrpyc_found = downloaded_unrpyc
                
    return (unrpa_found, unrpyc_found)

# =========================================================================
# EXTRACTION & DECOMPILATION
# =========================================================================
def build_unrpa_cmd(unrpa_path, extra_args):
    if unrpa_path == 'unrpa': return ['unrpa'] + extra_args
    elif unrpa_path == '__python_module__': return find_working_python_cmd() + ['-m', 'unrpa'] + extra_args
    elif unrpa_path.endswith('.py'): return [sys.executable, unrpa_path] + extra_args
    else: return [unrpa_path] + extra_args

def decompile_rpyc_external(rpyc_path, unrpyc_path=None):
    """Декомпилирует .rpyc файл используя unrpyc."""
    if not unrpyc_path: return False
    rpy_path = rpyc_path[:-1]
    
    # Проверка: если .rpy файл уже существует, пропускаем декомпиляцию
    if os.path.exists(rpy_path):
        write_discovery_log("[RPYC] .rpy file already exists, skipping decompilation: {}".format(os.path.basename(rpy_path)))
        return True
    
    try:
        if unrpyc_path == 'unrpyc':
            cmd = ['unrpyc', rpyc_path]
            cwd = None
        elif unrpyc_path == '__python_module__':
            cmd = find_working_python_cmd() + ['-m', 'unrpyc', rpyc_path]
            cwd = None
        elif unrpyc_path.endswith('.py'):
            python_cmd = find_working_python_cmd()
            cmd = python_cmd + [unrpyc_path, rpyc_path]
            cwd = os.path.dirname(unrpyc_path)
        else:
            cmd = [unrpyc_path, rpyc_path]
            cwd = None
        
        write_discovery_log("[RPYC] Decompiling: {} -> {}".format(
            os.path.basename(rpyc_path), os.path.basename(rpy_path)))
            
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=cwd)
        if result.returncode == 0:
            if os.path.exists(rpy_path):
                write_discovery_log("[RPYC] Successfully decompiled: {}".format(os.path.basename(rpy_path)))
                return True
            else:
                write_discovery_log("[RPYC] unrpyc completed but .rpy not created")
                return False
        else:
            write_discovery_log("[RPYC] unrpyc failed (code {}): {}".format(
                result.returncode, (result.stderr or result.stdout)[:300]))
            return False
    
    except subprocess.TimeoutExpired:
        write_discovery_log("[RPYC] Decompilation timeout: {}".format(os.path.basename(rpyc_path)))
        return False
    except Exception as e:
        write_discovery_log("[RPYC] Error: {}".format(e))
        return False

def decompile_all_rpyc_files(unrpyc_path):
    """ЭТАП 2: Сканирует все .rpyc файлы в game/ и декомпилирует те, у которых нет .rpy."""
    if not unrpyc_path:
        write_discovery_log("[RPYC] No unrpyc available, skipping decompilation stage")
        return 0
    
    decompiled_count = 0
    skipped_count = 0
    failed_count = 0
    
    write_discovery_log("[RPYC] Scanning for .rpyc files to decompile...")
    
    for root, dirs, files in os.walk(CONFIG_GAMEDIR):
        if 'tl' in root or 'cache' in root: continue
        
        for file in files:
            if not file.endswith('.rpyc'): continue
            
            rpyc_path = os.path.join(root, file)
            rel_path = os.path.relpath(rpyc_path, CONFIG_GAMEDIR)
            
            # Проверяем, есть ли уже .rpy файл
            rpy_path = rpyc_path[:-1]  # .rpyc -> .rpy
            if os.path.exists(rpy_path):
                skipped_count += 1
                write_discovery_log("[RPYC] Skipped (rpy exists): {}".format(rel_path))
                continue
            
            # Декомпилируем
            if decompile_rpyc_external(rpyc_path, unrpyc_path):
                decompiled_count += 1
            else:
                failed_count += 1
                write_discovery_log("[RPYC] Failed to decompile: {}".format(rel_path))
    
    write_discovery_log("[RPYC] Total: decompiled {}, skipped {}, failed {}".format(
        decompiled_count, skipped_count, failed_count))
    return decompiled_count

def extract_rpa_scripts_only(unrpa_path):
    """ЭТАП 1: Извлекает скрипты из .rpa архивов используя CLI-утилиту unrpa."""
    extracted_count = 0
    skipped_count = 0
    
    for root, dirs, files in os.walk(CONFIG_GAMEDIR):
        if 'tl' in root or 'cache' in root: continue
        
        for file in files:
            if not file.endswith('.rpa'): continue
            rpa_path = os.path.join(root, file)
            
            write_discovery_log("[RPA] Processing archive: {}".format(file))
            
            file_list_output = None
            try:
                cmd = build_unrpa_cmd(unrpa_path, ['-l', rpa_path])
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    file_list_output = result.stdout
                else:
                    write_discovery_log("[RPA] unrpa -l failed (code {}): {}".format(result.returncode, result.stderr[:200]))
                    cmd = build_unrpa_cmd(unrpa_path, ['--list', rpa_path])
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        file_list_output = result.stdout
                    else:
                        continue
            except subprocess.TimeoutExpired:
                write_discovery_log("[RPA] unrpa list timeout")
                continue
            except Exception as e:
                write_discovery_log("[RPA] Error running unrpa list: {}".format(e))
                continue
            
            script_files = []
            if file_list_output:
                for line in file_list_output.strip().split('\n'):
                    line = line.strip()
                    if not line: continue
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
            
            temp_extract_dir = os.path.join(CONFIG_GAMEDIR, '_temp_rpa_extract_' + file.replace('.rpa', ''))
            try:
                if os.path.exists(temp_extract_dir):
                    shutil.rmtree(temp_extract_dir, ignore_errors=True)
                os.makedirs(temp_extract_dir, exist_ok=True)
                
                write_discovery_log("[RPA] Extracting {} to temporary directory...".format(file))
                
                cmd = build_unrpa_cmd(unrpa_path, ['-mp', temp_extract_dir, rpa_path])
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                if result.returncode != 0:
                    write_discovery_log("[RPA] unrpa extraction failed: {}".format(result.stderr[:200]))
                    shutil.rmtree(temp_extract_dir, ignore_errors=True)
                    continue
                
                write_discovery_log("[RPA] Extraction completed, filtering scripts...")
                
                for temp_root, temp_dirs, temp_files in os.walk(temp_extract_dir):
                    for temp_file in temp_files:
                        if not (temp_file.endswith('.rpy') or temp_file.endswith('.rpyc')): continue
                        
                        temp_path = os.path.join(temp_root, temp_file)
                        rel_path = os.path.relpath(temp_path, temp_extract_dir)
                        target_path = os.path.join(CONFIG_GAMEDIR, rel_path)
                        
                        if os.path.exists(target_path):
                            skipped_count += 1
                            write_discovery_log("[RPA] Skipped (already exists): {}".format(rel_path))
                            continue
                        
                        target_dir = os.path.dirname(target_path)
                        if target_dir: os.makedirs(target_dir, exist_ok=True)
                        
                        try:
                            with open(temp_path, 'rb') as src:
                                with open(target_path, 'wb') as dst:
                                    dst.write(src.read())
                            
                            size = os.path.getsize(target_path)
                            write_discovery_log("[RPA] Extracted: {} ({} bytes)".format(rel_path, size))
                            extracted_count += 1
                        except Exception as e:
                            write_discovery_log("[RPA] Error copying {}: {}".format(rel_path, e))
                
                shutil.rmtree(temp_extract_dir, ignore_errors=True)
                write_discovery_log("[RPA] Archive {} processed".format(file))
            except Exception as e:
                write_discovery_log("[RPA] Error processing {}: {}".format(file, e))
                if os.path.exists(temp_extract_dir):
                    shutil.rmtree(temp_extract_dir, ignore_errors=True)
    
    write_discovery_log("[RPA] Total: extracted {} scripts, skipped {}".format(extracted_count, skipped_count))
    return extracted_count

# =========================================================================
# MAIN ENTRY POINT
# =========================================================================

def main():
    write_discovery_log("\n" + "="*50)
    write_discovery_log("RESOURCE EXTRACTOR SESSION STARTED")
    write_discovery_log("="*50)
    write_discovery_log("[DEBUG] CONFIG_BASEDIR: {}".format(CONFIG_BASEDIR))
    write_discovery_log("[DEBUG] CONFIG_GAMEDIR: {}".format(CONFIG_GAMEDIR))
    
    unrpa_path, unrpyc_path = ensure_tools_installed()
    
    # ============================================================
    # ЭТАП 1: Распаковка RPA архивов
    # ============================================================
    write_discovery_log("\n[STAGE 1] RPA EXTRACTION")
    write_discovery_log("-"*30)
    
    if unrpa_path:
        write_discovery_log("[STAGE 1] Using unrpa: {}".format(unrpa_path))
        extracted = extract_rpa_scripts_only(unrpa_path)
        write_discovery_log("[STAGE 1] Completed. Extracted {} files.".format(extracted))
    else:
        write_discovery_log("[STAGE 1] unrpa not found, skipping RPA extraction.")
        write_discovery_log("[STAGE 1] If .rpa archives exist, extraction will not be performed.")
    
    # ============================================================
    # ЭТАП 2: Декомпиляция RPYC файлов
    # ============================================================
    write_discovery_log("\n[STAGE 2] RPYC DECOMPILATION")
    write_discovery_log("-"*30)
    
    if DECOMPILE_RPYC:
        if unrpyc_path:
            write_discovery_log("[STAGE 2] Using unrpyc: {}".format(unrpyc_path))
            decompiled = decompile_all_rpyc_files(unrpyc_path)
            write_discovery_log("[STAGE 2] Completed. Decompiled {} files.".format(decompiled))
        else:
            write_discovery_log("[STAGE 2] unrpyc not found, skipping decompilation.")
    else:
        write_discovery_log("[STAGE 2] DECOMPILE_RPYC is disabled, skipping.")
    
    write_discovery_log("\n" + "="*50)
    write_discovery_log("RESOURCE EXTRACTOR SESSION FINISHED")
    write_discovery_log("="*50 + "\n")

if __name__ == "__main__":
    main()