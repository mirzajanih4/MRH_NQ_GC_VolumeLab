class NQStrategy:

    def __init__(
            self,
            orderflow_engine,
            context_engine,
            session_engine
    ):
        self.orderflow_engine = orderflow_engine
        self.context_engine = context_engine
        self.session_engine = session_engine

    def evaluate(self):
        score = self.orderflow_engine.calculate_score()
        sweep_signal = self.orderflow_engine.detect_sweep()
        market_phase = self.context_engine.detect_market_phase()
        price_location = self.context_engine.detect_price_location()
        poc_location = self.context_engine.detect_poc_location()
        volume_node = self.context_engine.detect_volume_node()
        absorption_signal = self.orderflow_engine.detect_absorption()
        session = self.session_engine.detect_session()
        if (

                score >= 0.75
                and sweep_signal == "SWEEP_BUY"
                and market_phase == "TREND_UP"
                and price_location != "BELOW_VWAP"
                and poc_location != "BELOW_POC"
                and volume_node != "NEAR_HVN"
                and absorption_signal != "SELL_ABSORPTION"
        ):
            if session == "ASIA_OR_OFF_HOURS":
                return "NO_TRADE"
            return "BUY"

        if (
                score >= 0.75
                and sweep_signal == "SWEEP_SELL"
                and market_phase == "TREND_DOWN"
                and price_location != "ABOVE_VWAP"
                and poc_location != "ABOVE_POC"
                and volume_node != "NEAR_HVN"
                and absorption_signal != "BUY_ABSORPTION"
        ):
            return "SELL"

        return "NO_TRADE"
    def get_strategy_block_reason(self):

        score = self.orderflow_engine.calculate_score()
        sweep_signal = self.orderflow_engine.detect_sweep()
        market_phase = self.context_engine.detect_market_phase()
        price_location = self.context_engine.detect_price_location()
        poc_location = self.context_engine.detect_poc_location()
        volume_node = self.context_engine.detect_volume_node()
        absorption_signal = self.orderflow_engine.detect_absorption()
        session = self.session_engine.detect_session()

        if session == "ASIA_OR_OFF_HOURS":
            return "WRONG_SESSION"

        if volume_node == "NEAR_HVN":
            return "HVN_ZONE"

        if sweep_signal == "SWEEP_BUY" and absorption_signal == "SELL_ABSORPTION":
            return "ABSORPTION_CONFLICT"

        if sweep_signal == "SWEEP_SELL" and absorption_signal == "BUY_ABSORPTION":
            return "ABSORPTION_CONFLICT"

        if score < 0.75:
            return "LOW_ORDERFLOW_SCORE"

        return "NO_STRATEGY_BLOCK"
    def classify_setup(self):

        sweep_signal = self.orderflow_engine.detect_sweep()
        absorption_signal = self.orderflow_engine.detect_absorption()
        volume_node = self.context_engine.detect_volume_node()
        market_phase = self.context_engine.detect_market_phase()

        if (
            sweep_signal == "SWEEP_BUY"
            and volume_node == "NEAR_LVN"
            and market_phase == "TREND_UP"
        ):
            return "BREAKOUT_SETUP"

        if (
            sweep_signal == "SWEEP_SELL"
            and volume_node == "NEAR_LVN"
            and market_phase == "TREND_DOWN"
        ):
            return "BREAKDOWN_SETUP"

        if absorption_signal != "NO_ABSORPTION":
            return "ABSORPTION_SETUP"

        if volume_node == "NEAR_HVN":
            return "BALANCED_MARKET"

        return "UNCLASSIFIED_SETUP"
    def grade_setup(self):

        score = self.orderflow_engine.calculate_score()
        setup_type = self.classify_setup()
        volume_node = self.context_engine.detect_volume_node()

        if (
            score >= 1.0
            and setup_type == "BREAKOUT_SETUP"
            and volume_node == "NEAR_LVN"
        ):
            return "A_SETUP"

        if score >= 0.5:
            return "B_SETUP"

        return "C_SETUP"
    def get_final_signal(self, risk_engine):
        decision = self.evaluate()
        score = self.orderflow_engine.calculate_score()

        risk_allowed = risk_engine.allow_trade(
            score,
            self.session_engine.detect_session()
        )

        if decision == "BUY" and risk_allowed:
            return "BUY_ALLOWED"

        if decision == "SELL" and risk_allowed:
            return "SELL_ALLOWED"

        return "NO_TRADE"
    def show_decision(self, risk_engine):
        print("----- Strategy Decision -----")
        print(f"Decision: {self.evaluate()}")
        print(f"Final Signal: {self.get_final_signal(risk_engine)}")