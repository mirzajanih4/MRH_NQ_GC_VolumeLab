from config.settings import MIN_SCORE_FOR_TRADE


class RiskEngine:

    def __init__(self):
        self.max_score_required = MIN_SCORE_FOR_TRADE

    def get_required_score(self, session):

        if session == "NEW_YORK":
            return 0.65

        if session == "ASIA_OR_OFF_HOURS":
            return 0.90

        return self.max_score_required

    def allow_trade(self, orderflow_score, session):

        required_score = self.get_required_score(session)

        if orderflow_score >= required_score:
            return True

        return False
    def get_block_reason(self, score, session):

        required_score = self.get_required_score(session)

        if score < required_score:
            return "SCORE_TOO_LOW"

        return "NO_BLOCK"
    def show_risk_status(self, score, session):

        print("----- Risk Engine -----")

        allowed = self.allow_trade(score, session)

        print(f"Trade Allowed: {allowed}")
        print(f"Required Score: {self.get_required_score(session)}")