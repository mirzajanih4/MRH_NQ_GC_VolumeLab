def evaluate_dataset_quality_rule(
        dataset_quality_report
):

    dataset_quality_score = (
        dataset_quality_report.get(
            "dataset_quality_score",
            0
        )
    )

    dataset_quality_status = (
        dataset_quality_report.get(
            "dataset_quality_status",
            "NOT_EVALUATED"
        )
    )

    dataset_quality_pass = (
        dataset_quality_score >= 70
        and dataset_quality_status
        not in (
            "SCENARIO_REPETITION_AUDIT_REQUIRED",
            "INSUFFICIENT_SAMPLE_SIZE",
            "NOT_EVALUATED"
        )
    )

    return {
        "dataset_quality_pass":
            dataset_quality_pass,

        "dataset_quality_rule_score":
            20
            if dataset_quality_pass
            else 0,

        "dataset_quality_rule_reason":
            (
                "DATASET_QUALITY_PASS"
                if dataset_quality_pass
                else "DATASET_QUALITY_FAIL"
            )
    }


def evaluate_confidence_quality_rule(
        confidence_score
):

    confidence_quality_pass = (
        confidence_score >= 70
    )

    return {
        "confidence_quality_pass":
            confidence_quality_pass,

        "confidence_quality_rule_score":
            15
            if confidence_quality_pass
            else 0,

        "confidence_quality_rule_reason":
            (
                "CONFIDENCE_QUALITY_PASS"
                if confidence_quality_pass
                else "CONFIDENCE_QUALITY_FAIL"
            )
    }


def evaluate_virtual_outcome_rule(
        virtual_trade_outcome
):

    virtual_outcome_pass = (
        virtual_trade_outcome
        == "VIRTUAL_WIN"
    )

    return {
        "virtual_outcome_pass":
            virtual_outcome_pass,

        "virtual_outcome_rule_score":
            20
            if virtual_outcome_pass
            else 0,

        "virtual_outcome_rule_reason":
            (
                "VIRTUAL_OUTCOME_PASS"
                if virtual_outcome_pass
                else "VIRTUAL_OUTCOME_FAIL"
            )
    }


def evaluate_historical_reliability_rule(
        historical_win_rate,
        runtime_dataset_ready
):

    historical_reliability_pass = (
        historical_win_rate >= 55.0
        and runtime_dataset_ready
    )

    return {
        "historical_reliability_pass":
            historical_reliability_pass,

        "historical_reliability_rule_score":
            20
            if historical_reliability_pass
            else 0,

        "historical_reliability_rule_reason":
            (
                "HISTORICAL_RELIABILITY_PASS"
                if historical_reliability_pass
                else "HISTORICAL_RELIABILITY_FAIL"
            )
    }


def aggregate_qualification_rules(
        source_rule_result,
        dataset_quality_rule_result,
        confidence_rule_result,
        virtual_outcome_rule_result,
        historical_reliability_rule_result
):

    source_score = (
        source_rule_result.get(
            "score",
            0
        )
    )

    dataset_quality_score = (
        dataset_quality_rule_result.get(
            "dataset_quality_rule_score",
            0
        )
    )

    confidence_quality_score = (
        confidence_rule_result.get(
            "confidence_quality_rule_score",
            0
        )
    )

    virtual_outcome_score = (
        virtual_outcome_rule_result.get(
            "virtual_outcome_rule_score",
            0
        )
    )

    historical_reliability_score = (
        historical_reliability_rule_result.get(
            "historical_reliability_rule_score",
            0
        )
    )

    qualification_score = (
        source_score
        + dataset_quality_score
        + confidence_quality_score
        + virtual_outcome_score
        + historical_reliability_score
    )

    qualified = False

    qualification_reason = (
        "QUALIFICATION_INCOMPLETE"
    )

    return {
        "qualified": qualified,
        "qualification_score":
            qualification_score,
        "qualification_reason":
            qualification_reason
    }