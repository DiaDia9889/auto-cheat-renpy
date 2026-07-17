# Auto Cheat for Ren'Py

Version 6.0 - Universal Edition

Supports Ren'Py 6.99, 7.x, 8.x (Python 2.7 and 3.x)

102 unit tests passing

---

# ENGLISH

## What It Does

Smart auto-cheat for Ren'Py visual novels that automatically analyzes game code and displays hints with stat changes in choice menus and custom screens.

## Features

- Automatic setup - finds all variables, functions, labels, and screens
- Menu hints - shows variable changes in menu choices with colors
- Screen tracking - detects imagebutton screens and shows their effects
- Smart caching - scans once, loads instantly from JSON after
- Translation support - works with localizations
- Colored hints - green for +=, red for -=, blue for =
- High performance with caching
- Flexible JSON configuration
- Detailed logs for debugging
- Compatible with all Ren'Py versions
- 102 unit tests

## Installation

Copy these files to your game/ folder:
- auto_cheat.rpy
- auto_cheat_screens.rpy

Launch the game. On first run it will:
- Scan all .rpy files
- Find all numeric variables
- Detect functions that modify variables
- Discover labels and their changes
- Find screens with imagebutton
- Save everything to auto_cheat_config.json

Hints will appear automatically in menus. A CHOICES button appears on screens with imagebutton choices.

## How It Works

### Auto-Discovery

The script scans all .rpy files and finds:
- Variables declared with default or define
- Variables used in direct assignments like $ var = 0
- Functions that modify variables
- Labels and their variable changes
- Screens with imagebutton and Jump actions

Everything is saved to auto_cheat_config.json for instant loading on next run.

### Menu Parsing

When a menu choice appears:
1. Gets the choice text from Ren'Py
2. Finds the current scene file
3. Reads the original .rpy file
4. Extracts the code for that choice
5. Parses for variable changes
6. Adds colored hints to the text

### Screen Tracking

When a screen with imagebutton appears:
1. Tracks active screens via show_screen interception
2. Shows CHOICES button if screen has choices
3. Clicking it shows all buttons and their effects

## Configuration

### auto_cheat_config.json

Contains four sections:

variables - maps variable names to display names
patterns - describes how to parse function arguments
label_changes - variable changes in each label
screen_choices - imagebutton screens and their effects

You can edit this file manually to customize display names or add missing variables.

### Settings in auto_cheat.rpy

At the top of the file you can change:
- DEBUG_MODE - show all found variables
- FONT_SIZE_MODIFIER - hint text size
- LOGGING_MODE - enable/disable logging
- MAX_LOG_SIZE - max log file size before rotation

### Colors

Constants at top of auto_cheat.rpy:
- COLOR_PLUS - green for +=
- COLOR_MINUS - red for -=
- COLOR_EQUAL - blue for =
- COLOR_DEBUG - yellow for debug variables

## Log Files

auto_cheat.log - real-time parser activity, rotates at 5 MB
auto_cheat_parsing.log - auto-discovery process details

## Updating Config

If you add new variables or functions to the game:
1. Delete game/auto_cheat_config.json
2. Launch the game
3. Script rescans and updates the config

## Example

Game code:

    menu:
        "Accept":
            $ karma += 5
        "Refuse":
            $ karma -= 3

Player sees:

    Accept (karma +=5)
    Refuse (karma -=3)

With colors: green for +=, red for -=

## Screen Example

Game code:

    screen choice_screen():
        imagebutton:
            action Jump("truth_label")
        text "Tell truth"

        imagebutton:
            action Jump("lie_label")
        text "Lie"

    label truth_label:
        $ karma += 5

    label lie_label:
        $ karma -= 3

Player sees:
- CHOICES button in bottom-right corner
- Clicking shows panel with all buttons and their effects

## Troubleshooting

Hints not showing:
- Check auto_cheat_parsing.log
- Ensure DEBUG_MODE = True

Wrong values:
- Check auto_cheat_config.json
- Verify VAR and VAL order matches function call

CHOICES button not appearing:
- Screen must use imagebutton with action Jump(...)
- Other action types not supported

## Compatibility

Ren'Py 6.99.x with Python 2.7 - Full support
Ren'Py 7.x with Python 2.7 - Full support
Ren'Py 8.0+ with Python 3.9+ - Full support

## Testing

102 unit and integration tests included.

To run tests:
    cd test
    python3 run_tests.py

Tests cover menu parsing, text normalization, function parsing, label discovery, screen discovery, and edge cases.

---

# РУССКИЙ

## Что делает

Умный авто-чит для визуальных новелл на Ren'Py, который автоматически анализирует код игры и показывает подсказки с изменениями характеристик в меню выбора и кастомных экранах.

## Возможности

- Автоматическая настройка - находит все переменные, функции, label'ы и screen'ы
- Подсказки в меню - показывает изменения переменных с цветами
- Отслеживание screen'ов - обнаруживает экраны с imagebutton и показывает их эффекты
- Умное кэширование - сканирует один раз, дальше загружается мгновенно из JSON
- Поддержка переводов - работает с локализациями
- Цветные подсказки - зелёный для +=, красный для -=, синий для =
- Высокая производительность с кэшированием
- Гибкая настройка через JSON
- Подробные логи для отладки
- Совместимость со всеми версиями Ren'Py
- 102 юнит-теста

## Установка

Скопируйте в папку game/:
- auto_cheat.rpy
- auto_cheat_screens.rpy

Запустите игру. При первом запуске:
- Просканирует все .rpy файлы
- Найдёт все числовые переменные
- Обнаружит функции, меняющие переменные
- Найдёт label'ы и их изменения
- Найдёт screen'ы с imagebutton
- Сохранит всё в auto_cheat_config.json

Подсказки появятся автоматически. Кнопка CHOICES появится на экранах с imagebutton.

## Как работает

### Авто-обнаружение

Скрипт сканирует все .rpy файлы и находит:
- Переменные, объявленные через default или define
- Переменные в присваиваниях типа $ var = 0
- Функции, меняющие переменные
- Label'ы и их изменения переменных
- Screen'ы с imagebutton и Jump действиями

Всё сохраняется в auto_cheat_config.json для мгновенной загрузки при следующем запуске.

### Парсинг меню

Когда появляется вариант меню:
1. Получает текст варианта от Ren'Py
2. Находит текущий файл сцены
3. Читает оригинальный .rpy файл
4. Извлекает код для этого варианта
5. Парсит на предмет изменений переменных
6. Добавляет цветные подсказки к тексту

### Отслеживание screen'ов

Когда появляется screen с imagebutton:
1. Отслеживает активные screen'ы через перехват show_screen
2. Показывает кнопку CHOICES если screen имеет выборы
3. При нажатии показывает все кнопки и их эффекты

## Конфигурация

### auto_cheat_config.json

Содержит четыре секции:

variables - сопоставляет имена переменных с отображаемыми именами
patterns - описывает как парсить аргументы функций
label_changes - изменения переменных в каждом label
screen_choices - screen'ы с imagebutton и их эффекты

Можно редактировать вручную для настройки отображаемых имён или добавления недостающих переменных.

### Настройки в auto_cheat.rpy

В начале файла можно изменить:
- DEBUG_MODE - показывать все найденные переменные
- FONT_SIZE_MODIFIER - размер текста подсказок
- LOGGING_MODE - включить/выключить логирование
- MAX_LOG_SIZE - максимальный размер лога перед ротацией

### Цвета

Константы в начале auto_cheat.rpy:
- COLOR_PLUS - зелёный для +=
- COLOR_MINUS - красный для -=
- COLOR_EQUAL - синий для =
- COLOR_DEBUG - жёлтый для debug переменных

## Файлы логов

auto_cheat.log - активность парсера в реальном времени, ротируется при 5 МБ
auto_cheat_parsing.log - детали процесса авто-обнаружения

## Обновление конфига

Если добавили новые переменные или функции в игру:
1. Удалите game/auto_cheat_config.json
2. Запустите игру
3. Скрипт пересканирует и обновит конфиг

## Пример

Код игры:

    menu:
        "Принять":
            $ karma += 5
        "Отклонить":
            $ karma -= 3

Игрок видит:

    Принять (karma +=5)
    Отклонить (karma -=3)

С цветами: зелёный для +=, красный для -=

## Пример screen'а

Код игры:

    screen choice_screen():
        imagebutton:
            action Jump("truth_label")
        text "Сказать правду"

        imagebutton:
            action Jump("lie_label")
        text "Солгать"

    label truth_label:
        $ karma += 5

    label lie_label:
        $ karma -= 3

Игрок видит:
- Кнопку CHOICES в правом нижнем углу
- При нажатии открывается панель со всеми кнопками и их эффектами

## Устранение неполадок

Подсказки не появляются:
- Проверьте auto_cheat_parsing.log
- Убедитесь что DEBUG_MODE = True

Неправильные значения:
- Проверьте auto_cheat_config.json
- Убедитесь что порядок VAR и VAL соответствует вызову функции

Кнопка CHOICES не появляется:
- Screen должен использовать imagebutton с action Jump(...)
- Другие типы действий не поддерживаются

## Совместимость

Ren'Py 6.99.x с Python 2.7 - Полная поддержка
Ren'Py 7.x с Python 2.7 - Полная поддержка
Ren'Py 8.0+ с Python 3.9+ - Полная поддержка

## Тестирование

Включено 102 юнит- и интеграционных теста.

Для запуска тестов:
    cd test
    python3 run_tests.py

Тесты покрывают парсинг меню, нормализацию текста, парсинг функций, обнаружение label'ов, обнаружение screen'ов и граничные случаи.

---

Free to use in commercial and non-commercial projects.
Свободное использование в коммерческих и некоммерческих проектах.