from typing import Callable

import flet as ft

from subsearch.ui.core import Dirty, Registry, Rules, State, Theme
from subsearch.ui.keys import CardKey, FieldKey, LayoutKind, LayoutSpec
from subsearch.ui.widgets import WidgetBuilders


class LayoutRenderer:
    def __init__(self, theme: Theme, field_builder: Callable) -> None:
        self.theme = theme
        self.field_builder = field_builder

    def render(self, spec: LayoutSpec, state: State, on_change: Callable) -> ft.Control:
        renderers = {
            LayoutKind.STACK: self._render_stack,
            LayoutKind.ROW: self._render_row,
            LayoutKind.GRID: self._render_grid,
            LayoutKind.EXTENSIONS: self._render_extensions,
        }
        renderer = renderers.get(spec.kind)
        return renderer(spec, state, on_change) if renderer else ft.Container()

    def _render_stack(self, spec: LayoutSpec, state: State, on_change: Callable) -> ft.Control:
        fields = [self.field_builder(fk, state, on_change) for fk in spec.fields]
        return ft.Column(fields, spacing=self.theme.gap)

    def _render_row(self, spec: LayoutSpec, state: State, on_change: Callable) -> ft.Control:
        fields = [self.field_builder(fk, state, on_change) for fk in spec.fields]
        return ft.Row(
            fields,
            spacing=spec.spacing or self.theme.gap,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _render_grid(self, spec: LayoutSpec, state: State, on_change: Callable) -> ft.Control:
        col = spec.col or {"xs": 12, "md": 6}
        containers = [ft.Container(content=self.field_builder(fk, state, on_change), col=col) for fk in spec.fields]
        return ft.ResponsiveRow(
            containers,
            spacing=self.theme.gap,
            run_spacing=self.theme.gap,
            alignment=ft.MainAxisAlignment.START,
        )

    def _render_extensions(self, spec: LayoutSpec, state: State, on_change: Callable) -> ft.Control:
        items = []
        if spec.title:
            items.append(self._build_extensions_header(spec.title, state, on_change))

        cols = spec.col or {"xs": 6, "sm": 4, "md": 3, "lg": 3}
        extension_keys = self._get_extension_keys()
        containers = [
            ft.Container(content=self.field_builder(fk, state, on_change), col=cols) for fk in extension_keys
        ]
        items.append(
            ft.ResponsiveRow(
                containers,
                spacing=self.theme.gap,
                run_spacing=self.theme.gap,
                alignment=ft.MainAxisAlignment.START,
            )
        )
        return ft.Column(items, spacing=self.theme.gap)

    def _build_extensions_header(self, title: str, state: State, on_change: Callable) -> ft.Row:
        return ft.Row(
            [
                ft.Text(title, size=self.theme.font_size_text, color=self.theme.text_color),
                ft.Container(expand=True),
                self._build_invert_button(state, on_change),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_invert_button(self, state: State, on_change: Callable) -> ft.Control:
        def invert(e: ft.ControlEvent) -> None:
            for fk in self._get_extension_keys():
                current = state.get(fk)
                on_change(fk, not current)

        return ft.FilledButton(
            "Invert",
            on_click=invert,
            height=self.theme.height,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: self.theme.accent_color,
                    ft.ControlState.HOVERED: self.theme.accent_hover,
                },
                color={ft.ControlState.DEFAULT: self.theme.background},
                shape=ft.RoundedRectangleBorder(radius=self.theme.border_radius),
                side=ft.BorderSide(0, ft.Colors.TRANSPARENT),
                overlay_color=ft.Colors.TRANSPARENT,
            ),
        )

    def _get_extension_keys(self) -> list[FieldKey]:
        registry = Registry()
        return sorted(
            [k for k in registry.fields if str(k).startswith("FieldKey.EXT_")],
            key=lambda k: registry.fields[k].label,
        )


class UIFactory:
    def __init__(
        self,
        theme: Theme,
        registry: Registry,
        rules: Rules,
        dirty: Dirty,
        update_save_bar: Callable[[], None],
    ) -> None:
        self.theme = theme
        self.registry = registry
        self.rules = rules
        self.dirty = dirty
        self.update_save_bar = update_save_bar
        self.widget_builders = WidgetBuilders(theme, registry, rules, dirty, update_save_bar)
        self.layout_renderer = LayoutRenderer(theme, self._build_field)

    def card(self, card_key: CardKey, state: State, on_change: Callable) -> ft.Control:
        meta = self.registry.cards[card_key]
        items = []

        if meta.layout:
            for spec in meta.layout:
                items.append(self.layout_renderer.render(spec, state, on_change))
        else:
            for fk in meta.fields:
                items.append(self._build_field(fk, state, on_change))

        content_col = ft.Column(items, spacing=meta.spacing_override or self.theme.gap, expand=True)

        return ft.Container(
            content=ft.Column(
                [
                    self._build_card_header(meta.title, meta.icon),
                    content_col,
                ],
                spacing=self.theme.gap,
            ),
            padding=self.theme.padding * 3,
            bgcolor=self.theme.card_background,
            border=ft.border.all(1, self.theme.border_color),
            border_radius=self.theme.border_radius,
            expand=True,
        )

    def refresh_disables(self, state: State) -> None:
        disabled_map = self.rules.disabled_map(state)
        for fk, disabled in disabled_map.items():
            widget = self.widget_builders.field_widgets.get(fk)
            if widget and hasattr(widget, "disabled"):
                widget.disabled = disabled
                self._safe_update(widget)

    def refresh_language_options(self, state: State) -> None:
        for fk in [FieldKey.CURRENT_LANGUAGE]:
            if fk in self.widget_builders.language_groups:
                self.widget_builders.rebuild_language_list(fk, state, lambda k, v: None)

    def _build_card_header(self, title: str, icon: str) -> ft.Row:
        return ft.Row(
            [
                ft.Icon(icon, size=self.theme.icon_size, color=self.theme.text_color),
                ft.Text(title, size=self.theme.font_size_text, color=self.theme.text_color, weight=ft.FontWeight.W_500),
            ],
            spacing=self.theme.gap,
            alignment=ft.MainAxisAlignment.START,
        )

    def _build_field(self, fk: FieldKey, state: State, on_change: Callable) -> ft.Control:
        meta = self.registry.fields[fk]
        disabled_map = self.rules.disabled_map(state)
        disabled = disabled_map.get(fk, False)
        return self.widget_builders.build(meta, fk, state, on_change, disabled)

    def _safe_update(self, control: ft.Control) -> None:
        if hasattr(control, "page") and control.page:
            control.update()
