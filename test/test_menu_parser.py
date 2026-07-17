"""Интеграционные тесты полного парсера меню core_menu_parser."""
import os
import pytest


@pytest.fixture
def setup_test_env(cheat_fresh, tmp_path):
    """Настраивает окружение для интеграционных тестов."""
    cheat = cheat_fresh
    
    # Создаём структуру game/ внутри tmp_path
    game_dir = tmp_path / 'game'
    game_dir.mkdir(exist_ok=True)
    
    # gamedir указывает на папку game — как в реальной игре
    cheat['config'].gamedir = str(game_dir)
    
    # Мок возвращает 'game/test_scene.rpy' — парсер уберёт 'game/' 
    # и будет искать файл в gamedir/test_scene.rpy
    def mock_get_filename_line():
        return ('game/test_scene.rpy', 1)
    cheat['renpy'].get_filename_line = mock_get_filename_line
    
    # Настраиваем известные переменные
    cheat['MENU_VARIABLE_NAMES'].update({
        'var1': 'var1',
        'var2': 'var2',
        'score': 'Score',
        'leiaRS': 'Leia RS',
        'romantic2': 'Romantic',
        'pervy2': 'Pervy',
    })
    
    cheat['FUNCTION_PARSER_PATTERNS'].update({
        'add_points': 'VAR, VAL, _',
    })
    
    # Включаем debug-режим для тестов
    cheat['DEBUG_MODE'] = True
    
    return cheat, tmp_path


def write_test_rpy(tmp_path, content):
    """Создаёт тестовый .rpy файл в game/ директории."""
    game_dir = tmp_path / 'game'
    game_dir.mkdir(exist_ok=True)
    rpy_file = game_dir / 'test_scene.rpy'
    rpy_file.write_text(content, encoding='utf-8')
    return rpy_file


class TestBasicMenuParsing:
    """Базовый парсинг меню."""

    def test_simple_choice_with_assignment(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Choice 1":
            $ var1 += 1
        "Choice 2":
            $ var2 = 5
''')
        result = cheat['core_menu_parser']('Choice 1')
        assert 'var1' in result
        # Проверяем формат: var1 +=1 (без пробела между + и 1)
        assert '+=1' in result

        result = cheat['core_menu_parser']('Choice 2')
        assert 'var2' in result
        # Проверяем формат: var2 = 5 (с пробелами вокруг =)
        assert '= 5' in result

    def test_choice_with_function_call(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Give gift":
            $ add_points("leiaRS", 5, "img.webp")
''')
        result = cheat['core_menu_parser']('Give gift')
        assert 'leiaRS' in result or 'Leia RS' in result
        # Проверяем формат: +=5 (без пробела)
        assert '+=5' in result

    def test_choice_with_multiple_changes(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Choice":
            $ var1 += 1
            $ var2 += 2
            $ add_points("score", 10, "img.png")
''')
        result = cheat['core_menu_parser']('Choice')
        assert 'var1' in result
        assert 'var2' in result
        assert 'score' in result or 'Score' in result


class TestMenuWithConditions:
    """Меню с условиями if."""

    def test_choice_with_if_true(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Choice A" if True:
            $ var1 += 1
        "Choice B" if True:
            $ var2 += 1
''')
        result = cheat['core_menu_parser']('Choice A')
        assert 'var1' in result

    def test_choice_with_variable_condition(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Choice" if has_item:
            $ var1 += 1
''')
        result = cheat['core_menu_parser']('Choice')
        assert 'var1' in result


class TestMenuWithTags:
    """Меню с Ren'Py тегами в тексте."""

    def test_choice_with_color_tag(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Hello {color=#fff}world{/color}":
            $ var1 += 1
''')
        
        # Глубокая отладка: проверяем каждый этап парсинга
        game_dir = tmp_path / 'game'
        rpy_file = game_dir / 'test_scene.rpy'
        lines = rpy_file.read_text(encoding='utf-8').splitlines()
        
        print("\n=== DEEP DEBUG ===")
        print(f"Lines in file: {lines}")
        
        # Находим menu:
        menu_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith('menu') and ':' in line:
                menu_idx = i
                print(f"Found menu: at line {i}: {line!r}")
                break
        
        assert menu_idx is not None, "menu: not found in file"
        
        # Вызываем get_parsed_menu напрямую
        parsed = cheat['get_parsed_menu'](str(rpy_file), menu_idx, lines)
        print(f"Parsed menu blocks: {parsed}")
        print(f"Keys: {list(parsed.keys())}")
        
        # Проверяем нормализацию каждого ключа
        for key in parsed.keys():
            normalized = cheat['normalize_text'](key)
            print(f"Key: {key!r} -> Normalized: {normalized!r}")
        
        # Теперь проверяем, что ищет core_menu_parser
        caption = 'Hello {color=#fff}world{/color}'
        lookup = cheat['normalize_text'](caption)
        print(f"Looking for: {caption!r} -> Normalized: {lookup!r}")
        
        # Проверяем совпадение
        for key in parsed.keys():
            key_norm = cheat['normalize_text'](key)
            match = lookup == key_norm or lookup in key_norm or key_norm in lookup
            print(f"Comparing {lookup!r} with {key_norm!r} -> Match: {match}")
        
        result = cheat['core_menu_parser'](caption)
        print(f"Final result: {result!r}")
        
        assert 'var1' in result, f"Expected 'var1' in result, got: {result!r}"

    def test_choice_with_nested_tags(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Странные девушки.{color=#00FF00}{size=-15}(+1 pervy){/size}{/color}":
            $ pervy2 += 1
        "Красивые девушки.{color=#00FF00}{size=-15}(+1 romantic){/size}{/color}":
            $ romantic2 += 1
''')
        
        # Глубокая отладка
        game_dir = tmp_path / 'game'
        rpy_file = game_dir / 'test_scene.rpy'
        lines = rpy_file.read_text(encoding='utf-8').splitlines()
        
        print("\n=== DEEP DEBUG (nested tags) ===")
        
        # Находим menu:
        menu_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith('menu') and ':' in line:
                menu_idx = i
                break
        
        assert menu_idx is not None
        
        # Вызываем get_parsed_menu напрямую
        parsed = cheat['get_parsed_menu'](str(rpy_file), menu_idx, lines)
        print(f"Parsed menu blocks: {list(parsed.keys())}")
        
        for key in parsed.keys():
            normalized = cheat['normalize_text'](key)
            print(f"Key: {key!r} -> Normalized: {normalized!r}")
        
        caption = 'Странные девушки.{color=#00FF00}{size=-15}(+1 pervy){/size}{/color}'
        lookup = cheat['normalize_text'](caption)
        print(f"Looking for: {lookup!r}")
        
        result = cheat['core_menu_parser'](caption)
        print(f"Final result: {result!r}")
        
        assert 'pervy2' in result or 'Pervy' in result, f"Expected 'pervy2' or 'Pervy' in result, got: {result!r}"

class TestNegativeCases:
    """Случаи, когда подсказки не должны добавляться."""

    def test_no_changes_in_choice(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Just talk":
            "Character" "Hello!"
''')
        result = cheat['core_menu_parser']('Just talk')
        assert result == 'Just talk'

    def test_unknown_variable_in_non_debug_mode(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        cheat['DEBUG_MODE'] = False
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Choice":
            $ unknown_var += 1
''')
        result = cheat['core_menu_parser']('Choice')
        assert result == 'Choice'

    def test_choice_not_in_menu(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Choice 1":
            $ var1 += 1
''')
        result = cheat['core_menu_parser']('Non-existent choice')
        assert result == 'Non-existent choice'


class TestMultipleMenus:
    """Несколько меню в одном файле."""

    def test_correct_menu_selected(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "First menu A":
            $ var1 += 1
        "First menu B":
            $ var2 += 1

    menu:
        "Second menu A":
            $ var1 += 10
        "Second menu B":
            $ var2 += 10
''')
        result = cheat['core_menu_parser']('First menu A')
        # Проверяем формат: +=1 (без пробела)
        assert '+=1' in result
        # Убеждаемся, что это не +=10
        assert '+=10' not in result

        result = cheat['core_menu_parser']('Second menu A')
        assert '+=10' in result


class TestMinusAssignment:
    """Отрицательные изменения."""

    def test_minus_assignment(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Bad choice":
            $ var1 -= 5
''')
        result = cheat['core_menu_parser']('Bad choice')
        assert 'var1' in result
        # Проверяем формат: -=5 (без пробела)
        assert '-=5' in result
        assert cheat['COLOR_MINUS'] in result

    def test_function_with_negative_value(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Insult":
            $ add_points("leiaRS", -10, "img.webp")
''')
        result = cheat['core_menu_parser']('Insult')
        # Проверяем формат: -10 (без пробела между - и 10, но с пробелом перед -)
        assert '-10' in result or '-=10' in result