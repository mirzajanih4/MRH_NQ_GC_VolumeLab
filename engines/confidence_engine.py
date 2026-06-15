class ConfidenceEngine:

    def calculate_confidence(
            self,
            orderflow_score,
            setup_grade,
            volume_node,
            session,
            footprint_score,
            stack_strength
    ):

        confidence = 0

        confidence += orderflow_score * 50

        if setup_grade == "A_SETUP":
            confidence += 20

        elif setup_grade == "B_SETUP":
            confidence += 10

        if volume_node == "NEAR_LVN":
            confidence += 10

        if session == "NEW_YORK":
            confidence += 10

        confidence += footprint_score * 10
        if stack_strength == "LOW":
            confidence += 2

        elif stack_strength == "MEDIUM":
            confidence += 5

        elif stack_strength == "HIGH":
            confidence += 10
        if confidence > 100:
            confidence = 100

        return round(confidence, 2)