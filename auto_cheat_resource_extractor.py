#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_cheat_resource_extractor.py
Внешний скрипт для распаковки .rpa архивов и декомпиляции .rpyc файлов.
Запускается из auto_cheat.rpy в среде Python 3.
"""

import sys
import os
import argparse
import subprocess
import threading
import shutil
import glob
import re
import json
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

CONFIG_GAMEDIR = args.gamedir
CONFIG_BASEDIR = args.basedir
DISCOVERY_LOG_PATH = args.log_file

UNRPYC_PATH = None
UNRPA_PATH = None
PIP_PACKAGES = ['unrpa']
DECOMPILE_RPYC = True

# =========================================================================
# LOGGING & UTILS
# =========================================================================
def write_discovery_log(message):
    try:
        with open(DISCOVERY_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(str(message) + "\n")
    except:
        pass

def makedirs_compat(path, exist_ok=False):
    try:
        os.makedirs(path)
    except OSError:
        if not exist_ok or not os.path.isdir(path):
            raise

class SubprocessResult:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

def run_command(cmd, timeout=None, cwd=None):
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd
        )
        
        timer = None
        if timeout is not None:
            def kill_proc():
                if proc.poll() is None:
                    try:
                        proc.kill()
                    except:
                        pass
            timer = threading.Timer(timeout, kill_proc)
            timer.start()
            
        try:
            stdout, stderr = proc.communicate()
        finally:
            if timer is not None:
                timer.cancel()
                
        encoding = 'utf-8'
        if isinstance(stdout, bytes):
            stdout = stdout.decode(encoding, errors='replace')
        if isinstance(stderr, bytes):
            stderr = stderr.decode(encoding, errors='replace')
            
        return SubprocessResult(proc.returncode, stdout, stderr)
        
    except Exception as e:
        return SubprocessResult(-1, "", str(e))

# =========================================================================
# PYTHON & PIP UTILS
# =========================================================================
def find_working_python_cmd():
    cache_attr = '_working_python_cmd'
    if hasattr(find_working_python_cmd, cache_attr):
        return getattr(find_working_python_cmd, cache_attr)
        
    if sys.version_info[0] >= 3:
        setattr(find_working_python_cmd, cache_attr, [sys.executable])
        return [sys.executable]

    candidates = [
        ['py', '-3'], ['python3'], ['python']
    ] if sys.platform == 'win32' else [['python3'], ['python']]
    
    if sys.platform == 'win32':
        common_patterns = [
            r'C:\Python3*\python.exe',
            r'C:\Users\*\AppData\Local\Programs\Python\Python3*\python.exe',
            r'C:\Program Files\Python3*\python.exe',
        ]
        for pattern in common_patterns:
            matches = glob.glob(pattern)
            for match in matches:
                candidates.insert(0, [match])
    
    for candidate in candidates:
        try:
            proc = subprocess.Popen(
                candidate + ['--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            try:
                stdout, stderr = proc.communicate(timeout=10)
            except TypeError:
                stdout, stderr = proc.communicate()
            
            version_output = (stdout.decode('utf-8', errors='ignore').strip() or 
                            stderr.decode('utf-8', errors='ignore').strip())
            
            if proc.returncode == 0 and 'Python 3.' in version_output:
                setattr(find_working_python_cmd, cache_attr, candidate)
                return candidate
        except Exception:
            continue
    
    setattr(find_working_python_cmd, cache_attr, None)
    return None

def check_pip_available():
    python_cmd = find_working_python_cmd()
    if not python_cmd: return False
    try:
        result = run_command(python_cmd + ['-m', 'pip', '--version'], timeout=15)
        return result.returncode == 0
    except:
        return False

def install_packages_via_pip(packages):
    if not packages: return True
    python_cmd = find_working_python_cmd()
    if not python_cmd: return False
    try:
        cmd = python_cmd + ['-m', 'pip', 'install', '--upgrade', '--no-warn-script-location'] + packages
        result = run_command(cmd, timeout=300)
        return result.returncode == 0
    except:
        return False

def find_installed_package(package_name):
    try:
        result = run_command([package_name, '--help'], timeout=15)
        if result.returncode == 0 or 'usage' in (result.stdout + result.stderr).lower():
            return package_name
    except: pass
    
    python_cmd = find_working_python_cmd()
    if python_cmd:
        try:
            result = run_command(python_cmd + ['-m', package_name, '--help'], timeout=15)
            if result.returncode == 0 or 'usage' in (result.stdout + result.stderr).lower():
                return '__python_module__'
        except: pass
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
            UNRPA_PATH = path
            return path
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
            UNRPYC_PATH = path
            return path
    return None

def ensure_tools_installed():
    global UNRPA_PATH, UNRPYC_PATH
    unrpa_found = UNRPA_PATH if (UNRPA_PATH and os.path.exists(UNRPA_PATH)) else find_unrpa()
    unrpyc_found = UNRPYC_PATH if (UNRPYC_PATH and os.path.exists(UNRPYC_PATH)) else find_unrpyc()
    
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
    if not unrpyc_path: return False
    rpy_path = rpyc_path[:-1]
    
    try:
        if unrpyc_path == 'unrpyc':
            cmd = ['unrpyc', rpyc_path]
            cwd = None
        elif unrpyc_path == '__python_module__':
            cmd = find_working_python_cmd() + ['-m', 'unrpyc', rpyc_path]
            cwd = None
        elif unrpyc_path.endswith('.py'):
            python_cmd = find_working_python_cmd()
            if not python_cmd: return False
            cmd = python_cmd + [unrpyc_path, rpyc_path]
            cwd = os.path.dirname(unrpyc_path)
        else:
            cmd = [unrpyc_path, rpyc_path]
            cwd = None
        
        result = run_command(cmd, timeout=60, cwd=cwd)
        if result.returncode == 0 and os.path.exists(rpy_path):
            return True
        return False
    except Exception:
        return False

def extract_rpa_scripts_only(unrpa_path, unrpyc_path):
    extracted_count = 0
    
    for root, dirs, files in os.walk(CONFIG_GAMEDIR):
        if 'tl' in root or 'cache' in root: continue
        
        for file in files:
            if not file.endswith('.rpa'): continue
            rpa_path = os.path.join(root, file)
            
            file_list_output = None
            try:
                cmd = build_unrpa_cmd(unrpa_path, ['-l', rpa_path])
                result = run_command(cmd, timeout=30)
                if result.returncode == 0: file_list_output = result.stdout
                else:
                    cmd = build_unrpa_cmd(unrpa_path, ['--list', rpa_path])
                    result = run_command(cmd, timeout=30)
                    if result.returncode == 0: file_list_output = result.stdout
                    else: continue
            except: continue
            
            script_files = []
            if file_list_output:
                for line in file_list_output.strip().split('\n'):
                    line = line.strip()
                    if not line: continue
                    if line.endswith('.rpy') or line.endswith('.rpyc'): script_files.append(line)
                    elif ' ' in line:
                        parts = line.split()
                        if parts[-1].endswith('.rpy') or parts[-1].endswith('.rpyc'):
                            script_files.append(parts[-1])
            
            if not script_files: continue
            
            temp_extract_dir = os.path.join(CONFIG_GAMEDIR, '_temp_rpa_extract_' + file.replace('.rpa', ''))
            try:
                if os.path.exists(temp_extract_dir): shutil.rmtree(temp_extract_dir, ignore_errors=True)
                makedirs_compat(temp_extract_dir, exist_ok=True)
                
                cmd = build_unrpa_cmd(unrpa_path, ['-mp', temp_extract_dir, rpa_path])
                result = run_command(cmd, timeout=120)
                
                if result.returncode != 0:
                    shutil.rmtree(temp_extract_dir, ignore_errors=True)
                    continue
                
                for temp_root, temp_dirs, temp_files in os.walk(temp_extract_dir):
                    for temp_file in temp_files:
                        if not (temp_file.endswith('.rpy') or temp_file.endswith('.rpyc')): continue
                        
                        temp_path = os.path.join(temp_root, temp_file)
                        rel_path = os.path.relpath(temp_path, temp_extract_dir)
                        target_path = os.path.join(CONFIG_GAMEDIR, rel_path)
                        
                        if os.path.exists(target_path): continue
                        
                        target_dir = os.path.dirname(target_path)
                        if target_dir: makedirs_compat(target_dir, exist_ok=True)
                        
                        try:
                            with open(temp_path, 'rb') as src:
                                with open(target_path, 'wb') as dst:
                                    dst.write(src.read())
                            
                            extracted_count += 1
                            if temp_file.endswith('.rpyc') and DECOMPILE_RPYC and unrpyc_path:
                                decompile_rpyc_external(target_path, unrpyc_path)
                        except: pass
                
                shutil.rmtree(temp_extract_dir, ignore_errors=True)
            except:
                if os.path.exists(temp_extract_dir):
                    shutil.rmtree(temp_extract_dir, ignore_errors=True)
                    
    return extracted_count

# =========================================================================
# MAIN ENTRY POINT
# =========================================================================

def main():
    write_discovery_log("\n" + "="*50)
    write_discovery_log("RESOURCE EXTRACTOR SESSION STARTED")
    write_discovery_log("="*50)
    
    unrpa_path, unrpyc_path = ensure_tools_installed()
    
    if not unrpa_path:
        write_discovery_log("[EXTRACTOR] Cannot extract .rpa archives without unrpa")
        return
    
    extracted = extract_rpa_scripts_only(unrpa_path, unrpyc_path)
    write_discovery_log("[EXTRACTOR] Extraction finished. Extracted {} files.".format(extracted))
    
    write_discovery_log("="*50)
    write_discovery_log("RESOURCE EXTRACTOR SESSION FINISHED")
    write_discovery_log("="*50 + "\n")

if __name__ == "__main__":
    main()