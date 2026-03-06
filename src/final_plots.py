"""
Generate final publication-quality plots combining exact and semantic metrics.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict

PLOTS_DIR = "results/plots"

CONDITION_ORDER = ["vanilla_llm", "tool_augmented", "feedback_loop_1round", "feedback_loop_3round"]
CONDITION_LABELS = [
    "Vanilla LLM\n(no tools)",
    "Tool-Augmented\nLLM",
    "Feedback Loop\n(1 round)",
    "Feedback Loop\n(3 rounds)",
]
COLORS_EXACT = ["#5B9BD5", "#70AD47", "#FFC000", "#FF4B4B"]
COLORS_SEM = ["#2E75B6", "#375623", "#9C6500", "#843C39"]


def load_data():
    with open("results/raw_results.json") as f:
        raw = json.load(f)
    with open("results/semantic_metrics.json") as f:
        sem = json.load(f)
    with open("results/metrics.json") as f:
        metrics = json.load(f)
    return raw, sem, metrics


def plot_dual_accuracy(raw_data, sem_metrics, metrics_data, output_path):
    """Side-by-side exact vs semantic accuracy."""
    metrics = metrics_data["metrics"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), sharey=True)

    x = np.arange(len(CONDITION_ORDER))
    exact_accs = [metrics.get(c, {}).get("correction_accuracy", 0) for c in CONDITION_ORDER]
    sem_accs = [sem_metrics.get(c, 0) for c in CONDITION_ORDER]

    # Exact match
    bars1 = ax1.bar(x, exact_accs, color=COLORS_EXACT, edgecolor="black", linewidth=0.8, width=0.6)
    ax1.set_xticks(x)
    ax1.set_xticklabels(CONDITION_LABELS, fontsize=10)
    ax1.set_ylabel("Accuracy", fontsize=12)
    ax1.set_title("Exact Match Accuracy\n(strict string comparison)", fontsize=11)
    ax1.set_ylim(0, 1.1)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    for bar, acc in zip(bars1, exact_accs):
        ax1.text(bar.get_x() + bar.get_width()/2, acc + 0.03, f"{acc:.0%}",
                 ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Semantic match
    bars2 = ax2.bar(x, sem_accs, color=COLORS_SEM, edgecolor="black", linewidth=0.8, width=0.6)
    ax2.set_xticks(x)
    ax2.set_xticklabels(CONDITION_LABELS, fontsize=10)
    ax2.set_title("Semantic Accuracy\n(primary error corrected)", fontsize=11)
    ax2.set_ylim(0, 1.1)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    for bar, acc in zip(bars2, sem_accs):
        ax2.text(bar.get_x() + bar.get_width()/2, acc + 0.03, f"{acc:.0%}",
                 ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    plt.suptitle(
        "WetLabAgent Protocol Correction Performance\n"
        "BioProBench Error Correction Task (n=10 samples, Claude claude-sonnet-4-6)",
        fontsize=12, fontweight="bold", y=1.02
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_error_type_heatmap(raw_data, output_path):
    """Heatmap: condition × error_type semantic accuracy."""
    from src.semantic_analysis import semantic_correction_check

    by_cond = defaultdict(list)
    for r in raw_data:
        by_cond[r["condition"]].append(r)

    error_types = ["parameter", "reagent", "operation", "correct"]
    fig, ax = plt.subplots(figsize=(9, 4))

    matrix = np.zeros((len(CONDITION_ORDER), len(error_types)))
    counts = np.zeros((len(CONDITION_ORDER), len(error_types)), dtype=int)

    for i, cond in enumerate(CONDITION_ORDER):
        for j, et in enumerate(error_types):
            items = [r for r in by_cond[cond] if r["error_type"] == et]
            if items:
                sem_vals = [semantic_correction_check(
                    r["error_type"], r["ground_truth_corrupted"],
                    r["ground_truth_corrected"], r["llm_corrected_text"]
                ) for r in items]
                matrix[i, j] = sum(sem_vals) / len(sem_vals)
                counts[i, j] = len(items)
            else:
                matrix[i, j] = np.nan

    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(error_types)))
    ax.set_xticklabels([et.title() for et in error_types], fontsize=11)
    ax.set_yticks(range(len(CONDITION_ORDER)))
    ax.set_yticklabels([l.replace("\n", " ") for l in CONDITION_LABELS], fontsize=10)
    ax.set_title("Semantic Accuracy by Condition and Error Type\n(BioProBench, n in cell)", fontsize=11)

    # Annotate cells
    for i in range(len(CONDITION_ORDER)):
        for j in range(len(error_types)):
            if not np.isnan(matrix[i, j]):
                text = f"{matrix[i,j]:.0%}\n(n={counts[i,j]})"
                ax.text(j, i, text, ha="center", va="center", fontsize=9,
                        fontweight="bold", color="black" if 0.2 < matrix[i,j] < 0.8 else "white")

    plt.colorbar(im, ax=ax, label="Semantic Accuracy")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_over_correction_analysis(raw_data, output_path):
    """Stacked bar showing: correct exact, correct semantic only, incorrect."""
    from src.semantic_analysis import semantic_correction_check

    by_cond = defaultdict(list)
    for r in raw_data:
        by_cond[r["condition"]].append(r)

    correct_exact = []
    correct_semantic_only = []
    incorrect = []

    for cond in CONDITION_ORDER:
        items = by_cond[cond]
        ce = sum(1 for r in items if r["is_correction_correct"])
        cs = sum(1 for r in items if not r["is_correction_correct"] and
                 semantic_correction_check(r["error_type"], r["ground_truth_corrupted"],
                                           r["ground_truth_corrected"], r["llm_corrected_text"]))
        ci = len(items) - ce - cs
        n = len(items)
        correct_exact.append(ce / n)
        correct_semantic_only.append(cs / n)
        incorrect.append(ci / n)

    x = np.arange(len(CONDITION_ORDER))
    fig, ax = plt.subplots(figsize=(10, 5))

    p1 = ax.bar(x, correct_exact, color="#2ECC71", edgecolor="black", linewidth=0.8,
                label="Exact match (both correct & format)", width=0.6)
    p2 = ax.bar(x, correct_semantic_only, bottom=correct_exact,
                color="#F39C12", edgecolor="black", linewidth=0.8,
                label="Semantic only (correct fix, formatting changed)", width=0.6)
    p3 = ax.bar(x, incorrect, bottom=[a+b for a, b in zip(correct_exact, correct_semantic_only)],
                color="#E74C3C", edgecolor="black", linewidth=0.8,
                label="Incorrect fix", width=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(CONDITION_LABELS, fontsize=10)
    ax.set_ylabel("Fraction of Samples", fontsize=12)
    ax.set_title(
        "Protocol Correction Outcome Breakdown\n"
        "Over-correction: LLM correctly fixes error but also reformats text",
        fontsize=11
    )
    ax.set_ylim(0, 1.15)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.legend(fontsize=9, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_detection_vs_correction(metrics_data, output_path):
    """Radar-like bar chart comparing detection vs correction accuracy."""
    metrics = metrics_data["metrics"]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(CONDITION_ORDER))
    width = 0.35

    det_accs = [metrics.get(c, {}).get("detection_accuracy", 0) for c in CONDITION_ORDER]
    cor_accs = [metrics.get(c, {}).get("correction_accuracy", 0) for c in CONDITION_ORDER]

    b1 = ax.bar(x - width/2, det_accs, width, label="Error Detection Accuracy",
                color="#5B9BD5", edgecolor="black", linewidth=0.8)
    b2 = ax.bar(x + width/2, cor_accs, width, label="Exact Correction Accuracy",
                color="#FF4B4B", edgecolor="black", linewidth=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(CONDITION_LABELS, fontsize=10)
    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_title("Error Detection vs. Correction Accuracy by Condition\n(BioProBench, n=10)", fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.legend(fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for bar, acc in list(zip(b1, det_accs)) + list(zip(b2, cor_accs)):
        ax.text(bar.get_x() + bar.get_width()/2, acc + 0.02, f"{acc:.0%}",
                ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")

    raw_data, sem_metrics, metrics_data = load_data()

    plot_dual_accuracy(raw_data, sem_metrics, metrics_data, f"{PLOTS_DIR}/dual_accuracy.png")
    plot_error_type_heatmap(raw_data, f"{PLOTS_DIR}/error_type_heatmap.png")
    plot_over_correction_analysis(raw_data, f"{PLOTS_DIR}/over_correction_breakdown.png")
    plot_detection_vs_correction(metrics_data, f"{PLOTS_DIR}/detection_vs_correction.png")

    print("\nAll plots generated!")
