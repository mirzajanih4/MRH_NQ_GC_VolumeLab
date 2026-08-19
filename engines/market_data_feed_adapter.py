from abc import ABC, abstractmethod


class MarketDataFeedAdapter(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def get_latest_trade(self):
        pass