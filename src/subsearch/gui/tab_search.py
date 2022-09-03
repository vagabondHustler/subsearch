import tkinter as tk

from subsearch.data import __set_video__
from subsearch.gui import tk_data, tk_tools
from subsearch.utils import raw_config

TKCOLOR = tk_data.Color()
TKFONT = tk_data.Font()

HEARING_IMPARED = raw_config.get_config_key("hearing_impaired")
PCT = raw_config.get_config_key("percentage")
PROVIDERS = raw_config.get_config_key("providers")


class Providers(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.data = raw_config.get_config()
        number_of_buttons = len(PROVIDERS.items())
        label = tk.Label(self, text="Search providers")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=1, column=0, sticky="w", padx=2, pady=2)
        self.rownum = 0
        self.colnum = 2
        for i, key in zip(range(number_of_buttons), PROVIDERS.keys()):
            self.rownum += 1
            if self.rownum > 1:
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
            btn.grid(row=self.rownum, column=self.colnum, pady=2)
            if self.data["providers"][key] is False:
                btn.configure(fg=TKCOLOR.red)
            elif self.data["providers"][key] is True:
                btn.configure(fg=TKCOLOR.green)

            btn.bind("<Enter>", self.enter_button)
            btn.bind("<Leave>", self.leave_button)
            tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.orange)
        btn.bind("<ButtonPress>", self.press_button)

    def leave_button(self, event):
        btn = event.widget
        key = btn["text"]
        if self.data["providers"][key] is True:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.green)
        if self.data["providers"][key] is False:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.red)

    def press_button(self, event):
        btn = event.widget
        key = btn["text"]
        if self.data["providers"][key] is True:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.toggle_providers)
        if self.data["providers"][key] is False:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.toggle_providers)

    def toggle_providers(self, event):
        btn = event.widget
        key = btn["text"]
        if self.data["providers"][key] is True:
            self.data["providers"][key] = False
            btn.configure(fg=TKCOLOR.red)
        elif self.data["providers"][key] is False:
            self.data["providers"][key] = True
            btn.configure(fg=TKCOLOR.green)
        raw_config.set_config(self.data)


class HearingImpairedSubs(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{HEARING_IMPARED}")
        label = tk.Label(self, text="Hearing impaired")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TKCOLOR.dark_grey, font=TKFONT.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.ColorPicker(self.string_var, self.clabel)
        btn_true = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="True",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.green,
            height=2,
            width=18,
        )
        btn_true.grid(row=0, column=4, pady=2)
        btn_both = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="Both",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.blue,
            height=2,
            width=18,
        )
        btn_both.grid(row=0, column=3, pady=2)
        btn_false = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="False",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.red,
            height=2,
            width=18,
        )
        btn_false.grid(row=0, column=2, pady=2)
        btn_true.bind("<Enter>", self.enter_button)
        btn_true.bind("<Leave>", self.leave_button)
        btn_both.bind("<Enter>", self.enter_button)
        btn_both.bind("<Leave>", self.leave_button)
        btn_false.bind("<Enter>", self.enter_button)
        btn_false.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.button_set_true)
        if btn["text"] == "Both":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.blue)
            btn.bind("<ButtonRelease>", self.button_set_both)
        if btn["text"] == "False":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("hearing_impaired", True)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("hearing_impaired", False)

    def button_set_both(self, event):
        self.string_var.set(f"Both")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get().split(" ")[0]
        raw_config.set_config_key_value("hearing_impaired", update_svar)


class SearchThreshold(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{PCT} %")
        self.pct = PCT
        label = tk.Label(self, text="Search threshold")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TKCOLOR.dark_grey, font=TKFONT.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.ColorPicker(self.string_var, self.clabel, self.pct)
        btn_add = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="+",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.green,
            height=2,
            width=18,
        )
        btn_add.grid(row=0, column=4, pady=2)
        btn_sub = tk.Button(
            self,
            font=TKFONT.cas8b,
            text="-",
            bd=0,
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            activebackground=TKCOLOR.red,
            height=2,
            width=18,
        )
        btn_sub.grid(row=0, column=2, pady=2)
        btn_add.bind("<Enter>", self.enter_button)
        btn_add.bind("<Leave>", self.leave_button)
        btn_sub.bind("<Enter>", self.enter_button)
        btn_sub.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "+":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.button_add_5)
        if btn["text"] == "-":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.button_sub_5)

    def leave_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)
        tk_tools.ColorPicker(self.string_var, self.clabel)

    def button_add_5(self, event):
        self.pct += 5 if self.pct < 100 else 0
        self.string_var.set(f"{self.pct} %")

        tk_tools.ColorPicker(self.string_var, self.clabel, self.pct)
        update_svar = int(self.pct)
        raw_config.set_config_key_value("percentage", update_svar)

    def button_sub_5(self, event):
        self.pct -= 5 if self.pct > 0 else 0
        self.string_var.set(f"{self.pct} %")
        tk_tools.ColorPicker(self.string_var, self.clabel, self.pct)
        update_svar = int(self.pct)
        raw_config.set_config_key_value("percentage", update_svar)
