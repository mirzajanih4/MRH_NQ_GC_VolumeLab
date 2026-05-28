class FootprintEngine:

    def __init__(self):
        pass

    def analyze_footprint(self, ticks):

        buy_aggression = 0
        sell_aggression = 0

        for tick in ticks:

            if tick.side == "ASK":
                buy_aggression += tick.volume

            elif tick.side == "BID":
                sell_aggression += tick.volume

        footprint_score = 0

        if buy_aggression > sell_aggression:
            footprint_score += 0.5

        elif sell_aggression > buy_aggression:
            footprint_score += 0.5

        if abs(buy_aggression - sell_aggression) >= 20:
            footprint_score += 0.5

        delta_exhaustion = False

        if (
                buy_aggression > 25
                and sell_aggression > 0
                and abs(buy_aggression - sell_aggression) < buy_aggression
        ):
            delta_exhaustion = True

        absorption_clue = False

        if (
                delta_exhaustion
                and buy_aggression > sell_aggression
        ):
            absorption_clue = True

        footprint_data = {
            "buy_aggression": buy_aggression,
            "sell_aggression": sell_aggression,
            "bid_ask_imbalance": (
                    buy_aggression - sell_aggression
            ),
            "delta_exhaustion": delta_exhaustion,
            "absorption_clue": absorption_clue,
            "footprint_score": footprint_score
        }
        return footprint_data