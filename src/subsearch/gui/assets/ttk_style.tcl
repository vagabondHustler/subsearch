# Made by rdbende @ https://github.com/rdbende/Sun-Valley-ttk-theme
# Modified and new assets by vagabondHustler


source [file join [file dirname [info script]] dark.tcl]

option add *tearOff 0

proc set_theme {mode} {
    if {$mode == "dark"} {
        ttk::style theme use "ttk_style"

        array set colors {
            -fg             "#ffffff"
            -bg             "#1c1c1c"
            -disabledfg     "#59959"
            -selectfg       "#ffffff"
            -selectbg       "#2f60d8"
        }
        
        ttk::style configure . \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -troughcolor $colors(-bg) \
            -focuscolor $colors(-selectbg) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -insertwidth 1 \
            -insertcolor $colors(-fg) \
            -fieldbackground $colors(-bg) \
            -font {"Cascadia" 8 bold} \
            -borderwidth 0 \
            -relief flat

        tk_setPalette \
            background [ttk::style lookup . -background] \
            foreground [ttk::style lookup . -foreground] \
            highlightColor [ttk::style lookup . -focuscolor] \
            selectBackground [ttk::style lookup . -selectbackground] \
            selectForeground [ttk::style lookup . -selectforeground] \
            activeBackground [ttk::style lookup . -selectbackground] \
            activeForeground [ttk::style lookup . -selectforeground]
        
        ttk::style map . -foreground [list disabled $colors(-disabledfg)]

        option add *font [ttk::style lookup . -font]
    
    }
}
