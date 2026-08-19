import MetaTrader5 as mt5


MT5_TERMINAL_PATH = (
    r"C:\Program Files\STP Trading MetaTrader 5 Terminal\terminal64.exe"
)

MT5_SYMBOL = "NAS100.s"

DEMO_VOLUME = 0.01

DEMO_SL_DISTANCE = 20.0
DEMO_TP_DISTANCE = 40.0

DEMO_MAGIC = 146001


def build_demo_order_request(
        direction
):

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

    direction = direction.upper()

    if direction == "BUY":

        price = tick.ask

        order_type = (
            mt5.ORDER_TYPE_BUY
        )

        stop_loss = round(
            price - DEMO_SL_DISTANCE,
            2
        )

        take_profit = round(
            price + DEMO_TP_DISTANCE,
            2
        )

    elif direction == "SELL":

        price = tick.bid

        order_type = (
            mt5.ORDER_TYPE_SELL
        )

        stop_loss = round(
            price + DEMO_SL_DISTANCE,
            2
        )

        take_profit = round(
            price - DEMO_TP_DISTANCE,
            2
        )

    else:

        mt5.shutdown()

        return None

    request = {
        "action":
            mt5.TRADE_ACTION_DEAL,

        "symbol":
            MT5_SYMBOL,

        "volume":
            DEMO_VOLUME,

        "type":
            order_type,

        "price":
            price,

        "sl":
            stop_loss,

        "tp":
            take_profit,

        "deviation":
            20,

        "magic":
            DEMO_MAGIC,

        "comment":
            "MRH_DEMO_EXECUTION",

        "type_time":
            mt5.ORDER_TIME_GTC,

        "type_filling":
            mt5.ORDER_FILLING_IOC
    }

    mt5.shutdown()

    return request

def check_demo_order_request(
        direction
):

    request = build_demo_order_request(
        direction
    )

    if request is None:
        return None

    initialized = mt5.initialize(
        path=MT5_TERMINAL_PATH
    )

    if not initialized:
        return None

    check_result = mt5.order_check(
        request
    )

    mt5.shutdown()

    return check_result

def send_demo_order(
        direction
):

    request = build_demo_order_request(
        direction
    )

    if request is None:
        return {
            "sent": False,
            "reason": "REQUEST_BUILD_FAILED",
            "result": None
        }

    initialized = mt5.initialize(
        path=MT5_TERMINAL_PATH
    )

    if not initialized:
        return {
            "sent": False,
            "reason": "MT5_INITIALIZE_FAILED",
            "result": None
        }

    check_result = mt5.order_check(
        request
    )

    if (
            check_result is None
            or check_result.retcode != 0
    ):

        mt5.shutdown()

        return {
            "sent": False,
            "reason": "ORDER_CHECK_FAILED",
            "result": check_result
        }

    send_result = mt5.order_send(
        request
    )

    mt5.shutdown()

    if send_result is None:
        return {
            "sent": False,
            "reason": "ORDER_SEND_FAILED",
            "result": None
        }

    return {
        "sent": True,
        "reason": "ORDER_SENT",
        "result": send_result
    }