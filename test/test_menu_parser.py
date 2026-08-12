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

class TestDuplicateMenuChoices:
    """Одинаковые названия пунктов в разных menu: блоках.
    
    Покрывает баг: когда в нескольких menu: есть одинаковые пункты
    ("Налево", "Прямо", "Направо"), подсказки брались из первого menu:,
    а не из текущего.
    """

    def test_same_choice_names_different_menus(self, setup_test_env):
        """Одинаковые пункты в разных menu: дают разные подсказки."""
        cheat, tmp_path = setup_test_env
        
        content = '''label test:
    scene scene_o1 with dissolve
    dar "Text1"
    menu:
        dar "Text2?"

        "Налево":
            $ rally_cross_quant += 0

        "Прямо":
            $ rally_cross_quant += 0

        "Направо":
            $ rally_cross_quant += 1

    scene scene_o2 with dissolve
    dar "Text3"
    menu:
        dar Text4"

        "Налево":
            $ rally_cross_quant += 0

        "Прямо":
            $ rally_cross_quant += 1

        "Направо":
            $ rally_cross_quant += 0
'''
        write_test_rpy(tmp_path, content)
        
        # Добавляем переменную в известные
        cheat['MENU_VARIABLE_NAMES']['rally_cross_quant'] = 'rally_cross_quant'
        
        # Определяем строки, где находятся menu: (1-based для Ren'Py)
        lines = content.splitlines()
        menu_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith('menu') and ':' in line:
                menu_lines.append(i + 1)
        
        assert len(menu_lines) == 2, "Expected 2 menu: blocks"
        
        # ============================================================
        # Тестируем ПЕРВЫЙ menu: (line_number указывает на него)
        # ============================================================
        cheat['renpy'].get_filename_line = lambda: ('game/test_scene.rpy', menu_lines[0])
        
        # "Направо" в первом menu даёт += 1
        result = cheat['core_menu_parser']('Направо')
        assert 'rally_cross_quant' in result, f"Expected variable in result: {result}"
        assert '+=1' in result, f"Expected +=1 for 'Направо' in first menu: {result}"
        assert '+=0' not in result, f"Should not have +=0 for 'Направо' in first menu: {result}"
        
        # "Налево" в первом menu даёт += 0
        result = cheat['core_menu_parser']('Налево')
        assert 'rally_cross_quant' in result
        assert '+=0' in result, f"Expected +=0 for 'Налево' in first menu: {result}"
        
        # "Прямо" в первом menu даёт += 0
        result = cheat['core_menu_parser']('Прямо')
        assert 'rally_cross_quant' in result
        assert '+=0' in result, f"Expected +=0 for 'Прямо' in first menu: {result}"
        
        # ============================================================
        # Тестируем ВТОРОЙ menu: (line_number указывает на него)
        # ============================================================
        cheat['renpy'].get_filename_line = lambda: ('game/test_scene.rpy', menu_lines[1])
        
        # "Прямо" во втором menu даёт += 1 (в первом давало += 0!)
        result = cheat['core_menu_parser']('Прямо')
        assert 'rally_cross_quant' in result
        assert '+=1' in result, f"Expected +=1 for 'Прямо' in second menu: {result}"
        assert '+=0' not in result, f"Should not have +=0 for 'Прямо' in second menu: {result}"
        
        # "Направо" во втором menu даёт += 0 (в первом давало += 1!)
        result = cheat['core_menu_parser']('Направо')
        assert 'rally_cross_quant' in result
        assert '+=0' in result, f"Expected +=0 for 'Направо' in second menu: {result}"
        assert '+=1' not in result, f"Should not have +=1 for 'Направо' in second menu: {result}"
        
        # "Налево" во втором menu даёт += 0 (как и в первом)
        result = cheat['core_menu_parser']('Налево')
        assert 'rally_cross_quant' in result
        assert '+=0' in result

    def test_same_choice_names_line_inside_menu_block(self, setup_test_env):
        """line_number указывает на строку внутри menu: блока (не на сам menu:)."""
        cheat, tmp_path = setup_test_env
        
        content = '''label test:
    menu:
        dar "Подсказка перед выбором"

        "Налево":
            $ var1 += 1

        "Направо":
            $ var2 += 1

    menu:
        dar "Другая подсказка"

        "Налево":
            $ var1 += 100

        "Направо":
            $ var2 += 100
'''
        write_test_rpy(tmp_path, content)
        
        # Находим строки menu: (1-based)
        lines = content.splitlines()
        menu_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith('menu') and ':' in line:
                menu_lines.append(i + 1)
        
        # line_number указывает на строку ПОСЛЕ первого menu: (например, dar "...")
        # Это строка menu_lines[0] + 1
        cheat['renpy'].get_filename_line = lambda: ('game/test_scene.rpy', menu_lines[0] + 1)
        
        result = cheat['core_menu_parser']('Налево')
        assert 'var1' in result
        assert '+=1' in result
        assert '+=100' not in result
        
        # line_number указывает на строку ПОСЛЕ второго menu:
        cheat['renpy'].get_filename_line = lambda: ('game/test_scene.rpy', menu_lines[1] + 1)
        
        result = cheat['core_menu_parser']('Налево')
        assert 'var1' in result
        assert '+=100' in result
        assert '+=1' not in result or '+=100' in result  # +=1 может входить в +=100 как подстрока

    def test_fallback_when_line_number_is_zero(self, setup_test_env):
        """Если line_number = 0, используется fallback на поиск по тексту."""
        cheat, tmp_path = setup_test_env
        
        content = '''label test:
    menu:
        "Налево":
            $ var1 += 1

    menu:
        "Налево":
            $ var2 += 10
'''
        write_test_rpy(tmp_path, content)
        
        # line_number = 0 — fallback на поиск по тексту (берётся первый menu:)
        cheat['renpy'].get_filename_line = lambda: ('game/test_scene.rpy', 0)
        
        result = cheat['core_menu_parser']('Налево')
        # При fallback берётся первый menu:, так что var1 += 1
        assert 'var1' in result
        assert '+=1' in result
        assert '+=10' not in result

    def test_three_menus_same_choices(self, setup_test_env):
        """Три menu: с одинаковыми пунктами — каждый даёт свои подсказки."""
        cheat, tmp_path = setup_test_env
        
        content = '''label test:
    menu:
        "Go":
            $ score += 1

    menu:
        "Go":
            $ score += 10

    menu:
        "Go":
            $ score += 100
'''
        write_test_rpy(tmp_path, content)
        
        lines = content.splitlines()
        menu_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith('menu') and ':' in line:
                menu_lines.append(i + 1)
        
        assert len(menu_lines) == 3
        
        # Первый menu:
        cheat['renpy'].get_filename_line = lambda: ('game/test_scene.rpy', menu_lines[0])
        result = cheat['core_menu_parser']('Go')
        assert '+=1' in result
        assert '+=10' not in result
        assert '+=100' not in result
        
        # Второй menu:
        cheat['renpy'].get_filename_line = lambda: ('game/test_scene.rpy', menu_lines[1])
        result = cheat['core_menu_parser']('Go')
        assert '+=10' in result
        
        # Третий menu:
        cheat['renpy'].get_filename_line = lambda: ('game/test_scene.rpy', menu_lines[2])
        result = cheat['core_menu_parser']('Go')
        assert '+=100' in result

class TestBooleanValues:
    """Парсинг булевых значений True/False в меню."""

    def test_assign_true(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Say hello":
            $ emmeline_interest = True
        "Ignore her":
            $ emmeline_interest = False
''')
        cheat['MENU_VARIABLE_NAMES']['emmeline_interest'] = 'emmeline_interest'

        result = cheat['core_menu_parser']('Say hello')
        assert 'emmeline_interest' in result
        assert '= True' in result

        result = cheat['core_menu_parser']('Ignore her')
        assert 'emmeline_interest' in result
        assert '= False' in result

    def test_assign_true_with_color(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Accept quest":
            $ quest_started = True
''')
        cheat['MENU_VARIABLE_NAMES']['quest_started'] = 'quest_started'

        result = cheat['core_menu_parser']('Accept quest')
        assert 'quest_started' in result
        assert '= True' in result
        # True присваивается через =, значит цвет COLOR_EQUAL
        assert cheat['COLOR_EQUAL'] in result

    def test_assign_false_with_color(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Decline quest":
            $ quest_started = False
''')
        cheat['MENU_VARIABLE_NAMES']['quest_started'] = 'quest_started'

        result = cheat['core_menu_parser']('Decline quest')
        assert 'quest_started' in result
        assert '= False' in result
        assert cheat['COLOR_EQUAL'] in result

    def test_boolean_and_numeric_together(self, setup_test_env):
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Complex choice":
            $ flag = True
            $ score += 5
''')
        cheat['MENU_VARIABLE_NAMES']['flag'] = 'flag'
        cheat['MENU_VARIABLE_NAMES']['score'] = 'score'

        result = cheat['core_menu_parser']('Complex choice')
        assert 'flag' in result
        assert '= True' in result
        assert 'score' in result
        assert '+=5' in result

    def test_boolean_with_full_scene_code(self, setup_test_env):
        """Реальный кейс: меню с scene, pause, achievement и булевым значением."""
        cheat, tmp_path = setup_test_env
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Say hello":
            $ emmeline_interest = True
            mc "Hey."
            scene 12 with dissolve
            $ renpy.pause()
            scene 123 with dissolve
            $ achievement.grant("sa1_1")
            $ achievement.sync()
            s "Did I just see a grown-assed woman skipping?"
            pass
        "Ignore her":
            $ emmeline_interest = False
            scene 1234 with dissolve
            s "That was kind of a harsh diss."
            pass
''')
        cheat['MENU_VARIABLE_NAMES']['emmeline_interest'] = 'emmeline_interest'

        result = cheat['core_menu_parser']('Say hello')
        assert 'emmeline_interest' in result
        assert '= True' in result

        result = cheat['core_menu_parser']('Ignore her')
        assert 'emmeline_interest' in result
        assert '= False' in result

    def test_boolean_unknown_var_debug_mode(self, setup_test_env):
        """В DEBUG_MODE неизвестная булева переменная показывается с префиксом DEBUG."""
        cheat, tmp_path = setup_test_env
        cheat['DEBUG_MODE'] = True
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Choice":
            $ unknown_flag = True
''')
        result = cheat['core_menu_parser']('Choice')
        assert 'DEBUG:unknown_flag' in result
        assert '= True' in result

    def test_boolean_unknown_var_non_debug_mode(self, setup_test_env):
        """Без DEBUG_MODE неизвестная булева переменная не показывается."""
        cheat, tmp_path = setup_test_env
        cheat['DEBUG_MODE'] = False
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Choice":
            $ unknown_flag = True
''')
        result = cheat['core_menu_parser']('Choice')
        assert result == 'Choice'


class TestTranslationLookup:
    """Поиск вариантов меню через файлы перевода (игра на другом языке)."""

    def write_translation_file(self, tmp_path, language, filename, content):
        """Создаёт файл перевода в game/tl/<language>/<filename>."""
        tl_dir = tmp_path / 'game' / 'tl' / language
        tl_dir.mkdir(parents=True, exist_ok=True)
        tl_file = tl_dir / filename
        tl_file.write_text(content, encoding='utf-8')
        return tl_file

    def test_russian_translation_finds_english_choice(self, setup_test_env):
        """Русский текст варианта находит английский оригинал через tl/russian/."""
        cheat, tmp_path = setup_test_env

        # Оригинальный файл на английском
        write_test_rpy(tmp_path, '''label test:
    menu:
        "Say hello":
            $ emmeline_interest = True
        "Ignore her":
            $ emmeline_interest = False
''')
        cheat['MENU_VARIABLE_NAMES']['emmeline_interest'] = 'emmeline_interest'

        # Файл перевода
        self.write_translation_file(tmp_path, 'russian', 'test_scene.rpy', '''
translate test_menu_1:
    old "Say hello"
    new "Поздороваться"

translate test_menu_2:
    old "Ignore her"
    new "Проигнорировать"
''')

        # Устанавливаем язык перевода
        cheat['renpy'].game.preferences.language = 'russian'

        # Ищем по русскому тексту
        result = cheat['core_menu_parser']('Поздороваться')
        assert 'emmeline_interest' in result
        assert '= True' in result

        result = cheat['core_menu_parser']('Проигнорировать')
        assert 'emmeline_interest' in result
        assert '= False' in result

    def test_translation_with_numeric_values(self, setup_test_env):
        """Перевод работает и с числовыми значениями."""
        cheat, tmp_path = setup_test_env

        write_test_rpy(tmp_path, '''label test:
    menu:
        "Go left":
            $ score += 10
        "Go right":
            $ score -= 5
''')
        cheat['MENU_VARIABLE_NAMES']['score'] = 'score'

        self.write_translation_file(tmp_path, 'russian', 'test_scene.rpy', '''
translate m1:
    old "Go left"
    new "Идти налево"

translate m2:
    old "Go right"
    new "Идти направо"
''')

        cheat['renpy'].game.preferences.language = 'russian'

        result = cheat['core_menu_parser']('Идти налево')
        assert 'score' in result
        assert '+=10' in result

        result = cheat['core_menu_parser']('Идти направо')
        assert 'score' in result
        assert '-=5' in result

    def test_translation_with_tags_in_text(self, setup_test_env):
        """Перевод работает с Ren'Py тегами в тексте."""
        cheat, tmp_path = setup_test_env

        write_test_rpy(tmp_path, '''label test:
    menu:
        "Hello {color=#fff}world{/color}":
            $ var1 += 1
''')
        cheat['MENU_VARIABLE_NAMES']['var1'] = 'var1'

        self.write_translation_file(tmp_path, 'russian', 'test_scene.rpy', '''
translate m1:
    old "Hello {color=#fff}world{/color}"
    new "Привет {color=#fff}мир{/color}"
''')

        cheat['renpy'].game.preferences.language = 'russian'

        result = cheat['core_menu_parser']('Привет {color=#fff}мир{/color}')
        assert 'var1' in result
        assert '+=1' in result

    def test_no_translation_file_falls_back(self, setup_test_env):
        """Если файла перевода нет, подсказка не добавляется (текст не найден)."""
        cheat, tmp_path = setup_test_env

        write_test_rpy(tmp_path, '''label test:
    menu:
        "Say hello":
            $ var1 += 1
''')
        cheat['MENU_VARIABLE_NAMES']['var1'] = 'var1'

        # Язык установлен, но файла перевода нет
        cheat['renpy'].game.preferences.language = 'russian'

        result = cheat['core_menu_parser']('Поздороваться')
        assert result == 'Поздороваться'

    def test_no_language_set_uses_direct_match(self, setup_test_env):
        """Если язык не установлен, работает прямой поиск по тексту."""
        cheat, tmp_path = setup_test_env

        write_test_rpy(tmp_path, '''label test:
    menu:
        "Say hello":
            $ var1 += 1
''')
        cheat['MENU_VARIABLE_NAMES']['var1'] = 'var1'

        # Язык не установлен
        cheat['renpy'].game.preferences.language = None

        result = cheat['core_menu_parser']('Say hello')
        assert 'var1' in result
        assert '+=1' in result

    def test_translation_with_multiple_menus(self, setup_test_env):
        """Перевод работает корректно с несколькими menu: блоками."""
        cheat, tmp_path = setup_test_env

        content = '''label test:
    menu:
        "Go left":
            $ var1 += 1

    menu:
        "Go left":
            $ var1 += 100
'''
        write_test_rpy(tmp_path, content)
        cheat['MENU_VARIABLE_NAMES']['var1'] = 'var1'

        self.write_translation_file(tmp_path, 'russian', 'test_scene.rpy', '''
translate m1:
    old "Go left"
    new "Идти налево"
''')

        cheat['renpy'].game.preferences.language = 'russian'

        # Определяем строки menu:
        lines = content.splitlines()
        menu_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith('menu') and ':' in line:
                menu_lines.append(i + 1)

        # Первый menu:
        cheat['renpy'].get_filename_line = lambda: ('game/test_scene.rpy', menu_lines[0])
        result = cheat['core_menu_parser']('Идти налево')
        assert '+=1' in result
        assert '+=100' not in result

        # Второй menu:
        cheat['renpy'].get_filename_line = lambda: ('game/test_scene.rpy', menu_lines[1])
        result = cheat['core_menu_parser']('Идти налево')
        assert '+=100' in result

    def test_translation_single_quotes(self, setup_test_env):
        """Файл перевода с одинарными кавычками."""
        cheat, tmp_path = setup_test_env

        write_test_rpy(tmp_path, '''label test:
    menu:
        "Say hello":
            $ var1 += 1
''')
        cheat['MENU_VARIABLE_NAMES']['var1'] = 'var1'

        self.write_translation_file(tmp_path, 'russian', 'test_scene.rpy', """
translate m1:
    old 'Say hello'
    new 'Поздороваться'
""")

        cheat['renpy'].game.preferences.language = 'russian'

        result = cheat['core_menu_parser']('Поздороваться')
        assert 'var1' in result
        assert '+=1' in result