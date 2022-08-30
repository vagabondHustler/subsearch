import tkinter as tk
import webbrowser

from subsearch.data import __data__, __version__
from subsearch.gui import base_root, tk_data, tk_tools
from subsearch.utils import current_user, raw_config, raw_registry, updates

TKWINDOW = tk_data.Window()
TKCOLOR = tk_data.Color()
TKFONT = tk_data.Font()
TKMISC = tk_data.Misc()

LANGUAGES = raw_config.get_config_key("languages")
CURRENT_LANGUAGE = raw_config.get_config_key("current_language")
HEARING_IMPARED = raw_config.get_config_key("hearing_impaired")
PCT = raw_config.get_config_key("percentage")
SHOW_TERMINAL = raw_config.get_config_key("show_terminal")
CONTEXT_MENU_ICON = raw_config.get_config_key("context_menu_icon")
DL_WINDOW = raw_config.get_config_key("show_download_window")
AVAIL_EXT = raw_config.get_config_key("file_ext")
PROVIDERS = raw_config.get_config_key("providers")


class SelectLanguage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{CURRENT_LANGUAGE}")
        number_of_buttons = len(LANGUAGES)
        self.rownum = 0
        self.colnum = 0
        self.btn_active = None
        for i, key in zip(range(number_of_buttons), LANGUAGES.keys()):
            self.rownum += 1
            if self.rownum == 15:
                self.rownum = 1
                self.colnum += 1

            btn = tk.Button(
                self,
                font=TKFONT.cas8b,
                text=key,
                bd=0,
                bg=TKCOLOR.light_black,
                fg=TKCOLOR.white_grey,
                activebackground=TKCOLOR.orange,
                height=2,
                width=18,
            )
            btn.grid(row=self.rownum + 1, column=self.colnum, pady=2)
            if btn["text"] == self.string_var.get():
                btn.configure(fg=TKCOLOR.yellow)
                self.btn_active = btn

            # btn.bind("<Button-1>", self.enter_button)
            btn.bind("<Enter>", self.enter_button)
            btn.bind("<Leave>", self.leave_button)
            tk_tools.row_col_minsize(self, 18)

    def enter_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.orange)
        btn.bind("<ButtonRelease>", self.set_current_language)

    def leave_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)
        if btn["text"] == self.string_var.get():
            btn.configure(fg=TKCOLOR.yellow)

    # set language
    def set_current_language(self, event):
        btn = event.widget
        event.widget.configure(fg=TKCOLOR.yellow)
        self.string_var.set(btn.cget("text"))
        update_svar = btn["text"]
        raw_config.set_config_key_value("current_language", update_svar)
        if btn["text"] == self.string_var.get():
            btn.configure(fg=TKCOLOR.yellow)
            self.btn_active.configure(fg=TKCOLOR.white_grey)
            self.btn_active = btn


class HearingImparedSubs(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{HEARING_IMPARED}")
        label = tk.Label(self, text="Hearing impaired")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TKCOLOR.dark_grey, font=TKFONT.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.ColorPicker(self.string_var, self.clabel)
        btn_true = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="True",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.green,
            height=2,
            width=18,
        )
        btn_true.grid(row=0, column=4, pady=2)
        btn_both = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="Both",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.blue,
            height=2,
            width=18,
        )
        btn_both.grid(row=0, column=3, pady=2)
        btn_false = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="False",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.red,
            height=2,
            width=18,
        )
        btn_false.grid(row=0, column=2, pady=2)
        btn_true.bind("<Enter>", self.enter_button)
        btn_true.bind("<Leave>", self.leave_button)
        btn_both.bind("<Enter>", self.enter_button)
        btn_both.bind("<Leave>", self.leave_button)
        btn_false.bind("<Enter>", self.enter_button)
        btn_false.bind("<Leave>", self.leave_button)
        tk_tools.row_col_minsize(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.button_set_true)
        if btn["text"] == "Both":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.blue)
            btn.bind("<ButtonRelease>", self.button_set_both)
        if btn["text"] == "False":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("hearing_impaired", True)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("hearing_impaired", False)

    def button_set_both(self, event):
        self.string_var.set(f"Both")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get().split(" ")[0]
        raw_config.set_config_key_value("hearing_impaired", update_svar)


class SearchThreshold(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{PCT} %")
        self.pct = PCT
        label = tk.Label(self, text="Search threshold")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TKCOLOR.dark_grey, font=TKFONT.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.ColorPicker(self.string_var, self.clabel, self.pct)
        btn_add = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="+",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.green,
            height=2,
            width=18,
        )
        btn_add.grid(row=0, column=4, pady=2)
        btn_sub = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="-",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.red,
            height=2,
            width=18,
        )
        btn_sub.grid(row=0, column=2, pady=2)
        btn_add.bind("<Enter>", self.enter_button)
        btn_add.bind("<Leave>", self.leave_button)
        btn_sub.bind("<Enter>", self.enter_button)
        btn_sub.bind("<Leave>", self.leave_button)
        tk_tools.row_col_minsize(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "+":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.button_add_5)
        if btn["text"] == "-":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.button_sub_5)

    def leave_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)
        tk_tools.ColorPicker(self.string_var, self.clabel)

    def button_add_5(self, event):
        self.pct += 5 if self.pct < 100 else 0
        self.string_var.set(f"{self.pct} %")

        tk_tools.ColorPicker(self.string_var, self.clabel, self.pct)
        update_svar = int(self.pct)
        raw_config.set_config_key_value("percentage", update_svar)

    def button_sub_5(self, event):
        self.pct -= 5 if self.pct > 0 else 0
        self.string_var.set(f"{self.pct} %")
        tk_tools.ColorPicker(self.string_var, self.clabel, self.pct)
        update_svar = int(self.pct)
        raw_config.set_config_key_value("percentage", update_svar)


class Providers(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.data = raw_config.get_config()
        number_of_buttons = len(PROVIDERS.items())
        label = tk.Label(self, text="Search providers")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=1, column=0, sticky="w", padx=2, pady=2)
        self.rownum = 0
        self.colnum = 2
        for i, key in zip(range(number_of_buttons), PROVIDERS.keys()):
            self.rownum += 1
            if self.rownum > 1:
                self.rownum = 1
                self.colnum += 1

            btn = tk.Button(
                self,
                font=TKFONT.cas8b,
                text=key,
                bd=0,
                bg=TKCOLOR.light_black,
                fg=TKCOLOR.white_grey,
                activebackground=TKCOLOR.orange,
                height=2,
                width=18,
            )
            btn.grid(row=self.rownum, column=self.colnum, pady=2)
            if self.data["providers"][key] is False:
                btn.configure(fg=TKCOLOR.red)
            elif self.data["providers"][key] is True:
                btn.configure(fg=TKCOLOR.green)

            # btn.bind("<Button-1>", self.enter_button)
            btn.bind("<Enter>", self.enter_button)
            btn.bind("<Leave>", self.leave_button)
            tk_tools.row_col_minsize(self)

    def enter_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.orange)
        btn.bind("<ButtonPress>", self.press_button)

    def leave_button(self, event):
        btn = event.widget
        key = btn["text"]
        if self.data["providers"][key] is True:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.green)
        if self.data["providers"][key] is False:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.red)

    def press_button(self, event):
        btn = event.widget
        key = btn["text"]
        if self.data["providers"][key] is True:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.toggle_providers)
        if self.data["providers"][key] is False:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.toggle_providers)

    def toggle_providers(self, event):
        btn = event.widget
        key = btn["text"]
        if self.data["providers"][key] is True:
            self.data["providers"][key] = False
            btn.configure(fg=TKCOLOR.red)
        elif self.data["providers"][key] is False:
            self.data["providers"][key] = True
            btn.configure(fg=TKCOLOR.green)
        raw_config.set_config(self.data)


class ShowContextMenu(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"True")
        label = tk.Label(self, text="Context menu")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TKCOLOR.dark_grey, font=TKFONT.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.ColorPicker(self.string_var, self.clabel)
        btn_true = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="True",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.green,
            height=2,
            width=18,
        )
        btn_true.grid(row=0, column=3, pady=2)
        btn_false = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="False",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.red,
            height=2,
            width=18,
        )
        btn_false.grid(row=0, column=2, pady=2)
        btn_true.bind("<Enter>", self.enter_button)
        btn_true.bind("<Leave>", self.leave_button)
        btn_false.bind("<Enter>", self.enter_button)
        btn_false.bind("<Leave>", self.leave_button)
        tk_tools.row_col_minsize(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.button_set_true)
        if btn["text"] == "False":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        from subsearch.utils import raw_registry

        raw_registry.add_context_menu()
        raw_registry.write_all_valuex()

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        from subsearch.utils import raw_registry

        raw_registry.remove_context_menu()


class FileExtensions(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.data = raw_config.get_config()
        number_of_buttons = len(AVAIL_EXT.items())
        label = tk.Label(self, text="File extensions")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.rownum = 0
        self.colnum = 0
        for i, key in zip(range(number_of_buttons), AVAIL_EXT.keys()):
            self.rownum += 1
            if self.rownum > 4:
                self.rownum = 1
                self.colnum += 1

            btn = tk.Button(
                self,
                font=TKFONT.cas8b,
                text=key,
                bd=0,
                bg=TKCOLOR.light_black,
                fg=TKCOLOR.white_grey,
                activebackground=TKCOLOR.orange,
                height=2,
                width=18,
            )
            btn.grid(row=self.rownum, column=self.colnum, pady=2)
            if self.data["file_ext"][key] is False:
                btn.configure(fg=TKCOLOR.red)
            elif self.data["file_ext"][key] is True:
                btn.configure(fg=TKCOLOR.green)

            # btn.bind("<Button-1>", self.enter_button)
            btn.bind("<Enter>", self.enter_button)
            btn.bind("<Leave>", self.leave_button)
            tk_tools.row_col_minsize(self)

    def enter_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.orange)
        btn.bind("<ButtonPress>", self.press_button)

    def leave_button(self, event):
        btn = event.widget
        key = btn["text"]
        if self.data["file_ext"][key] is True:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.green)
        if self.data["file_ext"][key] is False:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.red)

    def press_button(self, event):
        btn = event.widget
        key = btn["text"]
        if self.data["file_ext"][key] is True:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.toggle_ext)
        if self.data["file_ext"][key] is False:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.toggle_ext)

    def toggle_ext(self, event):
        btn = event.widget
        key = btn["text"]
        if self.data["file_ext"][key] is True:
            self.data["file_ext"][key] = False
            btn.configure(fg=TKCOLOR.red)
        elif self.data["file_ext"][key] is False:
            self.data["file_ext"][key] = True
            btn.configure(fg=TKCOLOR.green)
        raw_config.set_config(self.data)

        self.update_registry()

    def update_registry(self):
        from subsearch.utils import raw_registry

        raw_registry.write_all_valuex()


class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{CONTEXT_MENU_ICON}")
        label = tk.Label(self, text="Context menu icon")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TKCOLOR.dark_grey, font=TKFONT.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.ColorPicker(self.string_var, self.clabel)

        btn_true = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="True",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.green,
            height=2,
            width=18,
        )
        btn_true.grid(row=0, column=3, pady=2)
        btn_false = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="False",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.red,
            height=2,
            width=18,
        )
        btn_false.grid(row=0, column=2, pady=2)
        btn_true.bind("<Enter>", self.enter_button)
        btn_true.bind("<Leave>", self.leave_button)
        btn_false.bind("<Enter>", self.enter_button)
        btn_false.bind("<Leave>", self.leave_button)
        tk_tools.row_col_minsize(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.button_set_true)
        if btn["text"] == "False":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("context_menu_icon", True)
        from subsearch.utils import raw_registry

        raw_registry.write_valuex("icon")

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("context_menu_icon", False)
        from subsearch.utils import raw_registry

        raw_registry.write_valuex("icon")


class ShowDownloadWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{DL_WINDOW}")
        label = tk.Label(self, text="Download window")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TKCOLOR.dark_grey, font=TKFONT.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.ColorPicker(self.string_var, self.clabel)
        btn_true = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="True",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.green,
            height=2,
            width=18,
        )
        btn_true.grid(row=0, column=3, pady=2)
        btn_false = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="False",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.red,
            height=2,
            width=18,
        )
        btn_false.grid(row=0, column=2, pady=2)
        btn_true.bind("<Enter>", self.enter_button)
        btn_true.bind("<Leave>", self.leave_button)
        btn_false.bind("<Enter>", self.enter_button)
        btn_false.bind("<Leave>", self.leave_button)
        tk_tools.row_col_minsize(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.button_set_true)
        if btn["text"] == "False":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("show_download_window", True)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("show_download_window", False)


class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{SHOW_TERMINAL}")
        label = tk.Label(self, text="Terminal on search")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TKCOLOR.dark_grey, font=TKFONT.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.ColorPicker(self.string_var, self.clabel)
        if current_user.check_is_exe() is False:
            btn_true = tk.Button(
                self,
                font=TKFONT.cas8b,
                text="True",
                bd=0,
                bg=TKCOLOR.light_black,
                fg=TKCOLOR.white_grey,
                activebackground=TKCOLOR.green,
                height=2,
                width=18,
            )
            btn_true.grid(row=0, column=3, pady=2)
            btn_false = tk.Button(
                self,
                font=TKFONT.cas8b,
                text="False",
                bd=0,
                bg=TKCOLOR.light_black,
                fg=TKCOLOR.white_grey,
                activebackground=TKCOLOR.red,
                height=2,
                width=18,
            )
            btn_false.grid(row=0, column=2, pady=2)
            btn_true.bind("<Enter>", self.enter_button)
            btn_true.bind("<Leave>", self.leave_button)
            btn_false.bind("<Enter>", self.enter_button)
            btn_false.bind("<Leave>", self.leave_button)
            tk_tools.row_col_minsize(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.button_set_true)
        if btn["text"] == "False":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("show_terminal", True)
        raw_registry.write_valuex("command")

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("show_terminal", False)
        raw_registry.write_valuex("command")


class CheckForUpdates(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"")
        label = tk.Label(self, text=f"")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.yellow, font=TKFONT.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        btn_check = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="Check for updates",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.green,
            height=2,
            width=18,
        )
        btn_check.grid(row=0, column=3, pady=2)
        self.btn_download = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.red,
            height=2,
            width=18,
        )
        self.btn_download.grid(row=0, column=2, pady=2)
        btn_check.bind("<Enter>", self.enter_button)
        btn_check.bind("<Leave>", self.leave_button)
        self.btn_download.bind("<Enter>", self.enter_button)
        self.btn_download.bind("<Leave>", self.leave_button)
        tk_tools.row_col_minsize(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "Check for updates":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.button_check)
        if btn["text"].startswith("Get"):
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.button_download)

    def leave_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)

    def button_check(self, event):
        self.string_var.set(f"Looking...")
        new_repo_avail, repo_is_prerelease = updates.is_new_version_avail()
        latest_version = updates.get_latest_version()
        if new_repo_avail and repo_is_prerelease:
            if "-rc" in latest_version:
                self.string_var.set(f"Release candidate")
            elif "-alpha" in latest_version:
                self.string_var.set(f"Alpha release")
            elif "-beta" in latest_version:
                self.string_var.set(f"Beta release")
        elif new_repo_avail and repo_is_prerelease is False:
            self.string_var.set(f"Stable release")
        else:
            self.string_var.set(f"Up to date")

        if new_repo_avail:
            self.btn_download.configure(text=f"Get v{latest_version}")

    def button_download(self, event):
        webbrowser.open("https://github.com/vagabondHustler/SubSearch/releases")


class Footer(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.mid_grey_black, width=TKWINDOW.width - 4, height=80)
        self.active_window = "language"

        self.language_grey_path = tk_tools.buttons("language_grey.png")
        self.language_silver_path = tk_tools.buttons("language_silver.png")
        self.language_white_path = tk_tools.buttons("language_white.png")
        self.language_grey_png = tk.PhotoImage(file=self.language_grey_path)
        self.language_silver_png = tk.PhotoImage(file=self.language_silver_path)
        self.language_white_png = tk.PhotoImage(file=self.language_white_path)
        self.language = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=TKCOLOR.mid_grey_black,
            highlightthickness=0,
        )
        self.language.place(relx=0.2, rely=0.5, anchor="center")
        self.language.bind("<Enter>", self.enter_language)
        self.language.bind("<Leave>", self.leave_language)
        self.update_img(self.language, self.language_grey_png)

        self.search_grey_path = tk_tools.buttons("search_grey.png")
        self.search_silver_path = tk_tools.buttons("search_silver.png")
        self.search_white_path = tk_tools.buttons("search_white.png")
        self.search_grey_png = tk.PhotoImage(file=self.search_grey_path)
        self.search_silver_png = tk.PhotoImage(file=self.search_silver_path)
        self.search_white_png = tk.PhotoImage(file=self.search_white_path)
        self.search = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=TKCOLOR.mid_grey_black,
            highlightthickness=0,
        )
        self.search.place(relx=0.5, rely=0.5, anchor="center")
        self.search.bind("<Enter>", self.enter_search)
        self.search.bind("<Leave>", self.leave_search)
        self.update_img(self.search, self.search_grey_png)

        self.settings_grey_path = tk_tools.buttons("settings_grey.png")
        self.settings_silver_path = tk_tools.buttons("settings_silver.png")
        self.settings_white_path = tk_tools.buttons("settings_white.png")
        self.settings_grey_png = tk.PhotoImage(file=self.settings_grey_path)
        self.settings_silver_png = tk.PhotoImage(file=self.settings_silver_path)
        self.settings_white_png = tk.PhotoImage(file=self.settings_white_path)
        self.settings = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=TKCOLOR.mid_grey_black,
            highlightthickness=0,
        )
        self.settings.place(relx=0.8, rely=0.5, anchor="center")
        self.settings.bind("<Enter>", self.enter_settings)
        self.settings.bind("<Leave>", self.leave_settings)
        self.update_img(self.settings, self.settings_grey_png)
        tk_tools.row_col_minsize(self)

        self.activate_window()

    def release_language(self, event):
        self.active_window = "language"
        self.activate_window()

    def release_search(self, event):
        self.active_window = "search"
        self.activate_window()

    def release_settings(self, event):
        self.active_window = "settings"
        self.activate_window()

    def press_language(self, event):
        self.language.bind("<ButtonRelease>", self.release_language)
        self.update_img(self.language, self.language_white_png, y=20)

    def press_search(self, event):
        self.search.bind("<ButtonRelease>", self.release_search)
        self.update_img(self.search, self.search_white_png, y=20)

    def press_settings(self, event):
        self.settings.bind("<ButtonRelease>", self.release_settings)
        self.update_img(self.settings, self.settings_white_png, y=20)

    def activate_window(self):
        # language window
        if self.active_window == "language":
            language_window.place(relx=0.5, rely=0.5, anchor="center")
            self.update_img(self.language, self.language_white_png)
        else:
            language_window.place(relx=1, rely=0.5, anchor="nw")
            self.update_img(self.language, self.language_grey_png)

        # search window
        if self.active_window == "search":
            search_window.place(relx=0.5, rely=0.5, anchor="center")
            self.update_img(self.search, self.search_white_png)
        else:
            search_window.place(relx=1, rely=0.5, anchor="nw")
            self.update_img(self.search, self.search_grey_png)

        # settings window
        if self.active_window == "settings":
            settings_window.place(relx=0.5, rely=0.5, anchor="center")
            self.update_img(self.settings, self.settings_white_png)
        else:
            settings_window.place(relx=1, rely=0.5, anchor="nw")
            self.update_img(self.settings, self.settings_grey_png)

    def enter_search(self, event):
        self.search.bind("<ButtonPress>", self.press_search)
        self.update_img(self.search, self.search_silver_png, y=25)

    def leave_search(self, event):
        self.search.unbind("<ButtonPress>")
        self.activate_window()

    def enter_settings(self, event):
        self.settings.bind("<ButtonPress>", self.press_settings)
        self.update_img(self.settings, self.settings_silver_png, y=25)

    def leave_settings(self, event):
        self.settings.unbind("<ButtonPress>")
        self.activate_window()

    def enter_language(self, event):
        self.language.bind("<ButtonPress>", self.press_language)
        self.update_img(self.language, self.language_silver_png, y=25)

    def leave_language(self, event):
        self.language.unbind("<ButtonPress>")
        self.activate_window()

    def update_img(self, canvas, img, x=27, y=27):
        canvas.delete("all")
        canvas.create_image(x, y, image=img)
        canvas.photoimage = img


class LanguageWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        SelectLanguage(self).pack(anchor="center")


class SearchWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        Providers(self).pack(anchor="center")
        HearingImparedSubs(self).pack(anchor="center")
        SearchThreshold(self).pack(anchor="center")


class SettingsWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        FileExtensions(self).pack(anchor="center")
        tk.Frame(self, height=80, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)
        ShowContextMenu(self).pack(anchor="center")
        ShowContextMenuIcon(self).pack(anchor="center")
        ShowDownloadWindow(self).pack(anchor="center")
        if current_user.check_is_exe() is False:
            ShowTerminalOnSearch(self).pack(anchor="center")
        tk.Frame(self, height=20, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)
        CheckForUpdates(self).pack(anchor="center")


def show_widget():
    global base_root, language_window, search_window, settings_window
    if current_user.got_key() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()

    base_root = base_root.main()
    content = tk.Frame(base_root, bg=TKCOLOR.dark_grey, width=TKWINDOW.width - 4, height=TKWINDOW.height - 120)
    content.place(x=2, y=40)
    language_window = LanguageWindow(content)
    search_window = SearchWindow(content)
    settings_window = SettingsWindow(content)
    footer = Footer(base_root)
    footer.place(x=2, y=TKWINDOW.height - 82)

    base_root.mainloop()
