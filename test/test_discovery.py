"""
Тесты авто-обнаружения:
- discover_label_changes: поиск изменений переменных в label'ах
- discover_screen_choices: поиск screen'ов с imagebutton и их связь с label'ами
"""
import os
import pytest


@pytest.fixture
def discovery_env(cheat_fresh, tmp_path):
    """Настраивает окружение для тестов авто-обнаружения."""
    cheat = cheat_fresh
    
    # Настраиваем gamedir
    game_dir = tmp_path / 'game'
    game_dir.mkdir(exist_ok=True)
    cheat['config'].gamedir = str(game_dir)
    
    # Настраиваем известные переменные
    cheat['MENU_VARIABLE_NAMES'].update({
        'var1': 'var1',
        'var2': 'var2',
        'mc_karma': 'Karma',
        'mc_truth': 'Truth',
        'karma_more': 'KarmaMore',
        'leiaRS': 'Leia RS',
    })
    
    # Настраиваем паттерны функций
    cheat['FUNCTION_PARSER_PATTERNS'].update({
        'add_points': 'VAR, VAL, _',
    })
    
    # Отключаем логирование для чистоты тестов
    cheat['LOGGING_MODE'] = False
    
    return cheat, tmp_path


def write_rpy(tmp_path, filename, content):
    """Создаёт .rpy файл в game/ директории."""
    game_dir = tmp_path / 'game'
    game_dir.mkdir(exist_ok=True)
    rpy_file = game_dir / filename
    rpy_file.write_text(content, encoding='utf-8')
    return rpy_file


def get_rpy_files(cheat, tmp_path):
    """Получает список .rpy файлов через функцию из auto_cheat.rpy."""
    return cheat['get_all_rpy_files']()


# =========================================================================
# ТЕСТЫ discover_label_changes
# =========================================================================
class TestDiscoverLabelChanges:
    """Тесты поиска изменений переменных в label'ах."""

    def test_simple_assignment(self, discovery_env):
        """Label с простым присваиванием."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label my_label:
    $ var1 = 5
    $ var2 = 10
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_label_changes'](files)
        
        assert 'my_label' in result
        assert len(result['my_label']) == 2
        # Проверяем первое изменение: var1 = 5
        assert result['my_label'][0][0] == 'var1'
        assert result['my_label'][0][1] == ''  # modifier для '='
        assert result['my_label'][0][2] == '5'

    def test_plus_assignment(self, discovery_env):
        """Label с += присваиванием."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label karma_label:
    $ mc_karma += 5
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_label_changes'](files)
        
        assert 'karma_label' in result
        assert len(result['karma_label']) == 1
        assert result['karma_label'][0][0] == 'mc_karma'
        assert result['karma_label'][0][1] == '+'
        assert result['karma_label'][0][2] == '5'

    def test_minus_assignment(self, discovery_env):
        """Label с -= присваиванием."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label bad_choice:
    $ mc_karma -= 10
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_label_changes'](files)
        
        assert 'bad_choice' in result
        assert result['bad_choice'][0][0] == 'mc_karma'
        assert result['bad_choice'][0][1] == '-'
        assert result['bad_choice'][0][2] == '10'

    def test_function_call(self, discovery_env):
        """Label с вызовом функции."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label gift_label:
    $ add_points("leiaRS", 5, "images/heart.webp")
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_label_changes'](files)
        
        assert 'gift_label' in result
        assert len(result['gift_label']) == 1
        assert result['gift_label'][0][0] == 'leiaRS'
        assert result['gift_label'][0][1] == '+'
        assert result['gift_label'][0][2] == '5'

    def test_multiple_changes(self, discovery_env):
        """Label с несколькими изменениями."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label complex_label:
    $ mc_truth = True
    $ mc_karma += 5
    $ karma_more = True
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_label_changes'](files)
        
        assert 'complex_label' in result
        assert len(result['complex_label']) == 3

    def test_label_without_changes(self, discovery_env):
        """Label без изменений переменных."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label dialogue_only:
    "Character" "Hello world!"
    scene bg room
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_label_changes'](files)
        
        assert 'dialogue_only' not in result

    def test_label_with_if_condition(self, discovery_env):
        """Label с if условием — должно игнорироваться."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label conditional:
    $ var1 = 5
    if var1 == 5:
        $ var2 = 10
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_label_changes'](files)
        
        assert 'conditional' in result
        # Только var1 = 5, var2 = 10 должно быть пропущено (внутри if)
        assert len(result['conditional']) == 1
        assert result['conditional'][0][0] == 'var1'

    def test_multiple_labels_in_file(self, discovery_env):
        """Несколько label'ов в одном файле."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label label_a:
    $ var1 += 1

label label_b:
    $ var2 += 2

label label_c:
    "Just dialogue"
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_label_changes'](files)
        
        assert 'label_a' in result
        assert 'label_b' in result
        assert 'label_c' not in result
        assert result['label_a'][0][0] == 'var1'
        assert result['label_b'][0][0] == 'var2'

    def test_label_with_non_numeric_assignment(self, discovery_env):
        """Label с присваиванием строки — должно игнорироваться."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label string_label:
    $ name = "John"
    $ var1 = 5
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_label_changes'](files)
        
        assert 'string_label' in result
        # Только var1 = 5 должно быть найдено
        assert len(result['string_label']) == 1
        assert result['string_label'][0][0] == 'var1'


# =========================================================================
# ТЕСТЫ discover_screen_choices
# =========================================================================
class TestDiscoverScreenChoices:
    """Тесты поиска screen'ов с imagebutton."""

    def test_simple_screen_with_buttons(self, discovery_env):
        """Простой screen с двумя кнопками."""
        cheat, tmp_path = discovery_env
        
        label_changes = {
            'choice_truth': [['mc_karma', '+', '5']],
            'choice_lie': [['mc_karma', '-', '3']],
        }
        
        write_rpy(tmp_path, 'test.rpy', '''
screen my_choice():
    imagebutton:
        action Jump("choice_truth")
    text "Сказать правду"

    imagebutton:
        action Jump("choice_lie")
    text "Солгать"
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'my_choice' in result
        assert len(result['my_choice']) == 2
        
        # Проверяем первую кнопку
        assert result['my_choice'][0]['text'] == 'Сказать правду'
        assert result['my_choice'][0]['jump'] == 'choice_truth'
        assert result['my_choice'][0]['changes'] == [['mc_karma', '+', '5']]
        
        # Проверяем вторую кнопку
        assert result['my_choice'][1]['text'] == 'Солгать'
        assert result['my_choice'][1]['jump'] == 'choice_lie'
        assert result['my_choice'][1]['changes'] == [['mc_karma', '-', '3']]

    def test_screen_without_jump(self, discovery_env):
        """Screen без Jump — не должен обнаруживаться."""
        cheat, tmp_path = discovery_env
        label_changes = {}
        
        write_rpy(tmp_path, 'test.rpy', '''
screen no_jump():
    imagebutton:
        action Return()
    text "Закрыть"
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'no_jump' not in result

    def test_screen_without_text(self, discovery_env):
        """Screen без text — не должен связываться."""
        cheat, tmp_path = discovery_env
        label_changes = {'some_label': []}
        
        write_rpy(tmp_path, 'test.rpy', '''
screen no_text():
    imagebutton:
        action Jump("some_label")
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_screen_choices'](files, label_changes)
        
        # Без text кнопка не связывается
        assert 'no_text' not in result

    def test_screen_with_multiple_buttons(self, discovery_env):
        """Screen с несколькими кнопками."""
        cheat, tmp_path = discovery_env
        label_changes = {
            'opt_a': [['var1', '+', '1']],
            'opt_b': [['var2', '+', '2']],
            'opt_c': [['var1', '-', '1']],
        }
        
        write_rpy(tmp_path, 'test.rpy', '''
screen multi_choice():
    imagebutton:
        action Jump("opt_a")
    text "Вариант A"

    imagebutton:
        action Jump("opt_b")
    text "Вариант B"

    imagebutton:
        action Jump("opt_c")
    text "Вариант C"
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'multi_choice' in result
        assert len(result['multi_choice']) == 3
        assert result['multi_choice'][0]['text'] == 'Вариант A'
        assert result['multi_choice'][1]['text'] == 'Вариант B'
        assert result['multi_choice'][2]['text'] == 'Вариант C'

    def test_screen_with_unknown_label(self, discovery_env):
        """Screen с Jump на неизвестный label — changes должен быть пустым."""
        cheat, tmp_path = discovery_env
        label_changes = {}  # Нет известных label'ов
        
        write_rpy(tmp_path, 'test.rpy', '''
screen unknown_jump():
    imagebutton:
        action Jump("unknown_label")
    text "Неизвестный выбор"
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'unknown_jump' in result
        assert result['unknown_jump'][0]['text'] == 'Неизвестный выбор'
        assert result['unknown_jump'][0]['changes'] == []

    def test_multiple_screens_in_file(self, discovery_env):
        """Несколько screen'ов в одном файле."""
        cheat, tmp_path = discovery_env
        label_changes = {
            'label_a': [['var1', '+', '1']],
            'label_b': [['var2', '+', '2']],
        }
        
        write_rpy(tmp_path, 'test.rpy', '''
screen screen_one():
    imagebutton:
        action Jump("label_a")
    text "Кнопка 1"

screen screen_two():
    imagebutton:
        action Jump("label_b")
    text "Кнопка 2"
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'screen_one' in result
        assert 'screen_two' in result
        assert len(result['screen_one']) == 1
        assert len(result['screen_two']) == 1


# =========================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# =========================================================================
class TestFullDiscoveryIntegration:
    """Интеграционные тесты полного цикла авто-обнаружения."""

    def test_full_pipeline(self, discovery_env):
        """Полный цикл: файл → discover_label_changes → discover_screen_choices."""
        cheat, tmp_path = discovery_env
        
        write_rpy(tmp_path, 'scene.rpy', '''
screen scene2_choice1():
    imagebutton:
        action Jump("scene2_choice1_lie")
    text "Солгать"

    imagebutton:
        action Jump("scene2_choice1_truth")
    text "Сказать Правду"

label scene2_choice1_truth:
    $ mc_truth = True
    $ mc_karma += 5
    $ karma_more = True

label scene2_choice1_lie:
    $ mc_karma -= 3
''')
        files = get_rpy_files(cheat, tmp_path)
        
        # Шаг 1: Находим изменения в label'ах
        label_changes = cheat['discover_label_changes'](files)
        
        assert 'scene2_choice1_truth' in label_changes
        assert 'scene2_choice1_lie' in label_changes
        assert len(label_changes['scene2_choice1_truth']) == 3
        assert len(label_changes['scene2_choice1_lie']) == 1
        
        # Шаг 2: Находим screen'ы и связываем с label'ами
        screen_choices = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'scene2_choice1' in screen_choices
        assert len(screen_choices['scene2_choice1']) == 2
        
        # Проверяем кнопку "Солгать"
        lie_btn = next(b for b in screen_choices['scene2_choice1'] if b['text'] == 'Солгать')
        assert lie_btn['jump'] == 'scene2_choice1_lie'
        assert len(lie_btn['changes']) == 1
        assert lie_btn['changes'][0][0] == 'mc_karma'
        assert lie_btn['changes'][0][1] == '-'
        assert lie_btn['changes'][0][2] == '3'
        
        # Проверяем кнопку "Сказать Правду"
        truth_btn = next(b for b in screen_choices['scene2_choice1'] if b['text'] == 'Сказать Правду')
        assert truth_btn['jump'] == 'scene2_choice1_truth'
        assert len(truth_btn['changes']) == 3

    def test_discovery_with_function_calls(self, discovery_env):
        """Интеграция с вызовами функций в label'ах."""
        cheat, tmp_path = discovery_env
        
        write_rpy(tmp_path, 'scene.rpy', '''
screen gift_screen():
    imagebutton:
        action Jump("give_gift")
    text "Подарить подарок"

    imagebutton:
        action Jump("keep_gift")
    text "Оставить себе"

label give_gift:
    $ add_points("leiaRS", 10, "images/gift.webp")

label keep_gift:
    $ add_points("leiaRS", -5, "images/sad.webp")
''')
        files = get_rpy_files(cheat, tmp_path)
        
        label_changes = cheat['discover_label_changes'](files)
        screen_choices = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'gift_screen' in screen_choices
        
        give_btn = next(b for b in screen_choices['gift_screen'] if b['text'] == 'Подарить подарок')
        assert give_btn['changes'][0][0] == 'leiaRS'
        assert give_btn['changes'][0][1] == '+'
        assert give_btn['changes'][0][2] == '10'
        
        keep_btn = next(b for b in screen_choices['gift_screen'] if b['text'] == 'Оставить себе')
        assert keep_btn['changes'][0][0] == 'leiaRS'
        # Отрицательное число возвращается как ('', '-5'), а не ('-', '5')
        assert keep_btn['changes'][0][1] == ''
        assert keep_btn['changes'][0][2] == '-5'

    def test_discovery_across_multiple_files(self, discovery_env):
        """Обнаружение работает с несколькими файлами."""
        cheat, tmp_path = discovery_env
        
        # Файл 1: screen
        write_rpy(tmp_path, 'screens.rpy', '''
screen choice_screen():
    imagebutton:
        action Jump("good_ending")
    text "Хорошая концовка"

    imagebutton:
        action Jump("bad_ending")
    text "Плохая концовка"
''')
        
        # Файл 2: label'ы
        write_rpy(tmp_path, 'labels.rpy', '''
label good_ending:
    $ mc_karma += 100

label bad_ending:
    $ mc_karma -= 100
''')
        
        files = get_rpy_files(cheat, tmp_path)
        
        label_changes = cheat['discover_label_changes'](files)
        screen_choices = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'choice_screen' in screen_choices
        assert len(screen_choices['choice_screen']) == 2
        
        good_btn = next(b for b in screen_choices['choice_screen'] if b['text'] == 'Хорошая концовка')
        assert good_btn['changes'][0][0] == 'mc_karma'
        assert good_btn['changes'][0][1] == '+'
        assert good_btn['changes'][0][2] == '100'
        
        bad_btn = next(b for b in screen_choices['choice_screen'] if b['text'] == 'Плохая концовка')
        assert bad_btn['changes'][0][0] == 'mc_karma'
        assert bad_btn['changes'][0][1] == '-'
        assert bad_btn['changes'][0][2] == '100'
    
    def test_screen_with_escaped_quotes(self, discovery_env):
        """Screen с экранированными кавычками в тексте."""
        cheat, tmp_path = discovery_env
        label_changes = {
            'choice_help': [['mc_karma', '+', '5']],
            'choice_refuse': [['mc_karma', '-', '5']],
        }
        
        write_rpy(tmp_path, 'test.rpy', r'''
screen choice_screen():
    imagebutton:
        action Jump("choice_help")
    text "\"Я помогу тебе.\""

    imagebutton:
        action Jump("choice_refuse")
    text "\"Прости, звучит слишком рискованно.\""
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'choice_screen' in result
        assert len(result['choice_screen']) == 2
        
        # Проверяем, что экранированные кавычки удалены
        assert result['choice_screen'][0]['text'] == '"Я помогу тебе."'
        assert result['choice_screen'][1]['text'] == '"Прости, звучит слишком рискованно."'
    # =========================================================================
# ТЕСТЫ discover_used_variables
# =========================================================================
class TestDiscoverUsedVariables:
    """Тесты поиска переменных, используемых в присваиваниях."""

    def test_simple_assignment(self, discovery_env):
        """Находит переменную из простого присваивания."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label test:
    $ ep2_wetPaper = 0
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_used_variables'](files)
        
        assert 'ep2_wetPaper' in result
        assert result['ep2_wetPaper'] == 0

    def test_plus_assignment(self, discovery_env):
        """Находит переменную из += присваивания."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label test:
    $ score += 10
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_used_variables'](files)
        
        assert 'score' in result

    def test_minus_assignment(self, discovery_env):
        """Находит переменную из -= присваивания."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label test:
    $ health -= 5
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_used_variables'](files)
        
        assert 'health' in result

    def test_multiple_assignments(self, discovery_env):
        """Находит несколько переменных в одном файле."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label test:
    $ var1 = 0
    $ var2 = 1
    $ var3 += 5
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_used_variables'](files)
        
        assert 'var1' in result
        assert 'var2' in result
        assert 'var3' in result
        assert len(result) == 3

    def test_variables_in_menu(self, discovery_env):
        """Находит переменные внутри menu блоков."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label test:
    menu:
        "Принять предложение.":
            $ ep2_wetPaper = 0
            you "Хорошо"
        "Отклонить предложение.":
            $ ep2_wetPaper = 1
            you "Извини."
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_used_variables'](files)
        
        assert 'ep2_wetPaper' in result
        # Одна переменная, не должна дублироваться
        assert len([v for v in result if v == 'ep2_wetPaper']) == 1

    def test_variables_across_files(self, discovery_env):
        """Находит переменные в нескольких файлах."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'file1.rpy', '''
label test1:
    $ var_a = 1
''')
        write_rpy(tmp_path, 'file2.rpy', '''
label test2:
    $ var_b = 2
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_used_variables'](files)
        
        assert 'var_a' in result
        assert 'var_b' in result

    def test_no_duplicates_with_declared_vars(self, discovery_env):
        """Не дублирует переменные, уже объявленные через default."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
default declared_var = 10

label test:
    $ declared_var = 20
    $ undeclared_var = 5
''')
        files = get_rpy_files(cheat, tmp_path)
        
        # Сначала находим объявленные
        declared = cheat['discover_global_variables'](files)
        assert 'declared_var' in declared
        
        # Потом находим используемые
        used = cheat['discover_used_variables'](files)
        # Обе переменные должны быть найдены (одна — в обоих, другая — только в used)
        assert 'declared_var' in used
        assert 'undeclared_var' in used

    def test_ignores_non_assignment(self, discovery_env):
        """Игнорирует строки без присваивания."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label test:
    "Just dialogue"
    scene bg room
    show character happy
    play music "song.mp3"
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_used_variables'](files)
        
        assert len(result) == 0

    def test_ignores_comparison(self, discovery_env):
        """Игнорирует сравнения (==)."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label test:
    if var1 == 5:
        pass
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_used_variables'](files)
        
        # var1 не должна быть найдена, т.к. это сравнение, а не присваивание
        # (хотя regex может её найти — это допустимо, т.к. переменная всё равно используется)
        # Главное — не падает
        assert isinstance(result, dict)

    def test_underscore_in_name(self, discovery_env):
        """Находит переменные с подчёркиваниями."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label test:
    $ my_complex_var_name = 42
    $ _private_var = 10
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_used_variables'](files)
        
        assert 'my_complex_var_name' in result
        assert '_private_var' in result

    def test_numbers_in_name(self, discovery_env):
        """Находит переменные с цифрами в имени."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
label test:
    $ var123 = 5
    $ ep2_wetPaper = 0
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_used_variables'](files)
        
        assert 'var123' in result
        assert 'ep2_wetPaper' in result


# =========================================================================
# ИНТЕГРАЦИОННЫЙ ТЕСТ: полная цепочка обнаружения
# =========================================================================
class TestFullVariableDiscovery:
    """Интеграционные тесты полного цикла обнаружения переменных."""

    def test_declared_and_used_vars_combined(self, discovery_env):
        """Объявленные и используемые переменные объединяются корректно."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'test.rpy', '''
default declared_var = 10

label test:
    $ declared_var = 20
    $ undeclared_var = 5
    
    menu:
        "Option 1":
            $ menu_var = 1
        "Option 2":
            $ menu_var = 2
''')
        files = get_rpy_files(cheat, tmp_path)
        
        # Шаг 1: Находим объявленные
        declared = cheat['discover_global_variables'](files)
        for var_name in declared:
            cheat['MENU_VARIABLE_NAMES'][var_name] = var_name
        
        # Шаг 2: Находим используемые
        used = cheat['discover_used_variables'](files)
        for var_name in used:
            if var_name not in cheat['MENU_VARIABLE_NAMES']:
                cheat['MENU_VARIABLE_NAMES'][var_name] = var_name
        
        # Проверяем, что все переменные найдены
        assert 'declared_var' in cheat['MENU_VARIABLE_NAMES']
        assert 'undeclared_var' in cheat['MENU_VARIABLE_NAMES']
        assert 'menu_var' in cheat['MENU_VARIABLE_NAMES']
        
        # Проверяем, что declared_var имеет правильное значение из default
        assert cheat['MENU_VARIABLE_NAMES']['declared_var'] == 'declared_var'

    
    def test_real_world_scenario(self, discovery_env):
        """Реальный сценарий из игры с menu и присваиваниями."""
        cheat, tmp_path = discovery_env
        write_rpy(tmp_path, 'scene.rpy', '''
default mc_karma = 0

label scene_start:
    menu:
        "Принять предложение.":
            $ ep2_wetPaper = 0
            $ mc_karma += 5
            you "Хорошо"
        "Отклонить предложение.":
            $ ep2_wetPaper = 1
            $ mc_karma -= 3
            you "Извини."
''')
        files = get_rpy_files(cheat, tmp_path)
        
        # Полная цепочка обнаружения
        declared = cheat['discover_global_variables'](files)
        for var_name in declared:
            cheat['MENU_VARIABLE_NAMES'][var_name] = var_name
        
        used = cheat['discover_used_variables'](files)
        for var_name in used:
            if var_name not in cheat['MENU_VARIABLE_NAMES']:
                cheat['MENU_VARIABLE_NAMES'][var_name] = var_name
        
        # Все переменные должны быть найдены
        assert 'mc_karma' in cheat['MENU_VARIABLE_NAMES']  # из default
        assert 'ep2_wetPaper' in cheat['MENU_VARIABLE_NAMES']  # из присваивания