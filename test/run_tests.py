#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт запуска тестов для auto_cheat.rpy.
Автоматически создаёт виртуальное окружение, если его нет.
Использование: python run_tests.py
"""
import os
import sys
import subprocess
import venv


def get_venv_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv')


def ensure_venv():
    """Создаёт venv, если его нет, и устанавливает pytest."""
    venv_dir = get_venv_dir()
    python_exe = os.path.join(venv_dir, 'bin', 'python')
    pip_exe = os.path.join(venv_dir, 'bin', 'pip')
    
    if not os.path.exists(python_exe):
        print("[*] Creating virtual environment in .venv/ ...")
        venv.create(venv_dir, with_pip=True)
        print("[OK] Virtual environment created")
        
        print("[*] Installing pytest...")
        subprocess.check_call([pip_exe, 'install', 'pytest', '-q'])
        print("[OK] pytest installed")
    else:
        # Проверяем, установлен ли pytest
        try:
            subprocess.check_output([pip_exe, 'show', 'pytest'], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print("[*] Installing pytest into existing venv...")
            subprocess.check_call([pip_exe, 'install', 'pytest', '-q'])
            print("[OK] pytest installed")
    
    return python_exe


def main():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    print("=" * 60)
    print("  Auto Cheat Test Runner")
    print("=" * 60)
    print()
    
    # Обеспечиваем наличие venv
    python_exe = ensure_venv()
    print()
    print("Running tests with: {}".format(python_exe))
    print("-" * 60)
    
    # Запускаем pytest внутри venv
    exit_code = subprocess.call([
        python_exe, '-m', 'pytest',
        '-v',
        '--tb=short',
        '--color=yes',
        test_dir
    ])
    
    print()
    print("-" * 60)
    if exit_code == 0:
        print("[OK] All tests passed!")
    else:
        print("[FAIL] Some tests failed. See output above.")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())