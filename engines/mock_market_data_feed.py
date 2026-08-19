from core.market_trade import MarketTrade
from engines.market_data_feed_adapter import (
    MarketDataFeedAdapter
)


class MockMarketDataFeed(
        MarketDataFeedAdapter
):

    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False

    def is_connected(self):
        return self.connected

    def get_latest_trade(self):

        if not self.connected:
            return None

        return MarketTrade(
            timestamp=1000,
            price=29500.25,
            volume=12,
            bid=29500.00,
            ask=29500.25,
            aggressor_side="BUY"
        )