class ProbabilityEngine:

    def __init__(self, analytics_engine):
        self.analytics_engine = analytics_engine

    def get_probability_by_setup_grade(self, setup_grade):

        win_rates = self.analytics_engine.calculate_win_rate_by_field(
            "setup_grade"
        )

        if setup_grade in win_rates:
            return win_rates[setup_grade]

        return 0
    def get_probability_by_setup_type(self, setup_type):

        win_rates = self.analytics_engine.calculate_win_rate_by_field(
            "setup_type"
        )

        if setup_type in win_rates:
            return win_rates[setup_type]

        return 0

    def get_probability_by_trade_quality(self, trade_quality):

        win_rates = self.analytics_engine.calculate_win_rate_by_field(
            "trade_quality"
        )

        if trade_quality in win_rates:
            return win_rates[trade_quality]

        return 0