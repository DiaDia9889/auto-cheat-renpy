# 🧪 Auto Cheat — Тесты

Набор юнит- и интеграционных тестов для `auto_cheat.rpy`.

## 📋 Что тестируется

| Файл теста | Что проверяет |
|---|---|
| `test_choice_pattern.py` | Regex для парсинга вариантов меню (с `if`, тегами, кавычками) |
| `test_normalize.py` | Удаление Ren'Py тегов и нормализация умных кавычек |
| `test_function_parser.py` | AST-парсер вызовов функций (`add_points`, и т.д.) |
| `test_calc_pattern.py` | Regex для парсинга `=`, `+=`, `-=` |
| `test_menu_parser.py` | Интеграционные тесты полного парсера меню |

## 🚀 Запуск тестов

### Вариант 1: Через скрипт (проще всего)

```bash
cd test
python run_tests.py
```

Скрипт сам установит `pytest`, если его нет, и запустит все тесты.

### Вариант 2: Напрямую через pytest

```bash
# Установка pytest (если ещё не установлен)
pip install pytest

# Запуск всех тестов
cd test
pytest -v

# Запуск конкретного файла
pytest test_choice_pattern.py -v

# Запуск конкретного теста
pytest test_choice_pattern.py::TestChoicesWithConditions::test_if_true -v

# Запуск тестов по ключевому слову
pytest -k "tags" -v
```

## 🏗️ Как это работает

Тесты **не требуют запуска Ren'Py**. Вместо этого:

1. `conftest.py` читает `auto_cheat.rpy`
2. Извлекает блок `init python:`
3. Подменяет Ren'Py API (`renpy.store`, `renpy.get_filename_line`, `config.gamedir` и т.д.) на моки
4. Выполняет код в изолированном namespace
5. Делает все функции доступными через фикстуру `cheat`

Это позволяет тестировать **чистую логику** парсера без зависимости от движка.

## 📂 Структура

```
test/
├── conftest.py              # Загрузчик и моки Ren'Py
├── test_choice_pattern.py   # Тесты regex вариантов меню
├── test_normalize.py        # Тесты нормализации текста
├── test_function_parser.py  # Тесты AST-парсера функций
├── test_calc_pattern.py     # Тесты regex присваиваний
├── test_menu_parser.py      # Интеграционные тесты
├── run_tests.py             # Скрипт запуска
└── README.md                # Этот файл
```

## 🔧 Добавление новых тестов

1. Создайте новый файл `test_<feature>.py` в папке `test/`
2. Используйте фикстуру `cheat` для доступа к функциям:
   ```python
   def test_my_feature(cheat):
       result = cheat['my_function'](args)
       assert result == expected
   ```
3. Для интеграционных тестов используйте `setup_test_env`:
   ```python
   def test_full_parsing(setup_test_env):
       cheat, tmp_path = setup_test_env
       # ... создайте .rpy файл и проверьте core_menu_parser
   ```

## ❓ Частые проблемы

**Q: Тесты не находят `auto_cheat.rpy`**  
A: Убедитесь, что `auto_cheat.rpy` находится в родительской директории относительно папки `test/`.

**Q: Ошибка `ModuleNotFoundError: pytest`**  
A: Запустите `pip install pytest` или используйте `python run_tests.py` — он установит сам.

**Q: Тесты проходят локально, но падают на CI**  
A: Проверьте, что кодировка файлов UTF-8. В Windows может потребоваться `set PYTHONIOENCODING=utf-8`.

## 📊 Покрытие

Тесты покрывают все ключевые сценарии:
- ✅ Простые варианты меню
- ✅ Варианты с условиями `if`
- ✅ Варианты с Ren'Py тегами (`{color}`, `{size}`, `{i}`, `{b}`)
- ✅ Вложенные теги
- ✅ Умные кавычки
- ✅ Вызовы функций с разными паттернами
- ✅ Присваивания `=`, `+=`, `-=`
- ✅ Отрицательные значения
- ✅ Несколько меню в одном файле
- ✅ Граничные случаи (пустые строки, синтаксические ошибки)