import tkinter as tk
import webbrowser
from tkinter import BooleanVar, ttk
from typing import Any

from subsearch.globals import decorators
from subsearch.globals.constants import DEVICE_INFO, FILE_PATHS, VERSION
from subsearch.gui import common_utils
from subsearch.gui.resources import config as cfg
from subsearch.utils import io_toml, io_winreg, string_parser, update


def _handle_other_check_btn(cls, value, child_key) -> None:
    for check_button, tuple_value in cls.checkbuttons.items():
        key = tuple_value[0]
        if key != child_key:
            continue
        elif value.get():
            check_button.state(["disabled"])
        elif not value.get():
            check_button.state(["!disabled"])


class FileExtensions(ttk.Labelframe):
    instances: list["FileExtensions"] = []

    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="File Exstensions", padding=10)
        parent_key = "file_extensions"
        keys = io_toml.load_toml_value(FILE_PATHS.config, "file_extensions")
        config_keys: dict[str, Any] = {f"{parent_key}.{key}": f".{key}" for key in keys}
        helper = common_utils.CheckbuttonWidgets(parent=self, config_keys=config_keys, columns=4)
        helper.create(anchor="nw", padx=4, pady=4, ipadx=10)


class SubsearchOption(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Subsearch Options", padding=10)
        config_keys: dict[str, Any] = {
            "gui.context_menu": "Context menu",
            "gui.context_menu_icon": "Context menu icon",
            "gui.system_tray": "System tray icon",
            "gui.summary_notification": "Notification when done",
            "gui.show_terminal": "Terminal while searching",
            "misc.single_instance": "Single instance",
        }
        helper = common_utils.CheckbuttonWidgets(parent=self, config_keys=config_keys, columns=2)
        helper.create(anchor="nw", padx=4, pady=4, ipadx=40)


class DownloadManagerOptions(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Download manager options", padding=10)
        config_keys: dict[str, Any] = {
            "download_manager.open_on_no_matches": "Open on no matches",
            "download_manager.always_open": "Always open",
            "download_manager.automatic_downloads": "Automatic downloads",
        }
        helper = common_utils.CheckbuttonWidgets(parent=self, config_keys=config_keys, columns=1)
        helper.create(anchor="nw", padx=4, pady=4, ipadx=20)


class AdvancedUser(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Advanced user ( Requests / API )", padding=10)
        self.data = io_toml.load_toml_data(FILE_PATHS.config)
        self.tip_present = False
        self.tip = None
        adv_user = self.data["advanced_user"]
        adv_default_values = [
            adv_user["api_call_limit"],
            adv_user["request_connect_timeout"],
            adv_user["request_read_timeout"],
        ]

        self.adv_user_options: dict = {
            "advanced_user.api_call_limit": "API call limit",
            "advanced_user.request_connect_timeout": "Request connection timeout",
            "advanced_user.request_read_timeout": "Request read timeout",
        }
        for name, description in self.adv_user_options.items():
            self.adv_user_options[name] = [io_toml.load_toml_value(FILE_PATHS.config, name), description]
        frame = None
        frame_c = tk.Frame(self)
        frame_r = tk.Frame(self)

        self.entry_fields: dict[ttk.Entry, tuple[str, tk.IntVar]] = {}
        for enum, (key, value) in enumerate(self.adv_user_options.items()):
            bool_value = value[0]
            description = value[1]

            int_value = tk.IntVar()
            int_value.set(bool_value)
            field_name = ttk.Label(frame_c, text=description, justify="left")
            field = ttk.Entry(frame_c, width=3, justify="right")
            field.insert(tk.END, adv_default_values[enum])
            field_name.pack(side="left", anchor="center", fill="x")
            field.pack(side="left", anchor="center", padx=4)
            field.bind("<Enter>", self.enter_entry_field)
            self.entry_fields[field] = key, int_value
            # field.bind("<Enter>", self.enter_button)
        frame_c.pack(side=tk.LEFT, expand=True, fill="x")
        frame_r.pack(side=tk.LEFT, expand=False, after=frame_c)

        apply_input = ttk.Button(frame_r, text="Apply", width=10)
        apply_input.bind("<Enter>", self.enter_btn_apply_input)
        apply_input.bind("<Leave>", self.leave_btn_apply_input)
        apply_input.pack(anchor="center")

    def enter_btn_apply_input(self, event) -> None:
        btn = event.widget
        field_ok = True
        tip_text = (
            "If you don't know what these values do, don't touch them.",
            "Sending too many requests can get your IP banned.",
        )
        self.tip = common_utils.ToolTip(btn, btn, *tip_text)
        self.tip.show()
        self.tip_present = True
        for field, values in self.entry_fields.items():
            field: ttk.Entry
            user_input = self.verify_field(field)
            if field.instate(["invalid"]):
                self.on_invalid_state(user_input)
                btn.unbind("<ButtonPress-1>")
                field_ok = False
        if field_ok:
            btn.bind("<ButtonPress-1>", self.update_config)

    def leave_btn_apply_input(self, event: tk.Event) -> None:
        btn = event.widget
        if self.tip_present and self.tip:
            self.tip.hide()
            self.tip_present = False
        btn.bind("<ButtonPress-1>", self.enter_btn_apply_input)

    def update_config(self, event) -> None:
        for field, values in self.entry_fields.items():
            value = field.get()
            key = values[0]
            io_toml.update_toml_key(FILE_PATHS.config, key, int(value))

    def verify_field(self, field: ttk.Entry) -> str:
        user_input = field.get()
        if not string_parser.valid_api_request_input(user_input):
            field.state(["invalid"])
        else:
            field.state(["!invalid"])
        return user_input

    def on_invalid_state(self, path): ...

    def enter_entry_field(self, event): ...


class CheckForUpdates(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Update Subsearch", padding=10, style="TLabelframePlain")
        frame_left = tk.Frame(self, bg=cfg.color.default_bg)
        frame_right = tk.Frame(self, bg=cfg.color.default_bg)

        self.var_current = tk.StringVar(self, f"Current version:\t\t{VERSION}")
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
        self.btn_update_install = ttk.Button(
            frame_right,
            text="Download & Update",
            width=20,
        )
        self.btn_search.pack(padx=2, pady=2)
        self.btn_visit_release_page.pack(padx=2, pady=2)
        self.btn_visit_release_page.state(["disabled"])
        self.btn_update_install.pack(padx=2, pady=2)
        self.btn_update_install.state(["disabled"])
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
            if DEVICE_INFO.mode == "executable":
                self.btn_update_install.state(["!disabled"])
                self.btn_update_install.bind("<ButtonRelease-1>", self.download_and_update)
            else:
                self.btn_update_install["text"] = "Only availible with MSI"
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

    def download_and_update(self, event) -> None:
        update.download_and_update()
        self.btn_visit_release_page.state(["disabled"])
