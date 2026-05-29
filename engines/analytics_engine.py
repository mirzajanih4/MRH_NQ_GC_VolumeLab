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