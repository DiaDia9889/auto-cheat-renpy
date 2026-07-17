"""Тесты AST-парсера вызовов функций parse_function_call_args."""


class TestSimpleCalls:
    """Простые вызовы функций."""

    def test_var_val_underscore(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['add_points'] = 'VAR, VAL, _'
        result = cheat['parse_function_call_args']('$ add_points("var1", 5, "img.png")')
        assert result == ('var1', '+', '5')

    def test_negative_value(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['add_points'] = 'VAR, VAL, _'
        result = cheat['parse_function_call_args']('$ add_points("var1", -3, "img.png")')
        assert result == ('var1', '', '-3')

    def test_zero_value(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['add_points'] = 'VAR, VAL, _'
        result = cheat['parse_function_call_args']('$ add_points("var1", 0, "img.png")')
        assert result == ('var1', '+', '0')

    def test_large_number(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['add_points'] = 'VAR, VAL, _'
        result = cheat['parse_function_call_args']('$ add_points("var1", 9999, "img.png")')
        assert result == ('var1', '+', '9999')


class TestDifferentPatterns:
    """Различные паттерны аргументов."""

    def test_val_var_order(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['give_score'] = 'VAL, VAR'
        result = cheat['parse_function_call_args']('$ give_score(10, "score")')
        assert result == ('score', '+', '10')

    def test_var_val_only(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['add_stat'] = 'VAR, VAL'
        result = cheat['parse_function_call_args']('$ add_stat("hp", 20)')
        assert result == ('hp', '+', '20')

    def test_multiple_underscores(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['complex_func'] = 'VAR, _, VAL, _'
        result = cheat['parse_function_call_args']('$ complex_func("var", "skip", 42, "skip2")')
        assert result == ('var', '+', '42')


class TestEdgeCases:
    """Граничные случаи."""

    def test_without_dollar_sign(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['add_points'] = 'VAR, VAL, _'
        result = cheat['parse_function_call_args']('add_points("var1", 5, "img.png")')
        assert result == ('var1', '+', '5')

    def test_unknown_function(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['known_func'] = 'VAR, VAL'
        result = cheat['parse_function_call_args']('$ unknown_func("var", 1)')
        assert result is None

    def test_not_a_function_call(self, cheat_fresh):
        cheat = cheat_fresh
        result = cheat['parse_function_call_args']('$ x = 5')
        assert result is None

    def test_empty_line(self, cheat_fresh):
        cheat = cheat_fresh
        result = cheat['parse_function_call_args']('')
        assert result is None

    def test_syntax_error_in_code(self, cheat_fresh):
        cheat = cheat_fresh
        result = cheat['parse_function_call_args']('$ this is not valid python!!!')
        assert result is None

    def test_method_call(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['add'] = 'VAR, VAL'
        # obj.method() — func.attr вместо func.id
        result = cheat['parse_function_call_args']('$ obj.add("var", 5)')
        assert result == ('var', '+', '5')


class TestFloatValues:
    """Числа с плавающей точкой."""

    def test_float_value(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['add_points'] = 'VAR, VAL, _'
        result = cheat['parse_function_call_args']('$ add_points("var1", 1.5, "img.png")')
        assert result == ('var1', '+', '1.5')

    def test_negative_float(self, cheat_fresh):
        cheat = cheat_fresh
        cheat['FUNCTION_PARSER_PATTERNS']['add_points'] = 'VAR, VAL, _'
        result = cheat['parse_function_call_args']('$ add_points("var1", -2.5, "img.png")')
        assert result == ('var1', '', '-2.5')