import tkinter as tk
from tkinter import ttk

from subsearch.data import __set_video__
from subsearch.gui import tk_data, tk_tools
from subsearch.utils import raw_config

TKCOLOR = tk_data.Color()
TKFONT = tk_data.Font()

SUBTILE_TYPE = raw_config.get_config_key("subtitle_type")
PCT = raw_config.get_config_key("percentage")
RENAME_BEST_MATCH = raw_config.get_config_key("rename_best_match")
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
            if self.rownum == 2:
                self.rownum = 1
                self.colnum += 1
            self.rownum += 1

            btn = tk.Button(
                self,
                font=TKFONT.cas8b,
                text=key.replace("_", " ").capitalize(),
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
        key = btn["text"].replace(" ", "_").lower()
        if self.data["providers"][key] is True:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.green)
        if self.data["providers"][key] is False:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.red)

    def press_button(self, event):
        btn = event.widget
        key = btn["text"].replace(" ", "_").lower()
        if self.data["providers"][key] is True:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.toggle_providers)
        if self.data["providers"][key] is False:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.toggle_providers)

    def toggle_providers(self, event):
        btn = event.widget
        key = btn["text"].replace(" ", "_").lower()
        if self.data["providers"][key] is True:
            self.data["providers"][key] = False
            btn.configure(fg=TKCOLOR.red)
        elif self.data["providers"][key] is False:
            self.data["providers"][key] = True
            btn.configure(fg=TKCOLOR.green)
        raw_config.set_config(self.data)


class SubtitleType(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()

        self.data = raw_config.get_config()
        number_of_buttons = len(SUBTILE_TYPE.items())
        label = tk.Label(self, text="Subtitle type")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=1, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TKCOLOR.dark_grey, font=TKFONT.cas8b)
        self.clabel.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        self.sub_type_txt()
        tk_tools.ColorPicker(self.string_var, self.clabel)
        self.rownum = 0
        self.colnum = 2
        for i, key in zip(range(number_of_buttons), SUBTILE_TYPE.keys()):
            self.rownum += 1
            if self.rownum > 1:
                self.rownum = 1
                self.colnum += 1

            btn = tk.Button(
                self,
                font=TKFONT.cas8b,
                text=key.replace("_", " ").title(),
                bd=0,
                bg=TKCOLOR.light_black,
                fg=TKCOLOR.white_grey,
                activebackground=TKCOLOR.orange,
                height=2,
                width=18,
            )
            btn.grid(row=self.rownum, column=self.colnum, pady=2)
            if self.data["subtitle_type"][key] is False:
                btn.configure(fg=TKCOLOR.red)
            elif self.data["subtitle_type"][key] is True:
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
        key = btn["text"].replace(" ", "_").lower()
        if self.data["subtitle_type"][key] is True:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.green)
        if self.data["subtitle_type"][key] is False:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.red)

    def press_button(self, event):
        btn = event.widget
        key = btn["text"].replace(" ", "_").lower()
        if self.data["subtitle_type"][key] is True:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.toggle_types)
        if self.data["subtitle_type"][key] is False:
            btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.toggle_types)

    def toggle_types(self, event):
        btn = event.widget
        key = btn["text"].replace(" ", "_").lower()
        if self.data["subtitle_type"][key] is True:
            self.data["subtitle_type"][key] = False
            btn.configure(fg=TKCOLOR.red)
        elif self.data["subtitle_type"][key] is False:
            self.data["subtitle_type"][key] = True
            btn.configure(fg=TKCOLOR.green)
        raw_config.set_config(self.data)
        self.sub_type_txt()

    def sub_type_txt(self):
        hi_sub = self.data["subtitle_type"]["hearing_impaired"]
        nonhi_sub = self.data["subtitle_type"]["non_hearing_impaired"]
        if (hi_sub and nonhi_sub) or (hi_sub is False and nonhi_sub is False):
            self.string_var.set(f"Both")
        if hi_sub and nonhi_sub is False:
            self.string_var.set(f"Only HI")
        if hi_sub is False and nonhi_sub:
            self.string_var.set(f"Only non-HI")
        tk_tools.ColorPicker(self.string_var, self.clabel)


class SearchThreshold(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.current_value = tk.IntVar()
        self.current_value.set(PCT)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{PCT} %")
        label = tk.Label(self, text="Search threshold")
        label.configure(bg=TKCOLOR.dark_grey, fg=TKCOLOR.white_grey, font=TKFONT.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=0, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TKCOLOR.dark_grey, font=TKFONT.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.ColorPicker(self.string_var, self.clabel, True)
        x, y = tk_tools.calculate_btn_size(self, 36)
        self.slider = ttk.Scale(
            self, from_=0, to=100, orient="horizontal", variable=self.current_value, length=x
        )  # vertical
        self.slider.grid(column=2, row=0, sticky="we", padx=4)
        self.slider.bind("<Enter>", self.enter_button)
        self.slider.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def get_value(self):
        return self.current_value.get()

    def set_value(self, event):
        self.string_var.set(f"{self.get_value()} %")

    def enter_button(self, event):
        btn = event.widget
        if btn == self.slider:
            self.slider.bind("<ButtonPress>", self.press_slider)
            self.slider.bind("<Double-ButtonRelease-1>", self.dubble_press)

    def leave_button(self, event):
        btn = event.widget
        if btn == self.slider:
            self.slider.configure(command=self.set_value)

    def dubble_press(self, event):
        btn = event.widget
        if btn == self.slider:
            self.current_value.set(90)
            self.string_var.set(f"{90} %")
            self.slider.update()
            self.update_config()

    def press_slider(self, event):
        btn = event.widget
        if btn == self.slider:
            self.slider.configure(command=self.set_value)
            self.slider.bind("<ButtonRelease>", self.release_slider)

    def release_slider(self, event):
        btn = event.widget
        if btn == self.slider:
            self.slider.configure(command=self.set_value)
            self.update_config()

    def update_config(self):
        update_svar = self.current_value.get()
        raw_config.set_config_key_value("percentage", update_svar)
        tk_tools.ColorPicker(self.string_var, self.clabel, True)


class RenameBestMatch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{RENAME_BEST_MATCH}")
        label = tk.Label(self, text="Rename best match")
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
        btn_true.grid(row=0, column=3, pady=2)
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
        btn_false.bind("<Enter>", self.enter_button)
        btn_false.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        if btn["text"] == "True":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.green)
            btn.bind("<ButtonRelease>", self.button_set_true)
        if btn["text"] == "False":
            btn.configure(bg=TKCOLOR.black, fg=TKCOLOR.red)
            btn.bind("<ButtonRelease>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget
        btn.configure(bg=TKCOLOR.light_black, fg=TKCOLOR.white_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("rename_best_match", True)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.ColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("rename_best_match", False)
