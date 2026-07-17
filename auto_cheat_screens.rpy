# =========================================================================
# SCREEN CHOICE INDICATOR & DETAILS
# =========================================================================

# Индикатор на экране с выборами
screen screen_choice_indicator(screens):
    zorder 199
    
    frame:
        xalign 0.98
        yalign 0.98
        background "#00000088"
        padding (8, 6)
        
        textbutton "CHOICES":
            action Show("screen_choice_details", screens=screens)
            text_size 14
            text_color "#f1c40f"

# Детальная информация о выборах
screen screen_choice_details(screens):
    modal True
    zorder 202
    
    add "#000000cc"
    
    frame:
        xsize 900
        ysize 600
        xalign 0.5
        yalign 0.5
        background "#1a1a1acc"
        padding (20, 20)
        
        vbox:
            spacing 15
            
            hbox:
                xfill True
                text "SCREEN CHOICES" size 26 color "#f1c40f" bold True
                textbutton "CLOSE" xalign 1.0:
                    action Hide("screen_choice_details")
                    text_color "#e74c3c"
                    text_size 20
            
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
                            xfill True
                            background "#2d2d2d88"
                            padding (10, 8)
                            
                            vbox:
                                spacing 8
                                
                                text "Screen: [screen_name]" size 22 color "#3498db" bold True
                                
                                for choice in choices:
                                    hbox:
                                        spacing 10
                                        xfill True
                                        
                                        text "• [choice['text']]" size 24 color "#fff" xsize 350
                                        
                                        if choice['changes']:
                                            $ changes_text = ", ".join([
                                                "{} {}{}".format(
                                                    c[0],
                                                    "+=" if c[1] == '+' else ("-=" if c[1] == '-' else "="),
                                                    c[2]
                                                ) for c in choice['changes']
                                            ])
                                            text changes_text size 20 color "#2ecc71"
                                        else:
                                            text "no changes" size 20 color "#888"

default cheat_input_value = ""

# Semi-transparent launcher button in the top right corner
screen cheat_launcher_btn():
    zorder 200
    frame:
        xalign 0.98
        yalign 0.02
        background "#00000088"
        padding (6, 4)
        textbutton "CHEAT":
            action ToggleScreen("cheat_manager_overlay")
            text_size 16
            text_color "#f1c40f"

# Main variables control panel overlay
screen cheat_manager_overlay():
    modal True
    zorder 201

    add "#000000cc"

    frame:
        xsize 850
        ysize 600
        xalign 0.5
        yalign 0.5
        background "#1a1a1acc"
        padding (20, 20)

        vbox:
            spacing 15

            hbox:
                xfill True
                text "STATS & VARIABLES CONTROL PANEL" size 22 color "#f1c40f" bold True
                textbutton "CLOSE [[X]]" xalign 1.0:
                    action ToggleScreen("cheat_manager_overlay")
                    text_color "#e74c3c"
                    text_size 16

            text "Select a variable to adjust stats dynamically in real-time:" size 14 color "#bbb"

            # Main viewport area for statistics variables
            viewport:
                scrollbars "vertical"
                mousewheel True
                xsize 810
                ysize 400
                has vbox spacing 8

                for var_real, var_display in MENU_VARIABLE_NAMES.items():
                    $ current_value = getattr(renpy.store, var_real, 0)
                    
                    frame:
                        xfill True
                        background "#2d2d2d88"
                        padding (10, 8)

                        hbox:
                            xfill True
                            yalign 0.5
                            spacing 15

                            hbox:
                                xsize 280
                                yalign 0.5
                                text "[var_display] ([var_real]) = " size 16
                                text "[current_value]" size 16 color "#3498db"

                            hbox:
                                spacing 4
                                yalign 0.5
                                textbutton "-10" action Function(cheat_change_var, var_real, -10) text_size 14 text_color "#e74c3c"
                                textbutton "-1" action Function(cheat_change_var, var_real, -1) text_size 14 text_color "#e74c3c"
                                textbutton "+1" action Function(cheat_change_var, var_real, 1) text_size 14 text_color "#2ecc71"
                                textbutton "+10" action Function(cheat_change_var, var_real, 10) text_size 14 text_color "#2ecc71"

                            hbox:
                                xalign 1.0
                                spacing 8
                                yalign 0.5
                                label "Set:" yalign 0.5 text_size 14 text_color "#aaa"
                                
                                frame:
                                    xsize 80
                                    ysize 30
                                    background "#111111"
                                    padding (5, 2)
                                    yalign 0.5
                                    input:
                                        value VariableInputValue("cheat_input_value")
                                        size 14
                                        color "#fff"
                                        allow "0123456789-"
                                
                                textbutton "OK" action Function(cheat_set_var, var_real, cheat_input_value) text_size 14 text_color "#3498db" yalign 0.5

            # Bottom info panel displaying version and build details
            hbox:
                xfill True
                yalign 1.0
                hbox:
                    spacing 5
                    text "System Status:" size 11 color "#555"
                    text "Active" size 11 color "#2ecc71"
                text "Cheat Plugin v5.3" xalign 1.0 size 11 color "#555"
