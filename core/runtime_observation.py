class RuntimeObservation:

    def __init__(
            self,
            previous_quote,
            current_quote
    ):

        self.timestamp = (
            current_quote.timestamp
        )

        self.bid = (
            current_quote.bid
        )

        self.ask = (
            current_quote.ask
        )

        self.spread = (
            current_quote.spread
        )

        self.mid_price = (
            current_quote.mid_price
        )

        self.mid_change = (
            current_quote.mid_price
            - previous_quote.mid_price
        )

        if self.mid_change > 0:
            self.quote_direction = "UP"

        elif self.mid_change < 0:
            self.quote_direction = "DOWN"

        else:
            self.quote_direction = "FLAT"

    def show(self):

        print(
            f"Time: {self.timestamp} | "
            f"Bid: {self.bid} | "
            f"Ask: {self.ask} | "
            f"Spread: {self.spread} | "
            f"Mid: {self.mid_price} | "
            f"Mid Change: {self.mid_change} | "
            f"Direction: {self.quote_direction}"
        )