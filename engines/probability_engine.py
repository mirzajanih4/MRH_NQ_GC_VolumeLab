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

    def calculate_probability_score(
            self,
            setup_grade,
            setup_type,
            trade_quality,
            stack_strength,
            footprint_score
    ):

        probabilities = []

        probabilities.append(
            self.get_probability_by_setup_grade(
                setup_grade
            )
        )

        probabilities.append(
            self.get_probability_by_setup_type(
                setup_type
            )
        )

        probabilities.append(
            self.get_probability_by_trade_quality(
                trade_quality
            )
        )

        probabilities.append(
            self.get_probability_by_stack_strength(
                stack_strength
            )
        )

        probabilities.append(
            self.get_probability_by_footprint_score(
                footprint_score
            )
        )

        if len(probabilities) == 0:
            return 0

        return round(
            sum(probabilities) / len(probabilities),
            2
        )

    def calculate_weighted_probability_score(
            self,
            setup_grade,
            setup_type,
            trade_quality,
            stack_strength,
            footprint_score
    ):

        score = 0

        score += (
                self.get_probability_by_setup_grade(
                    setup_grade
                ) * 0.30
        )

        score += (
                self.get_probability_by_setup_type(
                    setup_type
                ) * 0.25
        )

        score += (
                self.get_probability_by_trade_quality(
                    trade_quality
                ) * 0.25
        )

        score += (
                self.get_probability_by_stack_strength(
                    stack_strength
                ) * 0.10
        )

        score += (
                self.get_probability_by_footprint_score(
                    footprint_score
                ) * 0.10
        )

        return round(score, 2)

    def get_probability_grade(
            self,
            weighted_probability_score
    ):

        if weighted_probability_score >= 90:
            return "ELITE_PROBABILITY"

        elif weighted_probability_score >= 75:
            return "HIGH_PROBABILITY"

        elif weighted_probability_score >= 50:
            return "MEDIUM_PROBABILITY"

        return "LOW_PROBABILITY"
