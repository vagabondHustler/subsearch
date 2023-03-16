import tkinter as tk
from tkinter import ttk

from subsearch.data import GUI_DATA
from subsearch.gui import tkinter_utils
from subsearch.utils import io_json

SUBTILE_TYPE = io_json.get_json_key("subtitle_type")
PERCENTAGE_THRESHOLD = io_json.get_json_key("percentage_threshold")
PROVIDERS = io_json.get_json_key("providers")


class Providers(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.data = io_json.get_json_data()
        label = tk.Label(self, text="Search providers")
        label.configure(bg=GUI_DATA.colors.dark_grey, fg=GUI_DATA.colors.white_grey, font=GUI_DATA.fonts.cas8b)
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
                _lbl.configure(bg=GUI_DATA.colors.dark_grey, fg=GUI_DATA.colors.white_grey, font=GUI_DATA.fonts.cas8b)
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
        tkinter_utils.set_default_grid_size(self)

    def enter_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonPress-1>", self.press_button)

    def leave_button(self, event) -> None:
        btn = event.widget
        self.checkbox_value[btn][0]

    def press_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.toggle_types)

    def toggle_types(self, event) -> None:
        btn = event.widget
        key = self.checkbox_value[btn][0]
        value = self.checkbox_value[btn][1]
        if value.get() is True:
            self.data["providers"][key] = False
        elif value.get() is False:
            self.data["providers"][key] = True
        io_json.set_config(self.data)

    def toggle_providers(self, event) -> None:
        btn = event.widget
        key = btn["text"].replace(" ", "_").lower()
        if self.data["providers"][key] is True:
            self.data["providers"][key] = False
            btn.configure(fg=GUI_DATA.colors.red)
        elif self.data["providers"][key] is False:
            self.data["providers"][key] = True
            btn.configure(fg=GUI_DATA.colors.green)
        io_json.set_config(self.data)


class SubtitleType(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.string_var = tk.StringVar()
        self.data = io_json.get_json_data()
        label = tk.Label(self, text="Subtitle type")
        label.configure(bg=GUI_DATA.colors.dark_grey, fg=GUI_DATA.colors.white_grey, font=GUI_DATA.fonts.cas8b)
        label.grid(row=1, column=0, sticky="w", padx=2, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=GUI_DATA.colors.dark_grey, font=GUI_DATA.fonts.cas8b)
        self.clabel.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        self.sub_type_txt()
        tkinter_utils.VarColorPicker(self.string_var, self.clabel)
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
            tkinter_utils.set_default_grid_size(self)

    def enter_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonPress-1>", self.press_button)

    def press_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.toggle_types)

    def toggle_types(self, event) -> None:
        btn = event.widget
        key = self.checkbox_values[btn][0]
        value = self.checkbox_values[btn][1]
        if value.get() is True:
            self.data["subtitle_type"][key] = False
        elif value.get() is False:
            self.data["subtitle_type"][key] = True
        io_json.set_config(self.data)
        self.sub_type_txt()

    def sub_type_txt(self) -> None:
        hi_sub = self.data["subtitle_type"]["hearing_impaired"]
        nonhi_sub = self.data["subtitle_type"]["non_hearing_impaired"]
        if (hi_sub and nonhi_sub) or (hi_sub is False and nonhi_sub is False):
            self.string_var.set(f"Both")
        if hi_sub and nonhi_sub is False:
            self.string_var.set(f"Only HI")
        if hi_sub is False and nonhi_sub:
            self.string_var.set(f"Only non-HI")
        tkinter_utils.VarColorPicker(self.string_var, self.clabel)


class SearchThreshold(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.current_value = tk.IntVar()
        self.current_value.set(PERCENTAGE_THRESHOLD)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{PERCENTAGE_THRESHOLD} %")
        label = tk.Label(self, text="Search threshold")
        label.configure(bg=GUI_DATA.colors.dark_grey, fg=GUI_DATA.colors.white_grey, font=GUI_DATA.fonts.cas8b)
        label.grid(row=0, column=0, sticky="w", padx=0, pady=2)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=GUI_DATA.colors.dark_grey, font=GUI_DATA.fonts.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        tkinter_utils.VarColorPicker(self.string_var, self.clabel, True)
        x, y = tkinter_utils.calculate_btn_size(self, 36)
        self.slider = ttk.Scale(self, from_=0, to=100, orient="horizontal", variable=self.current_value, length=x - 2)
        self.slider.grid(column=2, row=0, sticky="we", padx=4)
        self.slider.bind("<Enter>", self.enter_button)
        self.slider.bind("<Leave>", self.leave_button)
        tkinter_utils.set_default_grid_size(self)

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
        tkinter_utils.VarColorPicker(self.string_var, self.clabel, True)


class RenameBestMatch(tkinter_utils.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        tkinter_utils.ToggleableFrameButton.__init__(self, parent, "Rename best match", "rename_best_match")
