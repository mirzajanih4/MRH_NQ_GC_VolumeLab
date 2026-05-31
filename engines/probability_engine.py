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

    def get_probability_by_stack_strength(self, stack_strength):

        win_rates = self.analytics_engine.calculate_win_rate_by_field(
            "stack_strength"
        )

        if stack_strength in win_rates:
            return win_rates[stack_strength]

        return 0

    def get_probability_by_footprint_score(self, footprint_score):

        win_rates = self.analytics_engine.calculate_win_rate_by_field(
            "footprint_score"
        )

        footprint_score = str(footprint_score)

        if footprint_score in win_rates:
            return win_rates[footprint_score]

        return 0

    def get_probability_by_quality_and_footprint(
            self,
            trade_quality,
            footprint_score
    ):

        win_rates = (
            self.analytics_engine
            .calculate_win_rate_by_combined_fields(
                "trade_quality",
                "footprint_score"
            )
        )

        key = (
            f"{trade_quality}|"
            f"{footprint_score}"
        )

        if key in win_rates:
            return win_rates[key]

        return 0

    def build_probability_model_snapshot(self):

        snapshot = {}

        snapshot["setup_grade"] = (
            self.analytics_engine
            .calculate_win_rate_by_field(
                "setup_grade"
            )
        )

        snapshot["setup_type"] = (
            self.analytics_engine
            .calculate_win_rate_by_field(
                "setup_type"
            )
        )

        snapshot["trade_quality"] = (
            self.analytics_engine
            .calculate_win_rate_by_field(
                "trade_quality"
            )
        )

        snapshot["stack_strength"] = (
            self.analytics_engine
            .calculate_win_rate_by_field(
                "stack_strength"
            )
        )

        snapshot["footprint_score"] = (
            self.analytics_engine
            .calculate_win_rate_by_field(
                "footprint_score"
            )
        )

        return snapshot