import json
import os
import tkinter as tk
import webbrowser

from subsearch.data import __data__, __version__
from subsearch.gui import tkdata, tools, widget_root
from subsearch.utils import current_user, raw_config, raw_registry, updates

TKWINDOW = tkdata.Window()
TKCOLOR = tkdata.Color()
TKFONT = tkdata.Font()
TKMISC = tkdata.Misc()

LANGUAGES = raw_config.get("languages")
OTH_LANGUAGES = raw_config.get("other_languages")
LANGUAGE, LANG_CODE2 = raw_config.get("language")
HEARING_IMPARED = raw_config.get("hearing_impaired")
PCT = raw_config.get("percentage")
SHOW_TERMINAL = raw_config.get("show_terminal")
CM_ICON = raw_config.get("cm_icon")
DL_WINDOW = raw_config.get("show_download_window")
AVAIL_EXT = raw_config.get("file_ext")

# set which language of the subtitles  should be included in the search
class SelectLanguage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{LANGUAGE}, {LANG_CODE2}")
        number_of_buttons = len(LANGUAGES)
        self.rowcount = 0
        self.colcount = 1
        for i in range(1, 4):
            tools.Create.label(self, text=TKMISC.col58, col=i, font=TKFONT.cas8)
        tools.Create.label(self, text="Selected language", sticky="w", font=TKFONT.cas8b)
        self.clabel = tools.Create.label(
            self,
            textvar=self.string_var,
            fg=TKCOLOR.yellow,
            col=2,
            font=TKFONT.cas8b,
        )
        for i in range(number_of_buttons):
            self.rowcount += 1
            if self.rowcount == 8:
                self.colcount += 1
                self.rowcount = 1
            tools.Create.button(
                self,
                text=LANGUAGES[i],
                row=self.rowcount + 1,
                col=self.colcount,
                height=2,
                width=24,
                padx=2,
                bind_to=self.set_language,
            )
        tools.Create.button(
            self,
            abgc=TKCOLOR.light_black,
            bge=TKCOLOR.light_black,
            fg=TKCOLOR.light_black,
            fge=TKCOLOR.light_black,
            row=self.rowcount + 2,
            col=self.colcount,
            height=2,
            width=24,
        )
        self.entry = tk.Entry(self, width=28, bd=0, font=TKFONT.cas8b, justify="center")
        self.entry.insert(0, "🞂 Enter language here 🞀")
        self.entry.configure(
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.purple,
            insertbackground=TKCOLOR.purple,
        )
        self.entry.grid(ipady=8, padx=2, pady=2, row=self.rowcount + 2, column=self.colcount)
        self.add_button = tools.Create.button(
            self,
            text="Add",
            abgc=TKCOLOR.purple,
            bge=TKCOLOR.black,
            fg=TKCOLOR.white_grey,
            fge=TKCOLOR.purple,
            row=self.rowcount + 3,
            col=self.colcount,
            height=2,
            width=10,
            padx=5,
            sticky="w",
            bind_to=self.add_language,
        )

        self.see_other_langs = tools.Create.button(
            self,
            text="∙ ∙ ∙",
            abgc=TKCOLOR.purple,
            bge=TKCOLOR.black,
            fg=TKCOLOR.white_grey,
            fge=TKCOLOR.purple,
            row=self.rowcount + 3,
            col=self.colcount,
            height=2,
            width=10,
            padx=5,
            sticky="e",
        )
        self.entry.bind("<Enter>", self.entry_enter)
        self.see_other_langs.bind("<Enter>", self.popup_window)
        self.entry.bind("<Return>", self.add_language)
        self.configure(bg=TKCOLOR.dark_grey)

    # pop up window with list of other languages
    def popup_window(self, event):
        # * see 'cleaner' version of this function src.gui.tools.Tooltip
        self.clear_entry()
        rows = len(OTH_LANGUAGES) / 2
        cols = 2
        row_size_y = 20.16
        col_size_x = 113
        csx = round(cols * col_size_x)
        csy = round(rows * row_size_y)

        self.toplvl = tk.Toplevel(background=TKCOLOR.light_black, borderwidth=0)
        self.toplvl.overrideredirect(True)

        self.frame = tk.Frame(
            self.toplvl,
            background=TKCOLOR.dark_grey,
            width=csx,
            height=csy,
            borderwidth=0,
        )
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        root_x = root.winfo_rootx() + TKWINDOW.width + 10
        root_y = root.winfo_rooty() + 37
        self.toplvl.geometry(f"{csx}x{csy}+{root_x}+{root_y}")
        for num, i in zip(range(0, 50), OTH_LANGUAGES):
            tools.Create.label(
                self.frame,
                bg=TKCOLOR.dark_grey,
                text=i,
                font=TKFONT.cas8,
                row=num if num < 25 else num - 25,
                col=0 if num < 25 else 1,
                sticky="w",
                padx=0,
                pady=0,
            )
        self.see_other_langs.configure(fg=TKCOLOR.purple)
        self.see_other_langs.bind("<Leave>", self.popup_window_destroy)

    def popup_window_destroy(self, event):
        self.fill_entry()
        self.see_other_langs.configure(fg=TKCOLOR.white_grey)
        self.see_other_langs.bind("<Enter>", self.popup_window)
        self.toplvl.destroy()

    # entry functions
    def entry_enter(self, event):
        if self.entry.get() == "🞂 Enter language here 🞀" or self.entry.get() == "E.g: Czech, cs":
            self.clear_entry()
            self.entry.bind("<Leave>", self.entry_leave)

    def entry_leave(self, event):
        if self.entry.get() == "" or self.entry.get() == "E.g: Czech, cs":
            self.fill_entry()
            self.entry.bind("<Enter>", self.entry_enter)

    def clear_entry(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, "")
        self.entry.configure(fg=TKCOLOR.purple)

    def fill_entry(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, "🞂 Enter language here 🞀")
        self.entry.configure(fg=TKCOLOR.purple)

    # set language
    def set_language(self, event):
        btn = event.widget
        self.string_var.set(btn.cget("text"))
        update_svar = self.string_var.get()
        raw_config.set_json("language", update_svar)

    # add language from entry
    def add_language(self, event):
        x = self.entry.get()
        for i in OTH_LANGUAGES:
            if x == i:
                self.string_var.set(self.entry.get())
                self.entry.configure(fg=TKCOLOR.white_grey)
                update_svar = self.string_var.get()
                raw_config.set_json("language", update_svar)
                return
        self.entry.delete(0, "end")
        self.entry.insert(0, "E.g: Czech, cs")
        self.entry.configure(fg=TKCOLOR.red)


# set HI, none-HI or both HI and none-HI subtitles should be included in the search
class HearingImparedSubs(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{HEARING_IMPARED}")
        for i in range(1, 4):
            tools.Create.label(self, text=TKMISC.col58, col=i, font=TKFONT.cas8)
        tools.Create.label(
            self,
            text="Hearing impaired subtitles",
            sticky="w",
            font=TKFONT.cas8b,
            anchor="w",
        )
        self.clabel = tools.Create.label(self, textvar=self.string_var, fg=TKCOLOR.blue, col=2, font=TKFONT.cas8b)
        tools.Create.button(
            self,
            text="True",
            width=7,
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text="Only use hearing impaired subtitles",
        )
        tools.Create.button(
            self,
            text="False",
            width=7,
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text="Only use non-hearing impaired subtitles",
        )
        tools.Create.button(
            self,
            text="Both",
            width=7,
            bind_to=self.button_set_both,
            tip_show=True,
            tip_text="Use both hearing impaired and regular subtitles",
        )

        tools.ColorPicker(self.string_var, self.clabel)
        self.configure(bg=TKCOLOR.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_json("hearing_impaired", True)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_json("hearing_impaired", False)

    def button_set_both(self, event):
        self.string_var.set(f"Both")
        tools.ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get().split(" ")[0]
        raw_config.set_json("hearing_impaired", update_svar)


# set how closely the subtitle name should match the release name of the media file
class SearchThreshold(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{PCT} %")
        self.pct = PCT
        for i in range(1, 4):
            tools.Create.label(self, text=TKMISC.col58, col=i, font=TKFONT.cas8)
        tools.Create.label(self, text="Search threshold", sticky="w", font=TKFONT.cas8b)
        self.clabel = tools.Create.label(self, textvar=self.string_var, fg=TKCOLOR.blue, col=2, font=TKFONT.cas8b)
        tools.Create.button(
            self,
            text="+",
            sticky="e",
            bind_to=self.button_add_5,
            tip_show=True,
            tip_text="Add 5% to the search threshold\nA higher value means less chance of finding subtitles that are not synced witht the movie/series",
        )
        tools.Create.button(
            self,
            text="-",
            sticky="w",
            bind_to=self.button_sub_5,
            tip_show=True,
            tip_text="Subtract 5% from the search threshold\nA lower value means more subtitles will be found and downloaded",
        )
        tools.ColorPicker(self.string_var, self.clabel, self.pct)
        self.configure(bg=TKCOLOR.dark_grey)

    def button_add_5(self, event):
        self.pct += 5 if self.pct < 100 else 0
        self.string_var.set(f"{self.pct} %")

        tools.ColorPicker(self.string_var, self.clabel, self.pct)
        update_svar = int(self.pct)
        raw_config.set_json("percentage_pass", update_svar)

    def button_sub_5(self, event):
        self.pct -= 5 if self.pct > 0 else 0
        self.string_var.set(f"{self.pct} %")
        tools.ColorPicker(self.string_var, self.clabel, self.pct)
        update_svar = int(self.pct)
        raw_config.set_json("percentage_pass", update_svar)


# remove or restore the context menu option when right-clicking
class ShowContextMenu(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"True")
        for i in range(1, 4):
            tools.Create.label(self, text=TKMISC.col58, col=i, font=TKFONT.cas8)
        tools.Create.label(self, text="Show context menu", sticky="w", font=TKFONT.cas8b)
        self.clabel = tools.Create.label(
            self,
            textvar=self.string_var,
            fg=TKCOLOR.blue,
            col=2,
            font=TKFONT.cas8b,
            anchor="center",
        )
        tools.Create.button(
            self,
            text="True",
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text="Add SubSearch to the context menu when you right click inside a folder",
        )
        tools.Create.button(
            self,
            text="False",
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text="Remove SubSearch from the context menu\nUsed to 'uninstall' SubSearch",
        )
        tools.ColorPicker(self.string_var, self.clabel)
        self.configure(bg=TKCOLOR.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tools.ColorPicker(self.string_var, self.clabel)
        from subsearch.utils import raw_registry

        raw_registry.add_context_menu()
        raw_registry.write_all_valuex()

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tools.ColorPicker(self.string_var, self.clabel)
        from subsearch.utils import raw_registry

        raw_registry.remove_context_menu()


# * need cleanup and comments but works
# remove or restore the context menu option when right-clicking
class AssociateExtensions(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.ext_window_show = False
        for i in range(1, 4):
            tools.Create.label(self, text=TKMISC.col58, col=i, font=TKFONT.cas8)
        tools.Create.label(self, text="Associated extensions", sticky="w", font=TKFONT.cas8b)

        self.ext_button = tools.Create.button(
            self,
            text="Show menu",
            height=1,
            width=24,
            tip_show=True,
            tip_text="Which file extension to show the context menu on",
        )
        self.fesm = FileExtSubMenu(self)
        self.ext_button.bind("<Button-1>", self.toggle_window)
        self.configure(bg=TKCOLOR.dark_grey)

    def toggle_window(self, event):
        self.ext_window_show = self.fesm.window_showing_check()
        if self.ext_window_show:
            self.fesm.toggle_window()
            self.ext_window_show = self.fesm.window_showing_check()
        else:
            self.fesm.show()
            self.ext_window_show = self.fesm.window_showing_check()


class FileExtSubMenu(tk.Toplevel):
    def __init__(self, parent):
        self.parent = parent
        self.window_showing = False

    def show(self):
        self.files = []
        self.btn = []
        self.window_showing = True
        tk.Toplevel.__init__(self, self.parent)
        self.configure(background=TKCOLOR.light_black)
        # remove the standard window titlebar from the tooltip
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        button_width = 10
        exit_size = 19
        border_size = 2 * 2
        top_bar = tk.Frame(self, background=TKCOLOR.light_black)
        _frame = tk.Frame(self, background=TKCOLOR.light_grey)
        data = raw_config.get_json()
        for i in range(len(AVAIL_EXT.keys())):
            self.files.append("Button" + str(i))

        for i, ext in zip(range(len(self.files)), AVAIL_EXT.keys()):
            rownum = i
            if (rownum % 2) == 0:
                colnum = 0
            else:
                rownum -= 1
                colnum = 1

            self.btn.append(
                tk.Button(
                    _frame,
                    text=ext,
                    font=TKFONT.cas8b,
                    bg=TKCOLOR.dark_grey,
                    fg=TKCOLOR.white_grey,
                    activebackground=TKCOLOR.dark_grey,
                    activeforeground=TKCOLOR.yellow,
                    width=button_width,
                    bd=0,
                    command=lambda c=i: self.btn[c].cget("text"),
                )
            )
            if data["file_ext"][ext] is False:
                self.btn[i].configure(fg=TKCOLOR.red)
            elif data["file_ext"][ext] is True:
                self.btn[i].configure(fg=TKCOLOR.green)

            self.btn[i].grid(row=rownum, column=colnum)
            self.btn[i].bind("<Button-1>", self.set_language)
        # get size of the label to use later for positioning and sizing of the tooltip, + 2 to account padx/pady 1px
        _x, _y = self.btn[0].winfo_reqwidth() + 2, self.btn[0].winfo_reqheight() + 2
        # 2 rows half is length, 2 columns is width
        nrow = round(len(AVAIL_EXT) / 2)
        ncol = round(2)
        x = round(_x * ncol)
        y = round(_y * nrow)
        x_offset = TKWINDOW.width + button_width - _x
        y_offset = TKWINDOW.height - y - nrow
        # set the size of the tooltip background to be 1px larger than the label
        _frame.configure(width=x + border_size, height=y + border_size)
        top_bar.configure(width=x + border_size, height=exit_size)
        # offset the frame 1px from edge of the tooltip corner
        _frame.place(x=2, y=exit_size)
        top_bar.place(x=x, y=0, anchor="ne")
        # top_bar.lift()
        root_x = self.parent.winfo_rootx() + x_offset  # offset tooltip by extra 4px so it doesn't overlap the parent
        root_y = root.winfo_rooty() + y_offset  # place ext window at the bot of the roo offset by ext window hight
        # set position of the tooltip, size and add 2px around the tooltip for a 1px border
        self.geometry(f"{x}x{y+nrow}+{root_x}+{root_y}")

        self.exit_path = tools.buttons("exit.png")
        self.exit_grey_path = tools.buttons("exit_grey.png")
        self.exit_png = tk.PhotoImage(file=self.exit_path)
        self.exit_grey_png = tk.PhotoImage(file=self.exit_grey_path)
        self.exit = tk.Canvas(
            self,
            width=exit_size,
            height=exit_size,
            bg=TKCOLOR.light_black,
            highlightthickness=0,
        )
        self.exit.place(relx=1, y=0, anchor="ne")
        self.update_img(self.exit, self.exit_grey_png)
        self.exit.bind("<Enter>", self.exit_enter)
        self.exit.bind("<Leave>", self.exit_leave)
        top_bar.bind("<Button-1>", self.tb_press)
        top_bar.bind("<B1-Motion>", self.tb_drag)
        return self.window_showing

    def set_language(self, event):

        btn = event.widget
        data = raw_config.get_json()
        if data["file_ext"][btn.cget("text")] is True:
            data["file_ext"][btn.cget("text")] = False
            btn.configure(fg=TKCOLOR.red)
        else:
            data["file_ext"][btn.cget("text")] = True
            btn.configure(fg=TKCOLOR.green)
        file = os.path.join(__data__, "config.json")
        with open(file, "w") as f:
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

    def exit_release(self, event):
        from subsearch.utils import raw_registry

        raw_registry.write_all_valuex()
        self.window_showing = False
        self.destroy()

    def toggle_window(self):
        from subsearch.utils import raw_registry

        self.destroy()
        self.window_showing = False
        raw_registry.write_all_valuex()

    def window_showing_check(self):
        return self.window_showing

    def exit_press(self, event):
        self.exit.configure(bg=TKCOLOR.dark_red)
        self.exit.bind("<ButtonRelease-1>", self.exit_release)

    def exit_enter(self, event):
        self.exit.configure(bg=TKCOLOR.red)
        self.update_img(self.exit, self.exit_png)
        self.exit.bind("<ButtonPress-1>", self.exit_press)

    def exit_leave(self, event):
        self.exit.configure(bg=TKCOLOR.light_black)
        self.update_img(self.exit, self.exit_grey_png)
        self.exit.unbind("<ButtonRelease-1>")

    def update_img(self, canvas, img):
        canvas.delete("all")
        canvas.create_image(9, 9, image=img)
        canvas.photoimage = img

    def tb_press(self, event):
        self._offsetx = self.winfo_pointerx() - self.winfo_rootx()
        self._offsety = self.winfo_pointery() - self.winfo_rooty()

    def tb_drag(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry(f"+{x}+{y}")


# remove or restore the icon next to the context menu option when right clicking
class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{CM_ICON}")
        for i in range(1, 4):
            tools.Create.label(self, text=TKMISC.col58, col=i, font=TKFONT.cas8)
        tools.Create.label(self, text="Show context menu icon", sticky="w", font=TKFONT.cas8b)
        self.clabel = tools.Create.label(
            self,
            textvar=self.string_var,
            fg=TKCOLOR.blue,
            col=2,
            font=TKFONT.cas8b,
        )
        tools.Create.button(
            self,
            text="True",
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text="Add a icon next to SubSearch in the context menu",
        )
        tools.Create.button(
            self,
            text="False",
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text="Remove the icon next to SubSearch in the context menu",
        )
        tools.ColorPicker(self.string_var, self.clabel)
        self.configure(bg=TKCOLOR.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_json("context_menu_icon", True)
        from subsearch.utils import raw_registry

        raw_registry.write_valuex("icon")

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_json("context_menu_icon", False)
        from subsearch.utils import raw_registry

        raw_registry.write_valuex("icon")


# remove or restore the icon next to the context menu option when right clicking
class ShowDownloadWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{DL_WINDOW}")
        for i in range(1, 4):
            tools.Create.label(self, text=TKMISC.col58, col=i, font=TKFONT.cas8)
        tools.Create.label(self, text="Show download window", sticky="w", font=TKFONT.cas8b)
        self.clabel = tools.Create.label(
            self,
            textvar=self.string_var,
            fg=TKCOLOR.blue,
            col=2,
            font=TKFONT.cas8b,
        )
        tools.Create.button(
            self,
            text="True",
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text="If no subtitles are found show a window with the disregarded subtitles with download buttons to each of them",
        )
        tools.Create.button(
            self,
            text="False",
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text="No window will be shown if no subtitles are found\nThe list can be found in search.log",
        )
        tools.ColorPicker(self.string_var, self.clabel)
        self.configure(bg=TKCOLOR.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_json("show_download_window", True)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_json("show_download_window", False)


# show a terminal with what the code is doing while searching
class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()

        self.string_var.set(f"{SHOW_TERMINAL}")
        for i in range(1, 4):
            tools.Create.label(self, text=TKMISC.col58, col=i, font=TKFONT.cas8)
        tools.Create.label(self, text="Show terminal on search", sticky="w", font=TKFONT.cas8b)
        self.clabel = tools.Create.label(
            self,
            textvar=self.string_var,
            fg=TKCOLOR.blue,
            col=2,
            font=TKFONT.cas8b,
        )
        if current_user.check_is_exe() is False:
            tools.Create.button(
                self,
                text="True",
                sticky="e",
                bind_to=self.button_set_true,
                tip_show=True,
                tip_text="Show the terminal when searching for subtitles\nEverything shown in the terminal is avalible in search.log",
            )
            tools.Create.button(
                self,
                text="False",
                sticky="w",
                bind_to=self.button_set_false,
                tip_show=True,
                tip_text="Hide the terminal when searching for subtitles",
            )
        tools.ColorPicker(self.string_var, self.clabel)
        self.configure(bg=TKCOLOR.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_json("show_terminal", True)
        raw_registry.write_valuex("command")

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_json("show_terminal", False)
        raw_registry.write_valuex("command")


# check for new updates on the github repository
class CheckForUpdates(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"")
        for i in range(1, 4):
            tools.Create.label(self, text=TKMISC.col58, col=i, font=TKFONT.cas8)
        tools.Create.label(
            self,
            text=f"SubScene version {__version__}",
            sticky="w",
            font=TKFONT.cas8b,
        )
        tools.Create.label(self, textvar=self.string_var, fg=TKCOLOR.blue, col=2, font=TKFONT.cas8b)
        tools.Create.button(
            self,
            text="Check for updates",
            height=2,
            width=24,
            fge=TKCOLOR.green,
            bind_to=self.button_check,
        )
        self.configure(bg=TKCOLOR.dark_grey)

    def button_check(self, event):
        self.string_var.set(f"Searching for updates...")
        value, release_type = updates.is_new_version_available()
        latest_version = updates.check_for_updates()
        if value:
            self.string_var.set(f"New version available!")
            tools.Create.button(
                self,
                text=f"Get {latest_version}",
                height=2,
                width=24,
                bind_to=self.button_download,
            )

        if value is False and release_type is None:
            self.string_var.set(f"You are up to date!")
        elif value is False and release_type is None:
            self.string_var.set(f"New {release_type} update available")
        elif value is False and release_type is not None:
            self.string_var.set(f"Branch ahead of main branch")

    def button_download(self, event):
        webbrowser.open("https://github.com/vagabondHustler/SubSearch/releases")


def show_widget():
    global root
    if current_user.got_key() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()

    root = widget_root.main()
    SelectLanguage(root).pack(anchor="center")
    tk.Frame(root, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)
    HearingImparedSubs(root).pack(anchor="center")
    SearchThreshold(root).pack(anchor="center")
    tk.Frame(root, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)
    ShowContextMenu(root).pack(anchor="center")
    ShowContextMenuIcon(root).pack(anchor="center")
    AssociateExtensions(root).pack(anchor="center")
    ShowDownloadWindow(root).pack(anchor="center")
    if current_user.check_is_exe() is False:
        ShowTerminalOnSearch(root).pack(anchor="center")
    tk.Frame(root, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)
    CheckForUpdates(root).pack(anchor="center")
    tk.Frame(root, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)

    root.mainloop()
