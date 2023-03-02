import tkinter as tk
from pathlib import Path
from tkinter import Label, StringVar, ttk

from subsearch.data import GUI_DATA, __paths__, __version__, __video__
from subsearch.utils import file_manager, raw_config, raw_registry

GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080

DEFAULT_LABEL_CONFIG = dict(bg=GUI_DATA.colors.dark_grey, fg=GUI_DATA.colors.white_grey, font=GUI_DATA.fonts.cas8b)
DEFAULT_LABEL_GRID = dict(row=0, column=0, sticky="w", padx=2, pady=2)
DEFAULT_BTN_TOGGLE_GRID = dict(row=0, column=2, pady=2)


def get_tab_png(tab: str):
    return Path(__paths__.tabs) / tab


def calculate_btn_size(cls, _width=18, _height=2):
    generic_btn = tk.Button(cls, width=_width, height=_height)
    x, y = generic_btn.winfo_reqwidth(), generic_btn.winfo_reqheight()
    return x, y


def calculate_checkbtn_size(cls, _width=16):
    generic_checkbtn = ttk.Checkbutton(cls, width=_width)
    return generic_checkbtn.winfo_reqwidth()


def set_default_grid_size(cls, _width=18):
    btn_size = tk.Button(cls, width=_width, height=2)
    x, _y = btn_size.winfo_reqwidth(), btn_size.winfo_reqheight()
    col_count, row_count = cls.grid_size()
    for col in range(col_count):
        cls.grid_columnconfigure(col, minsize=x)

    for row in range(row_count):
        cls.grid_rowconfigure(row, minsize=0)


def asset_tab(cls, img, type, x=27, y=27):
    path = get_tab_png(f"{img}_{type}.png")
    png = tk.PhotoImage(file=path)
    update_asset(cls, png, x, y)


def asset_icon(cls, x=18, y=18):
    path = str(__paths__.icon).replace(".ico", ".png")
    ico = tk.PhotoImage(file=path)
    update_asset(cls, ico, x, y)


def update_asset(cls, img, x, y):
    cls.delete("all")
    cls.create_image(x, y, image=img)
    cls.photoimage = img


def set_custom_btn_styles():
    custom_style = ttk.Style()
    # configure the style option for a specific widget (in this case, a ttk.Button)
    custom_style.configure("True.TButton", foreground=GUI_DATA.colors.green)
    custom_style.configure("False.TButton", foreground=GUI_DATA.colors.red)


class WindowPosition(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

    def set(
        self,
        w=GUI_DATA.size.root_width,
        h=GUI_DATA.size.root_height,
        ws_value_offset=0,
        hs_value_offset=0,
        other: bool = False,
    ):
        ws = self.winfo_screenwidth() + ws_value_offset
        hs = self.winfo_screenheight() + hs_value_offset
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        if other:
            return w, h, x, y
        return value


class VarColorPicker:
    def __init__(self, string_var: StringVar, clabel: Label, is_pct: bool = False):
        self.string_var = string_var
        self.clabel = clabel
        self.is_pct = is_pct
        self.pick()

    def pick(self):  # string boolean
        if self.string_var.get() == "True":
            self.clabel.configure(fg=GUI_DATA.colors.green)
        elif self.string_var.get() == "False":
            self.clabel.configure(fg=GUI_DATA.colors.red)
        elif self.string_var.get() == "Both":
            self.clabel.configure(fg=GUI_DATA.colors.blue)
        elif self.string_var.get().startswith("Only"):
            self.clabel.configure(fg=GUI_DATA.colors.green)

        if self.is_pct:
            _pct = raw_config.get_config_key("percentage_threshold")
            if _pct in range(75, 101):
                self.clabel.configure(fg=GUI_DATA.colors.green)
            elif _pct in range(50, 75):
                self.clabel.configure(fg=GUI_DATA.colors.green_brown)
            elif _pct in range(25, 50):
                self.clabel.configure(fg=GUI_DATA.colors.red_brown)
            elif _pct in range(0, 25):
                self.clabel.configure(fg=GUI_DATA.colors.red)


class ToolTip(tk.Toplevel):
    def __init__(self, parent, _widget, *_text, _background=GUI_DATA.colors.light_black):
        self.parent = parent
        self.widget = _widget
        self.text = _text
        self.background = _background

    def show(self):
        tk.Toplevel.__init__(self, self.parent)
        self.configure(background=GUI_DATA.colors.light_black)
        # remove the standard window titlebar from the tooltip
        self.overrideredirect(True)
        # unpack *args and put each /n on a new line
        lines = "\n".join(self.text)
        frame = tk.Frame(self, background=GUI_DATA.colors.light_black)
        label = tk.Label(
            frame,
            text=lines,
            background=self.background,
            foreground=GUI_DATA.colors.white_grey,
            justify="left",
        )
        # get size of the label to use later for positioning and sizing of the tooltip
        x, y = label.winfo_reqwidth(), label.winfo_reqheight()
        # set the size of the tooltip background to be 1px larger than the label
        frame.configure(width=x + 1, height=y + 1)

        widget_pos = self.widget.winfo_rootx()
        widget_width = self.widget.winfo_reqwidth()
        widget_center = round(widget_width / 2)
        btn_pos_middle = widget_pos + widget_center
        frame_width = frame.winfo_reqwidth()
        frame_center = round(frame_width / 2)
        center_tip_over_mouse = btn_pos_middle - frame_center
        # offset the frame 1px from edge of the tooltip corner
        frame.place(x=1, y=1, anchor="nw")
        label.place(x=0, y=0, anchor="nw")
        root_x = center_tip_over_mouse  # offset the tooltip by extra 4px so it doesn't overlap the widget
        root_y = self.widget.winfo_rooty() - self.widget.winfo_height() - 4
        # set position of the tooltip, size and add 2px around the tooltip for a 1px border
        self.geometry(f"{x+2}x{y+2}+{root_x}+{root_y}")

    def hide(self):
        self.destroy()


class ToggleableFrameButton(tk.Frame):
    """Creates a toggleable button widget.

    The ToggleableFrameButton class inherits from the tk.Frame class and creates a button widget that can be toggled between True and False values.

    The button widget can be customized with a label, a configuration key, and a Boolean value to indicate whether to write the value to the registry.

    Attributes:
    parent (tkinter.Tk): The parent widget of the button.
    setting_label (str): The label text to be displayed next to the button.
    config_key (str): The key in the configuration file that the button corresponds to.
    write_to_reg (bool): Whether to write the button value to the registry.
    show_if_exe (bool): Whether to show the button if the program is running from an executable.

    Methods:
    init(self, parent, setting_label: str, config_key: str, write_to_reg: bool = False, show_if_exe=True) -> None:
    Initializes the ToggleableFrameButton class and sets its attributes.


    enter_button(self, event) -> None:
        Changes the text and style of the button widget when the user hovers over it.

    leave_button(self, event) -> None:
        Does nothing when the user stops hovering over the button widget.

    button_set_true(self, event) -> None:
        Sets the button value to True and updates the configuration file and registry if necessary.

    button_set_false(self, event) -> None:
        Sets the button value to False and updates the configuration file and registry if necessary.

    """

    def __init__(self, parent, setting_label: str, config_key: str, write_to_reg: bool = False, show_if_exe=True) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{raw_config.get_config_key(config_key)}")
        self.setting_name = setting_label
        self.config_key = config_key
        self.write_to_reg = write_to_reg
        self.show_if_exe = show_if_exe
        if show_if_exe is False and file_manager.running_from_exe() is False:
            return None
        label = tk.Label(self, text=self.setting_name)
        label.configure(DEFAULT_LABEL_CONFIG)
        label.grid(DEFAULT_LABEL_GRID)
        btn_toggle = ttk.Button(
            self,
            textvariable=self.string_var,
            width=40,
            style=f"{self.string_var.get()}.TButton",
        )
        btn_toggle.grid(DEFAULT_BTN_TOGGLE_GRID, padx=8)
        btn_toggle.bind("<Enter>", self.enter_button)
        btn_toggle.bind("<Leave>", self.leave_button)
        set_default_grid_size(self)

    def enter_button(self, event) -> None:
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_false)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_true)

    def leave_button(self, event) -> None:
        btn = event.widget

    def button_set_true(self, event) -> None:
        btn = event.widget
        self.string_var.set(f"True")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value(self.config_key, True)
        if self.write_to_reg:
            raw_registry.add_context_menu()
            raw_registry.write_all_valuex()
        self.enter_button(event)

    def button_set_false(self, event) -> None:
        btn = event.widget
        self.string_var.set(f"False")
        btn["style"] = f"{self.string_var.get()}.TButton"
        raw_config.set_config_key_value(self.config_key, False)
        if self.write_to_reg:
            raw_registry.remove_context_menu()
        self.enter_button(event)
