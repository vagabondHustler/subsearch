import dearpygui.dearpygui as dpg
from typing import Dict, Any, Callable, Optional, Tuple
from subsearch.utils import io_toml
from subsearch.globals.constants import FILE_PATHS


NESTED_UI_CONFIG = io_toml.load_toml_data(FILE_PATHS.ui_config)


def get_nested_key(path: str, sep: str = ".", data: dict[str, Any]=NESTED_UI_CONFIG) -> Any:
    keys = path.split(sep)
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
    return data


def get_nested_tooltip_key(path: str, sep: str = ".") -> Any:
    tooltip_data = NESTED_UI_CONFIG.get("tooltip", {})
    return get_nested_key(path, sep, tooltip_data)


class DynamicWidget:
    """
    Represents a dynamically generated Dear PyGui widget with state management.
    """

    def __init__(self, key: str, config: Dict[str, Any], tooltip: Optional[str] = None) -> None:
        """
        Initialize a dynamic widget.

        Args:
            key: Dot-separated configuration key
            config: Widget configuration dictionary
            tooltip: Optional tooltip text
        """
        self.key = key
        self.config = config
        self.tooltip = tooltip
        self.widget_id = None
        self.tooltip_id = None
        self.widget_type = config.get("type", "text")
        self.label = config.get("label", key.split(".")[-1])
        self.default_value = config.get("default", self._get_default_for_type())
        self.mutual_exclusion = config.get("mutual_exclusion", [])
        self.dependent = config.get("dependent", [])

        # Track all widgets for dependency and mutual exclusion handling
        self._all_widgets: Dict[str, "DynamicWidget"] = {}

    def _get_default_for_type(self) -> Any:
        defaults = {"checkbox": False, "text": "", "slider": 0, "input_int": 0, "input_text": ""}
        return defaults.get(self.widget_type, "")

    def _mutual_exclusion_callback(self, sender, app_data, user_data) -> None:
        if self.widget_type != "checkbox" and not app_data:
            return None
        for exclude_key in self.mutual_exclusion:
            if exclude_key not in self._all_widgets:
                return None
            exclude_widget = self._all_widgets[exclude_key]
            if exclude_widget.widget_id and exclude_widget.widget_type == "checkbox":
                dpg.set_value(exclude_widget.widget_id, False)

        self._update_dependents()

        if user_data and callable(user_data):
            user_data(sender, app_data, self.key)

    def _is_all_dependencies_satisfied(self, widget: "DynamicWidget") -> bool:
        for dep_key in widget.dependent:
            if dep_key not in self._all_widgets:
                return False
            if not self._all_widgets[dep_key].get_value():
                return False
        return True

    def _handle_dependent_widget(self, widget: "DynamicWidget") -> None:
        all_satisfied = self._is_all_dependencies_satisfied(widget)
        dpg.configure_item(widget.widget_id, enabled=all_satisfied)
        if not all_satisfied and widget.widget_type == "checkbox":
            dpg.set_value(widget.widget_id, False)

    def _update_dependents(self):
        for widget in self._all_widgets.values():
            if not widget.dependent:
                continue
            if not widget.widget_id:
                continue
            self._handle_dependent_widget(widget)

    def set_widget_registry(self, registry: Dict[str, "DynamicWidget"]) -> None:
        """Set reference to all widgets for mutual exclusion and dependency handling."""
        self._all_widgets = registry

    def create(self, parent: int, callback: Optional[Callable] = None) -> int:
        """
        Create the Dear PyGui widget.

        Args:
            parent: Parent container ID
            callback: Optional user callback function

        Returns:
            Widget ID
        """
        kwargs = {
            "label": self.label,
            "default_value": self.default_value,
            "parent": parent,
            "callback": lambda s, a, u: self._mutual_exclusion_callback(s, a, callback),
        }

        # Create widget based on type
        if self.widget_type == "checkbox":
            self.widget_id = dpg.add_checkbox(**kwargs)
        elif self.widget_type == "text":
            kwargs.pop("callback", None)  # Text widgets don't have callbacks
            self.widget_id = dpg.add_text(**kwargs)
        elif self.widget_type == "slider":
            kwargs["min_value"] = self.config.get("min", 0)
            kwargs["max_value"] = self.config.get("max", 100)
            self.widget_id = dpg.add_slider_int(**kwargs)
        elif self.widget_type == "input_int":
            self.widget_id = dpg.add_input_int(**kwargs)
        elif self.widget_type == "input_text":
            self.widget_id = dpg.add_input_text(**kwargs)
        else:
            raise ValueError(f"Unsupported widget type: {self.widget_type}")

        # Add tooltip if exists
        if self.tooltip and self.widget_type != "text":
            with dpg.tooltip(parent=self.widget_id):
                self.tooltip_id = dpg.add_text(self.tooltip)

        # Set initial enabled state based on dependencies
        if self.dependent:
            dpg.configure_item(self.widget_id, enabled=False)

        return self.widget_id

    def get_value(self) -> Any:
        if self.widget_id is None:
            return self.default_value

        if self.widget_type == "text":
            return dpg.get_value(self.widget_id) if hasattr(dpg, "get_value") else self.default_value

        return dpg.get_value(self.widget_id)

    def set_value(self, value: Any):
        if self.widget_id:
            dpg.set_value(self.widget_id, value)


class DynamicWidgetBuilder:
    """
    Builder class for creating multiple dynamic widgets from TOML configuration.
    """

    def __init__(self):
        self.widgets: Dict[str, DynamicWidget] = {}

    def build_dynamic_widgets(
        self, *keys: str, parent: Optional[int] = None, callback: Optional[Callable] = None
    ) -> Dict[str, DynamicWidget]:
        """
        Build multiple dynamic widgets from configuration keys.

        Args:
            *keys: Variable number of dot-separated configuration keys
            parent: Optional parent container ID
            callback: Optional callback function for all widgets

        Returns:
            Dictionary mapping keys to DynamicWidget objects
        """
        # Create all widget objects first
        for key in keys:
            config = get_nested_key(key)
            tooltip = get_nested_tooltip_key(key)
            widget = DynamicWidget(key, config, tooltip)
            self.widgets[key] = widget

        # Set widget registry for cross-widget communication
        for widget in self.widgets.values():
            widget.set_widget_registry(self.widgets)

        # Create widgets in Dear PyGui
        if parent is not None:
            for widget in self.widgets.values():
                widget.create(parent, callback)

            # Initial dependency update
            for widget in self.widgets.values():
                widget._update_dependents()

        return self.widgets

    def get_values(self) -> Dict[str, Any]:
        return {key: widget.get_value() for key, widget in self.widgets.items()}

    def get_widget(self, key: str) -> Optional[DynamicWidget]:
        return self.widgets.get(key)


def build_dynamic_widgets(
    *keys: str, parent: Optional[int] = None, callback: Optional[Callable] = None
) -> Tuple[Dict[str, DynamicWidget], DynamicWidgetBuilder]:
    """
    Convenience function to build dynamic widgets.

    Args:
        *keys: Variable number of dot-separated configuration keys
        parent: Optional parent container ID
        callback: Optional callback function for all widgets

    Returns:
        Tuple of (widgets dictionary, builder instance)
    """
    builder = DynamicWidgetBuilder()
    widgets = builder.build_dynamic_widgets(*keys, parent=parent, callback=callback)
    return widgets, builder


# def _example_usage() -> None:
#     """
#     Complete example demonstrating widget creation with callbacks.
#     """

#     def on_widget_change(sender, app_data, widget_key):
#         """Callback when any widget changes."""
#         print(f"Widget '{widget_key}' changed to: {app_data}")

#     dpg.create_context()


#     with dpg.window(label="Dynamic Widget Example", width=400, height=300, tag="main_window"):
#         dpg.add_text("Dynamic Widgets from TOML Configuration", color=(100, 200, 255))
#         dpg.add_separator()

#         with dpg.group() as widget_container:
#             widgets, builder = build_dynamic_widgets(
#                 "app.context_menu.menu", "app.context_menu.icon", parent=widget_container, callback=on_widget_change
#             )

#         dpg.add_separator()
#         with dpg.group() as widget_container:
#             widgets, builder = build_dynamic_widgets(
#                 "search.subtitle_prefrence.accept_threshold", parent=widget_container, callback=on_widget_change
#             )
#         dpg.add_separator()
        
#         def print_values():
#             values = builder.get_values()
#             print("\nCurrent Widget Values:")
#             for key, value in values.items():
#                 print(f"  {key}: {value}")

#         dpg.add_button(label="Print Current Values", callback=lambda: print_values())

#     dpg.create_viewport(title="Dynamic Widget System", width=450, height=350)
#     dpg.setup_dearpygui()
#     dpg.show_viewport()
#     dpg.set_primary_window("main_window", True)
#     dpg.start_dearpygui()
#     dpg.destroy_context()


# if __name__ == "__main__":
#     _example_usage()
