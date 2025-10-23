# sidebar.py
import flet as ft
from subsearch.ui.core import Registry, Theme
from subsearch.ui.keys import ScreenKey


class Sidebar:
    def __init__(self, theme: Theme, registry: Registry, on_pick) -> None:
        self.theme = theme
        self.registry = registry
        self.on_pick = on_pick
        self.root: ft.Container | None = None
        self.items: dict[ScreenKey, ft.Container] = {}
        self.active: ScreenKey | None = None
        self._build()

    def _build(self) -> None:
        rows = [self._build_item(sk, sc) for sk, sc in self.registry.screens.items()]
        self.root = ft.Container(
            width=self.theme.sidebar_width,
            bgcolor=self.theme.background_elevated,
            content=ft.Column(rows, spacing=0, width=self.theme.sidebar_width),
        )

    def _build_item(self, screen_key: ScreenKey, screen_config: dict) -> ft.Container:
        nav_item = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(screen_config["icon"], size=self.theme.icon_size, color=self.theme.text_muted),
                    ft.Text(screen_config["title"], color=self.theme.text_color, size=self.theme.font_size_text),
                ],
                spacing=self.theme.gap,
            ),
            padding=ft.padding.symmetric(self.theme.padding, self.theme.padding),
            on_click=lambda e, k=screen_key: self.on_pick(k),
        )
        self.items[screen_key] = nav_item
        return nav_item

    def set_active(self, screen_key: ScreenKey) -> None:
        self.active = screen_key
        for sk, item in self.items.items():
            is_active = sk == screen_key
            item.bgcolor = self.theme.card_background if is_active else None
            item.border = self._get_border(is_active)
            item.update()

    def _get_border(self, is_active: bool) -> ft.Border | None:
        if not is_active:
            return None
        return ft.border.only(
            left=ft.BorderSide(4, self.theme.accent_color), right=ft.BorderSide(1, self.theme.background)
        )
