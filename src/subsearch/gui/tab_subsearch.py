import tkinter as tk
import webbrowser
from tkinter import ttk

from subsearch.data import __version__
from subsearch.data.data_fields import TkColor, TkFont
from subsearch.gui import tk_tools
from subsearch.utils import current_user, raw_config, raw_registry, updates

SHOW_TERMINAL = raw_config.get_config_key("show_terminal")
LOG_TO_FILE = raw_config.get_config_key("log_to_file")
CONTEXT_MENU_ICON = raw_config.get_config_key("context_menu_icon")
DL_WINDOW = raw_config.get_config_key("show_download_window")
AVAIL_EXT = raw_config.get_config_key("file_ext")


class FileExtensions(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.data = raw_config.get_config()
        number_of_buttons = len(AVAIL_EXT.items())
        label = tk.Label(self, text="File extensions")
        label.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.rownum = 0
        self.colnum = 0
        self.checkbox_value = {}
        number_of_rows = 4

        for i, (key, value) in zip(range(number_of_buttons), AVAIL_EXT.items()):
            self.rownum += 1
            if self.rownum > number_of_rows:
                self.rownum = 1
                self.colnum += 1

            valuevar = tk.BooleanVar()
            valuevar.set(value)
            btn = ttk.Checkbutton(self, text=key, onvalue=True, offvalue=False, variable=valuevar)
            btn.grid(row=self.rownum, column=self.colnum, pady=2)
            self.checkbox_value[btn] = key, valuevar
            btn.bind("<Enter>", self.enter_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        btn.bind("<ButtonPress-1>", self.press_button)

    def press_button(self, event):
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.toggle_ext)

    def toggle_ext(self, event):
        btn = event.widget
        key = self.checkbox_value[btn][0]
        value = self.checkbox_value[btn][1]
        if value.get() is True:
            self.data["file_ext"][key] = False
        elif value.get() is False:
            self.data["file_ext"][key] = True
        raw_config.set_config(self.data)

        self.update_registry()

    def update_registry(self):
        from subsearch.utils import raw_registry

        raw_registry.write_all_valuex()


class ShowContextMenu(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"True")
        label = tk.Label(self, text="Context menu")
        label.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TkColor().dark_grey, font=TkFont().cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        btn_true = ttk.Button(
            self,
            text="True",
            width=18,
        )
        btn_true.grid(row=0, column=3, pady=2)
        btn_false = ttk.Button(
            self,
            text="False",
            width=18,
        )
        btn_false.grid(row=0, column=2, pady=2)
        btn_true.bind("<Enter>", self.enter_button)
        btn_true.bind("<Leave>", self.leave_button)
        btn_false.bind("<Enter>", self.enter_button)
        btn_false.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_true)
        if btn["text"] == "False":

            btn.bind("<ButtonRelease-1>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        from subsearch.utils import raw_registry

        raw_registry.add_context_menu()
        raw_registry.write_all_valuex()

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        from subsearch.utils import raw_registry

        raw_registry.remove_context_menu()


class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{CONTEXT_MENU_ICON}")
        label = tk.Label(self, text="Context menu icon")
        label.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TkColor().dark_grey, font=TkFont().cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        btn_true = ttk.Button(
            self,
            text="True",
            width=18,
        )
        btn_true.grid(row=0, column=3, pady=2)
        btn_false = ttk.Button(
            self,
            text="False",
            width=18,
        )
        btn_false.grid(row=0, column=2, pady=2)
        btn_true.bind("<Enter>", self.enter_button)
        btn_true.bind("<Leave>", self.leave_button)
        btn_false.bind("<Enter>", self.enter_button)
        btn_false.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_true)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("context_menu_icon", True)
        from subsearch.utils import raw_registry

        raw_registry.write_valuex("icon")

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("context_menu_icon", False)
        from subsearch.utils import raw_registry

        raw_registry.write_valuex("icon")


class ShowDownloadWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{DL_WINDOW}")
        label = tk.Label(self, text="Download window")
        label.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TkColor().dark_grey, font=TkFont().cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        btn_true = ttk.Button(
            self,
            text="True",
            width=18,
        )
        btn_true.grid(row=0, column=3, pady=2)
        btn_false = ttk.Button(
            self,
            text="False",
            width=18,
        )
        btn_false.grid(row=0, column=2, pady=2)
        btn_true.bind("<Enter>", self.enter_button)
        btn_true.bind("<Leave>", self.leave_button)
        btn_false.bind("<Enter>", self.enter_button)
        btn_false.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_true)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("show_download_window", True)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("show_download_window", False)


class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{SHOW_TERMINAL}")
        label = tk.Label(self, text="Terminal on search")
        label.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TkColor().dark_grey, font=TkFont().cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        if current_user.running_from_exe() is False:
            btn_true = ttk.Button(
                self,
                text="True",
                width=18,
            )
            btn_true.grid(row=0, column=3, pady=2)
            btn_false = ttk.Button(
                self,
                text="False",
                width=18,
            )
            btn_false.grid(row=0, column=2, pady=2)
        btn_true.bind("<Enter>", self.enter_button)
        btn_true.bind("<Leave>", self.leave_button)
        btn_false.bind("<Enter>", self.enter_button)
        btn_false.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_true)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("show_terminal", True)
        raw_registry.write_valuex("command")

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("show_terminal", False)
        raw_registry.write_valuex("command")


class LogToFile(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{LOG_TO_FILE}")
        label = tk.Label(self, text="Create subsearch.log")
        label.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TkColor().dark_grey, font=TkFont().cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        btn_true = ttk.Button(
            self,
            text="True",
            width=18,
        )
        btn_true.grid(row=0, column=3, pady=2)
        btn_false = ttk.Button(
            self,
            text="False",
            width=18,
        )
        btn_false.grid(row=0, column=2, pady=2)
        btn_true.bind("<Enter>", self.enter_button)
        btn_true.bind("<Leave>", self.leave_button)
        btn_false.bind("<Enter>", self.enter_button)
        btn_false.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_true)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("log_to_file", True)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("log_to_file", False)


class CheckForUpdates(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"")
        label = tk.Label(self, text=f"Version {__version__}")
        label.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TkColor().dark_grey, fg=TkColor().yellow, font=TkFont().cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        btn_check = ttk.Button(
            self,
            text="Check for updates",
            width=18,
        )
        btn_check.grid(row=0, column=3, pady=2)
        self.btn_download = ttk.Button(
            self,
            text="",
            width=18,
        )
        self.btn_download.grid(row=0, column=2, pady=2)
        btn_check.bind("<Enter>", self.enter_button)
        self.btn_download.bind("<Enter>", self.enter_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "Check for updates":
            btn.bind("<ButtonRelease-1>", self.button_check)
        if btn["text"].startswith("Get"):
            btn.bind("<ButtonRelease-1>", self.button_download)

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
