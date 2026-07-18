# Auto Cheat for Ren'Py - Universal Edition

Version: 6.2 | Ren'Py: 6.99, 7.x, 8.x | Python: 2.7, 3.x | Tests: 104 passed

---

# ENGLISH

## Description

Smart auto-cheat for Ren'Py visual novels that automatically analyzes game code and displays hints with stat changes directly in choice menus and custom imagebutton screens.

## Features

- Fully automatic setup - finds all variables, functions, labels, and screens
- Menu hints - shows variable changes in menu choices with colors
- Automatic imagebutton overlay - displays hints directly on screens with choices
- Screen tracking - detects imagebutton screens via show_screen interception
- Smart caching - scans once, loads instantly from JSON after
- Translation support - works with localizations
- Colored hints - green for +=, red for -=, blue for =
- High performance with file and parsing result caching
- Flexible JSON configuration
- Detailed logs for debugging
- Compatible with Ren'Py 6.99, 7.x, 8.x
- 104 unit tests

## Installation

Copy to game/ folder:
- auto_cheat.rpy
- auto_cheat_screens.rpy

Launch game. First run will:
- Scan all .rpy files
- Find all numeric variables (default, define)
- Detect functions that modify variables
- Discover labels and their changes
- Find screens with imagebutton and link them to labels
- Save to auto_cheat_config.json

Hints appear automatically in menus. On screens with imagebutton choices, an overlay with hints appears automatically.

## How It Works

### Auto-Discovery

The script scans all .rpy files and finds:
- Variables declared with default or define
- Functions that modify variables
- Labels and their variable changes
- Screens with imagebutton and Jump/Call/Return actions

Everything is saved to auto_cheat_config.json for instant loading.

### Menu Parsing

When a menu choice appears:
1. Gets the choice text from Ren'Py
2. Finds the current scene file
3. Reads the original .rpy file
4. Extracts the code for that choice
5. Parses for variable changes
6. Adds colored hints to the text

### Automatic Imagebutton Overlay

When a screen with imagebutton choices appears:
1. Tracks active screens via show_screen/hide_screen interception
2. Checks if the active screen has choices in SCREEN_CHOICES
3. Automatically shows an overlay with all buttons and their effects
4. Hides the overlay when the screen closes

The overlay appears automatically - no button clicks needed.

## Configuration

### auto_cheat_config.json

Contains four sections:

variables - maps variable names to display names
patterns - describes how to parse function arguments
label_changes - variable changes in each label
screen_choices - imagebutton screens and their effects

### Settings in auto_cheat.rpy

At top of file:
- DEBUG_MODE - show all found variables
- DISCOVER_USED_VARIABLES - discover variables from $ assignments (default: False)
- FONT_SIZE_MODIFIER - hint text size
- LOGGING_MODE - enable/disable logging
- MAX_LOG_SIZE - max log file size before rotation

### Colors

Constants at top of auto_cheat.rpy:
- COLOR_PLUS - green for +=
- COLOR_MINUS - red for -=
- COLOR_EQUAL - blue for =
- COLOR_DEBUG - yellow for debug variables

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
- Automatic overlay appears at the bottom of the screen
- Shows all buttons and their effects without clicking

## Troubleshooting

Hints not showing:
- Check auto_cheat_parsing.log
- Ensure DEBUG_MODE = True

Overlay not appearing:
- Screen must use imagebutton with action Jump/Call/Return
- Check auto_cheat.log for errors

## Compatibility

Ren'Py 6.99.x with Python 2.7 - Full support
Ren'Py 7.x with Python 2.7 - Full support
Ren'Py 8.0+ with Python 3.9+ - Full support

## Testing

104 unit and integration tests included.

To run tests:
    cd test
    python3 run_tests.py

---

# РУССКИЙ

## Описание

Умный авто-чит для визуальных новелл на Ren'Py, который автоматически анализирует код игры и показывает подсказки с изменениями характеристик в меню выбора и кастомных экранах.

## Возможности

- Автоматическая настройка - находит все переменные, функции, label'ы и screen'ы
- Подсказки в меню - показывает изменения переменных с цветами
- Автоматический overlay для imagebutton - показывает подсказки прямо на экранах с выборами
- Отслеживание screen'ов - обнаруживает экраны через перехват show_screen
- Умное кэширование - сканирует один раз, дальше загружается мгновенно из JSON
- Поддержка переводов - работает с локализациями
- Цветные подсказки - зелёный для +=, красный для -=, синий для =
- Высокая производительность с кэшированием
- Гибкая настройка через JSON
- Подробные логи для отладки
- Совместимость с Ren'Py 6.99, 7.x, 8.x
- 104 юнит-теста

## Установка

Скопируйте в папку game/:
- auto_cheat.rpy
- auto_cheat_screens.rpy

Запустите игру. При первом запуске скрипт просканирует все файлы и сохранит результат в auto_cheat_config.json.

Подсказки появляются автоматически в меню. На экранах с imagebutton автоматически появляется overlay с подсказками.

## Как работает

### Авто-обнаружение

Скрипт сканирует все .rpy файлы и находит:
- Переменные, объявленные через default или define
- Функции, меняющие переменные
- Label'ы и их изменения переменных
- Screen'ы с imagebutton и Jump/Call/Return действиями

Всё сохраняется в auto_cheat_config.json для мгновенной загрузки.

### Парсинг меню

Когда появляется вариант меню, скрипт извлекает код для этого варианта и добавляет цветные подсказки к тексту.

### Автоматический overlay для imagebutton

Когда появляется screen с imagebutton:
1. Отслеживает активные screen'ы через перехват show_screen/hide_screen
2. Проверяет, есть ли активный screen в SCREEN_CHOICES
3. Автоматически показывает overlay со всеми кнопками и их эффектами
4. Скрывает overlay при закрытии screen'а

Overlay появляется автоматически - не нужно нажимать кнопки.

## Конфигурация

### auto_cheat_config.json

Содержит четыре секции:
- variables - сопоставляет имена переменных с отображаемыми именами
- patterns - описывает как парсить аргументы функций
- label_changes - изменения переменных в каждом label
- screen_choices - screen'ы с imagebutton и их эффекты

### Настройки в auto_cheat.rpy

В начале файла:
- DEBUG_MODE - показывать все найденные переменные
- DISCOVER_USED_VARIABLES - обнаруживать переменные из $ присваиваний (по умолчанию: False)
- FONT_SIZE_MODIFIER - размер текста подсказок
- LOGGING_MODE - включить/выключить логирование
- MAX_LOG_SIZE - максимальный размер лога перед ротацией

### Цвета

Константы в начале auto_cheat.rpy:
- COLOR_PLUS - зелёный для +=
- COLOR_MINUS - красный для -=
- COLOR_EQUAL - синий для =
- COLOR_DEBUG - жёлтый для debug переменных

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
- Автоматический overlay появляется внизу экрана
- Показывает все кнопки и их эффекты без нажатий

## Устранение неполадок

Подсказки не появляются:
- Проверьте auto_cheat_parsing.log
- Убедитесь что DEBUG_MODE = True

Overlay не появляется:
- Screen должен использовать imagebutton с action Jump/Call/Return
- Проверьте auto_cheat.log на ошибки

## Совместимость

Ren'Py 6.99.x с Python 2.7 - Полная поддержка
Ren'Py 7.x с Python 2.7 - Полная поддержка
Ren'Py 8.0+ с Python 3.9+ - Полная поддержка

## Тестирование

Включено 104 юнит- и интеграционных теста.

Для запуска:
    cd test
    python3 run_tests.py

---

Free to use in commercial and non-commercial projects.
Свободное использование в коммерческих и некоммерческих проектах.