import time
class ReplayEngine:

    def __init__(self, volume_engine):
        self.volume_engine = volume_engine

    def show_statistics(self, final_signal, setup_type):

        print("----- Replay Statistics -----")

        total_ticks = len(self.volume_engine.ticks)

        total_volume = (
            self.volume_engine.ask_volume
            + self.volume_engine.bid_volume
        )

        print(f"Total Ticks: {total_ticks}")
        print(f"Total Volume: {total_volume}")
        print(f"Final CVD: {self.volume_engine.cvd}")
        print(f"Final Signal: {final_signal}")

        print(f"Setup Type: {setup_type}")

    def replay_ticks(self, ticks, use_delay=True):

        print("----- Replay Started -----")

        previous_time = None

        for tick in ticks:

            if previous_time is not None:

                delay = (
                    tick.timestamp - previous_time
                ).total_seconds()

                if use_delay and delay > 0:
                    time.sleep(delay)

            self.volume_engine.process_tick(tick)

            tick.show()

            previous_time = tick.timestamp

        print("----- Replay Finished -----")