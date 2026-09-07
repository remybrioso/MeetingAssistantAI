import pytest

from gui.components.audio_level_meter import AudioLevelMeter


class FakeProgressBar:

    def __init__(self) -> None:
        self.values = []

    def set(self, value) -> None:
        self.values.append(value)


class FakeMeter:

    def __init__(self) -> None:
        self.values = []

    def set_level(self, value) -> None:
        self.values.append(value)


class FakeLabel:

    def __init__(self) -> None:
        self.values = []

    def configure(self, **kwargs) -> None:
        self.values.append(kwargs)


def build_meter_without_tk() -> AudioLevelMeter:
    meter = AudioLevelMeter.__new__(AudioLevelMeter)
    meter.progress_bar = FakeProgressBar()
    return meter


@pytest.mark.parametrize(
    ("input_level", "expected_level"),
    [
        (-0.2, 0.0),
        (0.35, 0.35),
        (1.4, 1.0),
    ],
)
def test_audio_level_meter_clamps_levels(
    input_level,
    expected_level,
) -> None:
    meter = build_meter_without_tk()

    meter.set_level(input_level)

    assert meter.level == expected_level
    assert meter.progress_bar.values == [expected_level]


def test_audio_level_meter_handles_non_numeric_levels() -> None:
    meter = build_meter_without_tk()

    meter.set_level("not-a-level")

    assert meter.level == 0.0


def test_status_panel_level_callbacks_and_finish_reset_are_independent() -> None:
    from gui.components.status_panel import StatusPanel

    panel = StatusPanel.__new__(StatusPanel)
    panel.microphone_meter = FakeMeter()
    panel.system_audio_meter = FakeMeter()
    panel.rec_label = FakeLabel()

    StatusPanel.on_microphone_audio_level(panel, 0.4)
    StatusPanel.on_system_audio_level(panel, 0.7)
    StatusPanel.on_meeting_finished(panel)

    assert panel.microphone_meter.values == [0.4, 0.0]
    assert panel.system_audio_meter.values == [0.7, 0.0]
    assert panel.rec_label.values == [{"text": ""}]
