import tkinter as tk
from tkinter import Label, StringVar, ttk

from PIL import Image, ImageTk

from subsearch.data import __version__, app_paths, gui
from subsearch.gui import spritesheet_data
from subsearch.utils import file_manager, io_json, io_winreg

GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080

DEFAULT_LABEL_CONFIG = dict(bg=gui.colors.dark_grey, fg=gui.colors.white_grey, font=gui.fonts.cas8b)
DEFAULT_LABEL_GRID = dict(row=0, column=0, sticky="w", padx=2, pady=2)
DEFAULT_BTN_TOGGLE_GRID = dict(row=0, column=2, pady=2)


def get_sprite(sprite_name):
    spritesheet_path = app_paths.gui_assets / "spritesheet.png"
    spritesheet_image = Image.open(spritesheet_path)
    sprite_x = spritesheet_data[sprite_name][0]
    sprite_y = spritesheet_data[sprite_name][1]
    sprite_width = spritesheet_data[sprite_name][2]
    sprite_height = spritesheet_data[sprite_name][3]
    sprite = spritesheet_image.crop((sprite_x, sprite_y, sprite_x + sprite_width, sprite_y + sprite_height))
    return sprite


def calculate_btn_size(cls, width_=18, height_=2) -> tuple[int, int]:
    """
    Calculate the required size of a button based on its content.

    Args:
        cls: The class from which the method is being called.
        width_ (optional): The initial width of the button before calculation. Defaults to 18.
        height_ (optional): The initial height of the button before calculation. Defaults to 2.

    Returns:
        A tuple of integer values representing the calculated width and height of the button
    """

    generic_btn = tk.Button(cls, width=width_, height=height_)
    x, y = generic_btn.winfo_reqwidth(), generic_btn.winfo_reqheight()
    return x, y


def calculate_checkbtn_size(cls, width_=16) -> int:
    """
    Calculates the required width of a ttk Checkbutton widget in pixels.

    Args:
        cls (class): The parent class where the Checkbutton will be placed.
        width_ (int, optional): The desired width of the ttk check button. Defaults to 16.

    Returns:
        int: The required width in pixels of a ttk Checkbutton based on its current settings.
    """

    generic_checkbtn = ttk.Checkbutton(cls, width=width_)
    return generic_checkbtn.winfo_reqwidth()


def set_default_grid_size(cls, width_=18) -> None:
    """
    Set the default grid size for a tkinter GUI window.

    Args:
        cls (object): The class object.
        width_ (int, optional): The default width. Defaults to 18.

    Returns:
        None
    """
    btn_size = tk.Button(cls, width=width_, height=2)
    x, _y = btn_size.winfo_reqwidth(), btn_size.winfo_reqheight()
    col_count, row_count = cls.grid_size()
    for col in range(col_count):
        cls.grid_columnconfigure(col, minsize=x)

    for row in range(row_count):
        cls.grid_rowconfigure(row, minsize=0)


def asset_tab(cls, img, type, x=27, y=27) -> None:
    """
    Attach an image displayed as a tab onto the application window.

    Args:
        cls (class): The class representing the application.
        img (str): The name of the image file.
        type (str): The type of the image file.
        x (int, optional): The width of the image in pixels. Defaults to 27.
        y (int, optional): The height of the image in pixels. Defaults to 27.
    """
    path = get_sprite(f"{img}_{type}")
    png = ImageTk.PhotoImage(path)
    update_asset(cls, png, x, y)


def update_asset(cls, img, x, y) -> None:
    """
    Updates an asset in a tkinter canvas with the provided image.

    Args:
        cls: The canvas instance that houses the current asset.
        img: The image asset to replace the current asset within the canvas.
        x: The X coordinate for positioning of the new asset.
        y: The Y coordinate for positioning of the new asset.

    Returns:
        None
    """

    cls.delete("all")
    cls.create_image(x, y, image=img)
    cls.photoimage = img


def set_custom_btn_styles() -> None:
    """
    Sets custom button styles

    Args:
        None

    Returns:
        None
    """

    custom_style = ttk.Style()
    custom_style.configure("True.TButton", foreground=gui.colors.green)
    custom_style.configure("False.TButton", foreground=gui.colors.red)


class WindowPosition(tk.Frame):
    """
    A class that creates and manages the positioning of a tkinter frame.

    Args:
        parent: The parent widget.

    Attributes:
        None

    Methods:
        set(w=int, h=int, ws_value_offset=int, hs_value_offset=int, other=bool): Sets the window dimension
            in width and height. It also sets offsets by which to move the window horizontally (ws_value_offset)
            and vertically (hs_value_offset). If other=True, it allows changing other dimensions not typically
            touched (eg. height of frame/window title bar)

    Returns:
       None
    """

    def __init__(self, parent) -> None:
        """
        Constructor Method for WindowPosition Class

        Args:
            parent: The parent widget.
        """
        tk.Frame.__init__(self, parent)

    def set(
        self,
        w=gui.size.root_width,
        h=gui.size.root_height,
        ws_value_offset=0,
        hs_value_offset=0,
        other: bool = False,
    ):
        """
        Set the size of the current window/Frame

        Args:
             w: An optional integer for setting the width of the window/frame
             h: An optional integer for setting the height of the window/frame
             ws_value_offset: An optional integer for setting the horizontal offset of the window/frame
             hs_value_offset: An optional integer for setting the vertical offset of the window/frame
             other: An optional bool variable to allow changing other dimensions not typically touched
                    eg. height of frame/window title bar

        Returns:
              None
        """
        ws = self.winfo_screenwidth() + ws_value_offset
        hs = self.winfo_screenheight() + hs_value_offset
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        if other:
            return w, h, x, y
        return value


class VarColorPicker:
    """
    A class that initializes a color picker for given string variables.

    Args:
        string_var: A tkinter StringVar object to represent value of the color.
        clabel: A tkinter Label object to represent the color label.
        is_pct: A boolean variable initialized to False indicating if configured level in percentage.

    Attributes:
        string_var: A tkinter StringVar object representing value of the color.
        clabel: A tkinter Label object representing the color label.
        is_pct: A boolean variable to determine percentage threshold.

    Methods:
        pick(): Method to determine and update the color of clabel based on the string_var value.
    """

    def __init__(self, string_var: StringVar, clabel: Label, is_pct: bool = False):
        self.string_var = string_var
        self.clabel = clabel
        self.is_pct = is_pct
        self.pick()

    def pick(self) -> None:
        if self.string_var.get() == "True":
            self.clabel.configure(fg=gui.colors.green)
        elif self.string_var.get() == "False":
            self.clabel.configure(fg=gui.colors.red)
        elif self.string_var.get() == "Both":
            self.clabel.configure(fg=gui.colors.blue)
        elif self.string_var.get().startswith("Only"):
            self.clabel.configure(fg=gui.colors.green)

        if self.is_pct:
            _pct = io_json.get_json_key("percentage_threshold")
            if _pct in range(75, 101):
                self.clabel.configure(fg=gui.colors.green)
            elif _pct in range(50, 75):
                self.clabel.configure(fg=gui.colors.green_brown)
            elif _pct in range(25, 50):
                self.clabel.configure(fg=gui.colors.red_brown)
            elif _pct in range(0, 25):
                self.clabel.configure(fg=gui.colors.red)


class ToolTip(tk.Toplevel):
    """
    A toplevel widget that displays a message when the user hovers over a specified widget

    Args:
        parent (tkinter.Tk): The parent widget
        _widget (tkinter.Widget): The widget to attach the tooltip to
        *_text (str): The text to be displayed in the tooltip
        _background (str): The background color of the tooltip

    Methods:
        show(): Creates and displays a toplevel widget containing the text to be displayed in the tooltip
    """

    def __init__(self, parent, _widget, *_text, _background=gui.colors.light_black):
        self.parent = parent
        self.widget = _widget
        self.text = _text
        self.background = _background

    def show(self) -> None:
        tk.Toplevel.__init__(self, self.parent)
        self.configure(background=gui.colors.light_black)
        # remove the standard window titlebar from the tooltip
        self.overrideredirect(True)
        # unpack *args and put each /n on a new line
        lines = "\n".join(self.text)
        frame = tk.Frame(self, background=gui.colors.light_black)
        label = tk.Label(
            frame,
            text=lines,
            background=self.background,
            foreground=gui.colors.white_grey,
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

    def hide(self) -> None:
        self.destroy()


class ToggleableFrameButton(tk.Frame):
    """
    A button that toggles a configuration setting on or off.

    Args:
        parent (tk.Widget): The parent widget.
        setting_label (str): Name of the setting to be displayed.
        config_key (str): Key in the configuration file where the state is stored.
        write_to_reg (bool, optional): Whether to also write the state to registry. Defaults to False.
        show_if_exe (bool, optional): Only show the button if the program is not running from an executable. Defaults to True.
    """

    def __init__(self, parent, setting_label: str, config_key: str, **kwargs) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=gui.colors.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{io_json.get_json_key(config_key)}")
        self.setting_name = setting_label
        self.config_key = config_key
        self.write_to_reg = kwargs.get("write_to_reg", False)
        self.show_if_exe = kwargs.get("write_to_reg", True)
        self.tip_text = kwargs.get("tip_text", None)
        self.tip_present = False
        if self.show_if_exe is False and file_manager.running_from_exe():
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
        """
        Function called when the mouse enters the button area.

        Args:
            event: The tkinter event object.
        """
        btn = event.widget
        if btn["text"] == "True":
            btn.bind("<ButtonRelease-1>", self.button_set_false)
        if btn["text"] == "False":
            btn.bind("<ButtonRelease-1>", self.button_set_true)
        if self.tip_text is not None and self.tip_present is False:
            self.tip = ToolTip(btn, btn, self.tip_text)
            self.tip.show()
            self.tip_present = True

    def leave_button(self, event) -> None:
        """
        Function called when the mouse leaves the button area.

        Args:
            event: The tkinter event object.
        """
        btn = event.widget
        if self.tip_present:
            self.tip.hide()
            self.tip_present = False

    def button_set_true(self, event) -> None:
        """
        Function called when the button is set to True.

        Args:
            event: The tkinter event object.
        """
        btn = event.widget
        self.string_var.set(f"True")
        btn["style"] = f"{self.string_var.get()}.TButton"
        io_json.set_config_key_value(self.config_key, True)
        if self.write_to_reg:
            io_winreg.add_context_menu()
            io_winreg.write_all_valuex()
        self.enter_button(event)

    def button_set_false(self, event) -> None:
        """
        Function called when the button is set to False.

        Args:
            event: The tkinter event object.
        """
        btn = event.widget
        self.string_var.set(f"False")
        btn["style"] = f"{self.string_var.get()}.TButton"
        io_json.set_config_key_value(self.config_key, False)
        if self.write_to_reg:
            io_winreg.remove_context_menu()
        self.enter_button(event)


def set_ttk_theme(root):
    initializer_tcl = app_paths.gui_app_theme / "ttk_theme_initializer.tcl"
    root.tk.call("source", str(initializer_tcl))
    root.tk.call("set_theme")


def configure_root(root):
    """
    Initialize the root Tkinter window for the Subsearch application.

    Returns:
        tk.Tk: The initialized Tkinter root window.
    """
    if io_json.get_json_key("context_menu"):
        io_winreg.add_context_menu()
    root.configure(background=gui.colors.dark_grey)
    root.iconbitmap(app_paths.gui_assets / "subsearch.ico")
    root.geometry(WindowPosition.set(root))  # type: ignore
    root.resizable(False, False)
