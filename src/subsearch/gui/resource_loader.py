from PIL import Image, ImageTk

from subsearch.data.constants import APP_PATHS
from subsearch.gui import sprites


def get_sprite(sprite_name):
    spritesheet_path = APP_PATHS.gui_assets / "spritesheet.png"
    spritesheet_image = Image.open(spritesheet_path)
    sprite_x = sprites[sprite_name][0]
    sprite_y = sprites[sprite_name][1]
    sprite_width = sprites[sprite_name][2]
    sprite_height = sprites[sprite_name][3]
    sprite = spritesheet_image.crop((sprite_x, sprite_y, sprite_x + sprite_width, sprite_y + sprite_height))
    return sprite


def asset_menu_btn(cls, img, type, x=27, y=27) -> None:
    path = get_sprite(f"{img}_{type}")
    png = ImageTk.PhotoImage(path)
    update_asset(cls, png, x, y)


def update_asset(cls, img, x, y) -> None:
    cls.delete("all")
    cls.create_image(x, y, image=img)
    cls.photoimage = img


def set_ttk_theme(root):
    initializer_tcl = APP_PATHS.gui_styles / "theme_setter.tcl"
    root.tk.call("source", str(initializer_tcl))
    root.tk.call("set_theme")
