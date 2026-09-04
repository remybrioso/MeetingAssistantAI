import pytest

from gui.layout_policy import (
    ACTION_LAYOUT_BREAKPOINT,
    ACTION_LAYOUT_COMPACT_COLUMNS,
    ACTION_LAYOUT_NORMAL_COLUMNS,
    MAX_INITIAL_WINDOW_HEIGHT,
    MAX_INITIAL_WINDOW_WIDTH,
    action_column_count,
    initial_window_geometry,
)


@pytest.mark.parametrize(
    ("screen_width", "screen_height", "expected"),
    [
        (1366, 768, (1229, 676, 68, 46)),
        (1920, 1080, (1400, 900, 260, 90)),
        (2560, 1440, (1400, 900, 580, 270)),
    ],
)
def test_initial_window_geometry_is_centered_and_within_screen(
    screen_width,
    screen_height,
    expected,
):
    geometry = initial_window_geometry(
        screen_width,
        screen_height,
    )

    assert (
        geometry.width,
        geometry.height,
        geometry.x,
        geometry.y,
    ) == expected
    assert geometry.width > 0
    assert geometry.height > 0
    assert geometry.width <= screen_width
    assert geometry.height <= screen_height
    assert geometry.x == (screen_width - geometry.width) // 2
    assert geometry.y == (screen_height - geometry.height) // 2


def test_large_monitor_respects_initial_window_size_limits():
    geometry = initial_window_geometry(3840, 2160)

    assert geometry.width == MAX_INITIAL_WINDOW_WIDTH
    assert geometry.height == MAX_INITIAL_WINDOW_HEIGHT


@pytest.mark.parametrize(
    ("width", "expected_columns"),
    [
        (1300, ACTION_LAYOUT_NORMAL_COLUMNS),
        (800, ACTION_LAYOUT_COMPACT_COLUMNS),
        (
            ACTION_LAYOUT_BREAKPOINT - 1,
            ACTION_LAYOUT_COMPACT_COLUMNS,
        ),
        (
            ACTION_LAYOUT_BREAKPOINT,
            ACTION_LAYOUT_NORMAL_COLUMNS,
        ),
        (
            ACTION_LAYOUT_BREAKPOINT + 1,
            ACTION_LAYOUT_NORMAL_COLUMNS,
        ),
    ],
)
def test_action_column_count_uses_centralized_breakpoint(
    width,
    expected_columns,
):
    assert action_column_count(width) == expected_columns
    assert action_column_count(width) == expected_columns
