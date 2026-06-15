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

    def build_feature_matrix(self):

        records = self.load_dataset()

        prepared_rows = (
            self.prepare_training_dataset(records)
        )

        feature_columns = (
            self.get_training_feature_columns()
        )

        feature_matrix = []

        for row in prepared_rows:

            feature_row = {}

            for column in feature_columns:

                feature_row[column] = row.get(column)

            feature_matrix.append(
                feature_row
            )

        return feature_matrix

    def build_target_vector(self):

        records = self.load_dataset()

        prepared_rows = (
            self.prepare_training_dataset(records)
        )

        target_column = (
            self.get_training_target_column()
        )

        target_vector = []

        for row in prepared_rows:

            target_vector.append(
                row.get(target_column)
            )

        return target_vector

    def build_feature_target_shape_report(self):

        feature_matrix = (
            self.build_feature_matrix()
        )

        target_vector = (
            self.build_target_vector()
        )

        feature_count = 0

        if len(feature_matrix) > 0:
            feature_count = len(
                feature_matrix[0]
            )

        return {
            "samples": len(feature_matrix),
            "targets": len(target_vector),
            "feature_count": feature_count,
            "shape_valid": (
                len(feature_matrix) ==
                len(target_vector)
            )
        }

    def get_numeric_feature_columns(self):

        return [
            "confidence_score",
            "probability_score",
            "weighted_probability_score",
            "footprint_score"
        ]

    def convert_numeric_features(self, feature_row):

        converted_row = dict(
            feature_row
        )

        numeric_columns = (
            self.get_numeric_feature_columns()
        )

        for column in numeric_columns:

            value = converted_row.get(column)

            try:

                converted_row[column] = float(
                    value
                )

            except (
                TypeError,
                ValueError
            ):

                converted_row[column] = 0.0

        return converted_row

    def build_numeric_feature_matrix(self):

        feature_matrix = (
            self.build_feature_matrix()
        )

        numeric_feature_matrix = []

        for row in feature_matrix:

            converted_row = (
                self.convert_numeric_features(row)
            )

            numeric_feature_matrix.append(
                converted_row
            )

        return numeric_feature_matrix

    def get_categorical_feature_columns(self):

        return [
            "setup_grade",
            "setup_type",
            "trade_quality",
            "probability_grade",
            "stack_strength"
        ]

    def get_category_encoding_map(self):

        return {
            "setup_grade": {
                "A_SETUP": 3,
                "B_SETUP": 2,
                "C_SETUP": 1
            },

            "trade_quality": {
                "ELITE_QUALITY": 4,
                "HIGH_QUALITY": 3,
                "MEDIUM_QUALITY": 2,
                "LOW_QUALITY": 1
            },

            "probability_grade": {
                "HIGH_PROBABILITY": 3,
                "MEDIUM_PROBABILITY": 2,
                "LOW_PROBABILITY": 1
            },

            "stack_strength": {
                "HIGH": 3,
                "MEDIUM": 2,
                "LOW": 1,
                "NONE": 0
            }
        }

    def encode_categorical_features(self, feature_row):

        encoded_row = dict(
            feature_row
        )

        encoding_map = (
            self.get_category_encoding_map()
        )

        for column, mapping in encoding_map.items():

            value = encoded_row.get(column)

            encoded_row[column] = (
                mapping.get(value, 0)
            )

        return encoded_row

    def build_encoded_feature_matrix(self):

        numeric_feature_matrix = (
            self.build_numeric_feature_matrix()
        )

        encoded_feature_matrix = []

        for row in numeric_feature_matrix:

            encoded_row = (
                self.encode_categorical_features(row)
            )

            encoded_feature_matrix.append(
                encoded_row
            )

        return encoded_feature_matrix

    def build_encoding_quality_report(self):

        encoded_feature_matrix = (
            self.build_encoded_feature_matrix()
        )

        text_columns = []

        if len(encoded_feature_matrix) > 0:

            sample_row = encoded_feature_matrix[0]

            for column, value in sample_row.items():

                if isinstance(value, str):
                    text_columns.append(column)

        return {
            "total_rows": len(encoded_feature_matrix),
            "text_columns_remaining": text_columns,
            "encoding_valid": (
                text_columns == ["setup_type"]
            )
        }

    def get_target_encoding_map(self):

        return {
            "WIN": 1,
            "LOSS": 0
        }

    def build_encoded_target_vector(self):

        target_vector = (
            self.build_target_vector()
        )

        target_encoding_map = (
            self.get_target_encoding_map()
        )

        encoded_target_vector = []

        for target in target_vector:

            encoded_target_vector.append(
                target_encoding_map.get(target, -1)
            )

        return encoded_target_vector

    def build_encoded_dataset_quality_report(self):

        encoded_feature_matrix = (
            self.build_encoded_feature_matrix()
        )

        encoded_target_vector = (
            self.build_encoded_target_vector()
        )

        encoding_report = (
            self.build_encoding_quality_report()
        )

        invalid_targets = sum(
            1 for target in encoded_target_vector
            if target == -1
        )

        return {
            "feature_rows": len(encoded_feature_matrix),
            "target_rows": len(encoded_target_vector),
            "shape_valid": (
                len(encoded_feature_matrix) ==
                len(encoded_target_vector)
            ),
            "text_columns_remaining": encoding_report["text_columns_remaining"],
            "invalid_targets": invalid_targets,
            "ml_ready_for_training": (
                len(encoded_feature_matrix) ==
                len(encoded_target_vector) and
                invalid_targets == 0 and
                encoding_report["encoding_valid"] is True
            )
        }

    def get_setup_type_categories(self):

        return [
            "BREAKOUT_SETUP",
            "BREAKDOWN_SETUP",
            "ABSORPTION_SETUP",
            "BALANCED_MARKET"
        ]

    def encode_setup_type(self, feature_row):

        encoded_row = dict(
            feature_row
        )

        setup_type = encoded_row.get(
            "setup_type"
        )

        categories = (
            self.get_setup_type_categories()
        )

        del encoded_row["setup_type"]

        for category in categories:

            column_name = (
                "setup_type_" + category
            )

            encoded_row[column_name] = int(
                setup_type == category
            )

        return encoded_row

    def build_final_encoded_feature_matrix(self):

        encoded_feature_matrix = (
            self.build_encoded_feature_matrix()
        )

        final_feature_matrix = []

        for row in encoded_feature_matrix:

            final_row = (
                self.encode_setup_type(row)
            )

            final_feature_matrix.append(
                final_row
            )

        return final_feature_matrix

    def build_final_feature_matrix_quality_report(self):

        final_feature_matrix = (
            self.build_final_encoded_feature_matrix()
        )

        text_columns = []

        feature_count = 0

        if len(final_feature_matrix) > 0:

            sample_row = final_feature_matrix[0]

            feature_count = len(
                sample_row
            )

            for column, value in sample_row.items():

                if isinstance(value, str):

                    text_columns.append(
                        column
                    )

        return {
            "rows": len(final_feature_matrix),
            "feature_count": feature_count,
            "text_columns_remaining": text_columns,
            "fully_numeric": (
                len(text_columns) == 0
            )
        }

    def build_majority_class_baseline(self):

        encoded_targets = (
            self.build_encoded_target_vector()
        )

        wins = sum(
            1 for target in encoded_targets
            if target == 1
        )

        losses = sum(
            1 for target in encoded_targets
            if target == 0
        )

        if wins >= losses:
            majority_class = 1
            majority_label = "WIN"
        else:
            majority_class = 0
            majority_label = "LOSS"

        return {
            "wins": wins,
            "losses": losses,
            "majority_class": majority_class,
            "majority_label": majority_label
        }

    def build_baseline_accuracy_report(self):

        encoded_targets = (
            self.build_encoded_target_vector()
        )

        baseline = (
            self.build_majority_class_baseline()
        )

        majority_class = baseline["majority_class"]

        correct_predictions = sum(
            1 for target in encoded_targets
            if target == majority_class
        )

        total_predictions = len(
            encoded_targets
        )

        accuracy = 0

        if total_predictions > 0:

            accuracy = round(
                correct_predictions * 100 / total_predictions,
                2
            )

        return {
            "baseline_model": "MAJORITY_CLASS",
            "predicted_class": majority_class,
            "predicted_label": baseline["majority_label"],
            "correct_predictions": correct_predictions,
            "total_predictions": total_predictions,
            "accuracy_percent": accuracy
        }

    def build_baseline_quality_report(self):

        baseline_accuracy = (
            self.build_baseline_accuracy_report()
        )

        encoded_dataset_report = (
            self.build_encoded_dataset_quality_report()
        )

        return {
            "baseline_accuracy_percent":
                baseline_accuracy["accuracy_percent"],

            "dataset_ready":
                encoded_dataset_report["ml_ready_for_training"],

            "baseline_ready":
                baseline_accuracy["total_predictions"] > 0,

            "comparison_ready":
                (
                    encoded_dataset_report["ml_ready_for_training"]
                    and
                    baseline_accuracy["total_predictions"] > 0
                )
        }

    def predict_with_rule_based_model(self, feature_row):

        score = 0

        if feature_row.get("setup_grade", 0) >= 3:
            score += 2

        if feature_row.get("confidence_score", 0) >= 80:
            score += 2

        if feature_row.get("trade_quality", 0) >= 3:
            score += 2

        if feature_row.get("probability_score", 0) >= 50:
            score += 1

        if feature_row.get("weighted_probability_score", 0) >= 50:
            score += 1

        if feature_row.get("probability_grade", 0) >= 2:
            score += 1

        if feature_row.get("footprint_score", 0) >= 1.0:
            score += 1

        if feature_row.get("stack_strength", 0) >= 2:
            score += 1

        if score >= 6:
            return 1

        return 0

    def build_rule_based_predictions(self):

        final_feature_matrix = (
            self.build_final_encoded_feature_matrix()
        )

        predictions = []

        for feature_row in final_feature_matrix:

            prediction = (
                self.predict_with_rule_based_model(feature_row)
            )

            predictions.append(
                prediction
            )

        return predictions

    def build_rule_based_accuracy_report(self):

        predictions = (
            self.build_rule_based_predictions()
        )

        actual_targets = (
            self.build_encoded_target_vector()
        )

        correct_predictions = 0

        for prediction, actual in zip(
                predictions,
                actual_targets
        ):

            if prediction == actual:

                correct_predictions += 1

        total_predictions = len(
            actual_targets
        )

        accuracy = 0

        if total_predictions > 0:

            accuracy = round(
                correct_predictions * 100 /
                total_predictions,
                2
            )

        baseline_accuracy = (
            self.build_baseline_accuracy_report()
        )

        return {
            "model": "RULE_BASED",
            "correct_predictions": correct_predictions,
            "total_predictions": total_predictions,
            "accuracy_percent": accuracy,
            "baseline_accuracy":
                baseline_accuracy["accuracy_percent"],
            "beats_baseline":
                accuracy >
                baseline_accuracy["accuracy_percent"]
        }

    def build_leakage_risk_report(self):

        rule_based_report = (
            self.build_rule_based_accuracy_report()
        )

        accuracy = (
            rule_based_report["accuracy_percent"]
        )

        leakage_risk = (
            accuracy >= 90
        )

        return {
            "rule_based_accuracy": accuracy,
            "leakage_risk": leakage_risk,
            "requires_review": leakage_risk,
            "risk_reason":
                "Accuracy unusually high"
                if leakage_risk
                else
                "No obvious leakage risk"
        }

    def get_safe_rule_based_features(self):

        return [
            "setup_grade",
            "confidence_score",
            "footprint_score",
            "stack_strength"
        ]

    def predict_with_safe_rule_based_model(self, feature_row):

        score = 0

        if feature_row.get("setup_grade", 0) >= 3:
            score += 2

        if feature_row.get("confidence_score", 0) >= 80:
            score += 2

        if feature_row.get("footprint_score", 0) >= 1.0:
            score += 1

        if feature_row.get("stack_strength", 0) >= 2:
            score += 1

        if score >= 4:
            return 1

        return 0

    def build_safe_rule_based_predictions(self):

        final_feature_matrix = (
            self.build_final_encoded_feature_matrix()
        )

        predictions = []

        for feature_row in final_feature_matrix:

            prediction = (
                self.predict_with_safe_rule_based_model(feature_row)
            )

            predictions.append(
                prediction
            )

        return predictions

    def build_safe_rule_based_accuracy_report(self):

        predictions = (
            self.build_safe_rule_based_predictions()
        )

        actual_targets = (
            self.build_encoded_target_vector()
        )

        correct_predictions = 0

        for prediction, actual in zip(
                predictions,
                actual_targets
        ):

            if prediction == actual:

                correct_predictions += 1

        total_predictions = len(
            actual_targets
        )

        accuracy = 0

        if total_predictions > 0:

            accuracy = round(
                correct_predictions * 100 /
                total_predictions,
                2
            )

        baseline_accuracy = (
            self.build_baseline_accuracy_report()
        )

        return {
            "model": "SAFE_RULE_BASED",
            "correct_predictions": correct_predictions,
            "total_predictions": total_predictions,
            "accuracy_percent": accuracy,
            "baseline_accuracy":
                baseline_accuracy["accuracy_percent"],
            "beats_baseline":
                accuracy >
                baseline_accuracy["accuracy_percent"]
        }

    def build_feature_target_audit(self):

        records = self.load_dataset()

        prepared_rows = (
            self.prepare_training_dataset(records)
        )

        audit = {}

        feature_columns = (
            self.get_training_feature_columns()
        )

        for feature in feature_columns:

            audit[feature] = {
                "WIN": {},
                "LOSS": {}
            }

        for row in prepared_rows:

            label = row.get(
                "trade_label"
            )

            if label not in (
                    "WIN",
                    "LOSS"
            ):
                continue

            for feature in feature_columns:

                value = row.get(feature)

                current = (
                    audit[feature][label]
                    .get(value, 0)
                )

                audit[feature][label][value] = (
                    current + 1
                )

        return audit

    def build_feature_leakage_ranking(self):

        audit = self.build_feature_target_audit()

        ranking = []

        for feature, values in audit.items():

            win_total = sum(
                values["WIN"].values()
            )

            loss_total = sum(
                values["LOSS"].values()
            )

            strongest_gap = 0

            all_values = set(
                list(values["WIN"].keys()) +
                list(values["LOSS"].keys())
            )

            for value in all_values:

                win_count = (
                    values["WIN"].get(value, 0)
                )

                loss_count = (
                    values["LOSS"].get(value, 0)
                )

                gap = abs(
                    win_count - loss_count
                )

                if gap > strongest_gap:
                    strongest_gap = gap

            ranking.append({
                "feature": feature,
                "gap_score": strongest_gap,
                "win_total": win_total,
                "loss_total": loss_total
            })

        ranking.sort(
            key=lambda x: x["gap_score"],
            reverse=True
        )

        return ranking

    def build_normalized_leakage_ranking(self):

        audit = self.build_feature_target_audit()

        ranking = []

        for feature, values in audit.items():

            max_bias = 0

            all_values = set(
                list(values["WIN"].keys()) +
                list(values["LOSS"].keys())
            )

            for value in all_values:

                win_count = values["WIN"].get(value, 0)
                loss_count = values["LOSS"].get(value, 0)

                total = win_count + loss_count

                if total == 0:
                    continue

                bias = abs(
                    win_count - loss_count
                ) / total

                if bias > max_bias:
                    max_bias = bias

            ranking.append({
                "feature": feature,
                "normalized_bias": round(max_bias, 3)
            })

        ranking.sort(
            key=lambda x: x["normalized_bias"],
            reverse=True
        )

        return ranking

    def bucket_numeric_value(self, value, bucket_size=10):

        try:
            numeric_value = float(value)

        except (
            TypeError,
            ValueError
        ):
            return "UNKNOWN"

        bucket_start = int(
            numeric_value // bucket_size
        ) * bucket_size

        bucket_end = bucket_start + bucket_size

        return f"{bucket_start}-{bucket_end}"

    def build_bucketed_numeric_leakage_audit(self):

        records = self.load_dataset()

        prepared_rows = (
            self.prepare_training_dataset(records)
        )

        numeric_features = [
            "confidence_score",
            "probability_score",
            "weighted_probability_score",
            "footprint_score"
        ]

        audit = {}

        for feature in numeric_features:

            audit[feature] = {
                "WIN": {},
                "LOSS": {}
            }

        for row in prepared_rows:

            label = row.get("trade_label")

            if label not in ("WIN", "LOSS"):
                continue

            for feature in numeric_features:

                bucket = self.bucket_numeric_value(
                    row.get(feature)
                )

                current = (
                    audit[feature][label]
                    .get(bucket, 0)
                )

                audit[feature][label][bucket] = (
                    current + 1
                )

        return audit

    def build_feature_dependency_audit(self):

        records = self.load_dataset()

        prepared_rows = (
            self.prepare_training_dataset(records)
        )

        dependencies = {}

        feature_pairs = [
            ("confidence_score", "trade_quality"),
            ("trade_quality", "probability_grade"),
            ("probability_score", "probability_grade"),
            ("weighted_probability_score", "probability_grade"),
            ("setup_grade", "trade_quality")
        ]

        for left_feature, right_feature in feature_pairs:

            pair_key = (
                f"{left_feature} -> {right_feature}"
            )

            dependencies[pair_key] = {}

            for row in prepared_rows:

                left_value = row.get(left_feature)
                right_value = row.get(right_feature)

                key = (
                    str(left_value),
                    str(right_value)
                )

                dependencies[pair_key][key] = (
                    dependencies[pair_key]
                    .get(key, 0) + 1
                )

        return dependencies

    def build_core_feature_audit(self):

        records = self.load_dataset()

        prepared_rows = (
            self.prepare_training_dataset(records)
        )

        audit = {}

        core_features = [
            "setup_type",
            "setup_grade",
            "confidence_score",
            "footprint_score",
            "stack_strength"
        ]

        for feature in core_features:

            audit[feature] = {
                "WIN": {},
                "LOSS": {}
            }

        for row in prepared_rows:

            label = row.get("trade_label")

            if label not in (
                    "WIN",
                    "LOSS"
            ):
                continue

            for feature in core_features:

                value = str(
                    row.get(feature)
                )

                current = (
                    audit[feature][label]
                    .get(value, 0)
                )

                audit[feature][label][value] = (
                    current + 1
                )

        return audit

    def build_dead_feature_audit(self):

        records = self.load_dataset()

        prepared_rows = (
            self.prepare_training_dataset(records)
        )

        if not prepared_rows:
            return {}

        feature_names = list(
            prepared_rows[0].keys()
        )

        audit = {}

        for feature in feature_names:

            unique_values = set()

            for row in prepared_rows:

                unique_values.add(
                    str(row.get(feature))
                )

            audit[feature] = {
                "unique_count": len(unique_values),
                "values": sorted(
                    list(unique_values)
                )[:10]
            }

        return audit

    def get_core_training_feature_columns(self):

        return [
            "setup_type",
            "setup_grade",
            "confidence_score"
        ]

    def build_core_feature_matrix(self):

        records = self.load_dataset()

        prepared_rows = (
            self.prepare_training_dataset(records)
        )

        core_columns = (
            self.get_core_training_feature_columns()
        )

        core_matrix = []

        for row in prepared_rows:

            feature_row = {}

            for column in core_columns:

                feature_row[column] = row.get(column)

            core_matrix.append(feature_row)

        return core_matrix

    def build_core_feature_matrix_report(self):

        core_matrix = (
            self.build_core_feature_matrix()
        )

        feature_count = 0

        if len(core_matrix) > 0:
            feature_count = len(core_matrix[0])

        return {
            "rows": len(core_matrix),
            "feature_count": feature_count,
            "features": self.get_core_training_feature_columns()
        }

    def encode_core_feature_row(self, feature_row):

        encoded_row = {}

        setup_type = feature_row.get("setup_type")
        setup_grade = feature_row.get("setup_grade")

        encoded_row["setup_type_BREAKOUT_SETUP"] = int(
            setup_type == "BREAKOUT_SETUP"
        )

        encoded_row["setup_type_BREAKDOWN_SETUP"] = int(
            setup_type == "BREAKDOWN_SETUP"
        )

        encoded_row["setup_type_ABSORPTION_SETUP"] = int(
            setup_type == "ABSORPTION_SETUP"
        )

        encoded_row["setup_type_BALANCED_MARKET"] = int(
            setup_type == "BALANCED_MARKET"
        )

        encoded_row["setup_grade"] = {
            "A_SETUP": 2,
            "B_SETUP": 1,
            "C_SETUP": 0
        }.get(setup_grade, 0)

        try:
            encoded_row["confidence_score"] = float(
                feature_row.get("confidence_score")
            )

        except (
            TypeError,
            ValueError
        ):
            encoded_row["confidence_score"] = 0.0

        return encoded_row

    def build_encoded_core_feature_matrix(self):

        core_matrix = (
            self.build_core_feature_matrix()
        )

        encoded_matrix = []

        for row in core_matrix:

            encoded_matrix.append(
                self.encode_core_feature_row(row)
            )

        return encoded_matrix

    def build_encoded_core_feature_matrix_report(self):

        encoded_matrix = (
            self.build_encoded_core_feature_matrix()
        )

        text_columns = []

        feature_count = 0

        if len(encoded_matrix) > 0:

            feature_count = len(
                encoded_matrix[0]
            )

            for column, value in encoded_matrix[0].items():

                if isinstance(value, str):
                    text_columns.append(column)

        return {
            "rows": len(encoded_matrix),
            "feature_count": feature_count,
            "text_columns": text_columns,
            "fully_numeric": len(text_columns) == 0
        }

    def build_core_training_target_vector(self):

        return self.build_encoded_target_vector()

    def build_core_training_shape_report(self):

        encoded_matrix = (
            self.build_encoded_core_feature_matrix()
        )

        target_vector = (
            self.build_core_training_target_vector()
        )

        return {
            "feature_rows": len(encoded_matrix),
            "target_rows": len(target_vector),
            "shape_valid": len(encoded_matrix) == len(target_vector)
        }

    def predict_with_core_rule_based_model(self, feature_row):

        score = 0

        if feature_row.get("setup_grade", 0) >= 2:
            score += 1

        if feature_row.get("confidence_score", 0) >= 90:
            score += 2

        if feature_row.get("setup_type_BREAKOUT_SETUP", 0) == 1:
            score += 1

        if feature_row.get("setup_type_BREAKDOWN_SETUP", 0) == 1:
            score += 1

        if score >= 3:
            return 1

        return 0

    def build_core_rule_based_predictions(self):

        encoded_matrix = (
            self.build_encoded_core_feature_matrix()
        )

        predictions = []

        for feature_row in encoded_matrix:

            predictions.append(
                self.predict_with_core_rule_based_model(
                    feature_row
                )
            )

        return predictions

    def build_core_rule_based_accuracy_report(self):

        predictions = (
            self.build_core_rule_based_predictions()
        )

        actual_targets = (
            self.build_core_training_target_vector()
        )

        correct_predictions = 0

        for prediction, actual in zip(
                predictions,
                actual_targets
        ):

            if prediction == actual:
                correct_predictions += 1

        total_predictions = len(actual_targets)

        accuracy = 0

        if total_predictions > 0:
            accuracy = round(
                correct_predictions * 100 / total_predictions,
                2
            )

        baseline_accuracy = (
            self.build_baseline_accuracy_report()
        )

        return {
            "model": "CORE_RULE_BASED",
            "correct_predictions": correct_predictions,
            "total_predictions": total_predictions,
            "accuracy_percent": accuracy,
            "baseline_accuracy": baseline_accuracy["accuracy_percent"],
            "beats_baseline": accuracy > baseline_accuracy["accuracy_percent"]
        }

    def build_core_training_summary_report(self):

        matrix_report = (
            self.build_encoded_core_feature_matrix_report()
        )

        shape_report = (
            self.build_core_training_shape_report()
        )

        accuracy_report = (
            self.build_core_rule_based_accuracy_report()
        )

        return {
            "feature_set": "CORE_FEATURE_SET_V1",
            "features": self.get_core_training_feature_columns(),
            "matrix_rows": matrix_report["rows"],
            "feature_count": matrix_report["feature_count"],
            "fully_numeric": matrix_report["fully_numeric"],
            "shape_valid": shape_report["shape_valid"],
            "core_rule_accuracy": accuracy_report["accuracy_percent"],
            "baseline_accuracy": accuracy_report["baseline_accuracy"],
            "beats_baseline": accuracy_report["beats_baseline"]
        }