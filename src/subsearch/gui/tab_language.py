import tkinter as tk

from subsearch.gui import tk_data, tk_tools
from subsearch.utils import raw_config

TKCOLOR = tk_data.Color()
TKFONT = tk_data.Font()


LANGUAGES = raw_config.get_config_key("languages")
CURRENT_LANGUAGE = raw_config.get_config_key("current_language")


class SelectLanguage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{CURRENT_LANGUAGE}")
        number_of_buttons = len(LANGUAGES)
        self.btns = []
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

            btn.bind("<Enter>", self.enter_button)
            btn.bind("<Leave>", self.leave_button)
            tk_tools.set_default_grid_size(self, 18)

    def enter_button(self, event):
        btn = event.widget
        if LANGUAGES[btn["text"]] == "N/A":
            tip_text = "N/A with opensubtitles, provider will be skipped on search"
            self.tip = tk_tools.ToolTip(btn, btn, tip_text)
            self.tip.show()
        btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.orange)
        btn.bind("<ButtonRelease>", self.set_current_language)

    def leave_button(self, event):
        btn = event.widget
        if LANGUAGES[btn["text"]] == "N/A":
            self.tip.hide()
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)
        if btn["text"] == self.string_var.get():
            btn.configure(fg=TKCOLOR.yellow)

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
