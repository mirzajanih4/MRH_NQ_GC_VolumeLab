class Tick:

    def __init__(self, timestamp, price, volume, side):
        self.timestamp = timestamp
        self.price = price
        self.volume = volume
        self.side = side
        self.delta = 0

    def show(self):
        print(
            f"Time: {self.timestamp} | "
            f"Price: {self.price} | "
            f"Volume: {self.volume} | "
            f"Side: {self.side} | "
            f"Delta: {self.delta}"
        )