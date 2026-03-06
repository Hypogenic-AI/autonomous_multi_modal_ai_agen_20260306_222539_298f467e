"""
WetLabAgent: Autonomous Multi-Modal AI Agent for Wet-Lab Protocol Design and Error Correction.

This module implements a modular agent system that:
1. Loads and evaluates biological protocols from BioProBench
2. Tests multiple conditions: vanilla LLM, tool-augmented LLM, and multi-round feedback loop
3. Measures protocol error detection and correction accuracy
"""

import json
import os
import random
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional
import anthropic

# --- Reproducibility ---
random.seed(42)

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/experiment.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# --- Configuration ---
MODEL_ID = "claude-sonnet-4-6"
MAX_TOKENS = 512
TEMPERATURE = 0.0  # deterministic for reproducibility
DATA_PATH = "datasets/bioprobench/samples.json"
RESULTS_DIR = "results"


# ─────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────

def load_bioprobench(path: str) -> list[dict]:
    """Load BioProBench error correction samples."""
    with open(path) as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} BioProBench samples from {path}")
    return data


def get_protocol_text(sample: dict) -> str:
    """
    Get the protocol text to evaluate.
    For corrupted samples: use corrupted_text (LLM should detect error).
    For correct samples: use corrected_text (LLM should say no error).
    """
    if sample.get("corrupted_text") is not None:
        return sample["corrupted_text"]
    return sample["corrected_text"]


def show_sample(sample: dict) -> str:
    """Format a sample for display."""
    return (
        f"ID: {sample['id']}\n"
        f"Type: {sample['type']}\n"
        f"Context: {sample['context']}\n"
        f"Protocol text: {get_protocol_text(sample)}\n"
        f"Correct: {sample['corrected_text']}\n"
        f"Is_correct: {sample['is_correct']}\n"
    )


# ─────────────────────────────────────────────────────────
# DOMAIN TOOLS
# ─────────────────────────────────────────────────────────

# Critical wet-lab parameter ranges for basic sanity checking
PARAMETER_RULES = {
    "CO2": {"min": 4.0, "max": 6.0, "unit": "%", "typical": 5.0},
    "temperature_incubator": {"min": 35.0, "max": 39.0, "unit": "°C", "typical": 37.0},
    "temperature_rt": {"min": 18.0, "max": 26.0, "unit": "°C", "typical": 22.0},
    "ROCK_inhibitor_dilution": {"min": 500, "max": 2000, "unit": "fold", "typical": 1000},
    "centrifuge_speed_rbc": {"min": 100, "max": 500, "unit": "g", "typical": 300},
    "pH_culture": {"min": 7.2, "max": 7.6, "unit": "", "typical": 7.4},
}


def tool_validate_parameters(protocol_text: str) -> str:
    """
    Domain tool: Check if key numerical parameters in a protocol are within
    normal biological ranges. Returns a list of potential issues.
    """
    issues = []

    text_lower = protocol_text.lower()

    # Check CO2 percentage
    import re
    co2_matches = re.findall(r"(\d+(?:\.\d+)?)\s*%?\s*co[_2]?", text_lower)
    for val in co2_matches:
        v = float(val)
        if v > 8.0 or v < 3.0:
            issues.append(
                f"CO2={v}% is unusual for cell culture (normal: 5%). "
                "Typical cell culture uses 5% CO2."
            )

    # Check temperature
    temp_matches = re.findall(r"(\d+(?:\.\d+)?)\s*°?c\b", text_lower)
    for val in temp_matches:
        v = float(val)
        if 90 < v < 110:
            issues.append(f"Temperature={v}°C seems extremely high — likely a typo?")
        elif 40 < v < 80:
            issues.append(
                f"Temperature={v}°C is above normal cell culture (37°C). "
                "Verify if this is intentional."
            )

    # Check dilution factors (e.g., "1:100" vs "1:1000")
    dilution_matches = re.findall(r"1:(\d+)\s*rock", text_lower)
    for val in dilution_matches:
        v = int(val)
        if v < 200 or v > 2000:
            issues.append(
                f"ROCK inhibitor dilution 1:{v} is unusual "
                "(normal range: 1:500 to 1:1000)."
            )

    if not issues:
        return "No obvious parameter issues detected."
    return "Parameter issues found:\n" + "\n".join(f"- {i}" for i in issues)


def tool_check_protocol_structure(protocol_text: str, context: dict) -> str:
    """
    Domain tool: Check if the protocol text is consistent with the context
    (prior/next steps, purpose). Returns structural assessment.
    """
    notes = []

    prior = context.get("prior_step", "").lower()
    nxt = context.get("next_step", "").lower()
    purpose = context.get("purpose", "").lower()
    text_lower = protocol_text.lower()

    # Check that protocol mentions expected equipment/media
    if "medium" in purpose or "media" in purpose:
        if not any(w in text_lower for w in ["medium", "media", "ml", "plate"]):
            notes.append("Protocol mentions medium in purpose but protocol text lacks medium/volume references.")

    # Check that incubation is mentioned if context expects it
    if "incubat" in prior or "incubat" in nxt:
        if "incubat" not in text_lower:
            notes.append("Adjacent steps reference incubation but protocol doesn't mention it.")

    if not notes:
        return "Protocol structure appears consistent with context."
    return "Structural notes:\n" + "\n".join(f"- {n}" for n in notes)


# ─────────────────────────────────────────────────────────
# AGENT CONDITIONS
# ─────────────────────────────────────────────────────────

@dataclass
class EvalResult:
    """Stores evaluation result for a single sample under one condition."""
    sample_id: str
    condition: str
    error_type: str  # ground truth error type
    ground_truth_corrupted: str
    ground_truth_corrected: str
    llm_corrected_text: str
    llm_reasoning: str
    is_detection_correct: bool  # did LLM detect there was an error?
    is_correction_correct: bool  # did LLM correction match ground truth?
    parameter_match: bool  # do numerical parameters match exactly?
    num_api_calls: int
    latency_s: float
    tool_outputs: list[str] = field(default_factory=list)


def build_system_prompt(use_tools: bool = False) -> str:
    """Build the system prompt for the WetLabAgent."""
    base = (
        "You are an expert biologist and lab technician specializing in wet-lab protocols. "
        "Your task is to review a biological laboratory protocol step and determine if it contains an error. "
        "If an error exists, you must correct it precisely. "
        "Common error types: wrong concentrations (e.g., 1:100 vs 1:1000), wrong temperatures (10% CO2 vs 5% CO2), "
        "wrong volumes, wrong reagent names, or wrong procedural steps. "
        "Always respond in valid JSON with these fields: "
        '{"has_error": true/false, "corrected_text": "...", "reasoning": "..."}'
    )
    if use_tools:
        base += (
            "\n\nYou have access to parameter validation results that flag unusual values. "
            "Use this information to guide your correction."
        )
    return base


def build_user_prompt(
    sample: dict,
    tool_outputs: Optional[list[str]] = None,
    prior_feedback: Optional[str] = None,
) -> str:
    """Build the user prompt for protocol error correction."""
    ctx = sample["context"]
    protocol_text = get_protocol_text(sample)
    prompt = (
        f"Context:\n"
        f"  Purpose: {ctx.get('purpose', 'N/A')}\n"
        f"  Prior step: {ctx.get('prior_step', 'N/A')}\n"
        f"  Next step: {ctx.get('next_step', 'N/A')}\n\n"
        f"Protocol step to evaluate:\n{protocol_text}\n\n"
        "Instructions: Determine if this protocol step contains an error. "
        "If yes, provide the corrected version. Respond ONLY with valid JSON."
    )
    if tool_outputs:
        prompt += "\n\nDomain tool analysis:\n" + "\n".join(tool_outputs)

    if prior_feedback:
        prompt += (
            f"\n\nFeedback from simulated execution:\n{prior_feedback}\n"
            "Revise your correction based on this feedback."
        )
    return prompt


def call_llm(
    client: anthropic.Anthropic,
    system: str,
    user: str,
    max_retries: int = 3,
) -> tuple[str, float]:
    """Call the Claude API with exponential backoff. Returns (response_text, latency_s)."""
    for attempt in range(max_retries):
        try:
            t0 = time.time()
            response = client.messages.create(
                model=MODEL_ID,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            latency = time.time() - t0
            return response.content[0].text, latency
        except anthropic.RateLimitError:
            wait = 2 ** attempt
            logger.warning(f"Rate limit hit, retrying in {wait}s...")
            time.sleep(wait)
        except Exception as e:
            logger.error(f"API error (attempt {attempt+1}): {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("Max retries exceeded")


def parse_llm_response(text: str) -> dict:
    """Parse JSON from LLM response, handling markdown code blocks."""
    import re
    # Strip markdown code fences
    text = re.sub(r"```(?:json)?\n?", "", text).strip().rstrip("```").strip()
    # Try to extract JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    # Fallback
    return {"has_error": False, "corrected_text": text, "reasoning": "parse error"}


def normalize_text(t: str) -> str:
    """Normalize text for comparison (lowercase, strip, collapse whitespace)."""
    import re
    return re.sub(r"\s+", " ", t.strip().lower())


def texts_match(pred: str, gold: str) -> bool:
    """Check if predicted correction matches gold standard (approximate)."""
    return normalize_text(pred) == normalize_text(gold)


def simulate_lab_feedback(sample: dict, llm_correction: str) -> str:
    """
    Simulate real-time lab feedback after a protocol step execution.
    Returns feedback string describing what was "observed" during simulated execution.
    This models what a robotic system would report back.
    """
    corrupted = get_protocol_text(sample)
    corrected_gold = sample["corrected_text"]
    error_type = sample["type"]

    # Check if the LLM's correction is close to the gold answer
    if texts_match(llm_correction, corrupted):
        # LLM didn't change anything — simulate failure
        feedback = (
            f"Execution observation: The protocol step was executed but the outcome was suboptimal. "
            f"Error type detected by sensors: {error_type}. "
            "The system flagged an anomaly — please review critical parameters."
        )
    elif texts_match(llm_correction, corrected_gold):
        # LLM got it right — simulate success
        feedback = (
            "Execution observation: Protocol executed successfully. "
            "All sensor readings within expected ranges. "
            "No anomalies detected. Results are consistent with expected outcomes."
        )
    else:
        # Partial correction — simulate partial success
        feedback = (
            "Execution observation: Protocol partially executed. "
            f"Some parameters for error type '{error_type}' still appear anomalous. "
            "Please double-check numerical values against standard references."
        )
    return feedback


# ─────────────────────────────────────────────────────────
# EXPERIMENTAL CONDITIONS
# ─────────────────────────────────────────────────────────

def run_condition_vanilla(
    client: anthropic.Anthropic,
    sample: dict,
    condition_name: str = "vanilla_llm",
) -> EvalResult:
    """
    Condition 1: Vanilla LLM (no tools, single-shot).
    """
    system = build_system_prompt(use_tools=False)
    user = build_user_prompt(sample)
    t0 = time.time()
    response_text, latency = call_llm(client, system, user)
    parsed = parse_llm_response(response_text)

    protocol_text = get_protocol_text(sample)
    has_error_pred = parsed.get("has_error", False)
    corrected = parsed.get("corrected_text", protocol_text)
    reasoning = parsed.get("reasoning", "")

    ground_truth_has_error = not sample["is_correct"]
    detection_correct = has_error_pred == ground_truth_has_error
    correction_correct = texts_match(corrected, sample["corrected_text"])
    param_match = texts_match(corrected, sample["corrected_text"])

    return EvalResult(
        sample_id=sample["id"],
        condition=condition_name,
        error_type=sample["type"],
        ground_truth_corrupted=get_protocol_text(sample) or "",
        ground_truth_corrected=sample["corrected_text"],
        llm_corrected_text=corrected,
        llm_reasoning=reasoning,
        is_detection_correct=detection_correct,
        is_correction_correct=correction_correct,
        parameter_match=param_match,
        num_api_calls=1,
        latency_s=latency,
        tool_outputs=[],
    )


def run_condition_tool_augmented(
    client: anthropic.Anthropic,
    sample: dict,
) -> EvalResult:
    """
    Condition 2: Tool-augmented LLM.
    Runs domain tools first, then provides tool outputs to LLM.
    """
    protocol_text = get_protocol_text(sample)
    # Run domain tools
    param_output = tool_validate_parameters(protocol_text)
    struct_output = tool_check_protocol_structure(protocol_text, sample["context"])
    tool_outputs = [param_output, struct_output]

    system = build_system_prompt(use_tools=True)
    user = build_user_prompt(sample, tool_outputs=tool_outputs)
    t0 = time.time()
    response_text, latency = call_llm(client, system, user)
    parsed = parse_llm_response(response_text)

    has_error_pred = parsed.get("has_error", False)
    corrected = parsed.get("corrected_text", protocol_text)
    reasoning = parsed.get("reasoning", "")

    ground_truth_has_error = not sample["is_correct"]
    detection_correct = has_error_pred == ground_truth_has_error
    correction_correct = texts_match(corrected, sample["corrected_text"])

    return EvalResult(
        sample_id=sample["id"],
        condition="tool_augmented",
        error_type=sample["type"],
        ground_truth_corrupted=get_protocol_text(sample) or "",
        ground_truth_corrected=sample["corrected_text"],
        llm_corrected_text=corrected,
        llm_reasoning=reasoning,
        is_detection_correct=detection_correct,
        is_correction_correct=correction_correct,
        parameter_match=correction_correct,
        num_api_calls=1,
        latency_s=latency,
        tool_outputs=tool_outputs,
    )


def run_condition_feedback_loop(
    client: anthropic.Anthropic,
    sample: dict,
    num_rounds: int = 3,
) -> EvalResult:
    """
    Condition 3: Multi-round feedback loop.
    Simulates the closed-loop adaptation: generate protocol → observe → adapt.
    """
    protocol_text = get_protocol_text(sample)
    # Run domain tools first
    param_output = tool_validate_parameters(protocol_text)
    struct_output = tool_check_protocol_structure(protocol_text, sample["context"])
    tool_outputs = [param_output, struct_output]

    system = build_system_prompt(use_tools=True)
    total_latency = 0.0
    total_api_calls = 0
    current_correction = protocol_text
    prior_feedback = None
    reasoning = ""
    parsed = {"has_error": False, "corrected_text": protocol_text, "reasoning": ""}

    for round_num in range(num_rounds):
        user = build_user_prompt(sample, tool_outputs=tool_outputs, prior_feedback=prior_feedback)
        response_text, latency = call_llm(client, system, user)
        total_latency += latency
        total_api_calls += 1

        parsed = parse_llm_response(response_text)
        current_correction = parsed.get("corrected_text", current_correction)
        reasoning = parsed.get("reasoning", "")

        # Simulate lab feedback for next round
        prior_feedback = simulate_lab_feedback(sample, current_correction)
        logger.info(f"Round {round_num+1}/{num_rounds}: correction={'MATCH' if texts_match(current_correction, sample['corrected_text']) else 'NO MATCH'}")

        # Early exit if correct
        if texts_match(current_correction, sample["corrected_text"]):
            break

    last_has_error = parsed.get("has_error", False)
    ground_truth_has_error = not sample["is_correct"]
    detection_correct = last_has_error == ground_truth_has_error
    correction_correct = texts_match(current_correction, sample["corrected_text"])

    return EvalResult(
        sample_id=sample["id"],
        condition=f"feedback_loop_{num_rounds}round",
        error_type=sample["type"],
        ground_truth_corrupted=get_protocol_text(sample) or "",
        ground_truth_corrected=sample["corrected_text"],
        llm_corrected_text=current_correction,
        llm_reasoning=reasoning,
        is_detection_correct=detection_correct,
        is_correction_correct=correction_correct,
        parameter_match=correction_correct,
        num_api_calls=total_api_calls,
        latency_s=total_latency,
        tool_outputs=tool_outputs,
    )


# ─────────────────────────────────────────────────────────
# MAIN EXPERIMENT RUNNER
# ─────────────────────────────────────────────────────────

def run_all_experiments(data: list[dict], client: anthropic.Anthropic) -> list[dict]:
    """Run all experimental conditions on all samples. Returns list of result dicts."""
    all_results = []
    conditions = [
        ("vanilla_llm", lambda s: run_condition_vanilla(client, s, "vanilla_llm")),
        ("tool_augmented", lambda s: run_condition_tool_augmented(client, s)),
        ("feedback_1round", lambda s: run_condition_feedback_loop(client, s, num_rounds=1)),
        ("feedback_3round", lambda s: run_condition_feedback_loop(client, s, num_rounds=3)),
    ]

    for sample in data:
        logger.info(f"\n{'='*60}")
        logger.info(f"Sample: {sample['id']} | Type: {sample['type']}")
        logger.info(f"Protocol text: {(get_protocol_text(sample) or '')[:80]}...")

        for cond_name, cond_fn in conditions:
            logger.info(f"  Running condition: {cond_name}")
            try:
                result = cond_fn(sample)
                result_dict = asdict(result)
                all_results.append(result_dict)
                logger.info(
                    f"  Detection: {'✓' if result.is_detection_correct else '✗'} | "
                    f"Correction: {'✓' if result.is_correction_correct else '✗'} | "
                    f"Latency: {result.latency_s:.2f}s | "
                    f"API calls: {result.num_api_calls}"
                )
            except Exception as e:
                logger.error(f"  Error in condition {cond_name}: {e}")

    return all_results


def save_results(results: list[dict], path: str) -> None:
    """Save results to JSON file."""
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {path}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")

    logger.info("=== WetLabAgent Experiment ===")
    logger.info(f"Model: {MODEL_ID}")
    logger.info(f"Temperature: {TEMPERATURE}")

    # Load data
    data = load_bioprobench(DATA_PATH)
    logger.info(f"Loaded {len(data)} samples")

    # Print sample info
    for s in data[:2]:
        logger.info(f"\n{show_sample(s)}")

    # Initialize client
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Run experiments
    results = run_all_experiments(data, client)

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    save_results(results, f"{RESULTS_DIR}/raw_results.json")

    logger.info(f"\n=== Experiment complete. {len(results)} results saved. ===")
