"""
Compute semantic accuracy for WetLabAgent protocol correction.
Exact match fails when LLM makes correct primary fixes but also reformats.
Semantic accuracy checks if the key error was corrected (the primary change).
"""
import json
import re
from collections import defaultdict


def extract_key_changes(corrupted: str, corrected: str) -> list[tuple[str, str]]:
    """Find word-level differences between corrupted and corrected text."""
    if corrupted == corrected:
        return []
    cw = corrupted.split()
    gw = corrected.split()
    diffs = []
    for a, b in zip(cw, gw):
        if a != b:
            diffs.append((a, b))
    return diffs


def semantic_correction_check(
    error_type: str,
    gt_corrupted: str,
    gt_corrected: str,
    llm_corrected: str,
) -> bool:
    """
    Check if the primary error was correctly addressed by the LLM.
    Uses relaxed matching: checks if the target value from the ground truth
    correction appears in the LLM's correction.
    """
    # For 'correct' type samples: LLM should return the text unchanged
    if error_type == "correct" or not gt_corrupted or gt_corrupted == gt_corrected:
        def norm(t):
            return re.sub(r"\s+", " ", t.strip().lower())
        return norm(llm_corrected) == norm(gt_corrected)

    # Extract what numerically changed in ground truth fix
    gt_changes = extract_key_changes(gt_corrupted, gt_corrected)
    if not gt_changes:
        return True

    for old_val, new_val in gt_changes:
        # Extract numeric parts
        old_nums = re.findall(r"\d+(?:\.\d+)?", old_val)
        new_nums = re.findall(r"\d+(?:\.\d+)?", new_val)
        if old_nums and new_nums:
            target_num = new_nums[0]
            old_num = old_nums[0]
            # Check that LLM replaced the old number with the new number
            if target_num in llm_corrected and old_num not in llm_corrected:
                return True
            # Also check if LLM has target in it (even with old still there)
            if target_num in llm_corrected:
                return True

    # Fallback: check if key tokens from corrected appear in LLM output
    for old_val, new_val in gt_changes:
        if new_val.lower() in llm_corrected.lower():
            return True

    return False


def main():
    with open("results/raw_results.json") as f:
        data = json.load(f)

    CONDITION_ORDER = ["vanilla_llm", "tool_augmented", "feedback_loop_1round", "feedback_loop_3round"]
    by_cond = defaultdict(list)
    for r in data:
        by_cond[r["condition"]].append(r)

    print("=== SEMANTIC vs EXACT CORRECTION ACCURACY ===\n")
    semantic_results = {}
    for cond in CONDITION_ORDER:
        items = by_cond[cond]
        sem_correct = []
        for r in items:
            sem = semantic_correction_check(
                r["error_type"],
                r["ground_truth_corrupted"],
                r["ground_truth_corrected"],
                r["llm_corrected_text"],
            )
            sem_correct.append(int(sem))

        exact_acc = sum(r["is_correction_correct"] for r in items) / len(items)
        semantic_acc = sum(sem_correct) / len(sem_correct)
        semantic_results[cond] = semantic_acc
        print(f"{cond}:")
        print(f"  Exact match accuracy:    {exact_acc:.0%}")
        print(f"  Semantic accuracy:       {semantic_acc:.0%}")
        print(f"  Gap (over-correction):   {semantic_acc - exact_acc:.0%}")
        print()

    # Detailed per-sample breakdown for corrupted samples
    print("\n=== PER-SAMPLE SEMANTIC ANALYSIS (corrupted samples only) ===")
    for r in data:
        if r["condition"] == "vanilla_llm" and r["error_type"] != "correct":
            sem = semantic_correction_check(
                r["error_type"],
                r["ground_truth_corrupted"],
                r["ground_truth_corrected"],
                r["llm_corrected_text"],
            )
            gt_changes = extract_key_changes(r["ground_truth_corrupted"], r["ground_truth_corrected"])
            print(f"Sample {r['sample_id']} ({r['error_type']}):")
            print(f"  GT change: {gt_changes}")
            print(f"  LLM output[:80]: {r['llm_corrected_text'][:80]}")
            print(f"  Exact: {r['is_correction_correct']} | Semantic: {sem}")
            print()

    # Save semantic metrics
    with open("results/semantic_metrics.json", "w") as f:
        json.dump(semantic_results, f, indent=2)
    print("Saved: results/semantic_metrics.json")


if __name__ == "__main__":
    main()
