from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from theme import COLOR_MAP, COLOR_NAME, STYLE_MAP


import dearpygui.dearpygui as dpg

from enum import StrEnum


def make_dynamic_strenum(name: str, members: list[str]) -> type[StrEnum]:
    """Create a StrEnum dynamically at runtime."""
    return StrEnum(name, {m.upper(): m for m in members})


class Screen(StrEnum):
    """Available application screens."""

    HOME = "home"
    SETTINGS = "settings"
    PREFERENCES = "preferences"
    LANGUAGE = "language"


class Theme(StrEnum):
    """Available UI themes."""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class Difficulty(StrEnum):
    """Game difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class AppState:
    """Application state management."""

    current_screen: Screen = Screen.HOME
    selected_theme: Theme = Theme.LIGHT
    selected_difficulty: Difficulty = Difficulty.MEDIUM
    language_search: str = ""


LANGUAGES = [
    "English",
    "Spanish",
    "French",
    "German",
    "Italian",
    "Portuguese",
    "Russian",
    "Japanese",
    "Chinese",
    "Korean",
    "Arabic",
    "Hindi",
    "Swedish",
    "Norwegian",
    "Danish",
    "Finnish",
    "Dutch",
    "Polish",
]

SCREEN_LABELS = {
    Screen.HOME: "Home",
    Screen.SETTINGS: "Settings",
    Screen.PREFERENCES: "Preferences",
    Screen.LANGUAGE: "Language",
}


class ThemeBuilder:
    """Build and manage DearPyGUI themes."""

    @staticmethod
    def create_global_theme() -> int:
        """Create the main application theme."""
        s = "mvStyleVar_"
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                for style_attr, rgba in STYLE_MAP.items():
                    dpg.add_theme_style(style_attr, *rgba)
                
                for color_attr, rgba in COLOR_MAP.items():
                    dpg.add_theme_color(color_attr, rgba)
        return theme

    @staticmethod
    def create_content_area_text_theme() -> int:
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


class ScreenManager:
    """Manage screen navigation and state."""

    def __init__(self, state: AppState):
        self.state = state

    def switch_screen(self, sender, app_data, user_data: Screen) -> None:
        """Switch to a different screen."""
        screen = user_data
        self.state.current_screen = screen

        for scr in Screen:
            dpg.hide_item(f"{scr}_screen")

        dpg.show_item(f"{screen}_screen")
        dpg.set_value("content_area_text", SCREEN_LABELS[screen])


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
        for difficulty in Difficulty:
            dpg.set_value(f"difficulty_{difficulty}", difficulty == user_data)
        self.state.selected_difficulty = Difficulty(user_data)


class LanguageManager:
    """Manage language selection and filtering."""

    def __init__(self, state: AppState):
        self.state = state

    def filter_languages(self, sender, app_data: str) -> None:
        """Filter language list based on search query."""
        self.state.language_search = app_data.lower()
        for lang in LANGUAGES:
            if self.state.language_search in lang.lower():
                dpg.show_item(f"lang_{lang}")
            else:
                dpg.hide_item(f"lang_{lang}")

    def select_language(self, sender, app_data, user_data: str) -> None:
        """Handle language selection."""
        dpg.set_value("selected_language_text", f"Selected Language: {user_data}")
        for lang in LANGUAGES:
            dpg.set_value(f"lang_{lang}", lang == user_data)


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

    def create_content_area_text(self) -> None:
        """Create the content area title."""
        with dpg.child_window(width=200, height=20, border=False, no_scrollbar=True):
            dpg.bind_item_theme(dpg.last_item(), self.themes["content_area_text"])
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=2)
                dpg.add_text("Home", tag="content_area_text", color=(170, 178, 204, 255))

    def create_home_screen(self) -> None:
        """Create the home screen with feature toggles and volume controls."""
        with padded_child_window(tag="home_screen"):
            dpg.add_text("Feature Toggles:")
            dpg.add_checkbox(label="Enable Notifications", default_value=True)
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

    def create_settings_screen(self) -> None:
        """Create the settings screen with theme and display options."""
        with padded_child_window(tag="settings_screen"):
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
            dpg.add_text("Display Settings:")
            dpg.add_slider_int(
                label="Font Size",
                default_value=14,
                min_value=10,
                max_value=24,
                width=300,
            )
            dpg.add_slider_int(
                label="UI Scale",
                default_value=100,
                min_value=75,
                max_value=150,
                width=300,
            )

            dpg.add_spacer(height=20)
            dpg.add_checkbox(label="Fullscreen Mode", default_value=False)
            dpg.add_checkbox(label="Show FPS Counter", default_value=False)

    def create_preferences_screen(self) -> None:
        """Create the preferences screen with difficulty and gameplay options."""
        with padded_child_window(tag="preferences_screen"):
            dpg.add_text("Difficulty Level (Exclusive):")
            for difficulty in Difficulty:
                dpg.add_checkbox(
                    label=difficulty.title(),
                    tag=f"difficulty_{difficulty}",
                    default_value=(difficulty == Difficulty.MEDIUM),
                    callback=self.settings_manager.on_difficulty_select,
                    user_data=difficulty,
                )

            dpg.add_spacer(height=20)
            dpg.add_text("Gameplay Options:")
            dpg.add_checkbox(label="Enable Hints", default_value=True)
            dpg.add_checkbox(label="Skip Tutorials", default_value=False)
            dpg.add_checkbox(label="Inverted Controls", default_value=False)

            dpg.add_spacer(height=20)
            dpg.add_text("Sensitivity:")
            dpg.add_slider_float(
                label="Mouse Sensitivity",
                default_value=50,
                min_value=1,
                max_value=100,
                width=300,
            )
            dpg.add_slider_float(
                label="Scroll Speed",
                default_value=30,
                min_value=5,
                max_value=100,
                width=300,
            )

    def create_language_screen(self) -> None:
        """Create the language selection screen."""
        with padded_child_window(tag="language_screen"):
            dpg.add_text("Search for a language:")
            dpg.add_input_text(label="Search", callback=self.language_manager.filter_languages, width=300)

            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=10)

            dpg.add_text("Selected Language: English", tag="selected_language_text")
            dpg.add_spacer(height=10)

            with dpg.child_window(height=300, border=True):
                for lang in LANGUAGES:
                    dpg.add_checkbox(
                        label=lang,
                        tag=f"lang_{lang}",
                        default_value=(lang == "English"),
                        callback=self.language_manager.select_language,
                        user_data=lang,
                    )

    def create_content(self) -> None:
        """Create the main content area with all screens."""
        with dpg.group(horizontal=True):
            self.create_content_area_text()

        with dpg.child_window(
            tag="content_area",
            width=-1,
            height=-1,
            border=False,
            no_scrollbar=False,
        ):
            dpg.bind_item_theme(dpg.last_item(), self.themes["content"])
            self.create_home_screen()
            self.create_settings_screen()
            self.create_preferences_screen()
            self.create_language_screen()

    def build_main_window(self) -> None:
        """Build the main application window."""
        with dpg.window(tag="main_window", label="Subsearch", width=900, height=600):
            with dpg.group(horizontal=True):
                with menu_group():
                    self.create_menu()

                with dpg.group():
                    self.create_content()
                    # Hide non-home screens initially
                    for screen in Screen:
                        if screen != Screen.HOME:
                            dpg.hide_item(f"{screen}_screen")


class Application:
    """Main application class."""

    def __init__(self):
        self.state = AppState()
        self.screen_manager = ScreenManager(self.state)
        self.settings_manager = SettingsManager(self.state)
        self.language_manager = LanguageManager(self.state)

        dpg.create_context()

        # Create themes
        self.themes = {
            "global": ThemeBuilder.create_global_theme(),
            "content_area_text": ThemeBuilder.create_content_area_text_theme(),
            "menu": ThemeBuilder.create_menu_theme(),
            "content": ThemeBuilder.create_content_theme(),
        }

        # Setup font
        self.setup_font()

        # Build UI
        self.ui_builder = UIBuilder(self.screen_manager, self.settings_manager, self.language_manager, self.themes)
        self.ui_builder.build_main_window()

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
        dpg.create_viewport(title="Subsearch", width=900, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)

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
