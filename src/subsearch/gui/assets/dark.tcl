# Made by rdbende @ https://github.com/rdbende/Sun-Valley-ttk-theme
# Modified and new assets by vagabondHustler

package require Tk 8.6

namespace eval ttk::theme::ttk_styls {
    variable version 1.0
    package provide ttk::theme::ttk_style $version

    ttk::style theme create ttk_style -parent clam -settings {
        proc load_images {imgdir} {
            variable images
            foreach file [glob -directory $imgdir *.png] {
                set images([file tail [file rootname $file]]) \
                [image create photo -file $file -format png]
            }
        }
        load_images [file join [file dirname [info script]] btn]
        load_images [file join [file dirname [info script]] scrollbar]
        load_images [file join [file dirname [info script]] scale]
        load_images [file join [file dirname [info script]] checkbox]

        array set colors {
            -fg             "#bdbdbd"
            -bg             "#1a1b1b"
            -disabledfg     "#595959"
            -selectfg       "#ffffff"
            -selectbg       "#2f60d8"
        }

         ttk::style layout TButton {
            Button.button -children {
                Button.padding -children {
                    Button.label -side left -expand 1
                } 
            }
        }

        ttk::style layout Vertical.TScrollbar {
            Vertical.Scrollbar.trough -sticky ns -children {
                Vertical.Scrollbar.uparrow -side top
                Vertical.Scrollbar.downarrow -side bottom
                Vertical.Scrollbar.thumb -expand 1
            }
        }

        ttk::style layout Horizontal.TScrollbar {
            Horizontal.Scrollbar.trough -sticky ew -children {
                Horizontal.Scrollbar.leftarrow -side left
                Horizontal.Scrollbar.rightarrow -side right
                Horizontal.Scrollbar.thumb -expand 1
            }
        }

        ttk::style layout TCheckbutton {
            Checkbutton.button -children {
                Checkbutton.padding -children {
                    Checkbutton.indicator -side left
                    Checkbutton.label -side right -expand 1
                }
            }
        }

        # Button
        ttk::style configure TButton -padding {4 4} -anchor center -foreground $colors(-fg)

        ttk::style map TButton -foreground \
            [list disabled #bdbdbd \
                pressed #4c4c4c]

        ttk::style element create Button.button image \
            [list $images(btn_rest) \
                {selected disabled} $images(btn_disabled) \
                disabled $images(btn_disabled) \
                selected $images(btn_rest) \
                pressed $images(btn_pressed) \
                active $images(btn_hover) \
            ] -border 4 -sticky nsew

        # Scrollbar
        ttk::style element create Horizontal.Scrollbar.trough image $images(scroll_hor_trough) -sticky ew -border 6
        ttk::style element create Horizontal.Scrollbar.thumb image $images(scroll_hor_thumb) -sticky ew -border 3

        ttk::style element create Horizontal.Scrollbar.rightarrow image $images(scroll_right) -sticky {} -width 12
        ttk::style element create Horizontal.Scrollbar.leftarrow image $images(scroll_left) -sticky {} -width 12

        ttk::style element create Vertical.Scrollbar.trough image $images(scroll_vert_trough) -sticky ns -border 6
        ttk::style element create Vertical.Scrollbar.thumb image $images(scroll_vert_thumb) -sticky ns -border 3

        ttk::style element create Vertical.Scrollbar.uparrow image $images(scroll_up) -sticky {} -height 12
        ttk::style element create Vertical.Scrollbar.downarrow image $images(scroll_down) -sticky {} -height 12

        # Scale
        ttk::style element create Horizontal.Scale.trough image $images(scale_trough_hor) \
            -border 5 -padding 0

        ttk::style element create Vertical.Scale.trough image $images(scale_trough_vert) \
            -border 5 -padding 0

        ttk::style element create Scale.slider \
            image [list $images(scale_thumb_rest) \
                disabled $images(scale_thumb_disabled) \
                pressed $images(scale_thumb_pressed) \
                active $images(scale_thumb_hover) \
            ] -sticky {}
        
        # Checkbutton
        ttk::style configure TCheckbutton -width 16 -padding {1 1} -border 0 -foreground $colors(-fg) -background $colors(-bg)

        ttk::style element create Checkbutton.indicator image \
            [list $images(check_unsel_rest) \
                {alternate disabled} $images(check_tri_disabled) \
                {selected disabled} $images(check_disabled) \
                disabled $images(check_unsel_disabled) \
                {pressed alternate} $images(check_tri_hover) \
                {active alternate} $images(check_tri_hover) \
                alternate $images(check_tri_rest) \
                {pressed selected} $images(check_hover) \
                {active selected} $images(check_hover) \
                selected $images(check_rest) \
                {pressed !selected} $images(check_unsel_pressed) \
                active $images(check_unsel_hover) \
            ] -width 26 -sticky w

       
    }
}