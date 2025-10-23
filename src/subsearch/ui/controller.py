import json

import flet as ft

from subsearch.ui.components.savebar import SaveBar
from subsearch.ui.components.screen_host import ScreenHost
from subsearch.ui.components.sidebar import Sidebar
from subsearch.ui.components.titlebar import TitleBar
from subsearch.ui.core import Dirty, Registry, Rules, State, Theme, Validator
from subsearch.ui.keys import CardKey, FieldKey, ScreenKey
from subsearch.ui.layouts import UIFactory


class AppController:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.theme = Theme()
        self.registry = Registry()
        self.state = State(self.registry)
        self.dirty = Dirty()
        self.rules = Rules()
        self.validator = Validator(self.registry)
        self.ui_factory = UIFactory(self.theme, self.registry, self.rules, self.dirty, self._update_save_bar)
        self.save_bar = SaveBar(self.theme, self.registry)
        self.sidebar = Sidebar(self.theme, self.registry, self._navigate)
        self.screen_host = ScreenHost(self.theme)
        self.title_bar = TitleBar(self.theme, "Subsearch", self.page)
        self.active_screen: ScreenKey = ScreenKey.APP
        self._init_page()

    def _init_page(self) -> None:
        self._setup_window()
        self._restore_state()
        self._build_ui()
        self._wire_events()
        self._navigate(ScreenKey.APP)

    def _setup_window(self) -> None:
        self.page.window.frameless = True
        self.page.window.title_bar_hidden = True
        self.page.window.minimizable = True
        self.theme.style(self.page)

    def _restore_state(self) -> None:
        saved = self.page.client_storage.get("app_state")
        if saved:
            try:
                self.state.load(json.loads(saved))
            except Exception:
                pass
        self.dirty.set_original_values(self.state)

    def _build_ui(self) -> None:
        self.save_bar.set_handler(self._save)
        self._build_screens()
        self._add_root_layout()

    def _build_screens(self) -> None:
        for sk, sc in self.registry.screens.items():
            grid = self._build_screen_grid(sc["cards"])
            self.screen_host.set(sk, grid)

    def _build_screen_grid(self, card_keys: list[CardKey]) -> ft.ResponsiveRow:
        tiles = [self._build_card_tile(ck) for ck in card_keys]
        return ft.ResponsiveRow(tiles, spacing=self.theme.gap, run_spacing=self.theme.gap)

    def _build_card_tile(self, card_key: CardKey) -> ft.Container:
        col_map = {"xs": 12, "md": 12} if card_key == CardKey.SUBTITLE_STYLE else {"xs": 12, "md": 6}
        return ft.Container(content=self.ui_factory.card(card_key, self.state, self._on_change), col=col_map)

    def _add_root_layout(self) -> None:
        root = ft.Column(
            [
                self.title_bar.root,
                ft.Row([self.sidebar.root, self.screen_host.root], expand=True, spacing=0),
                self.save_bar.root,
            ],
            spacing=0,
            expand=True,
        )
        self.page.add(root)

    def _wire_events(self) -> None:
        self.page.window_prevent_close = True
        self.page.on_window_event = lambda e: self._on_window_event(e)

    def _on_window_event(self, event: ft.WindowEvent) -> None:
        if event.data == "close":
            self._persist_state()
            self.page.window_destroy()

    def _navigate(self, screen_key: ScreenKey) -> None:
        self.active_screen = screen_key
        self.sidebar.set_active(screen_key)
        self.screen_host.show(screen_key)

    def _on_change(self, fk: FieldKey, value, skip_rules: bool = False) -> None:
        self.state.set(fk, value)

        if not skip_rules:
            self.rules.apply(self.state)

        self.dirty.mark(fk, value)
        self.ui_factory.widget_builders.update_widget(fk, value)
        self.ui_factory.refresh_disables(self.state)

        if self._is_provider_field(fk):
            self.ui_factory.refresh_language_options(self.state)

        self._update_save_bar()

    def _is_provider_field(self, fk: FieldKey) -> bool:
        return fk in {FieldKey.OS_SITE, FieldKey.OS_HASH, FieldKey.YIFY_SITE, FieldKey.SUBSOURCE_SITE}

    def _update_save_bar(self) -> None:
        is_valid = self.validator.validate_all(self.state)
        self.save_bar.set_enabled(self.dirty.has_changes() and is_valid, self.dirty.changed)

    def _save(self) -> None:
        self.rules.apply(self.state)
        self._persist_state()
        self.dirty.update_originals_after_save(self.state)
        self._update_save_bar()
        self.page.update()

    def _persist_state(self) -> None:
        self.page.client_storage.set("app_state", json.dumps(self.state.snapshot()))


def main(page: ft.Page) -> None:
    AppController(page)
