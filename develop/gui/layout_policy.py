from dataclasses import dataclass


INITIAL_WINDOW_WIDTH_RATIO = 0.90
INITIAL_WINDOW_HEIGHT_RATIO = 0.88
MAX_INITIAL_WINDOW_WIDTH = 1400
MAX_INITIAL_WINDOW_HEIGHT = 900

ACTION_LAYOUT_BREAKPOINT = 1050
ACTION_LAYOUT_NORMAL_COLUMNS = 6
ACTION_LAYOUT_COMPACT_COLUMNS = 3


@dataclass(frozen=True, slots=True)
class WindowGeometry:
    width: int
    height: int
    x: int
    y: int

    def as_tk_geometry(self) -> str:
        return f"{self.width}x{self.height}+{self.x}+{self.y}"


def initial_window_geometry(
    screen_width: int,
    screen_height: int,
) -> WindowGeometry:
    if screen_width <= 0 or screen_height <= 0:
        raise ValueError(
            "screen_width y screen_height deben ser positivos."
        )

    width = min(
        round(screen_width * INITIAL_WINDOW_WIDTH_RATIO),
        MAX_INITIAL_WINDOW_WIDTH,
        screen_width,
    )
    height = min(
        round(screen_height * INITIAL_WINDOW_HEIGHT_RATIO),
        MAX_INITIAL_WINDOW_HEIGHT,
        screen_height,
    )

    return WindowGeometry(
        width=width,
        height=height,
        x=(screen_width - width) // 2,
        y=(screen_height - height) // 2,
    )


def action_column_count(width: int) -> int:
    if width < 0:
        raise ValueError("width no puede ser negativo.")

    if width < ACTION_LAYOUT_BREAKPOINT:
        return ACTION_LAYOUT_COMPACT_COLUMNS

    return ACTION_LAYOUT_NORMAL_COLUMNS
