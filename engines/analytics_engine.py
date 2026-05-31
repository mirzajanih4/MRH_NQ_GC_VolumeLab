import csv


class AnalyticsEngine:

    def __init__(self, file_path):
        self.file_path = file_path

    def load_records(self):

        records = []

        with open(self.file_path, mode="r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                records.append(row)

        return records

    def count_by_field(self, field_name):

        records = self.load_records()
        counts = {}

        for record in records:
            value = record[field_name]

            if value not in counts:
                counts[value] = 0

            counts[value] += 1

        return counts
    def calculate_win_rate(self):

        records = self.load_records()

        wins = 0
        losses = 0

        for record in records:

            outcome = record["trade_outcome"]

            if outcome == "WIN":
                wins += 1

            elif outcome == "LOSS":
                losses += 1

        total_trades = wins + losses

        if total_trades == 0:
            return 0

        return round((wins / total_trades) * 100, 2)
    def calculate_win_rate_by_field(self, field_name):

        records = self.load_records()
        stats = {}

        for record in records:

            field_value = record[field_name]
            outcome = record["trade_outcome"]

            if field_value not in stats:
                stats[field_value] = {
                    "wins": 0,
                    "losses": 0
                }

            if outcome == "WIN":
                stats[field_value]["wins"] += 1

            elif outcome == "LOSS":
                stats[field_value]["losses"] += 1

        win_rates = {}

        for field_value, result in stats.items():

            wins = result["wins"]
            losses = result["losses"]
            total = wins + losses

            if total == 0:
                win_rates[field_value] = 0
            else:
                win_rates[field_value] = round((wins / total) * 100, 2)

        return win_rates
    def calculate_average_confidence(self):

        records = self.load_records()

        total_confidence = 0
        count = 0

        for record in records:

            if "confidence_score" in record:
                total_confidence += float(record["confidence_score"])
                count += 1

        if count == 0:
            return 0

        return round(total_confidence / count, 2)

    def calculate_average_by_field(self, field_name):

        records = self.load_records()

        total_value = 0
        count = 0

        for record in records:

            if field_name in record and record[field_name] != "":
                total_value += float(record[field_name])
                count += 1

        if count == 0:
            return 0

        return round(total_value / count, 2)

    def count_confidence_buckets(self):

        records = self.load_records()
        buckets = {
            "LOW_CONFIDENCE": 0,
            "MEDIUM_CONFIDENCE": 0,
            "HIGH_CONFIDENCE": 0,
            "ELITE_CONFIDENCE": 0
        }

        for record in records:

            confidence = float(record["confidence_score"])

            if confidence < 40:
                buckets["LOW_CONFIDENCE"] += 1

            elif confidence < 70:
                buckets["MEDIUM_CONFIDENCE"] += 1

            elif confidence < 90:
                buckets["HIGH_CONFIDENCE"] += 1

            else:
                buckets["ELITE_CONFIDENCE"] += 1

        return buckets

    def calculate_win_rate_by_confidence_bucket(self):

        records = self.load_records()

        stats = {
            "LOW_CONFIDENCE": {"wins": 0, "losses": 0},
            "MEDIUM_CONFIDENCE": {"wins": 0, "losses": 0},
            "HIGH_CONFIDENCE": {"wins": 0, "losses": 0},
            "ELITE_CONFIDENCE": {"wins": 0, "losses": 0}
        }

        for record in records:

            confidence = float(record["confidence_score"])
            outcome = record["trade_outcome"]

            if confidence < 40:
                bucket = "LOW_CONFIDENCE"

            elif confidence < 70:
                bucket = "MEDIUM_CONFIDENCE"

            elif confidence < 90:
                bucket = "HIGH_CONFIDENCE"

            else:
                bucket = "ELITE_CONFIDENCE"

            if outcome == "WIN":
                stats[bucket]["wins"] += 1

            elif outcome == "LOSS":
                stats[bucket]["losses"] += 1

        win_rates = {}

        for bucket, result in stats.items():

            wins = result["wins"]
            losses = result["losses"]
            total = wins + losses

            if total == 0:
                win_rates[bucket] = 0
            else:
                win_rates[bucket] = round((wins / total) * 100, 2)

        return win_rates

    def calculate_win_rate_by_combined_fields(
            self,
            field_one,
            field_two
    ):

        records = self.load_records()
        stats = {}

        for record in records:

            combined_key = (
                f"{record[field_one]}|"
                f"{record[field_two]}"
            )

            outcome = record["trade_outcome"]

            if combined_key not in stats:
                stats[combined_key] = {
                    "wins": 0,
                    "losses": 0
                }

            if outcome == "WIN":
                stats[combined_key]["wins"] += 1

            elif outcome == "LOSS":
                stats[combined_key]["losses"] += 1

        win_rates = {}

        for key, result in stats.items():

            wins = result["wins"]
            losses = result["losses"]

            total = wins + losses

            if total == 0:
                win_rates[key] = 0

            else:
                win_rates[key] = round(
                    (wins / total) * 100,
                    2
                )

        return win_rates

    def build_feature_importance_snapshot(self):

        snapshot = {}

        snapshot["setup_grade"] = (
            self.calculate_win_rate_by_field(
                "setup_grade"
            )
        )

        snapshot["setup_type"] = (
            self.calculate_win_rate_by_field(
                "setup_type"
            )
        )

        snapshot["trade_quality"] = (
            self.calculate_win_rate_by_field(
                "trade_quality"
            )
        )

        snapshot["stack_strength"] = (
            self.calculate_win_rate_by_field(
                "stack_strength"
            )
        )

        snapshot["footprint_score"] = (
            self.calculate_win_rate_by_field(
                "footprint_score"
            )
        )

        snapshot["confidence_bucket"] = (
            self.calculate_win_rate_by_confidence_bucket()
        )

        return snapshot

    def build_ranked_feature_importance(self):

        snapshot = self.build_feature_importance_snapshot()

        ranked_items = []

        for feature_name, values in snapshot.items():

            for value_name, win_rate in values.items():
                ranked_items.append({
                    "feature": feature_name,
                    "value": value_name,
                    "win_rate": win_rate
                })

        ranked_items = sorted(
            ranked_items,
            key=lambda item: item["win_rate"],
            reverse=True
        )

        return ranked_items

    def get_top_features(
            self,
            minimum_win_rate=50
    ):

        ranked = (
            self.build_ranked_feature_importance()
        )

        selected = []

        for item in ranked:

            if (
                    item["win_rate"]
                    >= minimum_win_rate
            ):
                selected.append(item)

        return selected

    def build_ml_readiness_snapshot(self):

        selected_features = self.get_top_features()

        snapshot = {
            "selected_feature_count":
                len(selected_features),

            "dataset_ready":
                len(selected_features) >= 5,

            "selected_features":
                selected_features
        }

        return snapshot