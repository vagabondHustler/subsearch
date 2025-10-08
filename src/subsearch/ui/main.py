from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
from itertools import zip_longest
from pathlib import Path
from typing import Any, Callable

import dearpygui.dearpygui as dpg

from subsearch.globals.constants import APP_PATHS, FILE_PATHS
from subsearch.ui.theme import COLOR_MAP, COLOR_NAME, STYLE_MAP
from subsearch.ui import dynamic_ui
from subsearch.utils import io_toml


def make_dynamic_strenum(name: str, members: list[str]) -> StrEnum:
    return StrEnum(name, {m.upper(): m for m in members})


@dataclass
class ScreenConfig:
    tag: str
    label: str


SCREENS: dict[str, ScreenConfig] = {
    "subsearch": ScreenConfig(tag="subsearch", label="Subsearch"),
    "subtitle_language": ScreenConfig(tag="subtitle_language", label="Subtitle Language"),
    "subtitle_preferences": ScreenConfig(tag="subtitle_preferences", label="Subtitle Preferences"),
    "download_manager": ScreenConfig(tag="download_manager", label="Download Manager"),
    "about": ScreenConfig(tag="about", label="About"),
}


class Theme(StrEnum):
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ExampleExlusiveEnum(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class AppState:

    current_screen: str = SCREENS["subsearch"].tag
    selected_difficulty: ExampleExlusiveEnum = ExampleExlusiveEnum.MEDIUM
    language_search: str = ""
    selected_theme: Theme = Theme.LIGHT


LANGUAGES = io_toml.load_toml_data(FILE_PATHS.language_data)


class ThemeBuilder:
    @staticmethod
    def create_global_theme() -> int:
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                for style_attr, rgba in STYLE_MAP.items():
                    dpg.add_theme_style(style_attr, *rgba)

                for color_attr, rgba in COLOR_MAP.items():
                    dpg.add_theme_color(color_attr, rgba)
        return theme

    @staticmethod
    def create_content_bar_theme() -> int:
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLOR_NAME["crust"])
        return theme

    @staticmethod
    def create_menu_theme() -> int:
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLOR_NAME["mantle"])
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 1, 0)
        return theme

    @staticmethod
    def create_content_theme() -> int:
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLOR_NAME["base"])
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 4, 4)
        return theme

    @staticmethod
    def create_tooltip_theme() -> int:
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4)
        return theme


@contextmanager
def padded_child_window(tag: str, show: bool = True, border: bool = False, spacer_width: int = 10):
    with dpg.child_window(tag=tag, show=show, border=border):
        dpg.add_spacer(width=spacer_width)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=spacer_width)
            with dpg.group():
                yield


@contextmanager
def menu_group(width: int = 200, height: int = -1, horizontal: bool = True):
    with dpg.group(horizontal=horizontal) as grp:
        with dpg.child_window(width=width, height=height):
            yield grp


@contextmanager
def add_tooltip(cls, applies_to: str, text: str):
    with dpg.tooltip(applies_to):
        dpg.bind_item_theme(dpg.last_item(), cls.themes["tooltip"])
        dpg.add_text(f" {text} ")


class ScreenManager:
    def __init__(self, state: AppState) -> None:
        self.state = state

    def switch_screen(self, sender, app_data, user_data: str) -> None:
        config = SCREENS[user_data]
        self.state.current_screen = user_data

        for scr_cfg in SCREENS.values():
            dpg.hide_item(scr_cfg.tag)

        dpg.show_item(config.tag)
        dpg.set_value("content_bar", config.label)


class SettingsManager:
    def __init__(self, state: AppState) -> None:
        self.state = state

    def on_theme_select(self, sender, app_data, user_data: str) -> None:
        for theme in Theme:
            dpg.set_value(f"theme_{theme}", theme == user_data)
        self.state.selected_theme = Theme(user_data)

    def on_difficulty_select(self, sender, app_data, user_data: str) -> None:
        for difficulty in ExampleExlusiveEnum:
            dpg.set_value(f"difficulty_{difficulty}", difficulty == user_data)
        self.state.selected_difficulty = ExampleExlusiveEnum(user_data)


class LanguageManager:
    def __init__(self, state: AppState) -> None:
        self.state = state

    def filter_languages(self, sender, app_data: str) -> None:
        self.state.language_search = app_data.lower()

        for key, data in LANGUAGES.items():
            language_name = data["name"]
            tag = f"lang_{key}"

            if self.state.language_search in language_name.lower():
                dpg.show_item(tag)
            else:
                dpg.hide_item(tag)

    def select_language(self, sender, app_data, user_data: str) -> None:
        # user_data is the language key (e.g. "arabic")
        selected_name = LANGUAGES[user_data]["name"]
        self.state.language_search = selected_name

        dpg.set_value("selected_language_text", f"Selected Language: {selected_name}")

        for key in LANGUAGES.keys():
            dpg.set_value(f"lang_{key}", key == user_data)


class UIBuilder:
    def __init__(
        self,
        screen_manager: ScreenManager,
        settings_manager: SettingsManager,
        language_manager: LanguageManager,
        themes: dict[str, int],
    ) -> None:
        self.screen_manager = screen_manager
        self.settings_manager = settings_manager
        self.language_manager = language_manager
        self.themes = themes
        self.current_language: str = io_toml.load_toml_value(FILE_PATHS.config, "subtitle_filters.current_language")

        self.screen_builders: dict[str, Callable] = {
            "subsearch": self.create_subsearch_screen,
            "subtitle_language": self.create_subtitle_language_screen,
            "subtitle_preferences": self.create_search_preferences_screen,
            "download_manager": self.create_download_manager_screen,
            "about": self.create_about_screen,
        }

    def create_menu(self) -> None:
        dpg.bind_item_theme(dpg.last_item(), self.themes["menu"])
        dpg.add_spacer(height=10)

        for key, cfg in SCREENS.items():
            dpg.add_button(
                label=cfg.label,
                callback=self.screen_manager.switch_screen,
                user_data=key,
                width=-1,
                height=30,
            )

    def create_content_bar(self) -> None:
        with dpg.child_window(width=200, height=20, border=False, no_scrollbar=True):
            dpg.bind_item_theme(dpg.last_item(), self.themes["content_bar"])
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=2)
                dpg.add_text("Home", tag="content_bar", color=(170, 178, 204, 255))

    def create_content(self) -> None:
        with dpg.group(horizontal=True):
            self.create_content_bar()

        with dpg.child_window(
            tag="content_area",
            width=-1,
            height=-1,
            border=False,
            no_scrollbar=False,
        ):
            dpg.bind_item_theme(dpg.last_item(), self.themes["content"])

            for key, _ in SCREENS.items():
                builder = self.screen_builders.get(key)
                if builder:
                    builder()

    def build_ui_core(self) -> None:
        with dpg.window(tag="ui_core", label="Subsearch", width=900, height=600):
            with dpg.group(horizontal=True):
                with menu_group():
                    self.create_menu()

                with dpg.group():
                    self.create_content()

            first_screen_key = list(SCREENS.keys())[0]
            for key, cfg in SCREENS.items():
                if key != first_screen_key:
                    dpg.hide_item(cfg.tag)

    def create_subsearch_screen(self) -> None:
        with padded_child_window(tag=SCREENS["subsearch"].tag):
            dpg.add_text("Some dynamic settings:")
            widget_group = dynamic_ui.build_dynamic_widgets(
                "app.core.single_instance",
                "app.context_menu.menu",
                "app.context_menu.icon",
            )
            widget_group["app.core.single_instance"]
            dpg.add_spacer(height=20)
            dpg.add_text("Volume Control:")
            dpg.add_slider_float(label="Master Volume", default_value=75, min_value=0, max_value=100, width=300)
            dpg.add_slider_float(label="Music Volume", default_value=60, min_value=0, max_value=100, width=300)

            dpg.add_spacer(height=20)
            dpg.add_text("Theme Selection (Exclusive):")
            for theme in Theme:
                dpg.add_checkbox(
                    label=f"{theme.title()} Theme",
                    tag=f"theme_{theme}",
                    default_value=(theme == Theme.LIGHT),
                    callback=self.settings_manager.on_theme_select,
                    user_data=theme,
                )

            dpg.add_spacer(height=20)
            for difficulty in ExampleExlusiveEnum:
                dpg.add_checkbox(
                    label=difficulty.title(),
                    tag=f"difficulty_{difficulty}",
                    default_value=(difficulty == ExampleExlusiveEnum.MEDIUM),
                    callback=self.settings_manager.on_difficulty_select,
                    user_data=difficulty,
                )

    def create_subtitle_language_screen(self, columns: int = 3) -> None:
        with padded_child_window(tag=SCREENS["subtitle_language"].tag):
            dpg.add_text("Search for a language:")
            dpg.add_input_text(label="Search", callback=self.language_manager.filter_languages, width=300)

            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=10)

            selected_name = LANGUAGES.get(self.current_language, {}).get("name", "Unknown")
            dpg.add_text(f"Selected Language: {selected_name}", tag="selected_language_text")
            add_tooltip(self, "selected_language_text", "Select a language")

            dpg.add_spacer(height=10)
            self.add_language_selection(columns=columns)

    def create_search_preferences_screen(self) -> None:
        with padded_child_window(tag=SCREENS["subtitle_preferences"].tag):
            dpg.add_text("Providers to use:")
            dpg.add_input_text(label="Search")

    def create_download_manager_screen(self) -> None:
        with padded_child_window(tag=SCREENS["download_manager"].tag):
            dpg.add_text("Manage downloads:")

    def create_about_screen(self) -> None:
        with padded_child_window(tag=SCREENS["about"].tag):
            dpg.add_text("This is the About screen.")

    def _create_language_columns(self, columns: int) -> None:
        for _ in range(columns):
            dpg.add_table_column()

    def _populate_language_table(self, all_languages: list[tuple[str, Any]], columns: int) -> None:
        grouped = [all_languages[i::columns] for i in range(columns)]
        for row_items in zip_longest(*grouped):
            with dpg.table_row():
                for pair in row_items:
                    if pair is None:
                        dpg.add_spacer()
                        continue
                    key, data = pair
                    lang_name = data["name"]
                    dpg.add_checkbox(
                        label=lang_name,
                        tag=f"lang_{key}",
                        default_value=(key == self.current_language),
                        callback=self.language_manager.select_language,
                        user_data=key,
                    )

    def add_language_selection(self, columns: int) -> None:
        all_languages = list(LANGUAGES.items())
        with dpg.child_window(height=-1, border=True):
            with dpg.table(header_row=False):
                self._create_language_columns(columns)
                self._populate_language_table(all_languages, columns)


class Application:
    def __init__(self) -> None:
        self.state = AppState()
        self.screen_manager = ScreenManager(self.state)
        self.settings_manager = SettingsManager(self.state)
        self.language_manager = LanguageManager(self.state)

        dpg.create_context()

        self.themes = {
            "global": ThemeBuilder.create_global_theme(),
            "menu": ThemeBuilder.create_menu_theme(),
            "content": ThemeBuilder.create_content_theme(),
            "content_bar": ThemeBuilder.create_content_bar_theme(),
            "tooltip": ThemeBuilder.create_tooltip_theme(),
        }

        self.setup_font()

        self.ui_builder = UIBuilder(self.screen_manager, self.settings_manager, self.language_manager, self.themes)
        self.ui_builder.build_ui_core()

    def setup_font(self) -> None:
        font_path = Path("C:/Windows/Fonts/seguisb.ttf")
        if font_path.exists():
            with dpg.font_registry():
                self.font = dpg.add_font(str(font_path), 16)
        else:
            self.font = None

    def run(self) -> None:
        app_icon = str(APP_PATHS.gui_assets / "subsearch.ico")
        dpg.create_viewport(title="Subsearch", width=900, height=600, small_icon=app_icon, large_icon=app_icon)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("ui_core", True)

        if self.font:
            dpg.bind_font(self.font)
        dpg.bind_theme(self.themes["global"])

        dpg.start_dearpygui()
        dpg.destroy_context()


def main() -> None:
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
