import tkinter as tk
from tkinter import ttk

from subsearch.data.data_fields import TkColor, TkFont
from subsearch.gui import tk_tools
from subsearch.utils import raw_config

SUBTILE_TYPE = raw_config.get_config_key("subtitle_type")
PCT = raw_config.get_config_key("percentage")
RENAME_BEST_MATCH = raw_config.get_config_key("rename_best_match")
PROVIDERS = raw_config.get_config_key("providers")


class Providers(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.data = raw_config.get_config()
        label = tk.Label(self, text="Search providers")
        label.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
        label.grid(row=1, column=0, sticky="w", padx=2, pady=2)
        self.rownum = 0
        self.colnum = 2
        self.checkbox_value = {}
        self.last_key = ""
        for key, value in PROVIDERS.items():
            btn_txt = key.split("_")[-1].capitalize()
            lbl_txt = f"{key.split('_')[0]}".capitalize()
            valuevar = tk.BooleanVar()
            valuevar.set(value)
            if self.last_key.startswith(lbl_txt):
                self.colnum += 1
            if self.last_key != lbl_txt:
                self.rownum += 1
                self.colnum = 2
                _lbl = tk.Label(self, text=lbl_txt)
                _lbl.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
                _lbl.grid(row=self.rownum, column=2, sticky="w", padx=2, pady=2)
            else:
                self.rownum -= 1
            self.rownum += 1
            self.last_key = lbl_txt
            btn = ttk.Checkbutton(self, text=btn_txt, onvalue=True, offvalue=False, variable=valuevar)
            btn.grid(row=self.rownum, column=self.colnum, pady=2)
            self.checkbox_value[btn] = key, valuevar
            if self.data["providers"][key] is True:
                btn.configure(state="normal")

            btn.bind("<Enter>", self.enter_button)
            btn.bind("<Leave>", self.leave_button)
        tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        key = self.checkbox_value[btn][0]
        if key == "yifysubtitles_site":
            tip_text = "No filter for subtitle type on yifysubtitles"
            self.tip = tk_tools.ToolTip(btn, btn, tip_text)
            self.tip.show()
        btn.bind("<ButtonPress-1>", self.press_button)

    def leave_button(self, event):
        btn = event.widget
        key = self.checkbox_value[btn][0]
        if key == "yifysubtitles_site":
            self.tip.hide()

    def press_button(self, event):
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.toggle_types)

    def toggle_types(self, event):
        btn = event.widget
        key = self.checkbox_value[btn][0]
        value = self.checkbox_value[btn][1]
        if value.get() is True:
            self.data["providers"][key] = False
        elif value.get() is False:
            self.data["providers"][key] = True
        raw_config.set_config(self.data)

    def toggle_providers(self, event):
        btn = event.widget
        key = btn["text"].replace(" ", "_").lower()
        if self.data["providers"][key] is True:
            self.data["providers"][key] = False
            btn.configure(fg=TkColor().red)
        elif self.data["providers"][key] is False:
            self.data["providers"][key] = True
            btn.configure(fg=TkColor().green)
        raw_config.set_config(self.data)


class SubtitleType(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.string_var = tk.StringVar()
        self.data = raw_config.get_config()
        label = tk.Label(self, text="Subtitle type")
        label.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
        label.grid(row=1, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TkColor().dark_grey, font=TkFont().cas8b)
        self.clabel.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        self.sub_type_txt()
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        self.rownum = 0
        self.colnum = 2
        self.checkbox_values = {}
        for key, value in SUBTILE_TYPE.items():
            if key.startswith("non"):
                _text = "Regular"
            else:
                _text = key.replace("_", " ").title()
            valuevar = tk.BooleanVar()
            valuevar.set(value)
            self.rownum += 1
            if self.rownum > 1:
                self.rownum = 1
                self.colnum += 1
            btn = ttk.Checkbutton(self, text=_text, onvalue=True, offvalue=False, variable=valuevar)
            btn.grid(row=self.rownum, column=self.colnum, pady=2)
            self.checkbox_values[btn] = key, valuevar

            btn.bind("<Enter>", self.enter_button)
            tk_tools.set_default_grid_size(self)

    def enter_button(self, event):
        btn = event.widget
        btn.bind("<ButtonPress-1>", self.press_button)

    def press_button(self, event):
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.toggle_types)

    def toggle_types(self, event):
        btn = event.widget
        key = self.checkbox_values[btn][0]
        value = self.checkbox_values[btn][1]
        if value.get() is True:
            self.data["subtitle_type"][key] = False
        elif value.get() is False:
            self.data["subtitle_type"][key] = True
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
        tk_tools.VarColorPicker(self.string_var, self.clabel)


class SearchThreshold(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.current_value = tk.IntVar()
        self.current_value.set(PCT)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{PCT} %")
        label = tk.Label(self, text="Search threshold")
        label.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
        label.grid(row=0, column=0, sticky="w", padx=0, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TkColor().dark_grey, font=TkFont().cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.VarColorPicker(self.string_var, self.clabel, True)
        x, y = tk_tools.calculate_btn_size(self, 36)
        self.slider = ttk.Scale(self, from_=0, to=100, orient="horizontal", variable=self.current_value, length=x - 2)
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
        tk_tools.VarColorPicker(self.string_var, self.clabel, True)


class RenameBestMatch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{RENAME_BEST_MATCH}")
        label = tk.Label(self, text="Rename best match")
        label.configure(bg=TkColor().dark_grey, fg=TkColor().white_grey, font=TkFont().cas8b)
        label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=TkColor().dark_grey, font=TkFont().cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        btn_true = ttk.Button(
            self,
            text="True",
            width=18,
        )
        btn_true.grid(row=0, column=3, pady=2)
        btn_false = ttk.Button(
            self,
            text="False",
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
            btn.bind("<ButtonRelease>", self.button_set_true)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease>", self.button_set_false)

    def leave_button(self, event):
        btn = event.widget

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("rename_best_match", True)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tk_tools.VarColorPicker(self.string_var, self.clabel)
        raw_config.set_config_key_value("rename_best_match", False)
