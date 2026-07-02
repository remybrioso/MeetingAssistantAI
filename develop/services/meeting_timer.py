"""
meeting_timer.py

Cronómetro de la reunión.
"""

import threading
import time


class MeetingTimer:

    def __init__(self, bus):

        self.bus = bus

        self.seconds = 0

        self.running = False

        self.thread = None

    def start(self):

        if self.running:
            return

        self.running = True
        self.seconds = 0

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.thread.start()

    def stop(self):

        self.running = False

    def _run(self):

        while self.running:

            mins, secs = divmod(self.seconds, 60)

            hours, mins = divmod(mins, 60)

            self.bus.emit(
                "timer_tick",
                f"{hours:02}:{mins:02}:{secs:02}"
            )

            time.sleep(1)

            self.seconds += 1