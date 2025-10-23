# savebar.py
import flet as ft
from subsearch.ui.core import Registry, Theme
from subsearch.ui.keys import FieldKey


class SaveBar:
    def __init__(self, theme: Theme, registry: Registry) -> None:
        self.theme = theme
        self.registry = registry
        self.status_text: ft.Text | None = None
        self.changes_text: ft.Text | None = None
        self.save_button: ft.IconButton | None = None
        self.root: ft.Container | None = None
        self._build()

    def _build(self) -> None:
        self.status_text = ft.Text(
            "", size=self.theme.font_size_text, color=self.theme.text_muted, weight=ft.FontWeight.W_500
        )
        self.changes_text = ft.Text("", size=self.theme.font_size_subtitle, color=self.theme.text_muted)
        self.save_button = ft.IconButton(icon=ft.Icons.SAVE, disabled=True)

        self.root = ft.Container(
            padding=self.theme.padding,
            border=ft.border.only(top=ft.BorderSide(1, self.theme.border_color)),
            bgcolor=self.theme.background_elevated,
            content=ft.Row(
                [
                    ft.Container(expand=True),
                    ft.Row(
                        [
                            ft.Column(
                                [self.status_text, self.changes_text],
                                spacing=self.theme.gap_small,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                            self.save_button,
                        ],
                        spacing=self.theme.gap * 2,
                        alignment=ft.MainAxisAlignment.END,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=self.theme.gap,
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def set_handler(self, on_save) -> None:
        self.save_button.on_click = lambda e: on_save()

    def set_enabled(self, is_enabled: bool, changed_fields: set[FieldKey] | None = None) -> None:
        self.save_button.disabled = not is_enabled

        if is_enabled and changed_fields:
            self._set_changed_state(changed_fields)
        else:
            self._set_saved_state()

        self.root.update()

    def _set_changed_state(self, changed_fields: set[FieldKey]) -> None:
        count = len(changed_fields)
        self.status_text.value = f"{count} unsaved change{'s' if count != 1 else ''}"
        self.status_text.color = self.theme.accent_color
        self.changes_text.value = self._format_changed_fields(changed_fields)
        self.save_button.icon_color = self.theme.accent_color

    def _set_saved_state(self) -> None:
        self.status_text.value = "All changes saved"
        self.status_text.color = self.theme.text_muted
        self.changes_text.value = ""
        self.save_button.icon_color = self.theme.text_muted

    def _format_changed_fields(self, changed_fields: set[FieldKey]) -> str:
        names = [self.registry.fields[fk].label for fk in sorted(changed_fields, key=self._field_label)]
        if len(names) <= 5:
            return ", ".join(names)
        return ", ".join(names[:5]) + f" and {len(names) - 5} more"

    def _field_label(self, key: FieldKey) -> str:
        return self.registry.fields[key].label
