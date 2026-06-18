source [file join [file dirname [info script]] style_subsearch.tcl]

option add *tearOff 0

proc set_theme {} {
    
    ttk::style theme use "style_subsearch"

    array set colors {
        -fg             "#bdbdbd"
        -bg             "#1a1b1b"
        -disabledfg     "#59959"
        -selectfg       "#1a1b1b"
        -selectbg       "#bdbdbd"
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
