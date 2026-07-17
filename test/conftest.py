"""
conftest.py — загрузчик функций из auto_cheat.rpy для тестирования.
Извлекает блок `init python:`, подменяет Ren'Py API моками и экспортирует
все функции/переменные в pytest-фикстуру `cheat`.
"""
import os
import re
import sys
import types
import tempfile
import textwrap
import pytest

# =========================================================================
# MOCK REN'PY API
# =========================================================================
class MockStore:
    """Мок для renpy.store — хранилище переменных игры."""
    pass

class MockConfig:
    """Мок для config."""
    gamedir = tempfile.gettempdir()
    overlay_functions = []

class MockRenpy:
    """Мок для модуля renpy."""
    store = MockStore()
    config = MockConfig()

    @staticmethod
    def get_filename_line():
        return ("game/test.rpy", 1)

    @staticmethod
    def substitute(text):
        return text

    @staticmethod
    def restart_interaction():
        pass

    @staticmethod
    def get_screen(name):
        return None

    @staticmethod
    def show_screen(name, *args, **kwargs):
        pass

    @staticmethod
    def hide_screen(name, *args, **kwargs):
        pass

    @staticmethod
    def display_menu(items, **kwargs):
        return items[0] if items else None

    class loader:
        @staticmethod
        def load(path):
            return open(path, "rb")

# Регистрируем мок как модуль renpy
sys.modules['renpy'] = MockRenpy

# =========================================================================
# ИЗВЛЕЧЕНИЕ КОДА ИЗ auto_cheat.rpy
# =========================================================================
def load_cheat_module():
    """Извлекает Python-код из auto_cheat.rpy и выполняет его в изолированном namespace."""
    rpy_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'auto_cheat.rpy')
    
    if not os.path.exists(rpy_path):
        raise FileNotFoundError("auto_cheat.rpy not found at: {}".format(rpy_path))
    
    with open(rpy_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Ищем строку с 'init python:'
    start_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == 'init python:':
            start_idx = i + 1
            break
    
    if start_idx == -1:
        raise RuntimeError("Cannot find 'init python:' in auto_cheat.rpy")
    
    # Извлекаем все строки после 'init python:' до конца блока
    python_lines = []
    for i in range(start_idx, len(lines)):
        line = lines[i]
        # Пустые строки добавляем
        if not line.strip():
            python_lines.append(line)
            continue
        # Если строка имеет отступ — это часть блока
        if line.startswith('    ') or line.startswith('\t'):
            python_lines.append(line)
        else:
            # Строка без отступа — конец блока init python:
            break
    
    # Объединяем строки
    python_code = ''.join(python_lines)
    
    # Убираем общий отступ (4 пробела или 1 таб)
    python_code = textwrap.dedent(python_code)
    
    # Удаляем вызовы, которые могут упасть при загрузке
    python_code = re.sub(r'config\.overlay_functions\.append\([^)]+\)', 'pass', python_code)
    
    # Создаём namespace с моками
    namespace = {
        '__name__': '__cheat_test__',
        '__file__': rpy_path,
        'renpy': MockRenpy,
        'config': MockConfig,
    }
    
    # Выполняем код
    try:
        exec(compile(python_code, rpy_path, 'exec'), namespace)
    except Exception as e:
        # Сохраняем обработанный код для отладки
        debug_path = os.path.join(tempfile.gettempdir(), 'auto_cheat_extracted.py')
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(python_code)
        raise RuntimeError("Failed to execute auto_cheat.rpy: {}\nExtracted code saved to: {}".format(e, debug_path))
    
    return namespace

# =========================================================================
# PYTEST FIXTURE
# =========================================================================
@pytest.fixture(scope="session")
def cheat():
    """Фикстура, предоставляющая доступ ко всем функциям и переменным из auto_cheat.rpy."""
    return load_cheat_module()

@pytest.fixture
def cheat_fresh(cheat):
    """Свежая копия состояния перед каждым тестом (сброс кэшей)."""
    cheat['_file_cache'].clear()
    cheat['_cache_timestamps'].clear()
    cheat['_menu_parse_cache'].clear()
    # Сбрасываем глобальные словари к известному состоянию
    cheat['MENU_VARIABLE_NAMES'].clear()
    cheat['FUNCTION_PARSER_PATTERNS'].clear()
    return cheat