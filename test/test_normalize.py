"""Тесты функции normalize_text — удаление тегов и нормализация кавычек."""


class TestTagRemoval:
    """Удаление Ren'Py тегов."""

    def test_simple_color_tag(self, cheat):
        result = cheat['normalize_text']('{color=#fff}hello{/color}')
        assert result == 'hello'

    def test_nested_tags(self, cheat):
        text = '{color=#00FF00}{size=-15}(+1 pervy){/size}{/color}'
        result = cheat['normalize_text'](text)
        assert result == '(+1 pervy)'

    def test_deeply_nested_tags(self, cheat):
        text = '{a}{b}{c}deep{/c}{/b}{/a}'
        result = cheat['normalize_text'](text)
        assert result == 'deep'

    def test_mixed_content_with_tags(self, cheat):
        text = 'Странные девушки.{color=#00FF00}{size=-15}(+1 pervy){/color}'
        result = cheat['normalize_text'](text)
        assert result == 'Странные девушки.(+1 pervy)'

    def test_no_tags(self, cheat):
        result = cheat['normalize_text']('Just plain text')
        assert result == 'Just plain text'

    def test_italic_and_bold(self, cheat):
        result = cheat['normalize_text']('{i}{b}test{/b}{/i}')
        assert result == 'test'


class TestSmartQuotes:
    """Нормализация умных кавычек."""

    def test_smart_single_quote(self, cheat):
        result = cheat['normalize_text'](u"didn’t")
        assert result == "didn't"

    def test_smart_double_quotes(self, cheat):
        result = cheat['normalize_text'](u"“hello”")
        assert result == '"hello"'

    def test_em_dash(self, cheat):
        result = cheat['normalize_text'](u"hello—world")
        assert result == "hello-world"

    def test_en_dash(self, cheat):
        result = cheat['normalize_text'](u"1–2")
        assert result == "1-2"


class TestCombined:
    """Комбинация тегов и умных кавычек."""

    def test_tags_and_smart_quotes(self, cheat):
        text = u'{color=#fff}She said “hello”{/color}'
        result = cheat['normalize_text'](text)
        assert result == 'She said "hello"'

    def test_complex_real_world_example(self, cheat):
        text = u'Странные девушки.{color=#00FF00}{size=-15}(+1 pervy){/size}{/color}'
        result = cheat['normalize_text'](text)
        assert 'Странные девушки' in result
        assert '(+1 pervy)' in result
        assert '{' not in result
        assert '}' not in result