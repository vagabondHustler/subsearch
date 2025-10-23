from typing import Callable, Dict

import flet as ft

from subsearch.ui.core import Dirty, Registry, Rules, State, Theme
from subsearch.ui.keys import FieldKey, FieldMeta
from subsearch.ui.languages import languages


class WidgetBuilders:
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
        self.field_widgets: Dict[FieldKey, ft.Control] = {}
        self.slider_labels: Dict[FieldKey, ft.Text] = {}
        self.language_search: Dict[FieldKey, str] = {}
        self.language_groups: Dict[FieldKey, ft.RadioGroup] = {}
        self.language_boxes: Dict[FieldKey, ft.TextField] = {}

    def build(
        self,
        meta: FieldMeta,
        fk: FieldKey,
        state: State,
        on_change: Callable,
        disabled: bool,
    ) -> ft.Control:
        builders = {
            ft.Icons.CHECK_BOX: self.build_bool,
            ft.Icons.NUMBERS: self.build_int,
            ft.Icons.TUNE: self.build_slider,
            ft.Icons.TEXT_FIELDS: self.build_text,
            ft.Icons.ARROW_DROP_DOWN: self.build_select,
            ft.Icons.RADIO_BUTTON_CHECKED: self._build_radio,
            ft.Icons.LANGUAGE: self.build_language,
        }
        
        widget_map = {
            "BOOL": ft.Icons.CHECK_BOX,
            "INT": ft.Icons.NUMBERS,
            "SLIDER": ft.Icons.TUNE,
            "TEXT": ft.Icons.TEXT_FIELDS,
            "SELECT": ft.Icons.ARROW_DROP_DOWN,
            "RADIO_PICKER": ft.Icons.RADIO_BUTTON_CHECKED,
            "RADIO_MOVE": ft.Icons.RADIO_BUTTON_CHECKED,
            "LANGUAGE": ft.Icons.LANGUAGE,
        }
        
        icon = widget_map.get(meta.widget.name)
        builder = builders.get(icon) if icon else None
        
        if builder:
            return builder(meta, fk, state, on_change, disabled)
        return ft.Container()

    def build_bool(
        self, meta: FieldMeta, fk: FieldKey, state: State, on_change: Callable, disabled: bool
    ) -> ft.Control:
        c = ft.Checkbox(
            label=meta.label,
            value=bool(state.get(fk)),
            tooltip=meta.tip or "",
            on_change=lambda e: on_change(fk, bool(e.control.value)),
            disabled=disabled,
            active_color=self.theme.accent_color,
        )
        self.field_widgets[fk] = c
        return c

    def build_int(
        self, meta: FieldMeta, fk: FieldKey, state: State, on_change: Callable, disabled: bool
    ) -> ft.Control:
        t = ft.TextField(
            label=meta.label,
            value=str(state.get(fk)),
            width=self.theme.input_width - 56,
            height=self.theme.height,
            tooltip=meta.tip or "",
            content_padding=ft.padding.only(8, 0, 8, 0),
            on_change=lambda e: self._handle_int_change(e, fk, on_change),
            keyboard_type=ft.KeyboardType.NUMBER,
            disabled=disabled,
        )
        self.field_widgets[fk] = t

        return ft.Row(
            [t, self._build_int_buttons(t, fk, on_change, disabled)],
            spacing=self.theme.gap,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def build_slider(
        self, meta: FieldMeta, fk: FieldKey, state: State, on_change: Callable, disabled: bool
    ) -> ft.Control:
        label = ft.Text(str(int(state.get(fk))), size=self.theme.font_size_subtitle, color=self.theme.text_muted)
        self.slider_labels[fk] = label

        slider = ft.Slider(
            min=0,
            max=100,
            value=int(state.get(fk)),
            divisions=100,
            on_change=lambda e: self._handle_slider_change(e, fk, on_change),
            expand=True,
            disabled=disabled,
        )
        self.field_widgets[fk] = slider

        header = ft.Row(
            [
                ft.Text(meta.label, size=self.theme.font_size_text, color=self.theme.text_color),
                ft.Container(expand=True),
                label,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        return ft.Column([header, slider], spacing=6)

    def build_text(
        self, meta: FieldMeta, fk: FieldKey, state: State, on_change: Callable, disabled: bool
    ) -> ft.Control:
        t = ft.TextField(
            label=meta.label,
            value=str(state.get(fk)),
            width=self.theme.input_width,
            height=self.theme.height,
            tooltip=meta.tip or "",
            content_padding=ft.padding.only(8, 0, 8, 0),
            on_change=lambda e: on_change(fk, e.control.value),
            disabled=disabled,
        )
        self.field_widgets[fk] = t
        return t

    def build_select(
        self, meta: FieldMeta, fk: FieldKey, state: State, on_change: Callable, disabled: bool
    ) -> ft.Control:
        d = ft.Dropdown(
            label=meta.label,
            value=str(state.get(fk)),
            options=[ft.dropdown.Option("relative"), ft.dropdown.Option("absolute")],
            width=self.theme.input_width,
            tooltip=meta.tip or "",
            on_change=lambda e: on_change(fk, e.control.value),
            disabled=disabled,
        )
        self.field_widgets[fk] = d
        return d

    def build_language(
        self, meta: FieldMeta, fk: FieldKey, state: State, on_change: Callable, disabled: bool
    ) -> ft.Control:
        search_box = self._build_search_box(fk, state, on_change, disabled)
        group = self._build_radio_group(fk, state, on_change, disabled)

        self.language_groups[fk] = group
        self.language_boxes[fk] = search_box
        self.language_search[fk] = ""

        return ft.Column(
            [search_box, self._build_container(group)],
            spacing=8,
            expand=True,
        )

    def rebuild_language_list(self, fk: FieldKey, state: State, on_change: Callable) -> None:
        group = self.language_groups.get(fk)
        if not group:
            return

        disabled = self.rules.disabled_langs(state)
        group.content = self._build_language_list(fk, disabled)

        if hasattr(group, "page") and group.page:
            group.update()

    def update_widget(self, key: FieldKey, value) -> None:
        widget = self.field_widgets.get(key)
        if widget and hasattr(widget, "value"):
            widget.value = value
            self._safe_update(widget)

    def update_slider_label(self, key: FieldKey, value: int) -> None:
        label = self.slider_labels.get(key)
        if label:
            label.value = str(value)
            self._safe_update(label)

    def _build_radio(
        self, meta: FieldMeta, fk: FieldKey, state: State, on_change: Callable, disabled: bool
    ) -> ft.Control:
        if meta.widget.name == "RADIO_PICKER":
            return self._build_radio_group_widget(
                fk,
                state,
                disabled,
                "Picker Behavior",
                FieldKey.OPEN_ON_NO_MATCHES,
                FieldKey.ALWAYS_OPEN,
                self.registry.fields[FieldKey.OPEN_ON_NO_MATCHES].label,
                self.registry.fields[FieldKey.ALWAYS_OPEN].label,
            )
        else:
            return self._build_radio_group_widget(
                fk,
                state,
                disabled,
                "Move Strategy",
                FieldKey.MOVE_BEST,
                FieldKey.MOVE_ALL,
                self.registry.fields[FieldKey.MOVE_BEST].label,
                self.registry.fields[FieldKey.MOVE_ALL].label,
            )

    def _build_radio_group_widget(
        self,
        fk: FieldKey,
        state: State,
        disabled: bool,
        title: str,
        a: FieldKey,
        b: FieldKey,
        la: str,
        lb: str,
    ) -> ft.Control:
        selected = a if state.get(a) else b

        group = ft.RadioGroup(
            value=selected.name,
            on_change=lambda e: self._handle_radio_change(e, state, a, b),
            content=ft.Row([ft.Radio(value=a.name, label=la), ft.Radio(value=b.name, label=lb)]),
            disabled=disabled,
        )
        self.field_widgets[fk] = group

        return ft.Column(
            [ft.Text(title, size=self.theme.font_size_text, color=self.theme.text_color), group], spacing=6
        )

    def _build_search_box(
        self, fk: FieldKey, state: State, on_change: Callable, disabled: bool
    ) -> ft.TextField:
        return ft.TextField(
            label="Search language",
            height=self.theme.height,
            prefix_icon=ft.Icons.SEARCH,
            value="",
            on_change=lambda e: self._handle_search_change(fk, e.control.value, state, on_change),
            on_submit=lambda e: self._handle_search_submit(fk, state, on_change),
            border_color=self.theme.border_color,
            disabled=disabled,
            expand=True,
        )

    def _build_radio_group(
        self, fk: FieldKey, state: State, on_change: Callable, disabled: bool
    ) -> ft.RadioGroup:
        disabled_langs = self.rules.disabled_langs(state)
        return ft.RadioGroup(
            value=str(state.get(fk)),
            content=self._build_language_list(fk, disabled_langs),
            disabled=disabled,
            on_change=lambda e: on_change(fk, e.control.value),
        )

    def _build_container(self, group: ft.RadioGroup) -> ft.Container:
        return ft.Container(
            content=group,
            bgcolor=self.theme.background_elevated,
            border=ft.border.all(1, self.theme.border_color),
            border_radius=self.theme.border_radius,
            height=320,
            padding=8,
            expand=False,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

    def _build_language_list(self, fk: FieldKey, disabled: set[str]) -> ft.Control:
        search = self.language_search.get(fk, "")
        tiles = self._build_language_tiles(search)

        if not tiles:
            return ft.Column(
                [ft.Text("No matches", color=self.theme.text_muted, size=self.theme.font_size_subtitle)], tight=True
            )

        grid = ft.ResponsiveRow(
            tiles, spacing=self.theme.gap, run_spacing=self.theme.gap, alignment=ft.MainAxisAlignment.START
        )
        return ft.Column([grid], spacing=6, expand=True, scroll=ft.ScrollMode.ALWAYS)

    def _build_language_tiles(self, search: str) -> list[ft.Control]:
        tiles = []
        for code, lang in sorted(languages.items(), key=lambda it: it[1].name.lower()):
            if search and search.lower() not in f"{lang.name} {code}".lower():
                continue

            r = ft.Radio(
                value=code,
                label=lang.name,
                label_style=ft.TextStyle(size=self.theme.font_size_text, color=self.theme.text_color),
            )
            tiles.append(
                ft.Container(
                    content=r,
                    alignment=ft.alignment.center_left,
                    padding=ft.padding.only(left=8, right=8, top=6, bottom=6),
                    col={"xs": 12, "sm": 6, "md": 4, "lg": 3, "xl": 3},
                    height=36,
                )
            )
        return tiles

    def _build_int_buttons(
        self, textfield: ft.TextField, fk: FieldKey, on_change: Callable, disabled: bool
    ) -> ft.Row:
        return ft.Row(
            [
                self._build_int_button(
                    ft.Icons.REMOVE, "Decrease", lambda: self._dec_int(textfield, fk, on_change), disabled
                ),
                self._build_int_button(
                    ft.Icons.ADD, "Increase", lambda: self._inc_int(textfield, fk, on_change), disabled
                ),
            ],
            spacing=self.theme.gap_small,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_int_button(self, icon: str, tooltip: str, on_click: Callable, disabled: bool) -> ft.IconButton:
        return ft.IconButton(
            icon=icon,
            icon_size=self.theme.icon_size_small,
            tooltip=tooltip,
            on_click=lambda e: on_click(),
            disabled=disabled,
            width=self.theme.button_square,
            height=self.theme.button_square,
        )

    def _handle_int_change(self, e: ft.ControlEvent, fk: FieldKey, on_change: Callable) -> None:
        on_change(fk, self._to_int(e.control.value))

    def _handle_slider_change(self, e: ft.ControlEvent, fk: FieldKey, on_change: Callable) -> None:
        v = int(e.control.value)
        self.update_slider_label(fk, v)
        on_change(fk, v)

    def _handle_radio_change(self, e: ft.ControlEvent, state: State, a: FieldKey, b: FieldKey) -> None:
        if e.control.value == a.name:
            state.set(a, True)
            state.set(b, False)
        else:
            state.set(a, False)
            state.set(b, True)

        self.dirty.mark(a, state.get(a))
        self.dirty.mark(b, state.get(b))
        self.update_save_bar()

    def _handle_search_change(self, fk: FieldKey, value: str, state: State, on_change: Callable) -> None:
        self.language_search[fk] = value
        self.rebuild_language_list(fk, state, on_change)

    def _handle_search_submit(self, fk: FieldKey, state: State, on_change: Callable) -> None:
        disabled = self.rules.disabled_langs(state)
        search = self.language_search.get(fk, "").lower()
        best = self._find_best_match(search, disabled)

        if best:
            group = self.language_groups.get(fk)
            if group:
                group.value = best
                on_change(FieldKey.CURRENT_LANGUAGE, best)
                if hasattr(group, "page") and group.page:
                    group.update()

    def _find_best_match(self, search: str, disabled: set[str]) -> str | None:
        for code, lang in sorted(languages.items(), key=lambda it: it[1].name.lower()):
            if search and search not in f"{lang.name} {code}".lower():
                continue
            if code in disabled:
                continue
            return code
        return None

    def _inc_int(self, textfield: ft.TextField, fk: FieldKey, on_change: Callable) -> None:
        cur = self._to_int(textfield.value)
        nv = cur + 1
        textfield.value = str(nv)
        on_change(fk, nv)
        textfield.update()

    def _dec_int(self, textfield: ft.TextField, fk: FieldKey, on_change: Callable) -> None:
        cur = self._to_int(textfield.value)
        nv = max(0, cur - 1)
        textfield.value = str(nv)
        on_change(fk, nv)
        textfield.update()

    def _to_int(self, string_value: str) -> int:
        try:
            return int(str(string_value).strip())
        except Exception:
            return 0

    def _safe_update(self, control: ft.Control) -> None:
        if hasattr(control, "page") and control.page:
            control.update()