from engines.volume_engine import VolumeEngine
from engines.orderflow_engine import OrderflowEngine
from engines.context_engine import ContextEngine
from engines.risk_engine import RiskEngine
from engines.replay_engine import ReplayEngine

from strategies.nq_strategy import NQStrategy

from data.sample_ticks import (
    get_sample_ticks,
    get_sample_sell_ticks,
    get_sample_no_trade_ticks,
    get_sample_buy_lvn_ticks,
    get_sample_absorption_ticks,
    get_sample_sweep_absorption_ticks,
    get_sample_sell_lvn_ticks,
    get_sample_weak_footprint_ticks,
    get_sample_buy_stack_ticks,
    get_sample_sell_stack_ticks
)

import csv
from data.csv_loader import load_ticks_from_csv
from engines.session_engine import SessionEngine
from data.dataset_writer import save_dataset_record
from engines.analytics_engine import AnalyticsEngine
from engines.probability_engine import ProbabilityEngine
from engines.confidence_engine import ConfidenceEngine
from engines.footprint_engine import FootprintEngine
from engines.ml_training_engine import MLTrainingEngine
# ==========================================
# STEP126 Runtime / Research Mode
# ==========================================

RUNTIME_MODE = "RESEARCH"

# Available modes:
# "RUNTIME"
# "RESEARCH"
# "TRAINING"

SHOW_RUNTIME_DETAILS = True

def build_runtime_readiness_report():

    runtime_ready = (
        RUNTIME_MODE == "RUNTIME"
        and not SHOW_RUNTIME_DETAILS
    )

    runtime_status = (
        "PASS"
        if runtime_ready
        else "NOT_READY"
    )

    return {
        "step": "STEP128",
        "runtime_mode": RUNTIME_MODE,
        "show_runtime_details": SHOW_RUNTIME_DETAILS,

        "research_reports_enabled": (
            RUNTIME_MODE in (
                "RESEARCH",
                "TRAINING"
            )
        ),

        "runtime_details_enabled": SHOW_RUNTIME_DETAILS,

        "demo_runtime_candidate": runtime_ready,

        "runtime_ready": runtime_ready,

        "runtime_status": runtime_status
    }


def build_dataset_quality_report(analytics_engine):

    label_counts = analytics_engine.count_by_field(
        "trade_label"
    )

    scenario_counts = analytics_engine.count_by_field(
        "scenario"
    )

    total_records = sum(
        label_counts.values()
    )

    tradable_records = (
        label_counts.get("WIN", 0)
        + label_counts.get("LOSS", 0)
    )

    target_records = 350

    sample_size_progress = round(
        min(
            tradable_records / target_records,
            1.0
        ) * 100,
        2
    )

    raw_sample_size_ready = (
        tradable_records >= target_records
    )

    unique_scenarios = len(
        scenario_counts
    )

    max_scenario_repetition = (
        max(scenario_counts.values())
        if scenario_counts
        else 0
    )

    scenario_repetition_risk = (
        max_scenario_repetition > 1
    )

    if scenario_repetition_risk:
        dataset_quality_status = (
            "SCENARIO_REPETITION_AUDIT_REQUIRED"
        )

    elif raw_sample_size_ready:
        dataset_quality_status = (
            "RAW_SAMPLE_SIZE_READY"
        )

    else:
        dataset_quality_status = (
            "INSUFFICIENT_SAMPLE_SIZE"
        )

    if scenario_repetition_risk:
        dataset_quality_score = 50.0

    else:
        dataset_quality_score = sample_size_progress

    setup_type_count = len(
        analytics_engine.count_by_field(
            "setup_type"
        )
    )

    session_count = len(
        analytics_engine.count_by_field(
            "session"
        )
    )

    market_phase_count = len(
        analytics_engine.count_by_field(
            "market_phase"
        )
    )

    scenario_distribution = (
        analytics_engine.count_by_field(
            "scenario"
        )
    )

    scenario_counts_list = list(
        scenario_distribution.values()
    )

    scenario_balance_pass = (
        len(set(scenario_counts_list)) == 1
        if scenario_counts_list
        else False
    )

    scenario_independence_pass = (
            max_scenario_repetition == 1
    )

    runtime_dataset_separation_required = (
            scenario_balance_pass
            and not scenario_independence_pass
    )
    runtime_dataset_ready = (
            scenario_independence_pass
            and raw_sample_size_ready
    )

    runtime_dataset_status = (
        "READY"
        if runtime_dataset_ready
        else "NOT_READY"
    )

    research_dataset_only = (
        not runtime_dataset_ready
    )

    dataset_training_permission = (
        "RESEARCH_ONLY"
        if research_dataset_only
        else "RUNTIME_ALLOWED"
    )

    return {
        "step": "STEP129",
        "total_records": total_records,
        "tradable_records": tradable_records,
        "target_records": target_records,
        "sample_size_progress_percent":
            sample_size_progress,
        "raw_sample_size_ready":
            raw_sample_size_ready,
        "unique_scenarios":
            unique_scenarios,
        "max_scenario_repetition":
            max_scenario_repetition,
        "scenario_distribution":
            scenario_distribution,
        "scenario_balance_pass":
            scenario_balance_pass,

        "scenario_independence_pass":
            scenario_independence_pass,

        "runtime_dataset_separation_required":
            runtime_dataset_separation_required,
        "runtime_dataset_ready":
            runtime_dataset_ready,

        "runtime_dataset_status":
            runtime_dataset_status,

        "research_dataset_only":
            research_dataset_only,

        "dataset_training_permission":
            dataset_training_permission,

        "scenario_repetition_risk":
            scenario_repetition_risk,
        "setup_type_count":
            setup_type_count,
        "session_count":
            session_count,
        "market_phase_count":
            market_phase_count,
        "dataset_quality_score":
            dataset_quality_score,
        "dataset_quality_status":
            dataset_quality_status
    }

def classify_dataset_record_source(scenario):

    runtime_candidate = False

    dataset_record_class = "RESEARCH_RECORD"

    dataset_record_reason = (
        "SYNTHETIC_OR_REPEATED_SCENARIO"
    )

    return {
        "scenario": scenario,
        "runtime_candidate": runtime_candidate,
        "dataset_record_class":
            dataset_record_class,
        "dataset_record_reason":
            dataset_record_reason
    }

def qualify_runtime_candidate(record):

    source_independence_pass = (
        record.get(
            "dataset_record_class"
        ) != "RESEARCH_RECORD"
        and record.get(
            "dataset_record_reason"
        ) != "SYNTHETIC_OR_REPEATED_SCENARIO"
    )

    if not source_independence_pass:
        return {
            "qualified": False,
            "qualification_score": 0,
            "qualification_reason":
                "SOURCE_NOT_INDEPENDENT"
        }

    return {
        "qualified": False,
        "qualification_score": 25,
        "qualification_reason":
            "SOURCE_INDEPENDENCE_PASS"
    }

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

def aggregate_qualification_rules(
        source_rule_result,
        dataset_quality_rule_result,
        confidence_rule_result
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

    qualification_score = (
        source_score
        + dataset_quality_score
        + confidence_quality_score
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


volume_engine = VolumeEngine()
replay_engine = ReplayEngine(volume_engine)
orderflow_engine = OrderflowEngine(volume_engine)
risk_engine = RiskEngine()
context_engine = ContextEngine(volume_engine)
session_engine = SessionEngine(volume_engine)

nq_strategy = NQStrategy(
    orderflow_engine,
    context_engine,
    session_engine
)


# scenario = "CSV"
scenario = "CSV"
scenario_list = [
    "BUY",
    "SELL",
    "NO_TRADE",
    "BUY_LVN",
    "SELL_LVN",
    "ABSORPTION",
    "SWEEP_ABSORPTION",
    "CSV",
    "BUY_FAILED",
    "SELL_FAILED",
    "BUY_WEAK_WIN",
    "SELL_WEAK_WIN",
    "BREAKOUT_LOSS",
    "BREAKDOWN_WIN",
    "BUY_B_WIN",
    "SELL_B_WIN",
    "BUY_A_LOSS",
    "SELL_A_LOSS",
    "WEAK_FOOTPRINT",
    "BUY_STACK",
    "SELL_STACK",
]



def get_ticks_by_scenario(scenario):

    if scenario == "BUY":
        return get_sample_ticks()

    elif scenario == "SELL":
        return get_sample_sell_ticks()

    elif scenario == "NO_TRADE":
        return get_sample_no_trade_ticks()

    elif scenario == "BUY_LVN":
        return get_sample_buy_lvn_ticks()

    elif scenario == "ABSORPTION":
        return get_sample_absorption_ticks()

    elif scenario == "SWEEP_ABSORPTION":
        return get_sample_sweep_absorption_ticks()
    elif scenario == "SELL_LVN":
        return get_sample_sell_lvn_ticks()
    elif scenario == "CSV":
        return load_ticks_from_csv("data/sample_ticks.csv")

    elif scenario == "BUY_FAILED":
        return get_sample_ticks()

    elif scenario == "SELL_FAILED":
        return get_sample_sell_ticks()

    elif scenario == "BUY_WEAK_WIN":
        return get_sample_buy_lvn_ticks()

    elif scenario == "SELL_WEAK_WIN":
        return get_sample_sell_lvn_ticks()

    elif scenario == "BREAKOUT_LOSS":
        return get_sample_ticks()

    elif scenario == "BREAKDOWN_WIN":
        return get_sample_sell_lvn_ticks()

    elif scenario == "BUY_B_WIN":
        return get_sample_buy_lvn_ticks()

    elif scenario == "SELL_B_WIN":
        return get_sample_sell_lvn_ticks()

    elif scenario == "BUY_A_LOSS":

        return get_sample_ticks()

    elif scenario == "SELL_A_LOSS":
        return get_sample_sell_ticks()
    elif scenario == "WEAK_FOOTPRINT":
        return get_sample_weak_footprint_ticks()

    elif scenario == "BUY_STACK":
        return get_sample_buy_stack_ticks()

    elif scenario == "SELL_STACK":
        return get_sample_sell_stack_ticks()
    else:
        return []


def print_footprint_decision_alignment_audit(
        scenario,
        footprint_data,
        strategy_decision,
        final_signal,
        strategy_reason,
        risk_reason,
        orderflow_score,
        required_score
):

    print("----- STEP117 Footprint Decision Alignment Audit -----")
    print(f"Scenario: {scenario}")
    print(f"Stack Direction: {footprint_data['stack_direction']}")
    print(f"Stack Strength: {footprint_data['stack_strength']}")
    print(f"Footprint Score: {footprint_data['footprint_score']}")
    print(f"Strategy Decision: {strategy_decision}")
    print(f"Final Signal: {final_signal}")
    print(f"Strategy Block Reason: {strategy_reason}")
    print(f"Risk Block Reason: {risk_reason}")
    print(f"Orderflow Score: {orderflow_score}")
    print(f"Required Score: {required_score}")

    strong_footprint = (
            footprint_data["stack_strength"] in ("MEDIUM", "HIGH")
            or footprint_data["footprint_score"] >= 1.0
    )

    hvn_override_candidate = (
            strategy_reason == "HVN_ZONE"
            and footprint_data["footprint_score"] >= 1.5
            and footprint_data["stack_strength"] in (
                "MEDIUM",
                "HIGH"
            )
            and orderflow_score >= 1.0
    )

    hvn_context = "NOT_HVN"

    if context_engine.detect_volume_node() == "NEAR_HVN":

        if (
                footprint_data["footprint_score"] >= 1.5
                and footprint_data["stack_strength"] in (
                    "MEDIUM",
                    "HIGH"
                )
        ):
            hvn_context = "HVN_BREAKOUT_PRESSURE"

        elif footprint_data["absorption_clue"]:
            hvn_context = "HVN_REJECTION_ZONE"

        else:
            hvn_context = "HVN_ACCEPTANCE_ZONE"

    print(
        f"HVN Override Candidate: "
        f"{hvn_override_candidate}"
    )

    if strong_footprint and final_signal == "NO_TRADE":
        print("Alignment Status: STRONG_FOOTPRINT_BUT_NO_TRADE")
    elif strong_footprint:
        print("Alignment Status: STRONG_FOOTPRINT_ALIGNED")
    else:
        print("Alignment Status: WEAK_OR_NEUTRAL_FOOTPRINT")

# ticks = get_ticks_by_scenario(scenario)
def run_scenario(scenario):

    volume_engine = VolumeEngine()
    replay_engine = ReplayEngine(volume_engine)
    orderflow_engine = OrderflowEngine(volume_engine)
    risk_engine = RiskEngine()
    context_engine = ContextEngine(volume_engine)
    session_engine = SessionEngine(volume_engine)
    footprint_engine = FootprintEngine()
    nq_strategy = NQStrategy(
        orderflow_engine,
        context_engine,
        session_engine
    )
    confidence_engine = ConfidenceEngine()
    analytics_engine = AnalyticsEngine("data/replay_results.csv")
    probability_engine = ProbabilityEngine(analytics_engine)

    dataset_quality_report = (
        build_dataset_quality_report(
            analytics_engine
        )
    )

    dataset_quality_rule_result = (
        evaluate_dataset_quality_rule(
            dataset_quality_report
        )
    )



    ticks = get_ticks_by_scenario(scenario)

    replay_engine.replay_ticks(ticks, use_delay=False)
    footprint_data = footprint_engine.analyze_footprint(ticks)

    if SHOW_RUNTIME_DETAILS:
        print("----- Footprint Data -----")
        print(footprint_data)

        volume_engine.show_status()

        orderflow_engine.show_signals()

        nq_strategy.show_decision(risk_engine)

        risk_engine.show_risk_status(
            orderflow_engine.calculate_score(),
            session_engine.detect_session()
        )

    strategy_reason = nq_strategy.get_strategy_block_reason()

    risk_reason = risk_engine.get_block_reason(
        orderflow_engine.calculate_score(),
        session_engine.detect_session()
    )

    print_footprint_decision_alignment_audit(
        scenario,
        footprint_data,
        nq_strategy.evaluate(),
        nq_strategy.get_final_signal(risk_engine),
        strategy_reason,
        risk_reason,
        orderflow_engine.calculate_score(),
        risk_engine.get_required_score(
            session_engine.detect_session()
        )
    )

    if strategy_reason != "NO_STRATEGY_BLOCK":
        main_block_reason = strategy_reason

    elif risk_reason != "NO_BLOCK":
        main_block_reason = risk_reason

    else:
        main_block_reason = "NO_BLOCK"

    hvn_override_candidate = (
            main_block_reason == "HVN_ZONE"
            and footprint_data["footprint_score"] >= 1.5
            and footprint_data["stack_strength"] in (
                "MEDIUM",
                "HIGH"
            )
            and orderflow_engine.calculate_score() >= 1.0
    )
    hvn_context = "NOT_HVN"

    if context_engine.detect_volume_node() == "NEAR_HVN":

        if (
                footprint_data["footprint_score"] >= 1.5
                and footprint_data["stack_strength"] in (
                "MEDIUM",
                "HIGH"
        )
        ):
            hvn_context = "HVN_BREAKOUT_PRESSURE"

        elif footprint_data["absorption_clue"]:
            hvn_context = "HVN_REJECTION_ZONE"

        else:
            hvn_context = "HVN_ACCEPTANCE_ZONE"

    hvn_trade_eligibility = "NOT_ELIGIBLE"

    if (
            hvn_override_candidate
            and hvn_context == "HVN_BREAKOUT_PRESSURE"
    ):
        hvn_trade_eligibility = (
            "CONDITIONAL_ELIGIBLE"
        )


    print("----- Replay Summary -----")
    print(f"Orderflow Score: {orderflow_engine.calculate_score()}")
    print(f"Required Score: {risk_engine.get_required_score(session_engine.detect_session())}")
    print(f"Strategy Block Reason: {strategy_reason}")
    print(f"Main Block Reason: {main_block_reason}")
    print(f"Setup Type: {nq_strategy.classify_setup()}")
    print(f"Setup Grade: {nq_strategy.grade_setup()}")
    print(f"Market Phase: {context_engine.detect_market_phase()}")
    print(f"Price Location: {context_engine.detect_price_location()}")
    print(f"POC Location: {context_engine.detect_poc_location()}")
    print(f"Volume Node: {context_engine.detect_volume_node()}")
    print(f"Session: {session_engine.detect_session()}")
    replay_engine.show_statistics(
        nq_strategy.get_final_signal(risk_engine),
        nq_strategy.classify_setup()
    )
    final_signal = nq_strategy.get_final_signal(risk_engine)
    setup_type = nq_strategy.classify_setup()
    setup_grade = nq_strategy.grade_setup()

    # STEP 101.3E - Counter scenario setup override
    if scenario in (
            "BUY_FAILED",
            "BREAKOUT_LOSS",
            "SELL_FAILED",
            "BUY_A_LOSS",
            "SELL_A_LOSS"
    ):

        setup_type = "BREAKOUT_SETUP"
        setup_grade = "A_SETUP"

    elif scenario == "SELL_FAILED":
        setup_type = "BREAKDOWN_SETUP"
        setup_grade = "A_SETUP"

    elif scenario == "BUY_WEAK_WIN":
        setup_type = "BREAKOUT_SETUP"
        setup_grade = "B_SETUP"

    elif scenario in (
            "SELL_WEAK_WIN",
            "BREAKDOWN_WIN"
    ):
        setup_type = "BREAKDOWN_SETUP"
        setup_grade = "B_SETUP"

    elif scenario == "BUY_B_WIN":
        setup_type = "BREAKOUT_SETUP"
        setup_grade = "B_SETUP"

    elif scenario == "SELL_B_WIN":
        setup_type = "BREAKDOWN_SETUP"
        setup_grade = "B_SETUP"

    elif scenario == "BUY_A_LOSS":
        setup_type = "BREAKOUT_SETUP"
        setup_grade = "A_SETUP"

    elif scenario == "SELL_A_LOSS":
        setup_type = "BREAKDOWN_SETUP"
        setup_grade = "A_SETUP"

    if scenario in (
            "BUY_FAILED",
            "BREAKOUT_LOSS",
            "SELL_FAILED"
    ):
        trade_outcome = "LOSS"

    elif scenario in (
            "SELL_WEAK_WIN",
            "BUY_WEAK_WIN",
            "BREAKDOWN_WIN",
            "BUY_B_WIN",
            "SELL_B_WIN"
        ):

        trade_outcome = "WIN"

    elif final_signal == "NO_TRADE":
        trade_outcome = "SKIPPED"

    elif scenario in (
            "BUY",
            "ABSORPTION"
    ):
        trade_outcome = "WIN"

    elif scenario in (
            "BUY_LVN",
            "SELL",
            "SWEEP_ABSORPTION"
    ):
        trade_outcome = "LOSS"

    elif scenario == "SELL_LVN":
        trade_outcome = "WIN"

    else:
        trade_outcome = "LOSS"

    if trade_outcome == "WIN":
        trade_label = "WIN"

    elif trade_outcome == "LOSS":
        trade_label = "LOSS"

    else:
        trade_label = "SKIPPED"
    confidence_score = confidence_engine.calculate_confidence(
        orderflow_engine.calculate_score(),
        setup_grade,
        context_engine.detect_volume_node(),
        session_engine.detect_session(),
        footprint_data["footprint_score"],
        footprint_data["stack_strength"]
    )

    confidence_rule_result = (
        evaluate_confidence_quality_rule(
            confidence_score
        )
    )

    # STEP 102.2 - Trade quality decorrelation
    if setup_grade == "A_SETUP" and footprint_data["footprint_score"] >= 1.0:
        trade_quality = "HIGH_QUALITY"

    elif setup_grade == "B_SETUP" and footprint_data["footprint_score"] >= 1.0:
        trade_quality = "MEDIUM_QUALITY"

    elif setup_grade == "A_SETUP":
        trade_quality = "MEDIUM_QUALITY"

    else:
        trade_quality = "LOW_QUALITY"
    market_phase = context_engine.detect_market_phase()

    virtual_trade_direction = "NO_VIRTUAL_TRADE"

    if hvn_trade_eligibility == "CONDITIONAL_ELIGIBLE":

        if footprint_data["stack_direction"] == "BUY":
            virtual_trade_direction = "VIRTUAL_LONG"

        elif footprint_data["stack_direction"] == "SELL":
            virtual_trade_direction = "VIRTUAL_SHORT"

    virtual_trade_outcome = "PENDING"

    if virtual_trade_direction == "VIRTUAL_LONG":

        if market_phase == "TREND_UP":
            virtual_trade_outcome = "VIRTUAL_WIN"

        else:
            virtual_trade_outcome = "VIRTUAL_LOSS"

    elif virtual_trade_direction == "VIRTUAL_SHORT":

        if market_phase == "TREND_DOWN":
            virtual_trade_outcome = "VIRTUAL_WIN"

        else:
            virtual_trade_outcome = "VIRTUAL_LOSS"

    virtual_opportunity_score = 0

    if hvn_trade_eligibility == "CONDITIONAL_ELIGIBLE":
        virtual_opportunity_score += 25

    if hvn_context == "HVN_BREAKOUT_PRESSURE":
        virtual_opportunity_score += 25

    if footprint_data["stack_strength"] == "MEDIUM":
        virtual_opportunity_score += 20

    elif footprint_data["stack_strength"] == "HIGH":
        virtual_opportunity_score += 25

    if footprint_data["footprint_score"] >= 1.5:
        virtual_opportunity_score += 25

    elif footprint_data["footprint_score"] >= 1.0:
        virtual_opportunity_score += 15

    virtual_opportunity_grade = "LOW_OPPORTUNITY"

    baseline = 50

    if hvn_trade_eligibility == "CONDITIONAL_ELIGIBLE":
        edge_score = virtual_opportunity_score - baseline

    else:
        edge_score = 0

        if edge_score >= 40:
            edge_label = "STRONG_EDGE"

        elif edge_score >= 20:
            edge_label = "POSITIVE_EDGE"

        elif edge_score >= 0:
            edge_label = "WEAK_EDGE"

        else:
            edge_label = "NO_EDGE"

    if virtual_opportunity_score >= 90:
        virtual_opportunity_grade = "ELITE_OPPORTUNITY"

    elif virtual_opportunity_score >= 70:
        virtual_opportunity_grade = "HIGH_OPPORTUNITY"

    elif virtual_opportunity_score >= 50:
        virtual_opportunity_grade = "MEDIUM_OPPORTUNITY"

    baseline = 50

    if hvn_trade_eligibility == "CONDITIONAL_ELIGIBLE":
        edge_score = virtual_opportunity_score - baseline

    else:
        edge_score = 0

    edge_label = "NO_EDGE"

    if edge_score >= 40:
        edge_label = "STRONG_EDGE"

    elif edge_score >= 20:
        edge_label = "POSITIVE_EDGE"

    elif edge_score >= 0:
        edge_label = "WEAK_EDGE"

    record_source_classification = (
        classify_dataset_record_source(
            scenario
        )
    )

    qualification_result = (
        qualify_runtime_candidate(
            record_source_classification
        )
    )

    source_rule_result = {
        "passed":
            qualification_result[
                "qualified"
            ],

        "score":
            qualification_result[
                "qualification_score"
            ],

        "reason":
            qualification_result[
                "qualification_reason"
            ]
    }

    aggregated_qualification_result = (
        aggregate_qualification_rules(
            source_rule_result,
            dataset_quality_rule_result,
            confidence_rule_result
        )
    )


    dataset_record = {
        "scenario": scenario,
        "runtime_candidate":
            record_source_classification[
                "runtime_candidate"
            ],

        "dataset_record_class":
            record_source_classification[
                "dataset_record_class"
            ],

        "dataset_record_reason":
            record_source_classification[
                "dataset_record_reason"
            ],

        "qualified":
            qualification_result[
                "qualified"
            ],

        "qualification_score":
            qualification_result[
                "qualification_score"
            ],

        "qualification_reason":
            qualification_result[
                "qualification_reason"
            ],

        "aggregated_qualified":
            aggregated_qualification_result[
                "qualified"
            ],

        "aggregated_qualification_score":
            aggregated_qualification_result[
                "qualification_score"
            ],

        "aggregated_qualification_reason":
            aggregated_qualification_result[
                "qualification_reason"
            ],

        "dataset_quality_pass":
            dataset_quality_rule_result[
                "dataset_quality_pass"
            ],

        "dataset_quality_rule_score":
            dataset_quality_rule_result[
                "dataset_quality_rule_score"
            ],

        "dataset_quality_rule_reason":
            dataset_quality_rule_result[
                "dataset_quality_rule_reason"
            ],

        "confidence_quality_pass":
            confidence_rule_result[
                "confidence_quality_pass"
            ],

        "confidence_quality_rule_score":
            confidence_rule_result[
                "confidence_quality_rule_score"
            ],

        "confidence_quality_rule_reason":
            confidence_rule_result[
                "confidence_quality_rule_reason"
            ],

        "final_signal": nq_strategy.get_final_signal(risk_engine),
        "trade_outcome": trade_outcome,
        "trade_label": trade_label,
        "setup_type": setup_type,
        "setup_grade": setup_grade,
        "confidence_score": confidence_score,
        "trade_quality": trade_quality,

        "orderflow_score": orderflow_engine.calculate_score(),
        "required_score": risk_engine.get_required_score(
            session_engine.detect_session()
        ),
        "market_phase": context_engine.detect_market_phase(),
        "price_location": context_engine.detect_price_location(),
        "poc_location": context_engine.detect_poc_location(),
        "volume_node": context_engine.detect_volume_node(),
        "session": session_engine.detect_session(),
        "main_block_reason": main_block_reason,

        "hvn_override_candidate": hvn_override_candidate,

        "hvn_context": hvn_context,

        "hvn_trade_eligibility":
            hvn_trade_eligibility,

        "virtual_trade_direction":
            virtual_trade_direction,

        "virtual_trade_outcome":
            virtual_trade_outcome,

        "virtual_opportunity_score":
            virtual_opportunity_score,

        "virtual_opportunity_grade":
            virtual_opportunity_grade,

        "virtual_edge_score":
            edge_score,

        "virtual_edge_label":
            edge_label,

        "total_ticks": len(volume_engine.ticks),
        "total_volume": volume_engine.ask_volume + volume_engine.bid_volume,
        "final_cvd": volume_engine.cvd,
        "buy_aggression": footprint_data["buy_aggression"],
        "sell_aggression": footprint_data["sell_aggression"],
        "bid_ask_imbalance": footprint_data["bid_ask_imbalance"],
        "delta_exhaustion": footprint_data["delta_exhaustion"],
        "absorption_clue": footprint_data["absorption_clue"],
        "max_ask_stack": footprint_data["max_ask_stack"],
        "max_bid_stack": footprint_data["max_bid_stack"],
        "max_ask_stack_volume": footprint_data["max_ask_stack_volume"],
        "max_bid_stack_volume": footprint_data["max_bid_stack_volume"],
        "stacked_imbalance": footprint_data["stacked_imbalance"],
        "stack_direction": footprint_data["stack_direction"],
        "stack_strength": footprint_data["stack_strength"],
        "footprint_score": footprint_data["footprint_score"]
    }
    probability_score = probability_engine.calculate_probability_score(
        dataset_record["setup_grade"],
        dataset_record["setup_type"],
        dataset_record["trade_quality"],
        dataset_record["stack_strength"],
        dataset_record["footprint_score"]
    )
    weighted_probability_score = (
        probability_engine
        .calculate_weighted_probability_score(
            dataset_record["setup_grade"],
            dataset_record["setup_type"],
            dataset_record["trade_quality"],
            dataset_record["stack_strength"],
            dataset_record["footprint_score"]
        )

    )
    probability_grade = (
        probability_engine.get_probability_grade(
            weighted_probability_score
        )
    )
    dataset_record["probability_score"] = probability_score
    dataset_record["weighted_probability_score"] = weighted_probability_score
    dataset_record["probability_grade"] = probability_grade
    trade_snapshot = {

        "setup_grade":
            dataset_record["setup_grade"],

        "setup_type":
            dataset_record["setup_type"],

        "confidence_score":
            dataset_record["confidence_score"],

        "trade_quality":
            dataset_record["trade_quality"],
        "probability_score":
            probability_score,
        "weighted_probability_score":
            weighted_probability_score,
        "probability_grade":
            probability_grade,
        "footprint_score":
            dataset_record["footprint_score"],

        "stack_strength":
            dataset_record["stack_strength"],

        "buy_aggression":
            dataset_record["buy_aggression"],

        "sell_aggression":
            dataset_record["sell_aggression"],

        "bid_ask_imbalance":
            dataset_record["bid_ask_imbalance"],

        "delta_exhaustion":
            dataset_record["delta_exhaustion"],

        "absorption_clue":
            dataset_record["absorption_clue"],

        "stacked_imbalance":
            dataset_record["stacked_imbalance"],

        "stack_direction":
            dataset_record["stack_direction"],

        "hvn_override_candidate":
            dataset_record["hvn_override_candidate"],

        "hvn_context":
            dataset_record["hvn_context"],

        "hvn_trade_eligibility":
            dataset_record[
                "hvn_trade_eligibility"
            ],

        "virtual_trade_direction":
            dataset_record[
                "virtual_trade_direction"
            ],

        "virtual_trade_outcome":
            dataset_record[
                "virtual_trade_outcome"
            ],

        "virtual_opportunity_score":
            dataset_record["virtual_opportunity_score"],

        "virtual_opportunity_grade":
            dataset_record["virtual_opportunity_grade"],

        "virtual_edge_score":
            dataset_record["virtual_edge_score"],

        "virtual_edge_label":
            dataset_record["virtual_edge_label"],

        "trade_outcome":
            dataset_record["trade_outcome"],

        "trade_label":
            dataset_record["trade_label"]
    }
    print("----- Dataset Record -----")
    print(dataset_record)
    print("----- Trade Snapshot -----")
    print(trade_snapshot)
    ml_snapshot_file = "data/ml_trade_snapshots.csv"

    with open(
            ml_snapshot_file,
            mode="a",
            newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=trade_snapshot.keys()
        )

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow(trade_snapshot)

        print("ML Snapshot saved.")

    dataset_saved = save_dataset_record(
        "data/replay_results.csv",

        dataset_record
    )

    if dataset_saved:
        print("Dataset record saved.")

    else:
        print("Dataset record NOT saved due to schema mismatch.")


for scenario in scenario_list:

    print()
    print("===================================")
    print(f"RUNNING SCENARIO: {scenario}")
    print("===================================")

    run_scenario(scenario)
analytics_engine = AnalyticsEngine("data/replay_results.csv")
probability_engine = ProbabilityEngine(analytics_engine)
print("----- Dataset Analytics -----")
print(f"Final Signal Counts: {analytics_engine.count_by_field('final_signal')}")
print(f"Setup Type Counts: {analytics_engine.count_by_field('setup_type')}")
print(f"Setup Grade Counts: {analytics_engine.count_by_field('setup_grade')}")
print(f"Trade Outcome Counts: {analytics_engine.count_by_field('trade_outcome')}")
print(f"Stacked Imbalance Counts: {analytics_engine.count_by_field('stacked_imbalance')}")
print(f"Stack Direction Counts: {analytics_engine.count_by_field('stack_direction')}")
print(f"Stack Strength Counts: {analytics_engine.count_by_field('stack_strength')}")
print(f"Win Rate: {analytics_engine.calculate_win_rate()}%")
print(
    f"Average Confidence: "
    f"{analytics_engine.calculate_average_confidence()}"
)
print(
    f"Average Footprint Score: "
    f"{analytics_engine.calculate_average_by_field('footprint_score')}"
)
print(
    f"Average Ask Stack Volume: "
    f"{analytics_engine.calculate_average_by_field('max_ask_stack_volume')}"
)

print(
    f"Average Bid Stack Volume: "
    f"{analytics_engine.calculate_average_by_field('max_bid_stack_volume')}"
)
print(
    f"Win Rate By Setup Type: "
    f"{analytics_engine.calculate_win_rate_by_field('setup_type')}"
)
print(
    f"Win Rate By Setup Grade: "
    f"{analytics_engine.calculate_win_rate_by_field('setup_grade')}"
)
print(
    f"Win Rate By Stack Strength: "
    f"{analytics_engine.calculate_win_rate_by_field('stack_strength')}"
)
print(
    f"Win Rate By Stack Direction: "
    f"{analytics_engine.calculate_win_rate_by_field('stack_direction')}"
)
print(
    f"Win Rate By Footprint Score: "
    f"{analytics_engine.calculate_win_rate_by_field('footprint_score')}"
)
print(
    f"Win Rate By Confidence Score: "
    f"{analytics_engine.calculate_win_rate_by_field('confidence_score')}"
)
print(
    f"Confidence Bucket Counts: "
    f"{analytics_engine.count_confidence_buckets()}"
)
print(
    f"Win Rate By Confidence Bucket: "
    f"{analytics_engine.calculate_win_rate_by_confidence_bucket()}"
)
print(
    f"Trade Quality Counts: "
    f"{analytics_engine.count_by_field('trade_quality')}"
)

print(
    f"Win Rate By Trade Quality: "
    f"{analytics_engine.calculate_win_rate_by_field('trade_quality')}"
)
print(
    f"Win Rate By Quality + Footprint: "
    f"{analytics_engine.calculate_win_rate_by_combined_fields(
        'trade_quality',
        'footprint_score'
    )}"
)
print(
    f"Probability A_SETUP: "
    f"{probability_engine.get_probability_by_setup_grade('A_SETUP')}%"
)

print(
    f"Probability B_SETUP: "
    f"{probability_engine.get_probability_by_setup_grade('B_SETUP')}%"
)

print(
    f"Probability C_SETUP: "
    f"{probability_engine.get_probability_by_setup_grade('C_SETUP')}%"
)
print(
    f"Probability BREAKOUT_SETUP: "
    f"{probability_engine.get_probability_by_setup_type('BREAKOUT_SETUP')}%"
)

print(
    f"Probability BREAKDOWN_SETUP: "
    f"{probability_engine.get_probability_by_setup_type('BREAKDOWN_SETUP')}%"
)

print(
    f"Probability ABSORPTION_SETUP: "
    f"{probability_engine.get_probability_by_setup_type('ABSORPTION_SETUP')}%"
)
print(
    f"Probability LOW_QUALITY: "
    f"{probability_engine.get_probability_by_trade_quality('LOW_QUALITY')}%"
)

print(
    f"Probability MEDIUM_QUALITY: "
    f"{probability_engine.get_probability_by_trade_quality('MEDIUM_QUALITY')}%"
)

print(
    f"Probability HIGH_QUALITY: "
    f"{probability_engine.get_probability_by_trade_quality('HIGH_QUALITY')}%"
)

print(
    f"Probability ELITE_QUALITY: "
    f"{probability_engine.get_probability_by_trade_quality('ELITE_QUALITY')}%"
)
print(
    f"Probability STACK_NONE: "
    f"{probability_engine.get_probability_by_stack_strength('NONE')}%"
)

print(
    f"Probability STACK_LOW: "
    f"{probability_engine.get_probability_by_stack_strength('LOW')}%"
)

print(
    f"Probability STACK_MEDIUM: "
    f"{probability_engine.get_probability_by_stack_strength('MEDIUM')}%"
)

print(
    f"Probability STACK_HIGH: "
    f"{probability_engine.get_probability_by_stack_strength('HIGH')}%"
)
print(
    f"Probability FOOTPRINT_0_5: "
    f"{probability_engine.get_probability_by_footprint_score(0.5)}%"
)

print(
    f"Probability FOOTPRINT_1_0: "
    f"{probability_engine.get_probability_by_footprint_score(1.0)}%"
)

print(
    f"Probability FOOTPRINT_1_5: "
    f"{probability_engine.get_probability_by_footprint_score(1.5)}%"
)
print(
    f"Probability ELITE_1_0: "
    f"{probability_engine.get_probability_by_quality_and_footprint(
        'ELITE_QUALITY',
        '1.0'
    )}%"
)

print(
    f"Probability MEDIUM_1_5: "
    f"{probability_engine.get_probability_by_quality_and_footprint(
        'MEDIUM_QUALITY',
        '1.5'
    )}%"
)
print("\n----- Feature Ranking Snapshot -----")

print(
    f"Setup Grade Win Rates: "
    f"{analytics_engine.calculate_win_rate_by_field('setup_grade')}"
)

print(
    f"Setup Type Win Rates: "
    f"{analytics_engine.calculate_win_rate_by_field('setup_type')}"
)

print(
    f"Trade Quality Win Rates: "
    f"{analytics_engine.calculate_win_rate_by_field('trade_quality')}"
)

print(
    f"Stack Strength Win Rates: "
    f"{analytics_engine.calculate_win_rate_by_field('stack_strength')}"
)

print(
    f"Footprint Score Win Rates: "
    f"{analytics_engine.calculate_win_rate_by_field('footprint_score')}"
)

print(
    f"Confidence Bucket Win Rates: "
    f"{analytics_engine.calculate_win_rate_by_confidence_bucket()}"
)
print("\n----- Feature Importance Engine -----")

print(
    analytics_engine.build_feature_importance_snapshot()
)
print("\n----- Ranked Feature Importance -----")

for item in analytics_engine.build_ranked_feature_importance():
    print(item)
    print("\n----- Selected Features -----")

    for item in analytics_engine.get_top_features():
        print(item)
        print("\n----- ML Readiness Snapshot -----")

        print(
            analytics_engine.build_ml_readiness_snapshot()
        )
        print("\n----- Trade Label Counts -----")

        print(
            analytics_engine.count_by_field(
                "trade_label"
            )
        )
        print(
            analytics_engine.build_label_distribution()
        )
        print("\n----- Snapshot Quality Snapshot -----")

        print(
            analytics_engine.build_snapshot_quality_snapshot()
        )
        print("\n----- ML Dataset Quality Dashboard -----")

        print(
            analytics_engine.build_ml_dataset_quality_dashboard()
        )
        print("\n----- Probability Score Distribution -----")

        print(
            analytics_engine
            .build_probability_score_distribution()
        )
        print("\n----- ML Training Readiness Report -----")

        print(
            analytics_engine
            .build_ml_training_readiness_report()
        )
        ml_training_engine = MLTrainingEngine(
            "data/ml_trade_snapshots.csv"
        )

        print("\n----- ML Training Engine Summary -----")

        print(
            ml_training_engine.build_training_summary()
        )
        print("\n----- Training Statistics -----")

        print(
            ml_training_engine
            .build_training_statistics()
        )
        print("\n----- Training Label Distribution -----")

        print(
            ml_training_engine
            .build_label_distribution()
        )
        print("\n----- Tradable Dataset Statistics -----")

        print(
            ml_training_engine
            .build_tradable_dataset_stats()
        )
        print("\n----- Tradable Win Rate -----")

        print(
            ml_training_engine
            .calculate_tradable_win_rate()
        )
        print("\n----- Dataset Balance Report -----")

        print(
            ml_training_engine
            .build_dataset_balance_report()
        )
        prepared_training_stats = ml_training_engine.build_prepared_training_stats()
        print("\n----- Prepared Training Stats -----")

        print(
            prepared_training_stats
        )
        train_test_stats = (
            ml_training_engine
            .build_train_test_split_stats()
        )

        feature_matrix = ml_training_engine.build_feature_matrix()
        target_vector = ml_training_engine.build_target_vector()

        print("\n----- Feature Matrix Sample (first 3 rows) -----")
        for row in feature_matrix[:3]:
            print(row)

        encoded_feature_matrix = (
            ml_training_engine
            .build_encoded_feature_matrix()
        )

        print("\n----- Encoded Feature Matrix Sample (first 3 rows) -----")

        for row in encoded_feature_matrix[:3]:
            print(row)

        final_encoded_feature_matrix = (
            ml_training_engine
            .build_final_encoded_feature_matrix()
        )

        print("\n----- Final Encoded Feature Matrix Sample (first 3 rows) -----")

        for row in final_encoded_feature_matrix[:3]:
            print(row)

        final_matrix_quality_report = (
            ml_training_engine
            .build_final_feature_matrix_quality_report()
        )

        print("\n----- Final Feature Matrix Quality Report -----")

        print(
            final_matrix_quality_report
        )
        majority_baseline = (
            ml_training_engine
            .build_majority_class_baseline()
        )

        print("\n----- Majority Class Baseline -----")

        print(
            majority_baseline
        )
        baseline_accuracy_report = (
            ml_training_engine
            .build_baseline_accuracy_report()
        )

        print("\n----- Baseline Accuracy Report -----")

        print(
            baseline_accuracy_report
        )
        baseline_quality_report = (
            ml_training_engine
            .build_baseline_quality_report()
        )

        print("\n----- Baseline Quality Report -----")

        print(
            baseline_quality_report
        )
        rule_based_predictions = (
            ml_training_engine
            .build_rule_based_predictions()
        )

        print("\n----- Rule-Based Predictions Sample (first 20) -----")

        print(
            rule_based_predictions[:20]
        )
        rule_based_accuracy_report = (
            ml_training_engine
            .build_rule_based_accuracy_report()
        )

        print("\n----- Rule-Based Accuracy Report -----")

        print(
            rule_based_accuracy_report
        )
        leakage_risk_report = (
            ml_training_engine
            .build_leakage_risk_report()
        )

        print("\n----- Leakage Risk Report -----")

        print(
            leakage_risk_report
        )
        safe_rule_based_accuracy_report = (
            ml_training_engine
            .build_safe_rule_based_accuracy_report()
        )

        print("\n----- Safe Rule-Based Accuracy Report -----")

        print(
            safe_rule_based_accuracy_report
        )

        feature_target_audit = (
            ml_training_engine
            .build_feature_target_audit()
        )

        print("\n----- Feature Target Audit -----")

        for feature, result in feature_target_audit.items():
            print(feature)
            print(result)

        encoding_quality_report = (
            ml_training_engine
            .build_encoding_quality_report()
        )

        print("\n----- Feature Leakage Ranking -----")

        for item in ml_training_engine.build_feature_leakage_ranking():
            print(item)
        print("\n----- Normalized Leakage Ranking -----")

        for item in ml_training_engine.build_normalized_leakage_ranking():
            print(item)

        print("\n----- Bucketed Numeric Leakage Audit -----")

        bucketed_audit = (
            ml_training_engine
            .build_bucketed_numeric_leakage_audit()
        )

        for feature, result in bucketed_audit.items():
            print(feature)
            print(result)

        print("\n----- Feature Dependency Audit -----")

        dependency_audit = (
            ml_training_engine
            .build_feature_dependency_audit()
        )

        for feature_pair, result in dependency_audit.items():
            print(feature_pair)
            print(result)

        print("\n----- Core Feature Audit -----")

        core_audit = (
            ml_training_engine
            .build_core_feature_audit()
        )

        for feature, result in core_audit.items():
            print(feature)
            print(result)

        print("\n----- Dead Feature Audit -----")

        dead_audit = (
            ml_training_engine
            .build_dead_feature_audit()
        )

        for feature, result in dead_audit.items():

            if result["unique_count"] <= 3:
                print(feature)
                print(result)

        print("\n----- Core Feature Matrix Report -----")

        print(
            ml_training_engine
            .build_core_feature_matrix_report()
        )

        print("\n----- Encoded Core Feature Matrix Report -----")

        print(
            ml_training_engine
            .build_encoded_core_feature_matrix_report()
        )


        print("\n----- Core Training Shape Report -----")

        print(
            ml_training_engine
            .build_core_training_shape_report()
        )

        print("\n----- Core Rule-Based Accuracy Report -----")

        print(
            ml_training_engine
            .build_core_rule_based_accuracy_report()
        )

        print("\n----- Core Training Summary Report -----")

        print(
            ml_training_engine
            .build_core_training_summary_report()
        )

        print("\n----- Encoding Quality Report -----")

        print(
            encoding_quality_report
        )

        numeric_feature_matrix = (
            ml_training_engine
            .build_numeric_feature_matrix()
        )


        print("\n----- Numeric Feature Matrix Sample (first 3 rows) -----")

        for row in numeric_feature_matrix[:3]:
            print(row)

        print("\n----- Target Vector Sample (first 10 labels) -----")
        print(target_vector[:10])
        encoded_target_vector = (
            ml_training_engine
            .build_encoded_target_vector()
        )

        print("\n----- Encoded Target Vector Sample (first 10 labels) -----")

        print(
            encoded_target_vector[:10]
        )
        encoded_dataset_quality_report = (
            ml_training_engine
            .build_encoded_dataset_quality_report()
        )

        print("\n----- Encoded Dataset Quality Report -----")

        print(
            encoded_dataset_quality_report
        )

        shape_report = (
            ml_training_engine
            .build_feature_target_shape_report()
        )

        print("\n----- Feature Target Shape Report -----")

        print(
            shape_report
        )
        print("\n----- Train Test Split Stats -----")

        print(
            train_test_stats
        )
        label_balance = (
            ml_training_engine
            .build_train_test_label_balance()
        )

        print("\n----- Train Test Label Balance -----")

        print(
            label_balance
        )
        split_quality_report = (
            ml_training_engine
            .build_split_quality_report()
        )

        print("\n----- Split Quality Report -----")

        print(
            split_quality_report
        )

        print("\n----- First ML Model Report -----")

        print(
        ml_training_engine
        .build_first_ml_model_report()
        )

print("\n----- HVN Context Snapshot -----")

print(
    analytics_engine
    .build_hvn_context_snapshot()
)

print("\n----- HVN Trade Eligibility Snapshot -----")

print(
    analytics_engine
    .build_hvn_trade_eligibility_snapshot()
)

print(
    "\n----- HVN Eligibility Outcome Distribution -----"
)

print(
    analytics_engine
    .build_hvn_eligibility_outcome_distribution()
)

print(
    "\n----- Virtual Trade Distribution -----"
)

print(
    analytics_engine
    .build_virtual_trade_distribution()
)

print(
    "\n----- Virtual Dataset Snapshot -----"
)

print(
    analytics_engine
    .build_virtual_dataset_snapshot()
)

print(
    "\n----- Virtual Outcome Snapshot -----"
)

print(
    analytics_engine
    .build_virtual_outcome_snapshot()
)

print(
    "\n----- Virtual Performance Research Snapshot -----"
)

print(
    analytics_engine
    .build_virtual_performance_research_snapshot()
)

print(
    "\n----- Virtual Performance Sample Size Report -----"
)

print(
    analytics_engine
    .build_virtual_performance_sample_size_report()
)

print(
    "\n----- Virtual Bias Audit -----"
)

print(
    analytics_engine
    .build_virtual_bias_audit()
)

print(
    "\n----- Opportunity Population Validation -----"
)

print(
    analytics_engine
    .build_opportunity_population_validation()
)

print("\n----- STEP128 Runtime Readiness Report -----")

print(
    build_runtime_readiness_report()
)

print("\n----- STEP129 Dataset Quality Report -----")

print(
    build_dataset_quality_report(
        analytics_engine
    )
)

dataset_quality_report = (
    build_dataset_quality_report(
        analytics_engine
    )
)

dataset_quality_rule_result = (
    evaluate_dataset_quality_rule(
        dataset_quality_report
    )
)

print(
    "\n----- STEP133 Dataset Quality Rule Test -----"
)

print(
    dataset_quality_rule_result
)

source_rule_test_result = {
    "passed": False,
    "score": 0,
    "reason": "SOURCE_NOT_INDEPENDENT"
}

confidence_rule_pass_test = (
    evaluate_confidence_quality_rule(
        80.0
    )
)

confidence_rule_fail_test = (
    evaluate_confidence_quality_rule(
        52.5
    )
)

qualification_aggregator_test = (
    aggregate_qualification_rules(
        source_rule_test_result,
        dataset_quality_rule_result,
        confidence_rule_pass_test
    )
)

print(
    "\n----- STEP133 Qualification Aggregator Test -----"
)

print(
    qualification_aggregator_test
)

print(
    "\n----- STEP134 Confidence Rule PASS Test -----"
)

print(
    confidence_rule_pass_test
)

print(
    "\n----- STEP134 Confidence Rule FAIL Test -----"
)

print(
    confidence_rule_fail_test
)

print("\n----- Scenario Distribution -----")

for scenario, count in (
    build_dataset_quality_report(
        analytics_engine
    )["scenario_distribution"].items()
):
    print(f"{scenario}: {count}")


if RUNTIME_MODE in ("RESEARCH", "TRAINING"):

    print("\n----- Random Forest Report -----")

    print(

        ml_training_engine
        .build_random_forest_report()
    )

    print("\n----- Random Forest Overfitting Report -----")

    print(
        ml_training_engine
        .build_random_forest_overfitting_report()
    )
    print("\n----- Feature Importance Report -----")

    print(
        ml_training_engine
        .build_feature_importance_report()
    )

    print("\n----- ML Candidate Feature Audit -----")

    print(
        ml_training_engine
        .build_ml_candidate_feature_audit()
    )

    print("\n----- ML Feature Activation Gate -----")

    print(
        ml_training_engine
        .build_ml_feature_activation_gate()
    )

    print("\n----- Dynamic ML Feature Set Report -----")

    print(
        ml_training_engine
        .build_dynamic_ml_feature_set_report()
    )

    print("\n----- Dynamic Encoded Feature Matrix Report -----")

    print(
        ml_training_engine
        .build_dynamic_encoded_feature_matrix_report()
    )

    print("\n----- Dynamic ML Train/Test Readiness Report -----")

    print(
        ml_training_engine
        .build_dynamic_ml_train_test_readiness_report()
    )


    print("\n----- Confidence Dependency Audit -----")

    print(
        ml_training_engine.build_confidence_dependency_audit()
    )

    print("\n----- Signal Independence Map -----")

    print(
        ml_training_engine
        .build_signal_independence_map()
    )

    print("\n----- Feature Purification Report -----")

    print(
        ml_training_engine
        .build_feature_purification_report()
    )

    print("\n----- Footprint Signal Diagnostic Report -----")

    print(
        ml_training_engine
        .build_footprint_signal_diagnostic_report()
    )


    print("\n----- CORE V2 Dependency Safety Audit -----")

    print(
        ml_training_engine
        .build_core_v2_dependency_safety_audit()
    )

    print("\n----- Feature Expansion Benchmark -----")

    print(
        ml_training_engine
        .build_feature_expansion_benchmark()
    )

    print("\n----- Feature Interaction Benchmark -----")

    print(
        ml_training_engine
        .build_feature_interaction_benchmark()
    )

    print(
        ml_training_engine
        .build_random_forest_overfitting_report()
    )




    print("\n----- Probability Model Snapshot -----")

    probability_model_snapshot = (
        probability_engine.build_probability_model_snapshot()
    )

    print(probability_model_snapshot)
    probability_model_file = "data/probability_model_snapshot.csv"

    with open(
            probability_model_file,
            mode="w",
            newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "feature",
            "value",
            "probability"
        ])

        for feature_name, values in probability_model_snapshot.items():

            for value_name, probability in values.items():

                writer.writerow([
                    feature_name,
                    value_name,
                    probability
                ])

    print("Probability Model Snapshot saved.")

for scenario in scenario_list:

    print(
        f"\n===== RUNNING SCENARIO: {scenario} ====="
    )

    run_scenario(scenario)