"""
Тесты системы автоматического overlay для imagebutton'ов.
"""
import pytest
from conftest import write_rpy, get_rpy_files


class TestImagebuttonOverlayTracker:
    """Тесты функции imagebutton_overlay_tracker."""

    def test_overlay_hidden_when_no_current_screen(self, cheat_fresh):
        """Overlay скрывается когда нет активного screen'а."""
        cheat = cheat_fresh
        cheat['_current_choice_screen'] = None
        cheat['SCREEN_CHOICES'] = {'test_screen': []}
        
        # Сбрасываем renpy.get_screen в исходное состояние
        cheat['renpy'].get_screen = lambda name: None
        
        cheat['imagebutton_overlay_tracker']()
        
        # Overlay не должен быть показан
        assert not cheat['renpy'].get_screen("imagebutton_overlay")

    def test_overlay_hidden_when_screen_not_in_choices(self, cheat_fresh):
        """Overlay скрывается когда screen не в SCREEN_CHOICES."""
        cheat = cheat_fresh
        cheat['_current_choice_screen'] = 'unknown_screen'
        cheat['SCREEN_CHOICES'] = {'test_screen': []}
        
        # Сбрасываем renpy.get_screen
        cheat['renpy'].get_screen = lambda name: None
        
        cheat['imagebutton_overlay_tracker']()
        
        assert not cheat['renpy'].get_screen("imagebutton_overlay")

    def test_overlay_shown_when_screen_has_choices(self, cheat_fresh):
        """Overlay показывается когда screen есть в SCREEN_CHOICES."""
        cheat = cheat_fresh
        cheat['_current_choice_screen'] = 'test_screen'
        cheat['SCREEN_CHOICES'] = {
            'test_screen': [
                {'text': 'Option 1', 'jump': 'label_1', 'changes': [['var1', '+', '5']]}
            ]
        }
        
        # Мокаем renpy.get_screen - возвращает объект для test_screen
        def mock_get_screen(name):
            if name == 'test_screen':
                return object()  # Имитируем активный screen
            return None
        cheat['renpy'].get_screen = mock_get_screen
        
        cheat['imagebutton_overlay_tracker']()
        
        # _current_choice_screen не должен быть очищен
        assert cheat['_current_choice_screen'] == 'test_screen'

    def test_overlay_hidden_when_screen_not_active(self, cheat_fresh):
        """Overlay скрывается когда screen не активен."""
        cheat = cheat_fresh
        cheat['_current_choice_screen'] = 'test_screen'
        cheat['SCREEN_CHOICES'] = {'test_screen': [{'text': 'Test', 'changes': []}]}
        
        # ВАЖНО: явно устанавливаем, что screen НЕ активен
        cheat['renpy'].get_screen = lambda name: None
        
        cheat['imagebutton_overlay_tracker']()
        
        # _current_choice_screen должен быть очищен
        assert cheat['_current_choice_screen'] is None, \
            f"Expected None, got {cheat['_current_choice_screen']}"


class TestReturnActionParsing:
    """Тесты парсинга action Return()."""

    def test_return_action_detected(self, discovery_env):
        """Return() правильно обнаруживается."""
        cheat, tmp_path = discovery_env
        label_changes = {}
        
        write_rpy(tmp_path, 'test.rpy', '''
screen choice_screen():
    imagebutton:
        action Return()
    text "Отдохнуть"
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'choice_screen' in result
        assert len(result['choice_screen']) == 1
        
        btn = result['choice_screen'][0]
        assert btn['text'] == 'Отдохнуть'
        assert btn['action_type'] == 'return'
        assert btn['jump'] == '__return__'
        assert btn['changes'] == []

    def test_call_action_detected(self, discovery_env):
        """Call() правильно обнаруживается."""
        cheat, tmp_path = discovery_env
        label_changes = {
            'subroutine': [['var1', '+', '5']]
        }
        
        write_rpy(tmp_path, 'test.rpy', '''
screen choice_screen():
    imagebutton:
        action Call("subroutine")
    text "Выполнить"
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'choice_screen' in result
        btn = result['choice_screen'][0]
        assert btn['action_type'] == 'jump'  # Call обрабатывается как jump
        assert btn['jump'] == 'subroutine'

    def test_mixed_actions(self, discovery_env):
        """Screen с разными типами actions."""
        cheat, tmp_path = discovery_env
        label_changes = {
            'label_1': [['var1', '+', '5']],
            'label_2': [['var2', '-', '3']]
        }
        
        write_rpy(tmp_path, 'test.rpy', '''
screen mixed_screen():
    imagebutton:
        action Jump("label_1")
    text "Вариант 1"

    imagebutton:
        action Return()
    text "Отмена"

    imagebutton:
        action Call("label_2")
    text "Вариант 2"
''')
        files = get_rpy_files(cheat, tmp_path)
        result = cheat['discover_screen_choices'](files, label_changes)
        
        assert 'mixed_screen' in result
        assert len(result['mixed_screen']) == 3
        
        # Проверяем каждый тип
        btn1 = next(b for b in result['mixed_screen'] if b['text'] == 'Вариант 1')
        assert btn1['action_type'] == 'jump'
        
        btn2 = next(b for b in result['mixed_screen'] if b['text'] == 'Отмена')
        assert btn2['action_type'] == 'return'
        
        btn3 = next(b for b in result['mixed_screen'] if b['text'] == 'Вариант 2')
        assert btn3['action_type'] == 'jump'