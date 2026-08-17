import MetaTrader5 as mt5

from core.live_quote import LiveQuote


MT5_TERMINAL_PATH = (
    r"C:\Program Files\STP Trading MetaTrader 5 Terminal\terminal64.exe"
)

MT5_SYMBOL = "NAS100.s"


def get_live_quote():

    initialized = mt5.initialize(
        path=MT5_TERMINAL_PATH
    )

    if not initialized:
        return None

    symbol_selected = mt5.symbol_select(
        MT5_SYMBOL,
        True
    )

    if not symbol_selected:
        mt5.shutdown()
        return None

    tick = mt5.symbol_info_tick(
        MT5_SYMBOL
    )

    if tick is None:
        mt5.shutdown()
        return None

    live_quote = LiveQuote(
        timestamp=tick.time_msc,
        bid=tick.bid,
        ask=tick.ask
    )

    mt5.shutdown()

    return live_quote