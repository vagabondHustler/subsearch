import tkinter as tk
from tkinter import IntVar, ttk

from subsearch.data.constants import FILE_PATHS
from subsearch.gui import utils
from subsearch.utils import io_toml


class SelectLanguage(ttk.Labelframe):
    def __init__(self, parent) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Languages", padding=10)
        self.active_btn = None
        self.rownum = 0
        self.colnum = 1
        self.checkbox_values = {}
        self.name_find_key = {}
        self.tip_present = False
        self.languages = io_toml.load_toml_data(FILE_PATHS.language_data)
        self.current_language = io_toml.load_toml_value(FILE_PATHS.config, "subtitle_filters.language")
        self.checkbuttons: dict[ttk.Checkbutton, IntVar] = {}
        frame = None
        for enum, (language, language_data) in enumerate(self.languages.items()):
            if enum % 14 == 0:
                frame = ttk.Frame(self)
                frame.pack(side=tk.LEFT, anchor="n")

            valuevar = tk.IntVar()
            btn = ttk.Checkbutton(frame, text=language_data["name"], onvalue=1, offvalue=9, variable=valuevar, width=20)
            if self.current_language == language:
                valuevar.set(1)
                self.checkbox_values[btn] = valuevar
            else:
                valuevar.set(0)
                self.checkbox_values[btn] = valuevar
            btn.pack(padx=2, pady=8)
            if valuevar.get() == 1:
                self.active_btn = btn

            btn.bind("<Enter>", self.enter_button)
            btn.bind("<Leave>", self.leave_button)
            self.name_find_key[language_data["name"]] = language

    def enter_button(self, event) -> None:
        btn = event.widget
        toml_key = self.name_find_key[btn["text"]]
        providers = ", ".join(([_i.title() for _i in self.languages[toml_key]["incompatibility"]]))
        if providers:
            tip_text = f"If enabled, '{providers}' will be automatically skipped."
            self.tip = utils.ToolTip(btn, btn, tip_text)
            self.tip.show()
            self.tip_present = True
        btn.bind("<ButtonPress-1>", self.press_button)

    def leave_button(self, event) -> None:
        btn = event.widget
        if self.tip_present:
            self.tip.hide()
            self.tip_present = False

    def press_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.set_current_language)

    def set_current_language(self, event) -> None:
        btn = event.widget
        self.checkbox_values[self.active_btn].set(0)  # type: ignore
        self.active_btn.state(["!alternate"])  # type: ignore
        self.active_btn = btn
        value = self.name_find_key[btn["text"]]
        io_toml.update_toml_key(FILE_PATHS.config, "subtitle_filters.language", value)
