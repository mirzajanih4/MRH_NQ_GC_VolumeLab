class ConfidenceEngine:

    def calculate_confidence(
        self,
        orderflow_score,
        setup_grade,
        volume_node,
        session
    ):

        confidence = 0

        confidence += orderflow_score * 50

        if setup_grade == "A_SETUP":
            confidence += 30

        elif setup_grade == "B_SETUP":
            confidence += 15

        if volume_node == "NEAR_LVN":
            confidence += 10

        if session == "NEW_YORK":
            confidence += 10

        if confidence > 100:
            confidence = 100

        return round(confidence, 2)