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
    get_sample_sell_lvn_ticks
)
import csv
from data.csv_loader import load_ticks_from_csv
from engines.session_engine import SessionEngine
from data.dataset_writer import save_dataset_record
from engines.analytics_engine import AnalyticsEngine
from engines.probability_engine import ProbabilityEngine
from engines.confidence_engine import ConfidenceEngine
from engines.footprint_engine import FootprintEngine
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
    "CSV"

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

    else:
        return []


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
    ticks = get_ticks_by_scenario(scenario)

    replay_engine.replay_ticks(ticks, use_delay=False)
    footprint_data = footprint_engine.analyze_footprint(ticks)
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

    if strategy_reason != "NO_STRATEGY_BLOCK":
        main_block_reason = strategy_reason

    elif risk_reason != "NO_BLOCK":
        main_block_reason = risk_reason

    else:
        main_block_reason = "NO_BLOCK"

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
    setup_grade = nq_strategy.grade_setup()

    if final_signal == "NO_TRADE":
        trade_outcome = "SKIPPED"

    elif (
        final_signal == "BUY_ALLOWED"
        and setup_grade == "A_SETUP"
    ):
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
        nq_strategy.grade_setup(),
        context_engine.detect_volume_node(),
        session_engine.detect_session(),
        footprint_data["footprint_score"],
        footprint_data["stack_strength"]
    )
    if confidence_score < 40:
        trade_quality = "LOW_QUALITY"

    elif confidence_score < 70:
        trade_quality = "MEDIUM_QUALITY"

    elif confidence_score < 90:
        trade_quality = "HIGH_QUALITY"

    else:
        trade_quality = "ELITE_QUALITY"


    dataset_record = {
        "scenario": scenario,
        "final_signal": nq_strategy.get_final_signal(risk_engine),
        "trade_outcome": trade_outcome,
        "trade_label": trade_label,
        "setup_type": nq_strategy.classify_setup(),
        "setup_grade": nq_strategy.grade_setup(),
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
    trade_snapshot = {

        "setup_grade":
            dataset_record["setup_grade"],

        "setup_type":
            dataset_record["setup_type"],

        "confidence_score":
            dataset_record["confidence_score"],

        "trade_quality":
            dataset_record["trade_quality"],

        "footprint_score":
            dataset_record["footprint_score"],

        "stack_strength":
            dataset_record["stack_strength"],

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

    save_dataset_record(
        "data/replay_results.csv",

        dataset_record
    )

    print("Dataset record saved.")
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