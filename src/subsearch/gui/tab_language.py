import tkinter as tk
from tkinter import ttk

from subsearch.data.data_fields import TkColor
from subsearch.gui import tk_tools
from subsearch.utils import raw_config

LANGUAGES = raw_config.get_config_key("languages")
CURRENT_LANGUAGE = raw_config.get_config_key("current_language")


class SelectLanguage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.active_btn = None
        self.rownum = 0
        self.colnum = 1
        self.checkbox_values = {}
        for key in LANGUAGES.keys():
            if self.rownum == 14:
                self.rownum = 0
                self.colnum += 1
            valuevar = tk.IntVar()
            btn = ttk.Checkbutton(self, text=key, onvalue=1, offvalue=9, variable=valuevar, width=20)
            if CURRENT_LANGUAGE == key:
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
        tk_tools.set_default_grid_size(self, _width=6)

    def enter_button(self, event):
        btn = event.widget
        if LANGUAGES[btn["text"]] == "N/A":
            tip_text = "N/A with opensubtitles, provider will be skipped on search"
            self.tip = tk_tools.ToolTip(btn, btn, tip_text)
            self.tip.show()
        btn.bind("<ButtonPress-1>", self.press_button)

    def leave_button(self, event):
        btn = event.widget
        if LANGUAGES[btn["text"]] == "N/A":
            self.tip.hide()

    def press_button(self, event):
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.set_current_language)

    def set_current_language(self, event):
        btn = event.widget
        self.checkbox_values[self.active_btn].set(0)
        self.active_btn.state(["!alternate"])
        self.active_btn = btn

        raw_config.set_config_key_value("current_language", btn["text"])
