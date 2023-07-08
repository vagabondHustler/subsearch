import tkinter as tk
from tkinter import ttk

from subsearch.data import gui
from subsearch.gui import gui_toolkit
from subsearch.utils import io_json


class SelectLanguage(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=gui.colors.dark_grey)
        self.active_btn = None
        self.rownum = 0
        self.colnum = 1
        self.checkbox_values = {}
        self.name_find_key = {}
        self.tip_present = False
        self.languages = io_json.get_available_languages()
        self.current_language = io_json.get_json_key("current_language")
        for language, language_data in self.languages.items():
            if self.rownum == 14:
                self.rownum = 0
                self.colnum += 1
            valuevar = tk.IntVar()
            btn = ttk.Checkbutton(self, text=language_data["name"], onvalue=1, offvalue=9, variable=valuevar, width=20)
            if self.current_language == language:
                valuevar.set(1)
                self.checkbox_values[btn] = valuevar
            else:
                valuevar.set(0)
                self.checkbox_values[btn] = valuevar
            btn.grid(row=self.rownum, column=self.colnum, pady=8)
            if valuevar.get() == 1:
                self.active_btn = btn

            btn.bind("<Enter>", self.enter_button)
            btn.bind("<Leave>", self.leave_button)
            self.rownum += 1
            self.name_find_key[language_data["name"]] = language
        gui_toolkit.set_default_grid_size(self, width_=6)

    def enter_button(self, event) -> None:
        btn = event.widget
        json_key = self.name_find_key[btn["text"]]
        providers = ", ".join(([_i.title() for _i in self.languages[json_key]["incompatibility"]]))
        if providers:
            tip_text = f"If enabled, '{providers}' will be automatically skipped."
            self.tip = gui_toolkit.ToolTip(btn, btn, tip_text)
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
        json_key = self.name_find_key[btn["text"]]
        io_json.set_config_key_value("current_language", json_key)
