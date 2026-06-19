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

    def build_label_distribution(self):

        counts = self.count_by_field(
            "trade_label"
        )

        total = sum(counts.values())

        distribution = {}

        for label, count in counts.items():
            distribution[label] = round(
                (count / total) * 100,
                2
            )

        return distribution

    def build_snapshot_quality_snapshot(self):

        snapshot = {}

        snapshot["trade_labels"] = (
            self.count_by_field(
                "trade_label"
            )
        )

        snapshot["setup_grades"] = (
            self.count_by_field(
                "setup_grade"
            )
        )

        snapshot["trade_qualities"] = (
            self.count_by_field(
                "trade_quality"
            )
        )

        return snapshot

    def build_ml_dataset_quality_dashboard(self):

        dashboard = {}

        dashboard["trade_labels"] = (
            self.count_by_field(
                "trade_label"
            )
        )

        dashboard["trade_qualities"] = (
            self.count_by_field(
                "trade_quality"
            )
        )

        dashboard["probability_grades"] = (
            self.count_by_field(
                "probability_grade"
            )
        )

        return dashboard


    def build_probability_score_distribution(self):

        records = self.load_records()

        distribution = {
            "0_25": 0,
            "25_50": 0,
            "50_75": 0,
            "75_100": 0
        }

        for record in records:

            score = float(
                record.get(
                    "weighted_probability_score",
                    0
                )
            )

            if score < 25:
                distribution["0_25"] += 1

            elif score < 50:
                distribution["25_50"] += 1

            elif score < 75:
                distribution["50_75"] += 1

            else:
                distribution["75_100"] += 1

        return distribution

    def build_ml_training_readiness_report(self):

        records = self.load_records()

        label_counts = self.count_by_field(
            "trade_label"
        )

        total_records = len(records)

        feature_count = 11

        readiness_score = 0

        if total_records >= 10:
            readiness_score += 25

        if "WIN" in label_counts:
            readiness_score += 25

        if "LOSS" in label_counts:
            readiness_score += 25

        if feature_count >= 10:
            readiness_score += 25

        report = {
            "total_records": total_records,

            "wins":
                label_counts.get("WIN", 0),

            "losses":
                label_counts.get("LOSS", 0),

            "skipped":
                label_counts.get("SKIPPED", 0),

            "feature_count":
                feature_count,

            "dataset_ready":
                readiness_score >= 75,

            "ml_readiness_score":
                readiness_score
        }

        return report

    def build_hvn_context_snapshot(self):

        snapshot = {}

        snapshot["hvn_context_counts"] = (
            self.count_by_field(
                "hvn_context"
            )
        )

        snapshot["hvn_context_win_rates"] = (
            self.calculate_win_rate_by_field(
                "hvn_context"
            )
        )

        return snapshot

    def build_hvn_trade_eligibility_snapshot(self):

        snapshot = {}

        snapshot["eligibility_counts"] = (
            self.count_by_field(
                "hvn_trade_eligibility"
            )
        )

        snapshot["eligibility_win_rates"] = (
            self.calculate_win_rate_by_field(
                "hvn_trade_eligibility"
            )
        )

        return snapshot

    def build_hvn_eligibility_outcome_distribution(self):

        records = self.load_records()

        distribution = {}

        for record in records:

            eligibility = record[
                "hvn_trade_eligibility"
            ]

            outcome = record[
                "trade_outcome"
            ]

            if eligibility not in distribution:

                distribution[eligibility] = {
                    "WIN": 0,
                    "LOSS": 0,
                    "SKIPPED": 0
                }

            if outcome in (
                    "WIN",
                    "LOSS",
                    "SKIPPED"
            ):
                distribution[
                    eligibility
                ][outcome] += 1

        return distribution

    def build_virtual_trade_distribution(self):

        records = self.load_records()

        distribution = {
            "NO_VIRTUAL_TRADE": 0,
            "VIRTUAL_LONG": 0,
            "VIRTUAL_SHORT": 0,
            "MISSING_FIELD": 0
        }

        for record in records:

            direction = record.get(
                "virtual_trade_direction",
                "MISSING_FIELD"
            )

            if direction not in distribution:
                distribution[direction] = 0

            distribution[direction] += 1

        return distribution

    def build_virtual_dataset_snapshot(self):

        records = self.load_records()

        snapshot = {
            "legacy_records": 0,
            "virtual_records": 0,
            "virtual_long": 0,
            "virtual_short": 0
        }

        for record in records:

            direction = record.get(
                "virtual_trade_direction",
                ""
            )

            if direction == "":
                snapshot["legacy_records"] += 1

            else:

                snapshot["virtual_records"] += 1

                if direction == "VIRTUAL_LONG":
                    snapshot["virtual_long"] += 1

                elif direction == "VIRTUAL_SHORT":
                    snapshot["virtual_short"] += 1

        return snapshot

    def build_virtual_outcome_snapshot(self):

        records = self.load_records()

        snapshot = {
            "virtual_wins": 0,
            "virtual_losses": 0,
            "pending": 0,
            "virtual_win_rate": 0
        }

        for record in records:

            outcome = record.get(
                "virtual_trade_outcome",
                "PENDING"
            )

            if outcome == "VIRTUAL_WIN":
                snapshot["virtual_wins"] += 1

            elif outcome == "VIRTUAL_LOSS":
                snapshot["virtual_losses"] += 1

            else:
                snapshot["pending"] += 1

        total_finished = (
            snapshot["virtual_wins"]
            + snapshot["virtual_losses"]
        )

        if total_finished > 0:

            snapshot["virtual_win_rate"] = round(
                (
                    snapshot["virtual_wins"]
                    / total_finished
                ) * 100,
                2
            )

        return snapshot

    def calculate_virtual_win_rate_by_field(self, field_name):

        records = self.load_records()
        stats = {}

        for record in records:

            field_value = record.get(field_name, "UNKNOWN")
            virtual_outcome = record.get(
                "virtual_trade_outcome",
                "PENDING"
            )

            if field_value not in stats:
                stats[field_value] = {
                    "virtual_wins": 0,
                    "virtual_losses": 0
                }

            if virtual_outcome == "VIRTUAL_WIN":
                stats[field_value]["virtual_wins"] += 1

            elif virtual_outcome == "VIRTUAL_LOSS":
                stats[field_value]["virtual_losses"] += 1

        win_rates = {}

        for field_value, result in stats.items():

            wins = result["virtual_wins"]
            losses = result["virtual_losses"]
            total = wins + losses

            if total == 0:
                win_rates[field_value] = 0

            else:
                win_rates[field_value] = round(
                    (wins / total) * 100,
                    2
                )

        return win_rates


    def build_virtual_performance_sample_size_by_field(
            self,
            field_name
    ):

        records = self.load_records()
        sample_sizes = {}

        for record in records:

            field_value = record.get(
                field_name,
                "UNKNOWN"
            )

            virtual_outcome = record.get(
                "virtual_trade_outcome",
                "PENDING"
            )

            if field_value not in sample_sizes:
                sample_sizes[field_value] = {
                    "virtual_wins": 0,
                    "virtual_losses": 0,
                    "finished_virtual_trades": 0
                }

            if virtual_outcome == "VIRTUAL_WIN":
                sample_sizes[field_value]["virtual_wins"] += 1
                sample_sizes[field_value]["finished_virtual_trades"] += 1

            elif virtual_outcome == "VIRTUAL_LOSS":
                sample_sizes[field_value]["virtual_losses"] += 1
                sample_sizes[field_value]["finished_virtual_trades"] += 1

        return sample_sizes



    def build_virtual_performance_research_snapshot(self):

        snapshot = {}

        snapshot["virtual_win_rate_by_hvn_context"] = (
            self.calculate_virtual_win_rate_by_field(
                "hvn_context"
            )
        )

        snapshot["virtual_win_rate_by_stack_direction"] = (
            self.calculate_virtual_win_rate_by_field(
                "stack_direction"
            )
        )

        snapshot["virtual_win_rate_by_stack_strength"] = (
            self.calculate_virtual_win_rate_by_field(
                "stack_strength"
            )
        )

        snapshot["virtual_win_rate_by_trade_eligibility"] = (
            self.calculate_virtual_win_rate_by_field(
                "hvn_trade_eligibility"
            )
        )

        return snapshot


    def build_virtual_performance_sample_size_report(self):

        report = {}

        report["sample_size_by_hvn_context"] = (
            self.build_virtual_performance_sample_size_by_field(
                "hvn_context"
            )
        )

        report["sample_size_by_stack_direction"] = (
            self.build_virtual_performance_sample_size_by_field(
                "stack_direction"
            )
        )

        report["sample_size_by_stack_strength"] = (
            self.build_virtual_performance_sample_size_by_field(
                "stack_strength"
            )
        )

        report["sample_size_by_trade_eligibility"] = (
            self.build_virtual_performance_sample_size_by_field(
                "hvn_trade_eligibility"
            )
        )

        return report

    def build_virtual_bias_audit(self):

        records = self.load_records()

        total_records = len(records)

        virtual_records = 0
        eligible_records = 0
        not_eligible_records = 0

        for record in records:

            direction = record.get(
                "virtual_trade_direction",
                "NO_VIRTUAL_TRADE"
            )

            eligibility = record.get(
                "hvn_trade_eligibility",
                "UNKNOWN"
            )

            if direction != "NO_VIRTUAL_TRADE":
                virtual_records += 1

            if eligibility == "CONDITIONAL_ELIGIBLE":
                eligible_records += 1

            elif eligibility == "NOT_ELIGIBLE":
                not_eligible_records += 1

        coverage_percent = 0

        if total_records > 0:

            coverage_percent = round(
                (
                    virtual_records
                    / total_records
                ) * 100,
                2
            )

        return {
            "total_records": total_records,
            "virtual_records": virtual_records,
            "coverage_percent": coverage_percent,
            "eligible_records": eligible_records,
            "not_eligible_records": not_eligible_records
        }

    def build_opportunity_population_validation(self):

        records = self.load_records()

        validation = {}

        for record in records:

            grade = record.get(
                "virtual_opportunity_grade",
                "UNKNOWN"
            )

            outcome = record.get(
                "virtual_trade_outcome",
                "PENDING"
            )

            edge_score = float(
                record.get(
                    "virtual_edge_score",
                    0
                )
            )

            if grade not in validation:

                validation[grade] = {
                    "wins": 0,
                    "losses": 0,
                    "sample_size": 0,
                    "edge_total": 0
                }

            if outcome == "VIRTUAL_WIN":

                validation[grade]["wins"] += 1
                validation[grade]["sample_size"] += 1

            elif outcome == "VIRTUAL_LOSS":

                validation[grade]["losses"] += 1
                validation[grade]["sample_size"] += 1

            validation[grade]["edge_total"] += edge_score

        report = {}

        for grade, data in validation.items():

            sample_size = data["sample_size"]

            if sample_size > 0:

                win_rate = round(
                    (
                        data["wins"]
                        / sample_size
                    ) * 100,
                    2
                )

                avg_edge = round(
                    data["edge_total"]
                    / sample_size,
                    2
                )

            else:

                win_rate = 0
                avg_edge = 0

            report[grade] = {
                "sample_size": sample_size,
                "win_rate": win_rate,
                "average_edge_score": avg_edge
            }

        return report






