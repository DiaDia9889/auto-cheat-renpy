## [6.2] — 2026-07-18
### Added
- **Automatic Imagebutton Overlay System:** Implemented real-time overlay that automatically displays variable change hints on screens with imagebutton choices, eliminating the need to click a separate CHOICES button.
- **Screen Activity Validation:** Added comprehensive checks in `imagebutton_overlay_tracker` to ensure overlay only appears when:
  - A current choice screen is active (`_current_choice_screen` is set)
  - The screen exists in `SCREEN_CHOICES` configuration
  - The screen is actually being displayed (verified via `renpy.get_screen()`)
- **Automatic Overlay Cleanup:** Overlay automatically hides when the associated screen closes or when no valid choice screen is active.
- **Return/Call Action Support:** Extended screen choice parser to detect and properly handle `action Return()` and `action Call(...)` in addition to `action Jump(...)`.

### Changed
- **Overlay Display Logic:** Replaced manual CHOICES button interaction with automatic overlay display that appears instantly when choice screens are shown.
- **Screen Tracking Robustness:** Enhanced `_current_choice_screen` management to properly clear state when screens close, preventing stale overlay displays.

### Fixed
- **Overlay Persistence Bug:** Resolved issue where overlay would remain visible even after choice screens closed, by adding proper cleanup logic in `imagebutton_overlay_tracker`.
- **Screen Validation:** Added checks to prevent overlay from showing on screens without choices or when no screen is active.

---

## [6.1] — 2026-07-18
### Changed
- **Centralized Style Constants:** Migrated all color values to Python constants (`CC_GOLD`, `CC_RED`, `CC_GREEN`, etc.) and Ren'Py style definitions for easier customization.
- **Version Tracking:** Added `CHEAT_VERSION` constant for single-point version updates.
- **Code Deduplication:** Extracted repeated text/frame properties into reusable style definitions.

---

## [6.0] — 2026-07-18
### Added
- **Screen Choice Tracking System:** Implemented a comprehensive interception layer via `renpy.show_screen()` / `renpy.hide_screen()` monkey-patching to track active visual screens in real-time.
- **Label Discovery Engine:** Added a recursive `.rpy` scanner that parses all `label` blocks and extracts variable mutations from the first 30 lines of each label body.
- **ImageButton Screen Parser:** Introduced an automated detector that scans `screen` definitions for `imagebutton` elements with `action Jump(...)` directives, linking button text to their target labels and discovered variable changes.
- **CHOICES Overlay Indicator:** Deployed a persistent bottom-right corner button (`screen_choice_indicator`) that appears dynamically when an active screen contains imagebutton choices, opening a detailed modal panel listing all available options and their stat effects.
- **Used Variable Discovery:** Extended the auto-discovery pipeline to detect variables used in direct assignments (`$ var = value`) even when not declared via `default` or `define`, ensuring complete coverage of gameplay state mutations.
- **Comprehensive Test Suite:** Integrated 102 unit and integration tests covering menu parsing, text normalization, AST function parsing, label discovery, screen discovery, and edge cases with automated `venv` bootstrapping.

### Changed
- **Config Schema Expansion:** Extended `auto_cheat_config.json` with two new sections: `label_changes` (label-to-variable-changes mapping) and `screen_choices` (screen-to-button-effects mapping).
- **Screen Tracking Architecture:** Replaced the cumulative `_active_screens` set with a single `_current_choice_screen` variable to ensure only the currently visible screen's choices are displayed.

---

## [5.6] — 2026-07-18
### Fixed
- **Tag-Key Dictionary Mismatch:** Resolved a critical lookup bug where normalized caption text (tags stripped) was used as a dictionary key to access menu blocks whose keys retained original Ren'Py tags. The parser now stores the original key alongside the normalized match, ensuring correct code block extraction for choices containing `{color=...}`, `{size=...}`, and other inline tags.

---

## [5.5] — 2026-07-18
### Fixed
- **Nested Ren'Py Tag Normalization:** Replaced the single-pass `TAG_PATTERN` regex substitution with an iterative `while` loop that recursively strips nested tag structures (e.g., `{color=#00FF00}{size=-15}(+1 pervy){/size}{/color}`) until no braces remain.
- **Caption Comparison Robustness:** Enhanced the menu variant matching logic to compare normalized versions of both the incoming caption and the file-extracted choice text, preventing false negatives when Ren'Py tags are present in source but stripped at runtime.

---

## [5.4] — 2026-07-18
### Added
- **Conditional Menu Syntax Support:** Extended `CHOICE_PATTERN` regex to parse Ren'Py's conditional choice syntax (`"text" if condition:`), enabling correct extraction of options with inline guards like `"Choice" if True:` or `"Choice" if has_item:`.
- **Explicit Log Initialization:** Added proactive log file creation at script startup to ensure `auto_cheat.log` and `auto_cheat_parsing.log` exist before any write operations, preventing silent failures on fresh installations.

---

## [5.3] — 2026-07-18
### Changed
- **Color Constant Extraction:** Migrated all hardcoded hex color values from inline string formatting to named module-level constants (`COLOR_PLUS`, `COLOR_MINUS`, `COLOR_EQUAL`, `COLOR_DEBUG`), enabling single-point customization of the visual hint palette.

---

## [5.2] — 2026-07-18
### Fixed
- **Python 2.7 Full Compatibility:** Eliminated all remaining f-string syntax (`f"..."`) replacing them with `.format()` calls throughout the codebase, ensuring clean execution on Ren'Py 6.99.x / Python 2.7 interpreters.
- **Safe UTF-8 File I/O:** Introduced `read_file_text()` and `write_file_text()` helper functions that abstract encoding handling across Python versions — using binary mode with explicit `.decode('utf-8')` / `.encode('utf-8')` on Python 2, and native `encoding='utf-8'` parameter on Python 3.

---

## [5.1] — 2026-07-18
### Fixed
- **Indented Variable Declaration Discovery:** Corrected the `var_pattern` regex to use `^\s*` prefix matching, allowing detection of `default` and `define` statements nested inside `label` blocks or other indented scopes.
- **Persistent Variable Exclusion:** Added `(?!persistent\.)` negative lookahead to the variable discovery regex, preventing `persistent.*` variables from polluting the cheat panel.
- **Global Function Pattern Discovery:** Expanded the function call scanner from menu-only contexts to all `$`-prefixed lines across the entire game codebase, capturing patterns from labels, init blocks, and conditional branches.

---

## [5.0] — 2026-07-18
### Added
- **Smart Auto-Discovery System:** Implemented a multi-phase automated configuration engine that eliminates manual setup:
  - **Phase 1 — Variable Discovery:** Recursively scans all `.rpy` files (excluding `tl/` translation directories) for `default` and `define` numeric declarations.
  - **Phase 2 — Pattern Detection:** Parses all `$`-prefixed Python execution lines via AST, identifying function calls where string arguments match discovered variable names and numeric arguments represent values, auto-generating `FUNCTION_PARSER_PATTERNS` entries.
  - **Phase 3 — JSON Persistence:** Saves all discovered configuration to `auto_cheat_config.json` for instant subsequent loads.
- **Dual-Log Architecture:** Separated logging into two dedicated files:
  - `auto_cheat.log` — real-time parser activity and errors
  - `auto_cheat_parsing.log` — auto-discovery session details and diagnostics

---

## [4.0] — 2026-07-18
### Added
- **File Content Caching Engine:** Implemented an in-memory file cache with `mtime`-based invalidation, reducing repeated `.rpy` file reads by 10-100x on subsequent menu opens within the same session.
- **Parsed Menu Block Cache:** Introduced a dictionary-based cache keyed by `filepath:menu_line_index` to avoid re-parsing identical menu structures across multiple choice displays.
- **Log Rotation System:** Added automatic log file rotation at 5 MB threshold, renaming the existing log to `.bak` before creating a fresh file.
- **Multi-Change Variable Tracking:** Replaced single-change-per-variable logic with a `var_changes` dictionary accumulating all mutations per variable, enabling display of multiple stat shifts from a single menu choice.
- **Compiled Regex Patterns:** Pre-compiled all regular expressions (`CHOICE_PATTERN`, `CALC_PATTERN`, `TAG_PATTERN`) at module load time for micro-optimization of repeated search operations.
- **Translation-Aware Caption Rendering:** Integrated `renpy.substitute()` to resolve translated caption text before appending hint tags, ensuring hints display alongside localized strings rather than raw English originals.
- **Smart Quote Normalization:** Added automatic conversion of typographic quotes (`'`, `"`, `"`) and dashes (`–`, `—`) to their ASCII equivalents for reliable caption matching across localization variants.
- **Direct Filesystem Reading:** Replaced `renpy.loader.load()` with direct `open()` calls to bypass the translation file overlay, ensuring the parser always reads original `.rpy` source code.

---

## [3.8] — 2026-07-18
### Fixed
- **Tuple Extraction Logic:** Fixed a critical index bug (`item[0]`) in `custom_cheat_menu_proxy` that caused menu option captions to bypass the parser and hide sub-size text modifications.
- **Python 2.7 Compatibility Recovery:** Completely removed accidental f-strings inside string generation blocks, preventing `SyntaxError` crashes on Ren'Py 7.4.4.

---

## [3.7] — 2026-07-18
### Added
- **Configurable Runtime Logger:** Integrated an isolated logging engine writing directly to `game/auto_cheat.log`.
- **Wine-Safe File Streams:** Optimized logging handlers using absolute path combinations and automated encoding wrappers (`utf-8`) to prevent I/O blocking under Wine compatibility layers.
- **Granular Status Tracking:** Added deep tracing outputs for intercepted menu nodes, active AST evaluation blocks, and fallback execution pipelines.

---

## [3.6] — 2026-07-18
### Fixed
- **AST List Validation:** Resolved an internal Python structural mismatch where `tree.body` returned a list object instead of an absolute node definition. Fixed by forcing an explicit index retrieval on `tree.body[0]`.
- **Engine Node Resolution:** Integrated abstract node mapping handling both legacy `ast.Str` / `ast.Num` types (Ren'Py 7.x / Python 2) and modern `ast.Constant` definitions (Ren'Py 8.x / Python 3).

---

## [3.5] — 2026-07-18
### Added
- **Advanced Function Expression Parser:** Implemented an integrated Abstract Syntax Tree (AST) decoder to track custom gameplay scoring wrappers instead of basic math statements (e.g., parsing calls like `add_points("valueRS", 1, ...)`).
- **Positional Token Mapping (`FUNCTION_PARSER_PATTERNS`):** Introduced a flexible positional token string array framework using keywords: `VAR` (target variable string), `VAL` (numeric modifier adjustment value), and `_` (skipped function arguments).
- **Auto Keyword Mapping:** Added automatic resolution for custom keyword arguments (kwargs) mapping tags like `name=`, `value=`, or `amount=` out-of-the-box.

---

## [2.10] — 2026-07-18
### Fixed
- **Interface Layout Token Escaping:** Wrapped explicit `CLOSE [X]` braces into Ren'Py's native escape block `CLOSE [[X]]` to prevent the template rendering sub-engine from seeking an undefined global Python object named `X`.
- **Native Color Properties Overhaul:** Replaced unstable string-based tag injection loops (`{color=...}`) with standard visual parameters (`text_color`) across `auto_cheat_screens.rpy` elements to shield interface threads from token isolation failures.

---

## [2.5] — 2026-07-18
### Changed
- **Continuous Visual Anchoring:** Migrated overlay button instantiation calls from early boot sequences (`config.start_callbacks`) into live interface frame pipelines via `config.overlay_functions.append`. This ensures the `([CHEAT])` launcher button dynamically updates after save-state loads and scene cuts.
- **Strict Decoupling Strategy:** Separated the monolithic architecture into two independent files (`auto_cheat_core.rpy` and `auto_cheat_screens.rpy`) to completely insulate Python 2.7 runtime interpreters from formatting indent shifts typical in native screen languages.

---

## [2.0] — 2026-07-18
### Added
- **Full Graphic Variables Manager:** Introduced a responsive, scrollable UI panel layout mapping tracked game values in real-time.
- **Dynamic Adjusters:** Attached automated macro keys (`-10`, `-1`, `+1`, `+10`) manipulating memory states on the fly.
- **Precise Numerical Keyboard Input:** Integrated an atomic alphanumeric text capture field (`VariableInputValue`) allowing explicit data overrides linked directly to the live global engine container space.

---

## [1.3] — 2026-07-18
### Added
- **Dynamic Hex Colorization Palettes:** Applied conditional color assignments separating visual feedback hooks on choice lists:
  - `+=` (Positive shifts) mapped to Bright Green (`#2ecc71`).
  - `-=` (Negative shifts) mapped to Vibrant Red (`#e74c3c`).
  - `=` (Direct resets) mapped to Neon Blue (`#3498db`).
  - Unregistered Variables mapped to High-Visibility Amber Yellow (`#f1c40f`).
- **Global Font Compression Control:** Extracted a central font modifier index parameter `FONT_SIZE_MODIFIER` to dynamically rescale all generated tooltip outputs relative to native UI theme button values.

---

## [1.2] — 2026-07-18
### Added
- **Universal Quote Detection Regex:** Upgraded the string regex block matching logic to capture button titles bounded both by single quotes (`'V1'`) and double quotes (`"V1"`).
- **Direct Assignment Parsing:** Expanded math capture token criteria tracking clear stat rewrites (`$ m_score = 0`) transforming memory mutations into human-readable equivalence symbols (`=`).
- **Expression Collision Guarding:** Appended explicit line validation rules completely bypassing inline character validation tags (`if`, `==`) to shield the visual parsing flow from corrupting conditional execution statements.

---

## [1.1] — 2026-07-18
### Added
- **Low-Level Variable Interception:** Implemented a standalone initialization block rerouting all default runtime visual menu arrays by proxying the core internal function pointer (`menu = custom_cheat_menu_proxy`). This eliminates the requirement to tweak baseline UI script components (`screens.rpy`).
- **Amber Yellow Debug Diagnostics Tooling (`DEBUG_MODE`):** Embedded an isolated runtime tracker intercepting all newly uncovered metrics that aren't mapped inside custom translation dictionaries, logging them live on buttons using custom system labels.

---

## [1.0] — 2026-07-18
### Added
- **Initial Core Release:** Deployed a background file-stream search mechanism that identifies the engine's active game file line via `renpy.get_filename_line()`, opens the decompiled `.rpy` data array via `renpy.loader.load()`, and extracts stat modifications (`$ var += val`) on the fly.
