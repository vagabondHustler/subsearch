from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
from itertools import zip_longest
from pathlib import Path
from typing import Any

import dearpygui.dearpygui as dpg

from subsearch.globals.constants import APP_PATHS, FILE_PATHS
from subsearch.ui.theme import COLOR_MAP, COLOR_NAME, STYLE_MAP
from subsearch.utils import io_toml


def make_dynamic_strenum(name: str, members: list[str]) -> StrEnum:
    """Create a StrEnum dynamically at runtime."""
    return StrEnum(name, {m.upper(): m for m in members})


class Screen(StrEnum):
    """Available application screens."""

    SUBSEARCH = "subsearch"
    SUBTITLE_LANGUAGE = "subtitle_language"
    SUBTITLE_PREFRENCES = "subtitle_preferences"
    DOWNLOAD_MANAGER = "download_manager"
    ABOUT = "about"


class Theme(StrEnum):
    """Available UI themes."""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class TestDifficulty(StrEnum):
    """Game difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class AppState:
    """Application state management."""

    current_screen: Screen = Screen.SUBSEARCH
    selected_difficulty: TestDifficulty = TestDifficulty.MEDIUM
    language_search: str = ""
    selected_theme: Theme = Theme.LIGHT

LANGUAGES = io_toml.load_toml_data(FILE_PATHS.language_data)

SCREEN_LABELS = {
    Screen.SUBSEARCH: "Subsearch",
    Screen.SUBTITLE_LANGUAGE: "Subtitle Language",
    Screen.SUBTITLE_PREFRENCES: "Subtitle Preferences",
    Screen.DOWNLOAD_MANAGER: "Download Manager",
    Screen.ABOUT: "About",
}


class ThemeBuilder:
    """Build and manage DearPyGUI themes."""

    @staticmethod
    def create_global_theme() -> int:
        """Create the main application theme."""
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                for style_attr, rgba in STYLE_MAP.items():
                    dpg.add_theme_style(style_attr, *rgba)

                for color_attr, rgba in COLOR_MAP.items():
                    dpg.add_theme_color(color_attr, rgba)
        return theme

    @staticmethod
    def create_content_bar_theme() -> int:
        """Create theme for content area text."""
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLOR_NAME["crust"])
        return theme

    @staticmethod
    def create_menu_theme() -> int:
        """Create theme for the side menu."""
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLOR_NAME["mantle"])
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 1, 0)
        return theme

    @staticmethod
    def create_content_theme() -> int:
        """Create theme for content areas."""
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLOR_NAME["base"])
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 4, 4)
        return theme
    
    @staticmethod
    def create_tooltip_theme() -> int:
        """Create theme for content areas."""
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4)
        return theme


@contextmanager
def padded_child_window(tag: str, show: bool = True, border: bool = False, spacer_width: int = 10):
    """Create a child window with horizontal padding."""
    with dpg.child_window(tag=tag, show=show, border=border):
        dpg.add_spacer(width=spacer_width)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=spacer_width)
            with dpg.group():
                yield


@contextmanager
def menu_group(width: int = 200, height: int = -1, horizontal: bool = True):
    """Create a menu group container."""
    with dpg.group(horizontal=horizontal) as grp:
        with dpg.child_window(width=width, height=height):
            yield grp

@contextmanager
def add_tooltip(cls, applies_to: str, text:str):
    with dpg.tooltip(applies_to):
        dpg.bind_item_theme(dpg.last_item(), cls.themes["tooltip"])
        dpg.add_text(f" {text} ")

class ScreenManager:
    """Manage screen navigation and state."""

    def __init__(self, state: AppState):
        self.state = state

    def switch_screen(self, sender, app_data, user_data: Screen) -> None:
        """Switch to a different screen."""
        screen = user_data
        self.state.current_screen = screen

        for scr in Screen:
            dpg.hide_item(scr)

        dpg.show_item(screen)
        dpg.set_value("content_bar", SCREEN_LABELS[screen])


class SettingsManager:
    """Manage application settings."""

    def __init__(self, state: AppState):
        self.state = state

    def on_theme_select(self, sender, app_data, user_data: str) -> None:
        """Handle theme selection."""
        for theme in Theme:
            dpg.set_value(f"theme_{theme}", theme == user_data)
        self.state.selected_theme = Theme(user_data)

    def on_difficulty_select(self, sender, app_data, user_data: str) -> None:
        """Handle difficulty selection."""
        for difficulty in TestDifficulty:
            dpg.set_value(f"difficulty_{difficulty}", difficulty == user_data)
        self.state.selected_difficulty = TestDifficulty(user_data)


class LanguageManager:
    """Manage language selection and filtering."""

    def __init__(self, state: AppState):
        self.state = state

    def filter_languages(self, sender, app_data: str) -> None:
        """Filter language list based on search query."""
        self.state.language_search = app_data.lower()

        for key, data in LANGUAGES.items():
            language_name = data["name"]
            tag = f"lang_{key}"

            if self.state.language_search in language_name.lower():
                dpg.show_item(tag)
            else:
                dpg.hide_item(tag)

    def select_language(self, sender, app_data, user_data: str) -> None:
        """Handle language selection."""
        # user_data is the language key (e.g. "arabic")
        selected_name = LANGUAGES[user_data]["name"]
        self.state.language_search = selected_name


        dpg.set_value("selected_language_text", f"Selected Language: {selected_name}")

        for key in LANGUAGES.keys():
            dpg.set_value(f"lang_{key}", key == user_data)



class UIBuilder:
    """Build UI components."""
    def __init__(
        self,
        screen_manager: ScreenManager,
        settings_manager: SettingsManager,
        language_manager: LanguageManager,
        themes: dict[str, int],
    ):
        self.screen_manager = screen_manager
        self.settings_manager = settings_manager
        self.language_manager = language_manager
        self.themes = themes

    def create_menu(self) -> None:
        """Create the side navigation menu."""
        dpg.bind_item_theme(dpg.last_item(), self.themes["menu"])
        dpg.add_spacer(height=10)

        for screen in Screen:
            dpg.add_button(
                label=SCREEN_LABELS[screen],
                callback=self.screen_manager.switch_screen,
                user_data=screen,
                width=-1,
                height=30,
            )

    def create_content_bar(self) -> None:
        """Create the content area title."""
        with dpg.child_window(width=200, height=20, border=False, no_scrollbar=True):
            dpg.bind_item_theme(dpg.last_item(), self.themes["content_bar"])
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=2)
                dpg.add_text("Home", tag="content_bar", color=(170, 178, 204, 255))

    def create_subsearch_screen(self) -> None:
        """Create the home screen with feature toggles and volume controls."""
        with padded_child_window(tag="subsearch"):
            dpg.add_text("Feature Toggles:")
            dpg.add_checkbox(label="Enable Notifications", default_value=True, tag='test')
            dpg.add_checkbox(label="Auto-save", default_value=False)
            dpg.add_checkbox(label="Show Tooltips", default_value=True)

            dpg.add_spacer(height=20)
            dpg.add_text("Volume Control:")
            dpg.add_slider_float(
                label="Master Volume",
                default_value=75,
                min_value=0,
                max_value=100,
                width=300,
            )
            dpg.add_slider_float(
                label="Music Volume",
                default_value=60,
                min_value=0,
                max_value=100,
                width=300,
            )
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
            for difficulty in TestDifficulty:
                dpg.add_checkbox(
                    label=difficulty.title(),
                    tag=f"difficulty_{difficulty}",
                    default_value=(difficulty == TestDifficulty.MEDIUM),
                    callback=self.settings_manager.on_difficulty_select,
                    user_data=difficulty,
                )

            dpg.add_spacer(height=20)
            
    def _create_language_columns(self, columns) -> None:
        for _ in range(0, columns):
            dpg.add_table_column()
            
    def _populate_language_table(self, all_languages: dict[str, Any], columns) -> None:
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
                
    def create_subtitle_language_screen(self, columns: int) -> None:
        current_language = io_toml.load_toml_value(FILE_PATHS.config, "subtitle_filters.current_language")
        self.current_language = current_language  # store just the key (e.g. "english")

        with padded_child_window(tag="subtitle_language"):
            dpg.add_text("Search for a language:")
            dpg.add_input_text(label="Search", callback=self.language_manager.filter_languages, width=300)

            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=10)

            selected_name = LANGUAGES.get(current_language, {}).get("name", "Unknown")
            dpg.add_text(f"Selected Language: {selected_name}", tag="selected_language_text")
            add_tooltip(self, "selected_language_text", "hello")
            
            dpg.add_spacer(height=10)
            self.add_language_selection(columns=3)
            




    def create_search_preferences_screen(self) -> None:
        with padded_child_window(tag="subtitle_preferences"):
            dpg.add_text("Providers to use:")
            dpg.add_input_text(label="Search")

    def create_download_manager_screen(self) -> None:
        with padded_child_window(tag="download_manager"):
            dpg.add_text("Manage downloads:")
        ...

    def create_about_screen(self) -> None:
        with padded_child_window(tag="about"):
            dpg.add_text("This is a app:")

    def create_content(self) -> None:
        """Create the main content area with all screens."""
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
            self.create_subsearch_screen()
            self.create_subtitle_language_screen(columns=3)
            self.create_search_preferences_screen()
            self.create_download_manager_screen()
            self.create_about_screen()

    def build_ui_core(self) -> None:
        """Build the main application window."""
        with dpg.window(tag="ui_core", label="Subsearch", width=900, height=600):
            with dpg.group(horizontal=True):
                with menu_group():
                    self.create_menu()

                with dpg.group():
                    self.create_content()
                    for screen in Screen:
                        if screen != Screen.SUBSEARCH:
                            dpg.hide_item(screen)


class Application:
    """Main application class."""

    def __init__(self):
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
            "tooltip": ThemeBuilder.create_tooltip_theme()
        }

        self.setup_font()

        self.ui_builder = UIBuilder(self.screen_manager, self.settings_manager, self.language_manager, self.themes)
        self.ui_builder.build_ui_core()

    def setup_font(self) -> None:
        """Load and setup the application font."""
        font_path = Path("C:/Windows/Fonts/seguisb.ttf")
        if font_path.exists():
            with dpg.font_registry():
                self.font = dpg.add_font(str(font_path), 16)
        else:
            self.font = None

    def run(self) -> None:
        """Run the application."""
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
    """Application entry point."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
