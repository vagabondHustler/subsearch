# titlebar.py
import flet as ft
from subsearch.ui.core import Theme


class TitleBar:
    def __init__(self, theme: Theme, title: str, page: ft.Page) -> None:
        self.theme = theme
        self.title = title
        self.page = page
        self.root: ft.Container | None = None
        self._build()

    def _build(self) -> None:
        self.root = ft.Container(
            bgcolor=self.theme.background_elevated,
            height=40,
            content=ft.Row(
                [
                    self._build_title_section(),
                    ft.WindowDragArea(content=ft.Container(expand=True), maximizable=True, expand=True),
                    self._build_controls_section(),
                ],
                spacing=self.theme.gap,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _build_title_section(self) -> ft.Row:
        return ft.Row(
            [
                ft.Icon(ft.Icons.SUBTITLES, size=18, color=self.theme.text_muted),
                ft.Text(self.title, size=self.theme.font_size_menu, color=self.theme.text_color),
            ],
            spacing=self.theme.gap,
        )

    def _build_controls_section(self) -> ft.Row:
        return ft.Row(
            [
                self._build_minimize_button(),
                self._build_close_button(),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_minimize_button(self) -> ft.IconButton:
        return ft.IconButton(
            icon=ft.Icons.MINIMIZE,
            icon_size=18,
            tooltip="Minimize",
            on_click=lambda e: self._minimize(),
            style=ft.ButtonStyle(
                padding=0,
                shape=ft.RoundedRectangleBorder(radius=6),
                bgcolor={ft.ControlState.HOVERED: self.theme.background},
                color={ft.ControlState.DEFAULT: self.theme.text_muted},
            ),
            width=36,
            height=28,
        )

    def _build_close_button(self) -> ft.IconButton:
        return ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=18,
            tooltip="Close",
            on_click=lambda e: self.page.window.close(),
            style=ft.ButtonStyle(
                padding=0,
                shape=ft.RoundedRectangleBorder(radius=6),
                bgcolor={
                    ft.ControlState.DEFAULT: self.theme.background_elevated,
                    ft.ControlState.HOVERED: self.theme.danger_color,
                },
                color={
                    ft.ControlState.DEFAULT: self.theme.text_muted,
                    ft.ControlState.HOVERED: self.theme.background,
                },
            ),
            width=36,
            height=28,
        )

    def _minimize(self) -> None:
        self.page.window.minimizable = True
        self.page.window.minimized = True
        self.page.update()
