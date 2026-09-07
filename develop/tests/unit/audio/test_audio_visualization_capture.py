from pathlib import Path

import numpy as np
import pytest

from application.event_bus import EventBus
from engines.audio.microphone_engine import MicrophoneEngine
from engines.audio.recorder import AudioRecorder
from engines.audio.system_audio_engine import SystemAudioEngine
from services.audio_capture_service import AudioCaptureService


class FakeSoundFile:

    instances = []

    def __init__(self, *args, **kwargs) -> None:
        self.writes = []
        self.closed = False
        self.__class__.instances.append(self)

    def write(self, data) -> None:
        self.writes.append(data.copy())

    def close(self) -> None:
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False


class FakeInputStream:

    instances = []

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.started = False
        self.stopped = False
        self.closed = False
        self.__class__.instances.append(self)

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def close(self) -> None:
        self.closed = True


def test_audio_recorder_writes_pcm_and_rate_limits_level_callback(monkeypatch) -> None:
    import engines.audio.recorder as recorder_module

    FakeSoundFile.instances.clear()
    FakeInputStream.instances.clear()
    monkeypatch.setattr(recorder_module.sf, "SoundFile", FakeSoundFile)
    monkeypatch.setattr(recorder_module.sd, "InputStream", FakeInputStream)

    callback_levels = []
    clock_values = iter((0.0, 0.05, 0.11))
    monkeypatch.setattr(
        recorder_module.time,
        "monotonic",
        lambda: next(clock_values),
    )

    recorder = AudioRecorder(
        level_callback=callback_levels.append,
    )
    recorder.start(
        device_id=7,
        filename="mic.wav",
        samplerate=44100,
        channels=1,
    )

    block = np.full((4, 1), 0.5, dtype=np.float32)
    for _ in range(3):
        recorder._callback(block, 4, None, None)

    assert len(FakeInputStream.instances) == 1
    assert len(FakeSoundFile.instances[0].writes) == 3
    assert len(callback_levels) == 2
    assert all(0.0 <= value <= 1.0 for value in callback_levels)

    recorder.stop()
    assert FakeSoundFile.instances[0].closed is True


def test_audio_recorder_visualization_failure_does_not_stop_writing(monkeypatch) -> None:
    import engines.audio.recorder as recorder_module

    FakeSoundFile.instances.clear()
    FakeInputStream.instances.clear()
    monkeypatch.setattr(recorder_module.sf, "SoundFile", FakeSoundFile)
    monkeypatch.setattr(recorder_module.sd, "InputStream", FakeInputStream)

    def failing_callback(level):
        raise RuntimeError("visualization failed")

    recorder = AudioRecorder(level_callback=failing_callback)
    recorder.start(
        device_id=7,
        filename="mic.wav",
    )
    recorder._callback(
        np.ones((4, 1), dtype=np.float32),
        4,
        None,
        None,
    )

    assert len(FakeSoundFile.instances[0].writes) == 1
    recorder.stop()


def test_microphone_engine_forwards_optional_level_callback(
    tmp_path: Path,
) -> None:
    class FakeRecorder:

        def __init__(self) -> None:
            self.kwargs = None

        def start(self, **kwargs) -> None:
            self.kwargs = kwargs

        def stop(self) -> None:
            pass

    callback = lambda level: None
    engine = MicrophoneEngine(level_callback=callback)
    recorder = FakeRecorder()
    engine._recorder = recorder

    engine.start(
        device_id=3,
        filename=str(tmp_path / "audio" / "mic.wav"),
        samplerate=44100,
        channels=1,
    )

    assert recorder.kwargs["level_callback"] is callback


def test_system_audio_engine_writes_each_100ms_block_and_publishes_levels(
    monkeypatch,
    tmp_path: Path,
) -> None:
    import engines.audio.system_audio_engine as system_module

    blocks = [
        np.zeros((4800, 2), dtype=np.float32),
        np.full((4800, 2), 0.5, dtype=np.float32),
    ]
    record_calls = []

    class FakeLoopbackRecorder:

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def record(self, numframes):
            record_calls.append(numframes)
            block = blocks.pop(0)
            if not blocks:
                engine._recording = False
            return block

    class FakeLoopback:

        def recorder(self, samplerate):
            assert samplerate == 48000
            return FakeLoopbackRecorder()

    class FakeSpeaker:
        name = "speakers"

    fake_file = FakeSoundFile()
    monkeypatch.setattr(system_module.sc, "default_speaker", lambda: FakeSpeaker())
    monkeypatch.setattr(
        system_module.sc,
        "get_microphone",
        lambda id, include_loopback: FakeLoopback(),
    )
    monkeypatch.setattr(system_module.sf, "SoundFile", lambda *args, **kwargs: fake_file)

    levels = []
    engine = SystemAudioEngine(level_callback=levels.append)
    engine._recording = True
    engine._record(
        str(tmp_path / "system.wav"),
        48000,
    )

    assert record_calls == [4800, 4800]
    assert len(fake_file.writes) == 2
    assert len(levels) == 2
    assert all(0.0 <= value <= 1.0 for value in levels)


def test_audio_capture_service_emits_independent_normalized_levels() -> None:
    class Configuration:
        output_directory = "output"

    bus = EventBus()
    microphone_levels = []
    system_levels = []
    bus.subscribe(
        "microphone_audio_level",
        microphone_levels.append,
    )
    bus.subscribe(
        "system_audio_level",
        system_levels.append,
    )

    service = AudioCaptureService(
        Configuration(),
        event_bus=bus,
    )
    service._on_microphone_audio_level(1.25)
    service._on_system_audio_level(-0.25)

    assert microphone_levels == [1.0]
    assert system_levels == [0.0]
