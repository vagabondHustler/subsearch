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
    """
    Attach an image displayed as a menu button onto the application window.

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


def set_ttk_theme(root):
    initializer_tcl = APP_PATHS.gui_styles / "theme_setter.tcl"
    root.tk.call("source", str(initializer_tcl))
    root.tk.call("set_theme")
