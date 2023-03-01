import tkinter as tk
import webbrowser
from tkinter import ttk

from subsearch.data import GUI_DATA, __version__
from subsearch.gui import tk_tools
from subsearch.utils import file_manager, raw_config, raw_registry, updates

SHOW_TERMINAL = raw_config.get_config_key("show_terminal")
LOG_TO_FILE = raw_config.get_config_key("log_to_file")
CONTEXT_MENU = raw_config.get_config_key("context_menu")
CONTEXT_MENU_ICON = raw_config.get_config_key("context_menu_icon")
DLW_ON_FAIL = raw_config.get_config_key("manual_download_fail")
MANUAL_MODE = raw_config.get_config_key("manual_download_mode")
FILE_EXTENSIONS = raw_config.get_config_key("file_extensions")
USE_THREADING = raw_config.get_config_key("use_threading")
DEFAULT_LABEL_CONFIG = dict(bg=GUI_DATA.colors.dark_grey, fg=GUI_DATA.colors.white_grey, font=GUI_DATA.fonts.cas8b)
DEFAULT_LABEL_GRID = dict(row=0, column=0, sticky="w", padx=2, pady=2)
DEFAULT_BTN_TOGGLE_GRID = dict(row=0, column=2, pady=2)


class FileExtensions(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.data = raw_config.get_config()
        number_of_buttons = len(FILE_EXTENSIONS.items())
        label = tk.Label(self, text="File extensions")
        label.configure(DEFAULT_LABEL_CONFIG)
        label.grid(DEFAULT_LABEL_GRID)
        self.rownum = 0
        self.colnum = 0
        self.checkbox_value = {}
        number_of_rows = 4

        for i, (key, value) in zip(range(number_of_buttons), FILE_EXTENSIONS.items()):
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
            self.data["file_extensions"][key] = False
        elif value.get() is False:
            self.data["file_extensions"][key] = True
        raw_config.set_config(self.data)

        self.update_registry()

    def update_registry(self):
        from subsearch.utils import raw_registry

        raw_registry.write_all_valuex()


class ShowContextMenu(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{CONTEXT_MENU}")
        label = tk.Label(self, text="Context menu")
        label.configure(DEFAULT_LABEL_CONFIG)
        label.grid(DEFAULT_LABEL_GRID)
        btn_toggle = ttk.Button(
            self,
            textvariable=self.string_var,
            width=18,
            style=f"{self.string_var.get()}.TButton",
        )
        btn_toggle.grid(row=0, column=3, pady=2)
        btn_toggle.bind("<Enter>", self.enter_button)
        btn_toggle.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_false)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_true)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        btn = event.widget
        self.string_var.set(f"True")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("context_menu", True)
        raw_registry.add_context_menu()
        raw_registry.write_all_valuex()
        self.enter_button(event)

    def button_set_false(self, event):
        btn = event.widget
        self.string_var.set(f"False")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("context_menu", False)
        raw_registry.remove_context_menu()
        self.enter_button(event)


class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{CONTEXT_MENU_ICON}")
        label = tk.Label(self, text="Context menu icon")
        label.configure(DEFAULT_LABEL_CONFIG)
        label.grid(DEFAULT_LABEL_GRID)
        btn_toggle = ttk.Button(
            self,
            textvariable=self.string_var,
            width=18,
            style=f"{self.string_var.get()}.TButton",
        )
        btn_toggle.grid(DEFAULT_BTN_TOGGLE_GRID)
        btn_toggle.bind("<Enter>", self.enter_button)
        btn_toggle.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_false)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_true)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        btn = event.widget
        self.string_var.set(f"True")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("context_menu_icon", True)
        raw_registry.write_valuex("icon")
        self.enter_button(event)

    def button_set_false(self, event):
        btn = event.widget
        self.string_var.set(f"False")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("context_menu_icon", False)
        raw_registry.write_valuex("icon")
        self.enter_button(event)


class ShowDownloadWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{DLW_ON_FAIL}")
        label = tk.Label(self, text="Download window")
        label.configure(DEFAULT_LABEL_CONFIG)
        label.grid(DEFAULT_LABEL_GRID)
        btn_toggle = ttk.Button(
            self,
            textvariable=self.string_var,
            width=18,
            style=f"{self.string_var.get()}.TButton",
        )
        btn_toggle.grid(DEFAULT_BTN_TOGGLE_GRID)
        btn_toggle.bind("<Enter>", self.enter_button)
        btn_toggle.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_false)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_true)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        btn = event.widget
        self.string_var.set(f"True")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("manual_download_fail", True)
        self.enter_button(event)

    def button_set_false(self, event):
        btn = event.widget
        self.string_var.set(f"False")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("manual_download_fail", False)
        self.enter_button(event)


class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{SHOW_TERMINAL}")
        label = tk.Label(self, text="Terminal on search")
        label.configure(DEFAULT_LABEL_CONFIG)
        label.grid(DEFAULT_LABEL_GRID)
        if file_manager.running_from_exe() is False:
            btn_toggle = ttk.Button(
                self,
                textvariable=self.string_var,
                width=18,
                style=f"{self.string_var.get()}.TButton",
            )
            btn_toggle.grid(DEFAULT_BTN_TOGGLE_GRID)
            btn_toggle.bind("<Enter>", self.enter_button)
            btn_toggle.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_false)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_true)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        btn = event.widget
        self.string_var.set(f"True")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("show_terminal", True)
        raw_registry.write_valuex("command")
        self.enter_button(event)

    def button_set_false(self, event):
        btn = event.widget
        self.string_var.set(f"False")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("show_terminal", False)
        raw_registry.write_valuex("command")
        self.enter_button(event)


class LogToFile(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{LOG_TO_FILE}")
        label = tk.Label(self, text="Download window")
        label.configure(DEFAULT_LABEL_CONFIG)
        label.grid(DEFAULT_LABEL_GRID)
        btn_toggle = ttk.Button(
            self,
            textvariable=self.string_var,
            width=18,
            style=f"{self.string_var.get()}.TButton",
        )
        btn_toggle.grid(DEFAULT_BTN_TOGGLE_GRID)
        btn_toggle.bind("<Enter>", self.enter_button)
        btn_toggle.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_false)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_true)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        btn = event.widget
        self.string_var.set(f"False")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("log_to_file", True)
        self.enter_button(event)

    def button_set_false(self, event):
        btn = event.widget
        self.string_var.set(f"False")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("log_to_file", False)
        self.enter_button(event)


class UseThreading(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{USE_THREADING}")
        label = tk.Label(self, text="Download window")
        label.configure(DEFAULT_LABEL_CONFIG)
        label.grid(DEFAULT_LABEL_GRID)
        btn_toggle = ttk.Button(
            self,
            textvariable=self.string_var,
            width=18,
            style=f"{self.string_var.get()}.TButton",
        )
        btn_toggle.grid(DEFAULT_BTN_TOGGLE_GRID)
        btn_toggle.bind("<Enter>", self.enter_button)
        btn_toggle.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_false)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_true)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        btn = event.widget
        self.string_var.set(f"False")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("use_threading", True)
        self.enter_button(event)

    def button_set_false(self, event):
        btn = event.widget
        self.string_var.set(f"False")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value("use_threading", False)
        self.enter_button(event)


class CheckForUpdates(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"")
        label = tk.Label(self, text=f"Version {__version__}")
        label.configure(bg=GUI_DATA.colors.dark_grey, fg=GUI_DATA.colors.white_grey, font=GUI_DATA.fonts.cas8b)
        label.grid(DEFAULT_LABEL_GRID)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=GUI_DATA.colors.dark_grey, fg=GUI_DATA.colors.yellow, font=GUI_DATA.fonts.cas8b)
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
