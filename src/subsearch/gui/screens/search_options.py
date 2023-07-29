import tkinter as tk
from tkinter import ttk

from subsearch.data.constants import FILE_PATHS
from subsearch.gui import utils
from subsearch.gui.resources import config as cfg
from subsearch.utils import io_toml, string_parser


class Providers(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Subtitle providers", padding=10)
        self.data = io_toml.load_toml_data(FILE_PATHS.config)
        self.chekboxes = {}
        self.last_key = ""

        self.provider_options: dict = {
            "opensubtitles_site": "Opensubtitles",
            "opensubtitles_hash": "Opensubtitles with hash",
            "subscene_site": "Subscene",
            "yifysubtitles_site": "YIFYsubtitles",
        }
        for name, description in self.provider_options.items():
            self.provider_options[name] = [
                io_toml.load_toml_value(FILE_PATHS.config, "providers")[name],
                description,
            ]

        frame = None
        for enum, (key, value) in enumerate(self.provider_options.items()):
            if enum % 4 == 0:
                frame = tk.Frame(self)
                frame.pack(side=tk.LEFT, anchor="nw", expand=True)
            boolean = tk.BooleanVar()
            boolean.set(value[0])
            btn = ttk.Checkbutton(frame, text=value[1], onvalue=True, offvalue=False, variable=boolean)
            btn.pack(padx=4, pady=4, ipadx=20)
            self.chekboxes[btn] = key, boolean
            if self.data["providers"][key] is True:
                btn.configure(state="normal")

            btn.bind("<Enter>", self.enter_button)
            btn.bind("<Leave>", self.leave_button)

    def enter_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonPress-1>", self.press_button)

    def leave_button(self, event) -> None:
        btn = event.widget
        self.chekboxes[btn][0]

    def press_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.toggle_types)

    def toggle_types(self, event) -> None:
        btn = event.widget
        key = self.chekboxes[btn][0]
        value = self.chekboxes[btn][1]
        if value.get() is True:
            self.data["providers"][key] = False
        elif value.get() is False:
            self.data["providers"][key] = True
        io_toml.dump_toml_data(FILE_PATHS.config, self.data)

    def toggle_providers(self, event) -> None:
        btn = event.widget
        key = btn["text"].replace(" ", "_").lower()
        if self.data["providers"][key] is True:
            self.data["providers"][key] = False
            btn.configure(fg=cfg.color.red)
        elif self.data["providers"][key] is False:
            self.data["providers"][key] = True
            btn.configure(fg=cfg.color.green)
        io_toml.dump_toml_data(FILE_PATHS.config, self.data)


class SubtitleFilters(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Subtitle filters", padding=10)
        self.data = io_toml.load_toml_data(FILE_PATHS.config)
        self.subtitle_options: dict = {
            "subtitle_filters.hearing_impaired": "Hearing impaird",
            "subtitle_filters.non_hearing_impaired": "non-Hearing impaired",
            "subtitle_filters.only_foreign_parts": "Foreign parts only",
        }

        for name, description in self.subtitle_options.items():
            self.subtitle_options[name] = [io_toml.load_toml_value(FILE_PATHS.config, name), description]
        frame = None
        self.checkbuttons: dict[ttk.Checkbutton, tuple[str, tk.BooleanVar]] = {}
        for enum, (key, value) in enumerate(self.subtitle_options.items()):
            bool_value = value[0]
            description = value[1]
            if enum % 5 == 0:
                frame = ttk.Frame(self)
                frame.pack(side=tk.LEFT, anchor="nw", expand=True)

            boolean = tk.BooleanVar()
            boolean.set(bool_value)
            check_btn = ttk.Checkbutton(frame, text=description, onvalue=True, offvalue=False, variable=boolean)
            check_btn.pack(anchor="nw", padx=4, pady=4, ipadx=20)
            self.checkbuttons[check_btn] = key, boolean
            check_btn.bind("<Enter>", self.enter_button)

    def enter_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonPress-1>", self.press_button)

    def press_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.toggle_types)

    def toggle_types(self, event) -> None:
        btn = event.widget
        key = self.checkbuttons[btn][0]
        value = self.checkbuttons[btn][1]
        if value.get() is True:
            io_toml.update_toml_key(FILE_PATHS.config, key, False)
        elif value.get() is False:
            io_toml.update_toml_key(FILE_PATHS.config, key, True)


class SubtitlePostProcessing(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Subtitle post processing", padding=10)
        self.data = io_toml.load_toml_data(FILE_PATHS.config)

        self.subtitle_options: dict = {
            "subtitle_post_processing.rename": "Rename best subtitle",
            "subtitle_post_processing.move_best": "Move best subtitle",
            "subtitle_post_processing.move_all": "Move all subtitles",
        }
        for name, description in self.subtitle_options.items():
            self.subtitle_options[name] = [io_toml.load_toml_value(FILE_PATHS.config, name), description]
        frame = None
        self.checkbuttons: dict[ttk.Checkbutton, tuple[str, tk.BooleanVar]] = {}
        for enum, (key, value) in enumerate(self.subtitle_options.items()):
            bool_value = value[0]
            description = value[1]
            if enum % 1 == 0:
                frame = ttk.Frame(self)
                frame.pack(side=tk.LEFT, anchor="n")

            boolean = tk.BooleanVar()
            boolean.set(bool_value)
            check_btn = ttk.Checkbutton(frame, text=description, onvalue=True, offvalue=False, variable=boolean)
            check_btn.pack(padx=4, pady=4, ipadx=20)
            self.checkbuttons[check_btn] = key, boolean
            check_btn.bind("<Enter>", self.enter_button)

    def enter_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonPress-1>", self.press_button)

    def press_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.toggle_buttons)

    def toggle_buttons(self, event) -> None:
        btn = event.widget
        key = self.checkbuttons[btn][0]
        value = self.checkbuttons[btn][1]
        if value.get() is True:
            io_toml.update_toml_key(FILE_PATHS.config, key, False)
        elif value.get() is False:
            io_toml.update_toml_key(FILE_PATHS.config, key, True)


class SubtitlePostProcessingDirectory(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Subtitle move destination", padding=10)
        self.target_path = io_toml.load_toml_value(FILE_PATHS.config, "subtitle_post_processing.target_path")
        self.path_resolution = tk.StringVar()
        self._get_path_resolution()

        frame_l = tk.Frame(self)
        frame_c = tk.Frame(self)
        frame_r = tk.Frame(self)

        frame_l.pack(side=tk.LEFT, expand=False)
        frame_c.pack(side=tk.LEFT, expand=True, after=frame_l)
        frame_r.pack(side=tk.LEFT, expand=False, after=frame_c)

        self.btn_resolution = ttk.Button(frame_l, textvariable=self.path_resolution, width=10)
        self.entry_path = ttk.Entry(frame_c, width=50)
        apply_input = ttk.Button(frame_r, text="Apply", width=10)

        self.entry_path.insert(tk.END, f"{self.target_path}")

        self.btn_resolution.pack(anchor="center")
        self.entry_path.pack(anchor="center")
        apply_input.pack(anchor="center")

        self.btn_resolution.bind("<Enter>", self.enter_btn_resolution)
        self.btn_resolution.bind("<Leave>", self.leave_btn_resolution)
        apply_input.bind("<Enter>", self.enter_btn_apply_input)
        apply_input.bind("<Leave>", self.leave_btn_apply_input)
        self.entry_path.bind("<Enter>", self.enter_entry_path)

    def enter_entry_path(self, event):
        widget_ = event.widget
        path = widget_.get()
        old_path = path.replace("Invalid path: ", "")
        widget_.delete(0, tk.END)
        widget_.insert(tk.END, old_path)

    def enter_btn_apply_input(self, event):
        widget_ = event.widget
        path = self.verify_path()
        if self.entry_path.instate(["invalid"]):
            self.on_invalid_state(path)
            widget_.unbind("<ButtonPress-1>")
        elif not self.entry_path.instate(["invalid"]):
            widget_.bind("<ButtonPress-1>", self.update_config)

    def enter_btn_resolution(self, event) -> None:
        widget_ = event.widget
        widget_.bind("<ButtonPress-1>", self.toogle_path_resolution)

    def leave_btn_apply_input(self, event):
        widget_ = event.widget
        path = self.verify_path()
        if self.entry_path.instate(["invalid"]):
            self.on_invalid_state(path)
            widget_.unbind("<ButtonPress-1>")
        elif not self.entry_path.instate(["invalid"]):
            widget_.bind("<ButtonPress-1>", self.update_config)

    def leave_btn_resolution(self, event) -> None:
        widget_ = event.widget
        widget_.unbind("<ButtonPress-1>")

    def update_config(self, event):
        target_path = self.entry_path.get()
        path_resolution = self.path_resolution.get().lower()
        io_toml.update_toml_key(FILE_PATHS.config, "subtitle_post_processing.target_path", target_path)
        io_toml.update_toml_key(FILE_PATHS.config, "subtitle_post_processing.path_resolution", path_resolution)

    def verify_path(self) -> str:
        target_path = self.entry_path.get()
        path_resolution = self.path_resolution.get().lower()
        if not string_parser.valid_path(target_path, path_resolution):
            self.entry_path.state(["invalid"])
        else:
            self.entry_path.state(["!invalid"])
        return target_path

    def on_invalid_state(self, path):
        invalid_path = path.replace("Invalid path: ", "")
        self.entry_path.delete(0, tk.END)
        self.entry_path.insert(tk.END, f"Invalid path: {invalid_path}")

    def toogle_path_resolution(self, event) -> None:
        relative, absolute = "relative", "absolute"
        current_resolution = self.path_resolution.get().lower()
        if relative in current_resolution:
            self.btn_resolution["text"] = f"{absolute} path"
            self.path_resolution.set(absolute.capitalize())
        elif absolute in current_resolution:
            self.btn_resolution["text"] = f"{relative} to file"
            self.path_resolution.set(relative.capitalize())

    def _get_path_resolution(self) -> None:
        path_resolution: str = io_toml.load_toml_value(FILE_PATHS.config, "subtitle_post_processing.path_resolution")
        self.path_resolution.set(path_resolution.capitalize())


class SearchThreshold(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=cfg.color.default_bg)
        self.pct_threashold = io_toml.load_toml_value(FILE_PATHS.config, "subtitle_filters.accept_threshold")
        self.current_value = tk.IntVar()
        self.current_value.set(self.pct_threashold)
        self.pct_value = tk.StringVar()
        self.pct_value.set(f"{self.pct_threashold} %")

        frame_text = tk.Frame(self, bg=cfg.color.default_bg)
        frame_slider = tk.Frame(self, bg=cfg.color.default_bg)

        label_description = tk.Label(frame_text, text=f"Include subtitles matching video filename by")
        label_description.configure(bg=cfg.color.default_bg, fg=cfg.color.default_fg, font=cfg.font.cas8b)
        label_description.pack(side=tk.LEFT, anchor="n")

        self.label_pct = tk.Label(frame_text, textvariable=self.pct_value, width=4)
        self.label_pct.configure(bg=cfg.color.default_bg, font=cfg.font.cas8b)
        self.label_pct.pack(side=tk.LEFT, anchor="n")

        self.set_label_color()

        self.slider = ttk.Scale(
            frame_slider,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.current_value,
            length=500,
        )
        self.slider.pack(side=tk.LEFT, anchor="n")

        frame_text.pack(side=tk.TOP, anchor="n")
        frame_slider.pack(side=tk.TOP, anchor="n")
        self.slider.bind("<Enter>", self.enter_button)
        self.slider.bind("<Leave>", self.leave_button)

    def get_value(self):
        return self.current_value.get()

    def set_value(self, event) -> None:
        self.set_label_color()
        self.pct_value.set(f"{self.get_value()} %")

    def enter_button(self, event) -> None:
        btn = event.widget
        if btn == self.slider:
            self.slider.bind("<ButtonPress>", self.press_slider)
            self.slider.bind("<Double-ButtonRelease-1>", self.dubble_press)

    def leave_button(self, event) -> None:
        btn = event.widget
        if btn == self.slider:
            self.slider.configure(command=self.set_value)

    def dubble_press(self, event) -> None:
        btn = event.widget
        if btn == self.slider:
            self.current_value.set(90)
            self.pct_value.set(f"{90} %")
            self.slider.update()
            self.update_config()
            self.set_label_color()

    def press_slider(self, event) -> None:
        btn = event.widget
        if btn == self.slider:
            self.slider.configure(command=self.set_value)
            self.slider.bind("<ButtonRelease>", self.release_slider)

    def release_slider(self, event) -> None:
        btn = event.widget
        if btn == self.slider:
            self.slider.configure(command=self.set_value)
            self.update_config()

    def update_config(self) -> None:
        value = self.current_value.get()
        io_toml.update_toml_key(FILE_PATHS.config, "subtitle_filters.accept_threshold", value)

    def set_label_color(self) -> None:
        value = self.current_value.get()
        if value in range(75, 101):
            self.label_pct.configure(fg=cfg.color.green)
        elif value in range(50, 75):
            self.label_pct.configure(fg=cfg.color.green_brown)
        elif value in range(25, 50):
            self.label_pct.configure(fg=cfg.color.red_brown)
        elif value in range(0, 25):
            self.label_pct.configure(fg=cfg.color.red)
