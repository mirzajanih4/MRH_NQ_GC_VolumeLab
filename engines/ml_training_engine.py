import csv


class MLTrainingEngine:

    def __init__(self, dataset_path):
        self.dataset_path = dataset_path

    def load_dataset(self):

        records = []

        with open(
                self.dataset_path,
                mode="r"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                records.append(row)

        return records

    def build_training_summary(self):

        summary = {
            "dataset_path": self.dataset_path,
            "engine_ready": True,
            "training_started": False,
            "model_type": "NOT_SELECTED"
        }

        return summary

    def build_training_statistics(self):

        records = self.load_dataset()

        wins = 0
        losses = 0
        skipped = 0

        for record in records:

            label = record["trade_label"]

            if label == "WIN":
                wins += 1

            elif label == "LOSS":
                losses += 1

            elif label == "SKIPPED":
                skipped += 1

        return {
            "total_records": len(records),
            "wins": wins,
            "losses": losses,
            "skipped": skipped
        }

    def build_label_distribution(self):

        stats = self.build_training_statistics()

        total = stats["total_records"]

        if total == 0:
            return {}

        return {
            "WIN_PERCENT": round(
                stats["wins"] * 100 / total,
                2
            ),

            "LOSS_PERCENT": round(
                stats["losses"] * 100 / total,
                2
            ),

            "SKIPPED_PERCENT": round(
                stats["skipped"] * 100 / total,
                2
            )
        }

    def build_tradable_dataset_stats(self):

        records = self.load_dataset()

        tradable = [r for r in records if r["trade_label"] in ("WIN", "LOSS")]

        total_tradable = len(tradable)

        wins = sum(1 for r in tradable if r["trade_label"] == "WIN")
        losses = sum(1 for r in tradable if r["trade_label"] == "LOSS")

        return {
            "total_tradable": total_tradable,
            "wins": wins,
            "losses": losses
        }

    def calculate_tradable_win_rate(self):

        stats = self.build_tradable_dataset_stats()

        total = stats["total_tradable"]

        if total == 0:
            return 0

        return round(
            stats["wins"] * 100 / total,
            2
        )

    def build_dataset_balance_report(self):

        stats = self.build_tradable_dataset_stats()

        wins = stats["wins"]
        losses = stats["losses"]

        difference = abs(
            wins - losses
        )

        balanced = (
            difference <= 5
        )

        return {
            "wins": wins,
            "losses": losses,
            "difference": difference,
            "balanced": balanced
        }

    def prepare_training_dataset(self, dataset_rows):
        """
        Prepare dataset for future ML models.
        """

        prepared_rows = []

        for row in dataset_rows:

            if row.get("trade_label") == "SKIPPED":
                continue

            prepared_rows.append(row)

        return prepared_rows

    def build_prepared_training_stats(self):

        records = self.load_dataset()

        prepared_rows = self.prepare_training_dataset(records)

        wins = sum(
            1 for row in prepared_rows
            if row.get("trade_label") == "WIN"
        )

        losses = sum(
            1 for row in prepared_rows
            if row.get("trade_label") == "LOSS"
        )

        return {
            "prepared_total": len(prepared_rows),
            "prepared_wins": wins,
            "prepared_losses": losses,
            "skipped_removed": len(records) - len(prepared_rows)
        }

    def get_training_feature_columns(self):

        return [
            "setup_grade",
            "setup_type",
            "confidence_score",
            "trade_quality",
            "probability_score",
            "weighted_probability_score",
            "probability_grade",
            "footprint_score",
            "stack_strength"
        ]

    def get_training_target_column(self):

        return "trade_label"

    def split_train_test_dataset(self, prepared_rows, train_ratio=0.8):

        total_rows = len(prepared_rows)

        split_index = int(
            total_rows * train_ratio
        )

        train_rows = prepared_rows[:split_index]
        test_rows = prepared_rows[split_index:]

        return {
            "train_rows": train_rows,
            "test_rows": test_rows,
            "total_rows": total_rows,
            "train_count": len(train_rows),
            "test_count": len(test_rows),
            "train_ratio": train_ratio
        }

    def build_train_test_split_stats(self):

        records = self.load_dataset()

        prepared_rows = self.prepare_training_dataset(records)

        split_data = self.split_train_test_dataset(prepared_rows)

        return {
            "total_prepared_rows": split_data["total_rows"],
            "train_count": split_data["train_count"],
            "test_count": split_data["test_count"],
            "train_ratio": split_data["train_ratio"]
        }

    def build_train_test_label_balance(self):

        records = self.load_dataset()

        prepared_rows = self.prepare_training_dataset(records)

        split_data = self.split_train_test_dataset(
            prepared_rows
        )

        train_rows = split_data["train_rows"]
        test_rows = split_data["test_rows"]

        train_wins = sum(
            1 for row in train_rows
            if row.get("trade_label") == "WIN"
        )

        train_losses = sum(
            1 for row in train_rows
            if row.get("trade_label") == "LOSS"
        )

        test_wins = sum(
            1 for row in test_rows
            if row.get("trade_label") == "WIN"
        )

        test_losses = sum(
            1 for row in test_rows
            if row.get("trade_label") == "LOSS"
        )

        return {
            "train_wins": train_wins,
            "train_losses": train_losses,
            "test_wins": test_wins,
            "test_losses": test_losses
        }

    def build_split_quality_report(self):

        balance = self.build_train_test_label_balance()

        train_total = (
            balance["train_wins"] +
            balance["train_losses"]
        )

        test_total = (
            balance["test_wins"] +
            balance["test_losses"]
        )

        train_has_both_classes = (
            balance["train_wins"] > 0 and
            balance["train_losses"] > 0
        )

        test_has_both_classes = (
            balance["test_wins"] > 0 and
            balance["test_losses"] > 0
        )

        split_valid = (
            train_has_both_classes and
            test_has_both_classes
        )

        return {
            "train_total": train_total,
            "test_total": test_total,
            "train_has_both_classes": train_has_both_classes,
            "test_has_both_classes": test_has_both_classes,
            "split_valid": split_valid
        }