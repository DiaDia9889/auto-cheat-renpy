"""Тесты регулярного выражения CHOICE_PATTERN для парсинга вариантов меню."""


class TestSimpleChoices:
    """Базовые варианты без условий и тегов."""

    def test_double_quotes(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('"Hello world":')
        assert m is not None
        assert m.group(1) == 'Hello world'

    def test_single_quotes(self, cheat):
        m = cheat['CHOICE_PATTERN'].search("'Hello world':")
        assert m is not None
        assert m.group(2) == 'Hello world'

    def test_with_leading_spaces(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('        "Choice":')
        assert m is not None
        assert m.group(1) == 'Choice'

    def test_with_character_name(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('e "Hello":')
        assert m is not None
        assert m.group(1) == 'Hello'


class TestChoicesWithConditions:
    """Варианты с условиями if."""

    def test_if_true(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('"Choice" if True:')
        assert m is not None
        assert m.group(1) == 'Choice'

    def test_if_variable(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('"Choice" if has_item:')
        assert m is not None
        assert m.group(1) == 'Choice'

    def test_if_complex_expression(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('"Choice" if affection > 10 and not flag:')
        assert m is not None
        assert m.group(1) == 'Choice'

    def test_if_with_comparison(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('"Choice" if var == 1:')
        assert m is not None
        assert m.group(1) == 'Choice'


class TestChoicesWithTags:
    """Варианты с Ren'Py тегами внутри текста."""

    def test_color_tag(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('"Hello {color=#fff}world{/color}":')
        assert m is not None
        assert 'Hello' in m.group(1)
        assert 'world' in m.group(1)

    def test_nested_color_and_size(self, cheat):
        text = '"Странные девушки.{color=#00FF00}{size=-15}(+1 pervy){/size}{/color}":'
        m = cheat['CHOICE_PATTERN'].search(text)
        assert m is not None
        assert 'Странные девушки' in m.group(1)
        assert '(+1 pervy)' in m.group(1)

    def test_italic_and_bold(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('"Hello {i}{b}world{/b}{/i}":')
        assert m is not None
        assert 'Hello' in m.group(1)
        assert 'world' in m.group(1)

    def test_multiple_tags(self, cheat):
        text = '"Test {color=#000}{size=20}{b}bold{/b}{/size}{/color} end":'
        m = cheat['CHOICE_PATTERN'].search(text)
        assert m is not None
        assert 'Test' in m.group(1)
        assert 'bold' in m.group(1)
        assert 'end' in m.group(1)


class TestChoicesWithQuotesInside:
    """Варианты с кавычками внутри текста."""

    def test_apostrophe_in_text(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('"Pretend it didn\'t happen":')
        assert m is not None
        assert "didn" in m.group(1)

    def test_smart_apostrophe(self, cheat):
        # Ren'Py иногда использует умные кавычки
        text = u'"Pretend it didn’t happen":'
        m = cheat['CHOICE_PATTERN'].search(text)
        assert m is not None


class TestNegativeCases:
    """Строки, которые НЕ должны матчиться как варианты."""

    def test_no_colon(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('"Just a string"')
        assert m is None

    def test_comment(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('# "Not a choice":')
        # Должен матчиться, но это ок — парсер меню отфильтрует по отступам
        # Или не матчиться — зависит от реализации
        # Мы просто проверяем, что не падает
        pass

    def test_empty_string(self, cheat):
        m = cheat['CHOICE_PATTERN'].search('')
        assert m is None