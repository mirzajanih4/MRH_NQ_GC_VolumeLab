class FootprintEngine:

    def __init__(self):
        pass

    def analyze_footprint(self, ticks):

        buy_aggression = 0
        sell_aggression = 0

        current_ask_stack = 0
        current_bid_stack = 0

        max_ask_stack = 0
        max_bid_stack = 0

        for tick in ticks:

            if tick.side == "ASK":
                buy_aggression += tick.volume

                current_ask_stack += 1
                current_bid_stack = 0

                if current_ask_stack > max_ask_stack:
                    max_ask_stack = current_ask_stack

            elif tick.side == "BID":
                sell_aggression += tick.volume

                current_bid_stack += 1
                current_ask_stack = 0

                if current_bid_stack > max_bid_stack:
                    max_bid_stack = current_bid_stack

        footprint_score = 0

        if buy_aggression > sell_aggression:
            footprint_score += 0.5

        elif sell_aggression > buy_aggression:
            footprint_score += 0.5

        if abs(buy_aggression - sell_aggression) >= 20:
            footprint_score += 0.5

        if (
                max_ask_stack >= 3
                or max_bid_stack >= 3
        ):
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

        stacked_imbalance = False
        stack_direction = "NONE"

        if max_ask_stack >= 3:
            stacked_imbalance = True
            stack_direction = "BUY"

        elif max_bid_stack >= 3:
            stacked_imbalance = True
            stack_direction = "SELL"

        stack_strength = "NONE"

        if stacked_imbalance:

            if max_ask_stack >= 5 or max_bid_stack >= 5:
                stack_strength = "HIGH"

            elif max_ask_stack >= 4 or max_bid_stack >= 4:
                stack_strength = "MEDIUM"

            elif max_ask_stack >= 3 or max_bid_stack >= 3:
                stack_strength = "LOW"

        footprint_data = {
            "buy_aggression": buy_aggression,
            "sell_aggression": sell_aggression,
            "bid_ask_imbalance": (
                    buy_aggression - sell_aggression
            ),
            "delta_exhaustion": delta_exhaustion,
            "absorption_clue": absorption_clue,
            "max_ask_stack": max_ask_stack,
            "max_bid_stack": max_bid_stack,
            "stacked_imbalance": stacked_imbalance,
            "stack_direction": stack_direction,
            "stack_strength": stack_strength,
            "footprint_score": footprint_score
        }

        return footprint_data