class LiveQuote:

    def __init__(
            self,
            timestamp,
            bid,
            ask
    ):
        self.timestamp = timestamp
        self.bid = bid
        self.ask = ask

        self.spread = (
            ask - bid
        )

        self.mid_price = (
            bid + ask
        ) / 2

    def show(self):

        print(
            f"Time: {self.timestamp} | "
            f"Bid: {self.bid} | "
            f"Ask: {self.ask} | "
            f"Spread: {self.spread} | "
            f"Mid: {self.mid_price}"
        )