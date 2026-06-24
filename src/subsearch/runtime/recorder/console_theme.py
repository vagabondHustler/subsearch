from dataclasses import dataclass, field
from enum import StrEnum


class Emphasis(StrEnum):
    NORMAL = "normal"
    BOLD = "bold"
    ITALIC = "italic"


@dataclass(frozen=True, slots=True)
class LineStyle:
    """Color and emphasis for one transient line level, compiled to a rich style string."""

    color: str
    emphasis: Emphasis = Emphasis.NORMAL

    def to_rich_style(self) -> str:
        if self.emphasis is Emphasis.NORMAL:
            return self.color
        return f"{self.emphasis} {self.color}"


@dataclass(frozen=True, slots=True)
class ConsoleTheme:
    """Every visual knob for the console spinner display, in one place to tweak.

    Styles are rich style strings (color names, ``bold``/``dim`` modifiers, etc.).
    """

    spinner_name: str = "dots"
    spinner_style: str = "#b4befe"

    transient_indent_spaces: int = 0
    transient_level_styles: dict[str, LineStyle] = field(
        default_factory=lambda: {
            "banner": LineStyle("#a6adc8"),
            "info": LineStyle("#bac2de"),
            "warning": LineStyle("#f9e2af"),
            "error": LineStyle("#f38ba8"),
            "critical": LineStyle("#f38ba8", Emphasis.BOLD),
            "debug": LineStyle("#9399b2"),
        }
    )

    active_title_style: str = "bold #cdd6f4"  # the running phase
    done_title_style: str = "#a6adc8"  # finished phases

    summary_pinned_at_top: bool = True  # False = inline under each phase, True = pinned above all phases

    done_marker: str = "·"
    # the done-bullet color reflects the worst severity captured during the phase
    done_severity_styles: dict[str, str] = field(
        default_factory=lambda: {
            "clean": "#a6e3a1",
            "warning": "#f9e2af",
            "error": "#f38ba8",
            "critical": "bold #f38ba8",
        }
    )

    @property
    def transient_indent(self) -> str:
        return " " * self.transient_indent_spaces
