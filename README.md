# Auto Cheat for Ren'Py - Universal Edition

Version: 5.3 | Ren'Py: 6.99, 7.x, 8.x | Python: 2.7, 3.x

---

# ENGLISH

## Description

Smart auto-cheat for Ren'Py visual novels that automatically analyzes game code, finds all variables and functions, and displays hints with stat changes directly in choice menus.

## Features

- Fully automatic setup - finds all variables and functions
- Smart caching - scanning happens once, loads from JSON after
- Translation support - works with localizations
- Colored hints - green for +=, red for -=, blue for =
- High performance with file and parsing cache
- Flexible configuration via JSON
- Detailed logs for debugging
- Compatible with Ren'Py 6.99, 7.x, 8.x

## Installation

1. Copy to game/ folder:
   - auto_cheat.rpy
   - auto_cheat_screens.rpy

2. Launch game. First run will:
   - Scan all .rpy files
   - Find numeric variables (default, define)
   - Detect functions that modify variables
   - Save to auto_cheat_config.json

3. Hints will appear in choice menus

## How It Works

1. Auto-Discovery: Scans .rpy files (ignoring tl/ folder) for lines like:
   default lilyRS = 0

2. Pattern Detection: Parses lines with $ using Python AST. If function call has known variable name (string) and number, generates pattern:
   $ add_points("lilyRS", 5, "img.webp") -> "add_points": "VAR, VAL, _"

3. Real-time Parsing: When menu appears, reads original .rpy file, extracts code block, parses it, injects colored hints

4. Caching: Files and parsed menus cached in memory and disk (auto_cheat_config.json)

## Configuration

### auto_cheat_config.json

Structure:
{
    "variables": {
        "lilyRS": "Lily Relationship",
        "brookeRS": "Brooke Relationship"
    },
    "patterns": {
        "add_points": "VAR, VAL, _",
        "change_stat": "VAR, VAL"
    }
}

Variables: Map of {real_name: "Display Name"}
Patterns: How to parse function arguments
  VAR = Variable name (string)
  VAL = Numeric value
  _ = Ignore argument

### auto_cheat.rpy Settings

At top of file:
DEBUG_MODE = True          # Show ALL found variables
FONT_SIZE_MODIFIER = -4    # Hint font size (negative = smaller)
LOGGING_MODE = True        # Enable/disable logging
MAX_LOG_SIZE = 5242880     # Max log size (5 MB) before rotation

### Color Scheme

Constants at top of auto_cheat.rpy:
COLOR_PLUS = "#2ecc71"    # Green for +=
COLOR_MINUS = "#e74c3c"   # Red for -=
COLOR_EQUAL = "#3498db"   # Blue for =
COLOR_DEBUG = "#f1c40f"   # Yellow for DEBUG

## Log Files

auto_cheat.log: Real-time parser activity (errors, hints). Rotates at 5 MB.
auto_cheat_parsing.log: Auto-discovery process (scanned files, variables, patterns).

## Updating Config

If you add new variables or functions:
1. Delete game/auto_cheat_config.json
2. Launch game
3. Script will rescan and update config

## Troubleshooting

Hints not showing:
- Check auto_cheat_parsing.log for found variables
- Ensure DEBUG_MODE = True

Wrong values in hints:
- Check auto_cheat_config.json
- Ensure VAR and VAL order matches actual function call

Syntax errors (f-strings):
- Using outdated script version
- Update to v5.2+

Lag on first menu open:
- Normal - game scanning files
- Subsequent opens will be instant

## Compatibility

Ren'Py 6.99.x + Python 2.7: Full Support
Ren'Py 7.x + Python 2.7: Full Support
Ren'Py 8.0+ + Python 3.9+: Full Support

## Example

Game Code:
menu:
    "Pretend it didn't happen":
        $ add_points("leiaRS", 1, "images/heart.webp")
        $ miaRS += 1

Player sees:
Pretend it didn't happen (leiaRS +=1, miaRS +=1)
With colors: leiaRS and miaRS in green

---

# РУССКИЙ

## Описание

Умный авто-чит для визуальных новелл на Ren'Py, который автоматически анализирует код игры, находит все переменные и функции и выводит подсказки с изменениями характеристик прямо в меню выбора.

## Возможности

- Полностью автоматическая настройка - находит все переменные и функции
- Умное кэширование - сканирование один раз, далее загрузка из JSON
- Поддержка переводов - работает с локализациями
- Цветные подсказки - зелёный для +=, красный для -=, синий для =
- Высокая производительность с кэшированием файлов и парсинга
- Гибкая настройка через JSON
- Подробные логи для отладки
- Совместимость с Ren'Py 6.99, 7.x, 8.x

## Установка

1. Скопируйте в папку game/:
   - auto_cheat.rpy
   - auto_cheat_screens.rpy

2. Запустите игру. Первый запуск:
   - Просканирует все .rpy файлы
   - Найдёт числовые переменные (default, define)
   - Обнаружит функции, меняющие переменные
   - Сохранит в auto_cheat_config.json

3. Подсказки появятся в меню выбора

## Как это работает

1. Авто-обнаружение: Сканирует .rpy файлы (игнорируя папку tl/) в поисках строк:
   default lilyRS = 0

2. Определение паттернов: Парсит строки с $ через Python AST. Если вызов функции содержит имя известной переменной (строка) и число, генерирует паттерн:
   $ add_points("lilyRS", 5, "img.webp") -> "add_points": "VAR, VAL, _"

3. Парсинг в реальном времени: При появлении меню читает оригинальный .rpy файл, извлекает блок кода, парсит его, внедряет цветные подсказки

4. Кэширование: Файлы и распарсенные меню кэшируются в памяти и на диске (auto_cheat_config.json)

## Конфигурация

### auto_cheat_config.json

Структура:
{
    "variables": {
        "lilyRS": "Отношения с Лили",
        "brookeRS": "Отношения с Брук"
    },
    "patterns": {
        "add_points": "VAR, VAL, _",
        "change_stat": "VAR, VAL"
    }
}

Variables: Словарь {реальное_имя: "Отображаемое имя"}
Patterns: Как парсить аргументы функций
  VAR = Имя переменной (строка)
  VAL = Числовое значение
  _ = Игнорировать аргумент

### Настройки в auto_cheat.rpy

В начале файла:
DEBUG_MODE = True          # Показывать ВСЕ найденные переменные
FONT_SIZE_MODIFIER = -4    # Размер шрифта подсказок (отрицательный = меньше)
LOGGING_MODE = True        # Включить/выключить логирование
MAX_LOG_SIZE = 5242880     # Макс. размер лога (5 МБ) перед ротацией

### Цветовая схема

Константы в начале auto_cheat.rpy:
COLOR_PLUS = "#2ecc71"    # Зелёный для +=
COLOR_MINUS = "#e74c3c"   # Красный для -=
COLOR_EQUAL = "#3498db"   # Синий для =
COLOR_DEBUG = "#f1c40f"   # Жёлтый для DEBUG

## Файлы логов

auto_cheat.log: Активность парсера в реальном времени (ошибки, подсказки). Ротируется при 5 МБ.
auto_cheat_parsing.log: Процесс авто-обнаружения (просканированные файлы, переменные, паттерны).

## Обновление конфига

Если добавили новые переменные или функции:
1. Удалите game/auto_cheat_config.json
2. Запустите игру
3. Скрипт просканирует всё заново и обновит конфиг

## Устранение неполадок

Подсказки не появляются:
- Проверьте auto_cheat_parsing.log на наличие найденных переменных
- Убедитесь, что DEBUG_MODE = True

Неправильные значения в подсказках:
- Проверьте auto_cheat_config.json
- Убедитесь, что порядок VAR и VAL соответствует реальному вызову функции

Ошибки синтаксиса (f-strings):
- Используете устаревшую версию скрипта
- Обновитесь до v5.2+

Подтормаживание при первом открытии меню:
- Это нормально - игра сканирует файлы
- Последующие открытия будут мгновенными

## Совместимость

Ren'Py 6.99.x + Python 2.7: Полная поддержка
Ren'Py 7.x + Python 2.7: Полная поддержка
Ren'Py 8.0+ + Python 3.9+: Полная поддержка

## Пример

Код игры:
menu:
    "Pretend it didn't happen":
        $ add_points("leiaRS", 1, "images/heart.webp")
        $ miaRS += 1

Что видит игрок:
Pretend it didn't happen (leiaRS +=1, miaRS +=1)
С цветами: leiaRS и miaRS зелёным цветом

---

Free to use in commercial and non-commercial projects. Attribution appreciated but not required.
Свободное использование в коммерческих и некоммерческих проектах. Указание авторства приветствуется, но не обязательно.
