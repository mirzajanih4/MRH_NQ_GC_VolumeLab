class ContextEngine:

    def __init__(self, volume_engine):

        self.volume_engine = volume_engine

    def detect_market_phase(self):

        delta = self.volume_engine.get_delta_last_seconds(10)

        if delta > 20:
            return "TREND_UP"

        if delta < -20:
            return "TREND_DOWN"

        return "RANGE"
    def detect_price_location(self):

        if not self.volume_engine.ticks:
            return "UNKNOWN"

        current_price = self.volume_engine.ticks[-1].price
        vwap = self.volume_engine.get_vwap()

        tolerance = 0.25

        if current_price > vwap + tolerance:
            return "ABOVE_VWAP"

        if current_price < vwap - tolerance:
            return "BELOW_VWAP"

        return "NEAR_VWAP"
    def detect_poc_location(self):

        if not self.volume_engine.ticks:
            return "UNKNOWN"

        current_price = self.volume_engine.ticks[-1].price
        poc = self.volume_engine.get_poc()

        if poc is None:
            return "UNKNOWN"

        tolerance = 0.25

        if current_price > poc + tolerance:
            return "ABOVE_POC"

        if current_price < poc - tolerance:
            return "BELOW_POC"

        return "NEAR_POC"
    def detect_volume_node(self):

        if not self.volume_engine.ticks:
            return "UNKNOWN"

        current_price = self.volume_engine.ticks[-1].price

        hvn_prices = self.volume_engine.get_hvn()
        lvn_prices = self.volume_engine.get_lvn()

        tolerance = 0.25

        for price in hvn_prices:
            if abs(current_price - price) <= tolerance:
                return "NEAR_HVN"

        for price in lvn_prices:
            if abs(current_price - price) <= tolerance:
                return "NEAR_LVN"

        return "NO_NODE"
    def show_context(self):

        print("----- Market Context -----")

        print(f"Market Phase: {self.detect_market_phase()}")
        print(f"Price Location: {self.detect_price_location()}")
        print(f"POC Location: {self.detect_poc_location()}")
        print(f"Volume Node: {self.detect_volume_node()}")