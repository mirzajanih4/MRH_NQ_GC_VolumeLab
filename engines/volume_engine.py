class VolumeEngine:

    def __init__(self):
        self.ask_volume = 0
        self.bid_volume = 0
        self.cvd = 0
        self.ticks = []

    def process_tick(self, tick):
        self.ticks.append(tick)

        if tick.side == "ASK":
            self.ask_volume += tick.volume
            delta = tick.volume

        elif tick.side == "BID":
            self.bid_volume += tick.volume
            delta = -tick.volume

        else:
            delta = 0

        self.cvd += delta
        tick.delta = delta

        return delta

    def get_total_delta(self):
        total_delta = 0

        for tick in self.ticks:
            total_delta += tick.delta

        return total_delta

    def get_recent_delta(self, number_of_ticks):
        recent_ticks = self.ticks[-number_of_ticks:]

        recent_delta = 0

        for tick in recent_ticks:
            recent_delta += tick.delta

        return recent_delta

    def get_delta_last_seconds(self, seconds):

        if not self.ticks:
            return 0

        latest_time = self.ticks[-1].timestamp
        window_start = latest_time.timestamp() - seconds

        delta_sum = 0

        for tick in self.ticks:

            tick_time = tick.timestamp.timestamp()

            if tick_time >= window_start:
                delta_sum += tick.delta

        return delta_sum
    def get_volume_last_seconds(self, seconds):

        if not self.ticks:
            return 0

        latest_time = self.ticks[-1].timestamp
        window_start = latest_time.timestamp() - seconds

        volume_sum = 0

        for tick in self.ticks:

            tick_time = tick.timestamp.timestamp()

            if tick_time >= window_start:
                volume_sum += tick.volume

        return volume_sum
    def get_vwap(self):

        if not self.ticks:
            return 0

        total_price_volume = 0
        total_volume = 0

        for tick in self.ticks:
            total_price_volume += tick.price * tick.volume
            total_volume += tick.volume

        if total_volume == 0:
            return 0

        return total_price_volume / total_volume
    def get_volume_profile(self):

        profile = {}

        for tick in self.ticks:

            price = tick.price

            if price not in profile:
                profile[price] = 0

            profile[price] += tick.volume

        return profile
    def get_poc(self):

        profile = self.get_volume_profile()

        if not profile:
            return None

        poc_price = max(profile, key=profile.get)

        return poc_price
    def get_hvn(self):

        profile = self.get_volume_profile()

        if not profile:
            return []

        hvn_prices = []

        average_volume = sum(profile.values()) / len(profile)

        for price, volume in profile.items():

            if volume >= average_volume:
                hvn_prices.append(price)

        return hvn_prices
    def get_lvn(self):

        profile = self.get_volume_profile()

        if not profile:
            return []

        lvn_prices = []

        average_volume = sum(profile.values()) / len(profile)

        for price, volume in profile.items():

            if volume < average_volume:
                lvn_prices.append(price)

        return lvn_prices
    def is_delta_spike(self, seconds, threshold):

        delta = self.get_delta_last_seconds(seconds)

        if abs(delta) >= threshold:
            return True

        return False
    def is_liquidity_sweep(self, seconds, min_price_move, min_volume):

        if not self.ticks:
            return False

        latest_time = self.ticks[-1].timestamp
        window_start = latest_time.timestamp() - seconds

        prices = []
        total_volume = 0

        for tick in self.ticks:

            tick_time = tick.timestamp.timestamp()

            if tick_time >= window_start:
                prices.append(tick.price)
                total_volume += tick.volume

        if not prices:
            return False

        price_move = max(prices) - min(prices)

        if price_move >= min_price_move and total_volume >= min_volume:
            return True

        return False
    def get_sweep_direction(self, seconds, min_price_move, min_volume):

        if not self.is_liquidity_sweep(seconds, min_price_move, min_volume):
            return "NONE"

        latest_time = self.ticks[-1].timestamp
        window_start = latest_time.timestamp() - seconds

        recent_ticks = []

        for tick in self.ticks:

            tick_time = tick.timestamp.timestamp()

            if tick_time >= window_start:
                recent_ticks.append(tick)

        if not recent_ticks:
            return "NONE"

        first_price = recent_ticks[0].price
        last_price = recent_ticks[-1].price

        if last_price > first_price:
            return "BUY"

        if last_price < first_price:
            return "SELL"

        return "NONE"
    def get_sweep_signal(self, seconds, min_price_move, min_volume):

        direction = self.get_sweep_direction(
            seconds,
            min_price_move,
            min_volume
        )

        if direction == "BUY":
            return "SWEEP_BUY"

        if direction == "SELL":
            return "SWEEP_SELL"

        return "NO_SWEEP"
    def show_status(self):
        print("----- Volume Engine Status -----")
        print(f"Ask Volume: {self.ask_volume}")
        print(f"Bid Volume: {self.bid_volume}")
        print(f"CVD: {self.cvd}")
        print(f"Total Delta: {self.get_total_delta()}")
        print(f"Recent Delta (Last 2 Ticks): {self.get_recent_delta(2)}")
        print(f"Delta Last 10 Seconds: {self.get_delta_last_seconds(10)}")
        print(f"Volume Last 10 Seconds: {self.get_volume_last_seconds(10)}")
        print(f"Delta Spike: {self.is_delta_spike(10, 20)}")
        print(f"Liquidity Sweep: {self.is_liquidity_sweep(10, 0.5, 30)}")
        print(f"Sweep Direction: {self.get_sweep_direction(10, 0.5, 30)}")
        print(f"Sweep Signal: {self.get_sweep_signal(10, 0.5, 30)}")
        print(f"VWAP: {self.get_vwap():.2f}")
        print(f"Volume Profile: {self.get_volume_profile()}")
        print(f"POC: {self.get_poc()}")
        print(f"HVN: {self.get_hvn()}")
        print(f"LVN: {self.get_lvn()}")