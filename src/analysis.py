"""
Analysis module: Compute metrics, run statistical tests, and generate visualizations
for the WetLabAgent experiment.
"""

import json
import os
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

random.seed(42)
np.random.seed(42)

RESULTS_DIR = "results"
PLOTS_DIR = "results/plots"

CONDITION_ORDER = ["vanilla_llm", "tool_augmented", "feedback_loop_1round", "feedback_loop_3round"]
CONDITION_LABELS = {
    "vanilla_llm": "Vanilla LLM\n(no tools)",
    "tool_augmented": "Tool-Augmented\nLLM",
    "feedback_loop_1round": "Feedback Loop\n(1 round)",
    "feedback_loop_3round": "Feedback Loop\n(3 rounds)",
}
COLORS = ["#5B9BD5", "#70AD47", "#FFC000", "#FF4B4B"]


def load_results(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def compute_metrics(results: list[dict]) -> dict:
    """Compute per-condition aggregated metrics."""
    from collections import defaultdict
    by_condition = defaultdict(list)
    for r in results:
        by_condition[r["condition"]].append(r)

    metrics = {}
    for cond, rlist in by_condition.items():
        n = len(rlist)
        detection_acc = sum(r["is_detection_correct"] for r in rlist) / n
        correction_acc = sum(r["is_correction_correct"] for r in rlist) / n
        param_match = sum(r["parameter_match"] for r in rlist) / n
        avg_latency = np.mean([r["latency_s"] for r in rlist])
        avg_api_calls = np.mean([r["num_api_calls"] for r in rlist])

        # Per-type breakdown
        type_results = defaultdict(list)
        for r in rlist:
            type_results[r["error_type"]].append(r["is_correction_correct"])
        type_acc = {t: sum(v) / len(v) for t, v in type_results.items()}

        # Compute 95% CI for correction accuracy via bootstrap
        boot_accs = []
        boot_n = min(1000, max(100, n * 100))
        for _ in range(boot_n):
            sample = random.choices(rlist, k=n)
            boot_accs.append(sum(s["is_correction_correct"] for s in sample) / n)
        ci_lo = np.percentile(boot_accs, 2.5)
        ci_hi = np.percentile(boot_accs, 97.5)

        metrics[cond] = {
            "n": n,
            "detection_accuracy": detection_acc,
            "correction_accuracy": correction_acc,
            "parameter_match_rate": param_match,
            "avg_latency_s": avg_latency,
            "avg_api_calls": avg_api_calls,
            "correction_acc_ci_lo": ci_lo,
            "correction_acc_ci_hi": ci_hi,
            "per_error_type_correction_acc": type_acc,
        }
    return metrics


def run_statistical_tests(results: list[dict]) -> dict:
    """Run statistical tests comparing conditions."""
    from collections import defaultdict
    by_condition = defaultdict(list)
    for r in results:
        by_condition[r["condition"]].append(r)

    def binary_array(cond):
        return [int(r["is_correction_correct"]) for r in by_condition.get(cond, [])]

    tests = {}

    # Vanilla vs feedback_3round: McNemar's test
    van = binary_array("vanilla_llm")
    fb3 = binary_array("feedback_loop_3round")
    if len(van) == len(fb3) and len(van) > 0:
        # McNemar contingency
        a = sum(1 for v, f in zip(van, fb3) if v == 1 and f == 1)
        b = sum(1 for v, f in zip(van, fb3) if v == 1 and f == 0)
        c = sum(1 for v, f in zip(van, fb3) if v == 0 and f == 1)
        d = sum(1 for v, f in zip(van, fb3) if v == 0 and f == 0)
        # McNemar stat (with continuity correction)
        if (b + c) > 0:
            chi2 = (abs(b - c) - 1) ** 2 / (b + c)
            p_val = 1 - stats.chi2.cdf(chi2, df=1)
        else:
            chi2 = 0.0
            p_val = 1.0
        tests["mcnemar_vanilla_vs_feedback3"] = {
            "chi2": chi2, "p_value": p_val, "b": b, "c": c,
            "interpretation": "Significant" if p_val < 0.05 else "Not significant (small n)"
        }

    # McNemar: vanilla vs tool_augmented
    tool = binary_array("tool_augmented")
    if len(van) == len(tool) and len(van) > 0:
        b = sum(1 for v, t in zip(van, tool) if v == 1 and t == 0)
        c = sum(1 for v, t in zip(van, tool) if v == 0 and t == 1)
        if (b + c) > 0:
            chi2 = (abs(b - c) - 1) ** 2 / (b + c)
            p_val = 1 - stats.chi2.cdf(chi2, df=1)
        else:
            chi2 = 0.0
            p_val = 1.0
        tests["mcnemar_vanilla_vs_tool"] = {
            "chi2": chi2, "p_value": p_val, "b": b, "c": c,
            "interpretation": "Significant" if p_val < 0.05 else "Not significant (small n)"
        }

    # Effect size: Cohen's h for proportion comparison
    van_acc = np.mean(van) if van else 0
    fb3_acc = np.mean(fb3) if fb3 else 0
    if van_acc >= 0 and fb3_acc >= 0:
        h = 2 * np.arcsin(np.sqrt(fb3_acc)) - 2 * np.arcsin(np.sqrt(van_acc))
        tests["cohens_h_vanilla_vs_feedback3"] = {
            "h": abs(h),
            "interpretation": (
                "small" if abs(h) < 0.2 else
                "medium" if abs(h) < 0.5 else
                "large"
            )
        }

    return tests


def plot_correction_accuracy(metrics: dict, output_path: str) -> None:
    """Bar chart of correction accuracy per condition with CI error bars."""
    fig, ax = plt.subplots(figsize=(9, 5))

    conds_present = [c for c in CONDITION_ORDER if c in metrics]
    accs = [metrics[c]["correction_accuracy"] for c in conds_present]
    ci_lo = [metrics[c]["correction_acc_ci_lo"] for c in conds_present]
    ci_hi = [metrics[c]["correction_acc_ci_hi"] for c in conds_present]
    yerr_lo = [accs[i] - ci_lo[i] for i in range(len(accs))]
    yerr_hi = [ci_hi[i] - accs[i] for i in range(len(accs))]
    labels = [CONDITION_LABELS.get(c, c) for c in conds_present]
    colors = COLORS[:len(conds_present)]

    bars = ax.bar(
        range(len(conds_present)), accs,
        color=colors, edgecolor="black", linewidth=0.8, width=0.6,
        yerr=[yerr_lo, yerr_hi], capsize=6, error_kw={"linewidth": 1.5}
    )

    ax.set_xticks(range(len(conds_present)))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Correction Accuracy", fontsize=12)
    ax.set_title(
        "Protocol Error Correction Accuracy by Condition\n(BioProBench, n=10 samples, 95% Bootstrap CI)",
        fontsize=12
    )
    ax.set_ylim(0, 1.15)
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.7, label="Chance level")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))

    # Annotate bars
    for i, (bar, acc) in enumerate(zip(bars, accs)):
        ax.text(
            bar.get_x() + bar.get_width() / 2, acc + 0.04,
            f"{acc:.0%}", ha="center", va="bottom", fontsize=11, fontweight="bold"
        )

    ax.legend(fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_latency_vs_accuracy(metrics: dict, output_path: str) -> None:
    """Scatter plot of latency vs correction accuracy."""
    fig, ax = plt.subplots(figsize=(7, 5))

    conds_present = [c for c in CONDITION_ORDER if c in metrics]
    for i, cond in enumerate(conds_present):
        m = metrics[cond]
        ax.scatter(
            m["avg_latency_s"], m["correction_accuracy"],
            s=120, color=COLORS[i], edgecolor="black", linewidth=0.8,
            zorder=5, label=CONDITION_LABELS.get(cond, cond)
        )
        ax.annotate(
            CONDITION_LABELS.get(cond, cond).replace("\n", " "),
            (m["avg_latency_s"], m["correction_accuracy"]),
            textcoords="offset points", xytext=(8, 4), fontsize=9
        )

    ax.set_xlabel("Average Latency per Sample (seconds)", fontsize=12)
    ax.set_ylabel("Correction Accuracy", fontsize=12)
    ax.set_title("Efficiency-Accuracy Trade-off by Condition", fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.legend(fontsize=9, loc="lower right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_per_error_type(metrics: dict, output_path: str) -> None:
    """Grouped bar chart by error type for best conditions."""
    conds_to_show = ["vanilla_llm", "feedback_3round"]
    conds_present = [c for c in conds_to_show if c in metrics]

    # Get all error types
    error_types = set()
    for c in conds_present:
        error_types.update(metrics[c]["per_error_type_correction_acc"].keys())
    error_types = sorted(error_types)

    if not error_types:
        return

    x = np.arange(len(error_types))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))

    for i, cond in enumerate(conds_present):
        accs = [metrics[cond]["per_error_type_correction_acc"].get(et, 0) for et in error_types]
        offset = (i - len(conds_present) / 2 + 0.5) * width
        bars = ax.bar(x + offset, accs, width, label=CONDITION_LABELS.get(cond, cond),
                      color=COLORS[CONDITION_ORDER.index(cond)], edgecolor="black", linewidth=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels([et.replace("_", " ").title() for et in error_types], fontsize=11)
    ax.set_ylabel("Correction Accuracy", fontsize=12)
    ax.set_title("Correction Accuracy by Error Type\n(Vanilla LLM vs. Feedback Loop)", fontsize=12)
    ax.set_ylim(0, 1.15)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.legend(fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_improvement_over_rounds(results: list[dict], output_path: str) -> None:
    """
    Show cumulative accuracy improvement as feedback rounds increase.
    Uses vanilla (0 rounds), feedback_1round (1 round), feedback_3round (3 rounds).
    """
    from collections import defaultdict
    by_condition = defaultdict(list)
    for r in results:
        by_condition[r["condition"]].append(r)

    rounds = [0, 1, 3]
    cond_map = {0: "vanilla_llm", 1: "feedback_loop_1round", 3: "feedback_loop_3round"}
    accs = []
    for r in rounds:
        cond = cond_map.get(r)
        if cond and cond in by_condition:
            vals = [int(x["is_correction_correct"]) for x in by_condition[cond]]
            accs.append(np.mean(vals) if vals else 0)
        else:
            accs.append(None)

    fig, ax = plt.subplots(figsize=(7, 5))
    valid_rounds = [r for r, a in zip(rounds, accs) if a is not None]
    valid_accs = [a for a in accs if a is not None]

    ax.plot(valid_rounds, valid_accs, "o-", color="#FF4B4B", linewidth=2.5,
            markersize=10, markeredgecolor="black", markeredgewidth=0.8)
    for r, a in zip(valid_rounds, valid_accs):
        ax.annotate(f"{a:.0%}", (r, a), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=12, fontweight="bold")

    ax.set_xlabel("Number of Feedback Rounds", fontsize=12)
    ax.set_ylabel("Correction Accuracy", fontsize=12)
    ax.set_title("Effect of Iterative Feedback Rounds on Protocol Accuracy", fontsize=12)
    ax.set_xticks(valid_rounds)
    ax.set_xticklabels([f"{r} rounds\n({'baseline' if r==0 else 'feedback loop'})"
                         for r in valid_rounds], fontsize=10)
    ax.set_ylim(0, 1.1)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def print_metrics_table(metrics: dict) -> str:
    """Return a markdown table of key metrics."""
    rows = []
    rows.append("| Condition | Detection Acc | Correction Acc | 95% CI | Avg Latency (s) | API Calls |")
    rows.append("|-----------|--------------|---------------|--------|-----------------|-----------|")
    for cond in CONDITION_ORDER:
        if cond not in metrics:
            continue
        m = metrics[cond]
        rows.append(
            f"| {CONDITION_LABELS.get(cond, cond).replace(chr(10), ' ')} "
            f"| {m['detection_accuracy']:.0%} "
            f"| {m['correction_accuracy']:.0%} "
            f"| [{m['correction_acc_ci_lo']:.0%}, {m['correction_acc_ci_hi']:.0%}] "
            f"| {m['avg_latency_s']:.2f} "
            f"| {m['avg_api_calls']:.1f} |"
        )
    return "\n".join(rows)


if __name__ == "__main__":
    os.makedirs(PLOTS_DIR, exist_ok=True)

    # Load results
    results_path = f"{RESULTS_DIR}/raw_results.json"
    results = load_results(results_path)
    print(f"Loaded {len(results)} results")

    # Compute metrics
    metrics = compute_metrics(results)
    print("\n=== METRICS TABLE ===")
    print(print_metrics_table(metrics))

    # Statistical tests
    tests = run_statistical_tests(results)
    print("\n=== STATISTICAL TESTS ===")
    print(json.dumps(tests, indent=2))

    # Save metrics
    with open(f"{RESULTS_DIR}/metrics.json", "w") as f:
        json.dump({"metrics": metrics, "statistical_tests": tests}, f, indent=2)

    # Generate plots
    plot_correction_accuracy(metrics, f"{PLOTS_DIR}/correction_accuracy.png")
    plot_latency_vs_accuracy(metrics, f"{PLOTS_DIR}/latency_vs_accuracy.png")
    plot_per_error_type(metrics, f"{PLOTS_DIR}/per_error_type.png")
    plot_improvement_over_rounds(results, f"{PLOTS_DIR}/improvement_over_rounds.png")

    print("\n=== Analysis complete. Plots saved to results/plots/ ===")
