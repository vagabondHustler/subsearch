import tkinter as tk
from tkinter import ttk

from subsearch.gui import gui_toolkit
from subsearch.gui.resources import config as cfg
from subsearch.utils import io_json


class Providers(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Search providers", padding=10)
        self.data = io_json.get_json_data()
        self.chekboxes = {}
        self.last_key = ""

        self.provider_options: dict = {
            "opensubtitles_site": "Search on OpenSubtitles",
            "opensubtitles_hash": "Search on OpenSubtitles with hash",
            "subscene_site": "Search on Subscene",
            "yifysubtitles_site": "Search on YIFYsubtitles",
        }
        for name, description in self.provider_options.items():
            self.provider_options[name] = [io_json.get_json_key("providers")[name], description]

        frame = None
        for enum, (key, value) in enumerate(self.provider_options.items()):
            if enum % 4 == 0:
                frame = tk.Frame(self)
                frame.pack(side=tk.LEFT, anchor="n", expand=True)
            boolean = tk.BooleanVar()
            boolean.set(value[0])
            btn = ttk.Checkbutton(frame, text=value[1], onvalue=True, offvalue=False, variable=boolean)
            btn.pack(padx=4, pady=4, ipadx=60)
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
        io_json.set_json_data(self.data)

    def toggle_providers(self, event) -> None:
        btn = event.widget
        key = btn["text"].replace(" ", "_").lower()
        if self.data["providers"][key] is True:
            self.data["providers"][key] = False
            btn.configure(fg=cfg.color.red)
        elif self.data["providers"][key] is False:
            self.data["providers"][key] = True
            btn.configure(fg=cfg.color.green)
        io_json.set_json_data(self.data)


class SubtitleOptions(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Subtitle Options", padding=10)
        self.data = io_json.get_json_data()
        self.subtitle_options: dict = {
            "hearing_impaired": "Include hearing impaird subtitles",
            "non_hearing_impaired": "Include regular subtitles",
            "foreign_only": "Only include subtitles for foreign parts",
            "autoload_rename": "Rename subtitle for 'Autoload'",
            "autoload_move": "Move subtitle to 'Autoload' directory",
        }
        for name, description in self.subtitle_options.items():
            if "hearing_impaired" in name:
                subtitle_type = io_json.get_json_key("subtitle_type")
                self.subtitle_options[name] = [subtitle_type[name], description]
            else:
                self.subtitle_options[name] = [io_json.get_json_key(name), description]
        frame = None
        self.checkbuttons: dict[ttk.Checkbutton, tuple[str, tk.BooleanVar]] = {}
        for enum, (key, value) in enumerate(self.subtitle_options.items()):
            bool_value = value[0]
            description = value[1]
            if enum % 5 == 0:
                frame = ttk.Frame(self)
                frame.pack(side=tk.LEFT, anchor="n")

            boolean = tk.BooleanVar()
            boolean.set(bool_value)
            check_btn = ttk.Checkbutton(frame, text=description, onvalue=True, offvalue=False, variable=boolean)
            check_btn.pack(padx=4, pady=4, ipadx=60)
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
            if "hearing_impaired" in key:
                self.data["subtitle_type"][key] = False
            else:
                self.data[key] = False
        elif value.get() is False:
            if "hearing_impaired" in key:
                self.data["subtitle_type"][key] = True
            else:
                self.data[key] = True
        io_json.set_json_data(self.data)

    def add_missig_json_key(self, name, description):
        subtitle_type = io_json.get_json_key("subtitle_type")
        self.subtitle_options[name] = [subtitle_type[name], description]


class SearchThreshold(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=cfg.color.dark_grey)
        self.pct_threashold = io_json.get_json_key("percentage_threshold")

        self.current_value = tk.IntVar()
        self.current_value.set(self.pct_threashold)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{self.pct_threashold} %")

        frame_text = tk.Frame(self, bg=cfg.color.dark_grey)
        frame_slider = tk.Frame(self, bg=cfg.color.dark_grey)

        label_description = tk.Label(frame_text, text=f"Include subtitles matching video filename by")
        label_description.configure(bg=cfg.color.dark_grey, fg=cfg.color.white_grey, font=cfg.font.cas8b)
        label_description.pack(side=tk.LEFT, anchor="n")

        self.label_pct = tk.Label(frame_text, textvariable=self.string_var, width=4)
        self.label_pct.configure(bg=cfg.color.dark_grey, font=cfg.font.cas8b)
        self.label_pct.pack(side=tk.LEFT, anchor="n")

        gui_toolkit.VarColorPicker(self.string_var, self.label_pct, True)
        x, y = gui_toolkit.calculate_btn_size(self, 36)

        self.slider = ttk.Scale(
            frame_slider, from_=0, to=100, orient="horizontal", variable=self.current_value, length=500
        )
        self.slider.pack(side=tk.LEFT, anchor="n")

        frame_text.pack(side=tk.TOP, anchor="n")
        frame_slider.pack(side=tk.TOP, anchor="n")
        self.slider.bind("<Enter>", self.enter_button)
        self.slider.bind("<Leave>", self.leave_button)
        gui_toolkit.set_default_grid_size(self)

    def get_value(self):
        return self.current_value.get()

    def set_value(self, event) -> None:
        self.string_var.set(f"{self.get_value()} %")

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
            self.string_var.set(f"{90} %")
            self.slider.update()
            self.update_config()

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
        update_svar = self.current_value.get()
        io_json.set_config_key_value("percentage_threshold", update_svar)
        gui_toolkit.VarColorPicker(self.string_var, self.label_pct, True)
