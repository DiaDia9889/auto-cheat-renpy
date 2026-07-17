"""Тесты регулярного выражения CALC_PATTERN для парсинга присваиваний."""


class TestSimpleAssignment:
    """Простое присваивание (=)."""

    def test_integer(self, cheat):
        m = cheat['CALC_PATTERN'].search('var = 5')
        assert m is not None
        assert m.group(1) == 'var'
        assert m.group(2) == ''
        assert m.group(3) == '5'

    def test_float(self, cheat):
        m = cheat['CALC_PATTERN'].search('var = 1.5')
        assert m is not None
        assert m.group(3) == '1.5'

    def test_zero(self, cheat):
        m = cheat['CALC_PATTERN'].search('var = 0')
        assert m is not None
        assert m.group(3) == '0'


class TestPlusAssignment:
    """Присваивание с плюсом (+=)."""

    def test_plus_one(self, cheat):
        m = cheat['CALC_PATTERN'].search('var += 1')
        assert m is not None
        assert m.group(1) == 'var'
        assert m.group(2) == '+'
        assert m.group(3) == '1'

    def test_plus_large(self, cheat):
        m = cheat['CALC_PATTERN'].search('score += 100')
        assert m is not None
        assert m.group(2) == '+'
        assert m.group(3) == '100'


class TestMinusAssignment:
    """Присваивание с минусом (-=)."""

    def test_minus_one(self, cheat):
        m = cheat['CALC_PATTERN'].search('var -= 1')
        assert m is not None
        assert m.group(1) == 'var'
        assert m.group(2) == '-'
        assert m.group(3) == '1'

    def test_minus_large(self, cheat):
        m = cheat['CALC_PATTERN'].search('health -= 50')
        assert m is not None
        assert m.group(2) == '-'
        assert m.group(3) == '50'


class TestVariableNames:
    """Разные имена переменных."""

    def test_underscore_in_name(self, cheat):
        m = cheat['CALC_PATTERN'].search('my_var = 5')
        assert m is not None
        assert m.group(1) == 'my_var'

    def test_numbers_in_name(self, cheat):
        m = cheat['CALC_PATTERN'].search('var123 = 5')
        assert m is not None
        assert m.group(1) == 'var123'

    def test_rs_suffix(self, cheat):
        # Типичный паттерн для relationship stats
        m = cheat['CALC_PATTERN'].search('leiaRS += 1')
        assert m is not None
        assert m.group(1) == 'leiaRS'


class TestContextInLine:
    """Присваивание в контексте строки кода."""

    def test_with_dollar_sign(self, cheat):
        m = cheat['CALC_PATTERN'].search('$ var += 1')
        assert m is not None
        assert m.group(1) == 'var'

    def test_with_trailing_comment(self, cheat):
        m = cheat['CALC_PATTERN'].search('var += 1 # comment')
        assert m is not None
        assert m.group(3) == '1'

    def test_with_spaces(self, cheat):
        m = cheat['CALC_PATTERN'].search('  var  +=  5  ')
        assert m is not None
        assert m.group(1) == 'var'
        assert m.group(3) == '5'