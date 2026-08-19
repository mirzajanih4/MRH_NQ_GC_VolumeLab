class MarketTrade:

    def __init__(
            self,
            timestamp,
            price,
            volume,
            bid,
            ask,
            aggressor_side
    ):
        self.timestamp = timestamp
        self.price = price
        self.volume = volume
        self.bid = bid
        self.ask = ask
        self.aggressor_side = aggressor_side

    def show(self):
        print(
            f"Time: {self.timestamp} | "
            f"Price: {self.price} | "
            f"Volume: {self.volume} | "
            f"Bid: {self.bid} | "
            f"Ask: {self.ask} | "
            f"Aggressor: {self.aggressor_side}"
        )