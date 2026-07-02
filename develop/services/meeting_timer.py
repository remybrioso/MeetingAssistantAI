"""
meeting_timer.py

Cronómetro de reunión sin threads.
"""


class MeetingTimer:

    def __init__(self):

        self.seconds = 0
        self.running = False

    def start(self):

        self.seconds = 0
        self.running = True

    def stop(self):

        self.running = False

    def tick(self):

        if self.running:
            self.seconds += 1

        return self.formatted_time()

    def formatted_time(self):

        mins, secs = divmod(self.seconds, 60)
        hours, mins = divmod(mins, 60)

        return f"{hours:02}:{mins:02}:{secs:02}"