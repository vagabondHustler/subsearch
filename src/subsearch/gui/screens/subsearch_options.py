import tkinter as tk
import webbrowser
from tkinter import BooleanVar, ttk
from typing import Any

from subsearch.data import __version__
from subsearch.data.constants import DEVICE_INFO, FILE_PATHS
from subsearch.gui.resources import config as cfg
from subsearch.utils import decorators, io_toml, io_winreg, update


class FileExtensions(ttk.Labelframe):
    instances: list["FileExtensions"] = []

    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="File Exstensions", padding=10)
        FileExtensions.instances.append(self)
        self.data = io_toml.load_toml_data(FILE_PATHS.config)
        self.file_extensions = io_toml.load_toml_value(FILE_PATHS.config, "file_extensions")

        self.checkbuttons: dict[ttk.Checkbutton, tuple[str, BooleanVar]] = {}

        frame = None
        for enum, (key, value) in enumerate(self.file_extensions.items()):
            if enum % 4 == 0:
                frame = ttk.Frame(self)
                frame.pack(side=tk.LEFT, anchor="n")

            boolean = tk.BooleanVar()
            boolean.set(value)
            check_btn = ttk.Checkbutton(frame, text=key, onvalue=True, offvalue=False, variable=boolean)
            if not io_toml.load_toml_value(FILE_PATHS.config, "gui.context_menu"):
                check_btn.state(["disabled"])

            check_btn.pack(padx=4, pady=4, ipadx=10)
            self.checkbuttons[check_btn] = key, boolean
            check_btn.bind("<Enter>", self.enter_button)
        setattr(FileExtensions, "instance_cbtn", self.checkbuttons)

    def enter_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonPress-1>", self.press_button)

    def press_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.toggle_ext)

    @decorators.check_option_disabled
    def toggle_ext(self, event) -> None:
        btn = event.widget
        key = self.checkbuttons[btn][0]
        value = self.checkbuttons[btn][1]
        if value.get():
            self.data["file_extensions"][key] = False
        elif not value.get():
            self.data["file_extensions"][key] = True
        io_toml.dump_toml_data(FILE_PATHS.config, self.data)

        self.update_registry()

    def update_registry(self) -> None:
        io_winreg.write_all_valuex()

    def update_state(self):
        for key in self.checkbuttons.keys():
            if io_toml.load_toml_value(FILE_PATHS.config, "gui.context_menu"):
                key.state(["!disabled"])
            else:
                key.state(["disabled"])


class SubsearchOption(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Subsearch Options", padding=10)
        self.data = io_toml.load_toml_data(FILE_PATHS.config)
        self.subsearch_options: dict[str, Any] = {
            "gui.context_menu": "Context menu",
            "gui.context_menu_icon": "Context menu icon",
            "gui.system_tray": "System tray icon",
            "gui.summary_notification": "Notification when done",
            "gui.show_terminal": "Terminal while searching",
            "misc.manual_download_on_fail": "Manual download on fail",
            "misc.multithreading": "Multithreading",
            "misc.single_instance": "Single instance",
        }
        for name, description in self.subsearch_options.items():
            self.subsearch_options[name] = [
                io_toml.load_toml_value(FILE_PATHS.config, name),
                description,
            ]

        self.checkbuttons: dict[ttk.Checkbutton, tuple[str, BooleanVar]] = {}
        frame = None

        for enum, (key, value) in enumerate(self.subsearch_options.items()):
            if enum % 3 == 0:
                frame = ttk.Frame(self)
                frame.pack(side=tk.LEFT, anchor="n")

            boolean = tk.BooleanVar()
            boolean.set(value[0])
            check_btn = ttk.Checkbutton(frame, text=value[1], onvalue=True, offvalue=False, variable=boolean)
            context_menu = io_toml.load_toml_value(FILE_PATHS.config, "gui.context_menu")
            system_tray = io_toml.load_toml_value(FILE_PATHS.config, "gui.system_tray")
            if key == "gui.context_menu_icon" and not context_menu:
                check_btn.state(["disabled"])
            if key == "gui.show_terminal" and DEVICE_INFO.mode == "executable":
                check_btn.state(["disabled"])
            if key == "gui.summary_notification" and not system_tray:
                check_btn.state(["disabled"])
            check_btn.pack(padx=4, pady=4, ipadx=40)

            self.checkbuttons[check_btn] = key, boolean
            check_btn.bind("<Enter>", self.enter_button)

    def enter_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonPress-1>", self.press_button)

    def press_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.toggle_btn)

    @decorators.check_option_disabled
    def toggle_btn(self, event) -> None:
        btn = event.widget
        key = self.checkbuttons[btn][0]
        value = self.checkbuttons[btn][1]
        if value.get():
            io_toml.update_toml_key(FILE_PATHS.config, key, False)
        elif not value.get():
            io_toml.update_toml_key(FILE_PATHS.config, key, True)
        self.update_registry(btn)
        keys = [("gui.context_menu", "gui.context_menu_icon"), ("gui.system_tray", "gui.summary_notification")]
        for key_pair in keys:
            self.disable_check_btn_children(btn, value, key_pair)

    def disable_check_btn_children(self, btn: Any, value: BooleanVar, key_pair: tuple[str, str]):
        # FileExtension checkboxes
        parent_key = key_pair[0]
        child_key = key_pair[1]
        if btn["text"] != self.subsearch_options[parent_key][1]:
            return None
        [instance.update_state() for instance in FileExtensions.instances]

        # SubsearchOptions checkboxes
        for check_button, tuple_value in self.checkbuttons.items():
            key = tuple_value[0]
            if key != child_key:
                continue
            elif value.get():
                check_button.state(["disabled"])
            elif not value.get():
                check_button.state(["!disabled"])

    def update_registry(self, btn) -> None:
        if btn["text"] != self.subsearch_options["gui.context_menu"][1]:
            return None
        menu = io_toml.load_toml_value(FILE_PATHS.config, "gui.context_menu")
        if menu:
            io_winreg.add_context_menu()
        else:
            io_winreg.del_context_menu()


class CheckForUpdates(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Update Subsearch", padding=10, style="TLabelframePlain")
        frame_left = tk.Frame(self, bg=cfg.color.default_bg)
        frame_right = tk.Frame(self, bg=cfg.color.default_bg)

        self.var_current = tk.StringVar(self, f"Current version:\t\t{__version__}")
        self.var_latest = tk.StringVar(self, "Latest version: \t\t")
        self.var_misc = tk.StringVar()

        frame_current = tk.Label(frame_left, textvariable=self.var_current, justify="left")
        frame_latest = tk.Label(frame_left, textvariable=self.var_latest, justify="left")
        self.frame_misc = tk.Label(frame_left, textvariable=self.var_misc, justify="left")
        frame_current.pack(anchor="w")
        frame_latest.pack(anchor="w")
        self.frame_misc.pack(pady=16, anchor="w")

        self.btn_search = ttk.Button(
            frame_right,
            text="Search",
            width=20,
        )
        self.btn_visit_release_page = ttk.Button(
            frame_right,
            text="Open in webbrowser",
            width=20,
        )
        self.btn_search.pack(padx=2, pady=2)
        self.btn_visit_release_page.pack(padx=2, pady=2)
        self.btn_visit_release_page.state(["disabled"])
        self.btn_search.bind("<Enter>", self.enter_button)

        self.pack(anchor="center", fill="x")
        width = self.winfo_reqwidth()
        half_width = round(width // 2)
        frame_left.pack(side=tk.LEFT, anchor="n", expand=True, fill="x", ipadx=half_width)
        frame_right.pack(side=tk.LEFT, anchor="n", expand=True, fill="x", ipadx=half_width)

    def enter_button(self, event) -> None:
        btn = event.widget
        if btn == self.btn_search:
            btn.bind("<ButtonRelease-1>", self.search_button)

    def search_button(self, event) -> None:
        new_repo_avail, repo_is_prerelease = update.is_new_version_avail()
        latest_version = update.get_latest_version()
        if new_repo_avail:
            self.var_latest.set(f"Latest version: \t\t{latest_version}")
            self.btn_search.state(["disabled"])
            self.btn_visit_release_page.state(["!disabled"])
            self.btn_visit_release_page.bind("<ButtonRelease-1>", self.visit_repository_button)
            if repo_is_prerelease:
                self.var_misc.set(f"Pre-release")
                self.frame_misc.configure(fg=cfg.color.orange)
            else:
                self.var_misc.set(f"Latest")
                self.frame_misc.configure(fg=cfg.color.green)

        if not new_repo_avail:
            self.var_latest.set(f"Latest version: \t\t{latest_version}")
            self.var_misc.set(f"Latest version already installed")

    def visit_repository_button(self, event) -> None:
        webbrowser.open(f"https://github.com/vagabondHustler/subsearch/releases")
