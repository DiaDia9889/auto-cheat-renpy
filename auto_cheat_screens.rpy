# =========================================================================
# AUTO CHEAT SCREENS - OPTIMIZED EDITION
# =========================================================================
# v6.1 - Centralized style constants, Ren'Py style definitions,
#      - reduced repetition, version tracking
# =========================================================================

init python:
    # =========================================================================
    # COLOR PALETTE (single source of truth for all screens)
    # =========================================================================
    CC_GOLD       = "#f1c40f"   # Titles, highlights, CHEAT button
    CC_RED        = "#e74c3c"   # Close buttons, negative values
    CC_GREEN      = "#2ecc71"   # Positive values, stat changes
    CC_BLUE       = "#3498db"   # Current values, OK button
    CC_WHITE      = "#ffffff"   # Primary text
    CC_LIGHT_GRAY = "#bbb"      # Secondary text
    CC_MID_GRAY   = "#aaa"      # Labels, tertiary text
    CC_DIM_GRAY   = "#888"      # Disabled/inactive text
    CC_DARK_GRAY  = "#555"      # Footer text

    # Background colors (with alpha)
    CB_OVERLAY    = "#000000cc" # Full screen dimming
    CB_BUTTON     = "#00000088" # Small button backgrounds
    CB_PANEL      = "#1a1a1acc" # Main panel background
    CB_ITEM       = "#2d2d2d88" # List item backgrounds
    CB_INPUT      = "#111111"   # Input field background

    # =========================================================================
    # VERSION
    # =========================================================================
    CHEAT_VERSION = "6.1"

# =========================================================================
# STYLE DEFINITIONS (reusable across all screens)
# =========================================================================

# --- Text Styles ---
style cheat_title_text:
    size 26
    color CC_GOLD
    bold True

style cheat_subtitle_text:
    size 16
    color CC_LIGHT_GRAY

style cheat_label_text:
    size 16
    color CC_WHITE

style cheat_value_text:
    size 16
    color CC_BLUE

style cheat_footer_text:
    size 11
    color CC_DARK_GRAY

style cheat_footer_active_text:
    size 11
    color CC_GREEN

# --- Frame Styles ---
style cheat_panel_frame:
    background CB_PANEL
    padding (20, 20)

style cheat_item_frame:
    background CB_ITEM
    padding (10, 8)
    xfill True

style cheat_button_frame:
    background CB_BUTTON
    padding (8, 6)

style cheat_input_frame:
    background CB_INPUT
    padding (5, 2)
    xsize 80
    ysize 30

# --- Button Text Styles ---
style cheat_btn_close_text:
    size 20
    color CC_RED

style cheat_btn_small_text:
    size 14
    color CC_RED

style cheat_btn_positive_text:
    size 14
    color CC_GREEN

style cheat_btn_action_text:
    size 14
    color CC_BLUE

# =========================================================================
# SCREEN CHOICE INDICATOR & DETAILS
# =========================================================================

screen screen_choice_indicator(screens):
    zorder 199

    frame:
        style_prefix "cheat_button"
        xalign 0.98
        yalign 0.98

        textbutton "CHOICES":
            action Show("screen_choice_details", screens=screens)
            text_size 14
            text_color CC_GOLD

screen screen_choice_details(screens):
    modal True
    zorder 202

    add CB_OVERLAY

    frame:
        xsize 900
        ysize 600
        xalign 0.5
        yalign 0.5
        style "cheat_panel_frame"

        vbox:
            spacing 15

            hbox:
                xfill True
                text "SCREEN CHOICES" style "cheat_title_text"
                textbutton "CLOSE" xalign 1.0:
                    action Hide("screen_choice_details")
                    text_style "cheat_btn_close_text"

            viewport:
                scrollbars "vertical"
                mousewheel True
                xsize 800
                ysize 500

                vbox:
                    spacing 10

                    for screen_name in screens:
                        $ choices = SCREEN_CHOICES.get(screen_name, [])

                        frame:
                            style "cheat_item_frame"

                            vbox:
                                spacing 8

                                text "Screen: [screen_name]" size 22 color CC_BLUE bold True

                                for choice in choices:
                                    hbox:
                                        spacing 10
                                        xfill True

                                        $ action_icon = u"\u21A9" if choice.get('action_type') == 'return' else u"\u2192"
                                        $ action_color = CC_DIM_GRAY if choice.get('action_type') == 'return' else CC_WHITE

                                        text "[action_icon] [choice['text']]" size 24 color action_color xsize 350

                                        if choice.get('action_type') == 'return':
                                            text "Return (no changes)" size 20 color CC_DIM_GRAY
                                        elif choice['changes']:
                                            $ changes_text = ", ".join([
                                                "{} {}{}".format(
                                                    c[0],
                                                    "+=" if c[1] == '+' else ("-=" if c[1] == '-' else "="),
                                                    c[2]
                                                ) for c in choice['changes']
                                            ])
                                            text changes_text size 20 color CC_GREEN
                                        else:
                                            text "no changes" size 20 color CC_DIM_GRAY

# =========================================================================
# MAIN CHEAT UI
# =========================================================================

default cheat_input_value = ""

screen cheat_launcher_btn():
    zorder 200

    frame:
        style_prefix "cheat_button"
        xalign 0.98
        yalign 0.02

        textbutton "CHEAT":
            action ToggleScreen("cheat_manager_overlay")
            text_size 16
            text_color CC_GOLD

screen cheat_manager_overlay():
    modal True
    zorder 201

    add CB_OVERLAY

    frame:
        xsize 850
        ysize 600
        xalign 0.5
        yalign 0.5
        style "cheat_panel_frame"

        vbox:
            spacing 15

            # --- Header ---
            hbox:
                xfill True
                text "STATS & VARIABLES CONTROL PANEL" style "cheat_title_text"
                textbutton "CLOSE [[X]]" xalign 1.0:
                    action ToggleScreen("cheat_manager_overlay")
                    text_style "cheat_btn_close_text"

            text "Select a variable to adjust stats dynamically in real-time:" style "cheat_subtitle_text"

            # --- Variable List ---
            viewport:
                scrollbars "vertical"
                mousewheel True
                xsize 810
                ysize 400

                has vbox spacing 8

                for var_real, var_display in MENU_VARIABLE_NAMES.items():
                    $ current_value = getattr(renpy.store, var_real, 0)

                    frame:
                        style "cheat_item_frame"

                        hbox:
                            xfill True
                            yalign 0.5
                            spacing 15

                            # Variable name and current value
                            hbox:
                                xsize 280
                                yalign 0.5
                                text "[var_display] ([var_real]) = " style "cheat_label_text"
                                text "[current_value]" style "cheat_value_text"

                            # Quick adjust buttons
                            hbox:
                                spacing 4
                                yalign 0.5
                                textbutton "-10" action Function(cheat_change_var, var_real, -10) text_style "cheat_btn_small_text"
                                textbutton "-1"  action Function(cheat_change_var, var_real, -1)  text_style "cheat_btn_small_text"
                                textbutton "+1"  action Function(cheat_change_var, var_real, 1)  text_style "cheat_btn_positive_text"
                                textbutton "+10" action Function(cheat_change_var, var_real, 10) text_style "cheat_btn_positive_text"

                            # Manual input
                            hbox:
                                xalign 1.0
                                spacing 8
                                yalign 0.5

                                label "Set:" yalign 0.5 text_size 14 text_color CC_MID_GRAY

                                frame:
                                    style "cheat_input_frame"
                                    yalign 0.5

                                    input:
                                        value VariableInputValue("cheat_input_value")
                                        size 14
                                        color CC_WHITE
                                        allow "0123456789-"

                                textbutton "OK" action Function(cheat_set_var, var_real, cheat_input_value) text_style "cheat_btn_action_text" yalign 0.5

            # --- Footer ---
            hbox:
                xfill True
                yalign 1.0

                hbox:
                    spacing 5
                    text "System Status:" style "cheat_footer_text"
                    text "Active" style "cheat_footer_active_text"

                text "Cheat Plugin v[CHEAT_VERSION]" xalign 1.0 style "cheat_footer_text"