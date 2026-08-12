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

class TestBooleanAssignment:
    """Присваивание булевых значений (True/False)."""

    def test_assign_true(self, cheat):
        m = cheat['CALC_PATTERN'].search('emmeline_interest = True')
        assert m is not None
        assert m.group(1) == 'emmeline_interest'
        assert m.group(2) == ''
        assert m.group(3) == 'True'

    def test_assign_false(self, cheat):
        m = cheat['CALC_PATTERN'].search('emmeline_interest = False')
        assert m is not None
        assert m.group(1) == 'emmeline_interest'
        assert m.group(2) == ''
        assert m.group(3) == 'False'

    def test_true_with_dollar_sign(self, cheat):
        m = cheat['CALC_PATTERN'].search('$ emmeline_interest = True')
        assert m is not None
        assert m.group(1) == 'emmeline_interest'
        assert m.group(3) == 'True'

    def test_false_with_dollar_sign(self, cheat):
        m = cheat['CALC_PATTERN'].search('$ has_met_anna = False')
        assert m is not None
        assert m.group(1) == 'has_met_anna'
        assert m.group(3) == 'False'

    def test_true_with_underscore_variable(self, cheat):
        m = cheat['CALC_PATTERN'].search('quest_started = True')
        assert m is not None
        assert m.group(1) == 'quest_started'
        assert m.group(3) == 'True'

    def test_false_with_camel_case_variable(self, cheat):
        m = cheat['CALC_PATTERN'].search('isReady = False')
        assert m is not None
        assert m.group(1) == 'isReady'
        assert m.group(3) == 'False'


class TestBooleanEdgeCases:
    """Граничные случаи для булевых значений."""

    def test_true_case_sensitive(self, cheat):
        """true/TRUE не должны матчиться (Ren'Py использует True/False)."""
        m = cheat['CALC_PATTERN'].search('var = true')
        assert m is None

    def test_false_case_sensitive(self, cheat):
        m = cheat['CALC_PATTERN'].search('var = FALSE')
        assert m is None

    def test_true_as_part_of_word_not_matched(self, cheat):
        """TrueX не должен матчиться как True."""
        m = cheat['CALC_PATTERN'].search('var = TrueStory')
        assert m is None

    def test_true_with_trailing_comment(self, cheat):
        m = cheat['CALC_PATTERN'].search('$ flag = True # set flag')
        assert m is not None
        assert m.group(1) == 'flag'
        assert m.group(3) == 'True'

    def test_false_with_trailing_comment(self, cheat):
        m = cheat['CALC_PATTERN'].search('$ flag = False # reset')
        assert m is not None
        assert m.group(1) == 'flag'
        assert m.group(3) == 'False'

    def test_spaces_around_equals_with_true(self, cheat):
        m = cheat['CALC_PATTERN'].search('  var  =  True  ')
        assert m is not None
        assert m.group(1) == 'var'
        assert m.group(3) == 'True'


class TestMixedAssignments:
    """Числа и булевы значения в одном файле не конфликтуют."""

    def test_number_still_works(self, cheat):
        """Убеждаемся, что числа по-прежнему матчатся после добавления True/False."""
        m = cheat['CALC_PATTERN'].search('score += 10')
        assert m is not None
        assert m.group(2) == '+'
        assert m.group(3) == '10'

    def test_float_still_works(self, cheat):
        m = cheat['CALC_PATTERN'].search('speed = 2.5')
        assert m is not None
        assert m.group(3) == '2.5'

    def test_zero_not_confused_with_false(self, cheat):
        m = cheat['CALC_PATTERN'].search('counter = 0')
        assert m is not None
        assert m.group(3) == '0'

    def test_boolean_not_confused_with_number(self, cheat):
        m = cheat['CALC_PATTERN'].search('flag = True')
        assert m is not None
        assert m.group(3) == 'True'
        assert m.group(3) != '0'