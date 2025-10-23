# screen_host.py
import flet as ft
from subsearch.ui.core import Theme
from subsearch.ui.keys import ScreenKey


class ScreenHost:
    def __init__(self, theme: Theme) -> None:
        self.theme = theme
        self.root = ft.Container(expand=True)
        self.views: dict[ScreenKey, ft.Container] = {}

    def set(self, screen_key: ScreenKey, view: ft.Control) -> None:
        container = ft.Container(padding=self.theme.padding, content=view, expand=True)
        self.views[screen_key] = container

    def show(self, screen_key: ScreenKey) -> None:
        self.root.content = self.views[screen_key]
        self.root.update()
