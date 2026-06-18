source [file join [file dirname [info script]] sprites.tcl]

namespace eval style_subsearch {
    package provide ttk::theme::style_subsearch 0.1.0

    # Load Images
    proc load_images {imgfile} {
        variable sprites
        image create photo spritesheet -file $imgfile -format png
        foreach {name x y width height} $::sprite_data {
            set sprites($name) [image create photo -width $width -height $height]
            $sprites($name) copy spritesheet -from $x $y [expr {$x + $width}] [expr {$y + $height}]
        }
    }

    load_images [file join [file dirname [file dirname [info script]]] assets spritesheet.png]


    # Theme Creation
    ttk::style theme create style_subsearch -parent clam -settings {

        # Color Settings
        array set colors {
            -fg             "#bdbdbd"
            -bg             "#1a1b1b"
            -disabledfg     "#595959"
            -selectfg       "#ffffff"
            -selectbg       "#2f60d8"
        }

        # Button Layout
        ttk::style layout TButton {
            Button.button -children {
                Button.padding -children {
                    Button.label -side left -expand 1
                }
            }
        }

        # Vertical Scrollbar Layout
        ttk::style layout Vertical.TScrollbar {
            Vertical.Scrollbar.trough -sticky ns -children {
                Vertical.Scrollbar.uparrow -side top
                Vertical.Scrollbar.downarrow -side bottom
                Vertical.Scrollbar.thumb -expand 1
            }
        }

        # Horizontal Scrollbar Layout
        ttk::style layout Horizontal.TScrollbar {
            Horizontal.Scrollbar.trough -sticky ew -children {
                Horizontal.Scrollbar.leftarrow -side left
                Horizontal.Scrollbar.rightarrow -side right
                Horizontal.Scrollbar.thumb -expand 1
            }
        }

        # Checkbutton Layout
        ttk::style layout TCheckbutton {
            Checkbutton.button -children {
                Checkbutton.padding -children {
                    Checkbutton.indicator -side left
                    Checkbutton.label -side right -expand 1
                }
            }
        }

        # Button Configuration
        ttk::style configure TButton -padding {4 4} -anchor center -foreground $colors(-fg)

        ttk::style map TButton -foreground \
            [list disabled #232323 \
                pressed #4c4c4c]

        ttk::style element create Button.button image \
            [list $sprites(btn_rest) \
                {selected disabled} $sprites(btn_disabled) \
                disabled $sprites(btn_disabled) \
                selected $sprites(btn_rest) \
                pressed $sprites(btn_pressed) \
                active $sprites(btn_hover) \
            ] -border 4 -sticky nsew

        # Scrollbar Elements
        ttk::style element create Horizontal.Scrollbar.trough image $sprites(scroll_hor_trough) -sticky ew -border 6
        ttk::style element create Horizontal.Scrollbar.thumb image $sprites(scroll_hor_thumb) -sticky ew -border 3

        ttk::style element create Horizontal.Scrollbar.rightarrow image $sprites(scroll_right) -sticky {} -width 12
        ttk::style element create Horizontal.Scrollbar.leftarrow image $sprites(scroll_left) -sticky {} -width 12

        ttk::style element create Vertical.Scrollbar.trough image $sprites(scroll_vert_trough) -sticky ns -border 6
        ttk::style element create Vertical.Scrollbar.thumb image $sprites(scroll_vert_thumb) -sticky ns -border 3

        ttk::style element create Vertical.Scrollbar.uparrow image $sprites(scroll_up) -sticky {} -height 12
        ttk::style element create Vertical.Scrollbar.downarrow image $sprites(scroll_down) -sticky {} -height 12

        # Scale Elements
        ttk::style element create Horizontal.Scale.trough image $sprites(scale_trough_hor) -border 5 -padding 0

        ttk::style element create Vertical.Scale.trough image $sprites(scale_trough_vert) -border 5 -padding 0

        ttk::style element create Scale.slider \
            image [list $sprites(scale_thumb_rest) \
                disabled $sprites(scale_thumb_disabled) \
                pressed $sprites(scale_thumb_pressed) \
                active $sprites(scale_thumb_hover) \
            ] -sticky {}

        # Checkbutton Configuration
        ttk::style configure TCheckbutton -width 16 -padding {1 1} -border 0 -foreground $colors(-fg) -background $colors(-bg)

        ttk::style element create Checkbutton.indicator image \
            [list $sprites(check_unsel_rest) \
                {alternate disabled} $sprites(check_tri_disabled) \
                {selected disabled} $sprites(check_disabled) \
                disabled $sprites(check_unsel_disabled) \
                {pressed alternate} $sprites(check_tri_hover) \
                {active alternate} $sprites(check_tri_hover) \
                alternate $sprites(check_tri_rest) \
                {pressed selected} $sprites(check_hover) \
                {active selected} $sprites(check_hover) \
                selected $sprites(check_rest) \
                {pressed !selected} $sprites(check_unsel_pressed) \
                active $sprites(check_unsel_hover) \
            ] -width 26 -sticky w

        ttk::style map TCheckbutton -foreground \
            [list disabled #565656 \
            ]
        
        # Card
        ttk::style layout Card.TFrame {
        Card.field {
            Card.padding -expand 1 
            }
        }

        ttk::style element create Card.field image $sprites(card) -border 0 -padding 4 -sticky nsew

        # Labelframe
        ttk::style layout TLabelframe {
        Labelframe.border {
            Labelframe.padding -expand 1 -children {
            Labelframe.label -side left
                }
            }
        
        
        }
        # LabelframePlain
        ttk::style layout TLabelframePlain {
        Labelframe.plain {
            Labelframe.padding -expand 1 -children {
            Labelframe.label -side left
                }
            }
        
        }

        ttk::style element create Labelframe.border image $sprites(card) -border 5 -padding 4 -sticky nsew
        ttk::style configure TLabelframe.border.Label -font "Cascadia 8 bold" -foreground $colors(-fg) -background $colors(-bg)
        ttk::style configure TLabelframe.plain.Label -font "Cascadia 8 bold" -foreground $colors(-fg) -background $colors(-bg)

        # Entry
        ttk::style configure TEntry -foreground $colors(-fg) -padding {6 1 4 2}
        ttk::style map TEntry -foreground [list disabled "#757575" pressed "#cfcfcf"]

        ttk::style element create Entry.field image \
        [list $sprites(textbox_rest) \
            {focus hover !invalid} $sprites(textbox_focus) \
            invalid $sprites(textbox_error) \
            disabled $sprites(textbox_dis) \
            {focus !invalid} $sprites(textbox_focus) \
            hover $sprites(textbox_hover) \
        ] -border 5 -sticky nsew


    }
}
