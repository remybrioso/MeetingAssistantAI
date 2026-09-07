import numpy as np
import pytest

from engines.audio.audio_level import calculate_audio_level


def test_calculate_audio_level_returns_zero_for_silence_and_empty_input() -> None:
    assert calculate_audio_level(np.zeros((16, 1))) == 0.0
    assert calculate_audio_level(np.array([])) == 0.0


def test_calculate_audio_level_maps_typical_signal_to_visible_range() -> None:
    level = calculate_audio_level(np.full(32, 0.1))

    assert 0.0 < level < 1.0
    assert level == pytest.approx(2 / 3, abs=0.01)


def test_calculate_audio_level_reaches_full_scale_and_clamps_overshoot() -> None:
    assert calculate_audio_level(np.ones(8)) == 1.0
    assert calculate_audio_level(np.full(8, 2.0)) == 1.0
    assert calculate_audio_level(np.full(8, 1e308)) == 1.0


def test_calculate_audio_level_supports_stereo_without_modifying_input() -> None:
    samples = np.array(
        [
            [0.5, -0.5],
            [0.5, -0.5],
        ]
    )
    original = samples.copy()

    level = calculate_audio_level(samples)

    assert 0.0 < level < 1.0
    np.testing.assert_array_equal(samples, original)
