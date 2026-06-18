class SessionEngine:

    def __init__(self, volume_engine):
        self.volume_engine = volume_engine

    def detect_session(self):

        if not self.volume_engine.ticks:
            return "UNKNOWN"

        current_time = self.volume_engine.ticks[-1].timestamp
        hour = current_time.hour

        if 13 <= hour < 16:
            return "LONDON_NEW_YORK_OVERLAP"

        if 8 <= hour < 13:
            return "LONDON"

        if 16 <= hour < 21:
            return "NEW_YORK"

        return "ASIA_OR_OFF_HOURS"

    def show_session(self):

        print("----- Session Engine -----")
        print(f"Session: {self.detect_session()}")