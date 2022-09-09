import tkinter as tk

from subsearch.data import __icon__
from subsearch.gui import tk_data, tk_tools
from subsearch.utils import current_user, raw_config, raw_registry

TKWINDOW = tk_data.Window()
TKCOLOR = tk_data.Color()


def check_state(event):
    if hidden_root.state() == "iconic":
        root.wm_withdraw()
    if hidden_root.state() != "iconic":
        root.deiconify()


def main():
    global root, hidden_root
    if current_user.got_key() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()
    hidden_root = tk.Tk(className=f"subsearch")
    hidden_root.configure(background=TKCOLOR.black)
    hidden_root.iconbitmap(__icon__)
    hidden_root.geometry(tk_tools.WindowPosition.set(hidden_root))
    hidden_root.attributes("-alpha", 0)
    hidden_root.resizable(False, False)
    root = tk.Toplevel(hidden_root)
    root.geometry(tk_tools.WindowPosition.set(root))
    root.overrideredirect(1)
    tk_tools.CustomBorder(root).place(relx=0.5, rely=0.5, anchor="center")
    tk.Frame(root, height=40, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)
    tk_tools.TitleBar(root, hidden_root).place(x=TKWINDOW.width - 2, y=2, bordermode="inside", anchor="ne")
    hidden_root.bind("<FocusOut>", check_state)
    hidden_root.bind("<FocusIn>", check_state)
    return root
