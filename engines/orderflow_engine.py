from config.settings import (
    DELTA_SPIKE_THRESHOLD,
    SWEEP_PRICE_MOVE,
    SWEEP_VOLUME_THRESHOLD
)
class OrderflowEngine:

    def __init__(self, volume_engine):

        self.volume_engine = volume_engine

    def detect_sweep(self):

        signal = self.volume_engine.get_sweep_signal(
            seconds=10,
            min_price_move=SWEEP_PRICE_MOVE,
            min_volume=SWEEP_VOLUME_THRESHOLD
        )

        return signal

    def detect_delta_spike(self):

        if self.volume_engine.is_delta_spike(10, DELTA_SPIKE_THRESHOLD):
            return "DELTA_SPIKE"

        return "NO_DELTA_SPIKE"
    def detect_absorption(self):

        volume = self.volume_engine.get_volume_last_seconds(10)
        delta = self.volume_engine.get_delta_last_seconds(10)

        if not self.volume_engine.ticks:
            return "NO_ABSORPTION"

        first_price = self.volume_engine.ticks[0].price
        last_price = self.volume_engine.ticks[-1].price

        price_move = abs(last_price - first_price)

        if volume >= 30 and price_move <= 0.25:

            if delta > 10:
                return "SELL_ABSORPTION"

            if delta < -10:
                return "BUY_ABSORPTION"

            return "NEUTRAL_ABSORPTION"

        return "NO_ABSORPTION"
    def calculate_score(self):

        score = 0

        sweep_signal = self.detect_sweep()
        absorption_signal = self.detect_absorption()

        if sweep_signal != "NO_SWEEP":
            score += 0.6

        if self.detect_delta_spike() == "DELTA_SPIKE":
            score += 0.4

        # مخالف بودن absorption با حرکت
        if (
            sweep_signal == "SWEEP_BUY"
            and absorption_signal == "SELL_ABSORPTION"
        ):
            score -= 0.5

        if (
            sweep_signal == "SWEEP_SELL"
            and absorption_signal == "BUY_ABSORPTION"
        ):
            score -= 0.5

        # جلوگیری از score منفی
        if score < 0:
            score = 0

        return round(score, 2)
    def show_signals(self):

        print("----- Orderflow Signals -----")

        print(f"Sweep Signal: {self.detect_sweep()}")
        print(f"Delta Spike Signal: {self.detect_delta_spike()}")
        print(f"Orderflow Score: {self.calculate_score()}")
        print(f"Absorption Signal: {self.detect_absorption()}")