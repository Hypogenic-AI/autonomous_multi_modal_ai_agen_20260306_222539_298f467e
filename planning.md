# Research Planning: Autonomous Multi-Modal AI Agent for Wet-Lab Experiment Design

## Motivation & Novelty Assessment

### Why This Research Matters
Laboratory automation currently relies on rigid, pre-programmed protocols that cannot adapt to unexpected experimental results or novel conditions. A system that integrates AI-driven literature comprehension, dynamic hypothesis generation, and real-time feedback adaptation could dramatically accelerate scientific discovery by reducing the human bottleneck in iterative experimental workflows. This directly impacts fields like drug discovery, enzyme engineering, and synthetic biology where experiment-feedback cycles take days to weeks.

### Gap in Existing Work
Based on `literature_review.md`:
1. **No real-time feedback adaptation in wet-lab settings**: Current systems (GPT-Lab, Coscientist) either use rigid robotic protocols or operate in silico only.
2. **Biology wet-lab underrepresented**: Most autonomous experiment systems focus on chemistry; biology wet-lab automation (cell culture, assays) is less developed.
3. **No standardized benchmark for end-to-end autonomous wet-lab execution**: BioProBench covers protocol understanding but not adaptive execution.
4. **Multi-modal integration gap**: Existing tools handle text/structured data; wet-lab automation needs visual (plate images) + sensor + text integration.

### Our Novel Contribution
We design and evaluate a **modular multi-modal AI agent** that:
1. Uses an LLM backbone with wet-lab-specific tools (protocol generation, error detection, parameter adaptation)
2. Implements a closed feedback loop: LLM generates protocol → simulated lab execution → sensor-like results → LLM adapts → repeat
3. Evaluates on BioProBench error correction task — comparing AI-adapted protocols against static protocols
4. Demonstrates **measurable improvement in protocol quality** through iterative LLM feedback vs. one-shot generation

### Experiment Justification
- **Experiment 1** (Protocol Generation Quality): Tests if agent can generate valid wet-lab protocols comparable to expert-written ones. Necessary to establish baseline capability.
- **Experiment 2** (Error Detection & Correction): Tests if agent can identify and fix protocol errors in real-time, simulating the feedback loop. Directly tests the core hypothesis.
- **Experiment 3** (Iterative Adaptation): Tests if multiple rounds of LLM feedback improve protocol quality over static single-shot generation. Key test of "improved efficiency through adaptation."
- **Experiment 4** (Ablation Study): Compares: (a) LLM without tools, (b) LLM with tools, (c) LLM with multi-step feedback. Tests contribution of each component.

---

## Research Question
Can a multi-modal AI agent with a real-time feedback adaptation loop autonomously generate and refine wet-lab protocols with comparable accuracy to human-designed protocols, while demonstrating improvement over static pre-programmed approaches?

## Background and Motivation
Current laboratory automation systems execute fixed, pre-programmed scripts. When unexpected results occur (wrong pH, contamination, instrument variation), human intervention is required. AI agents that can interpret results and dynamically adjust protocols would eliminate this bottleneck. Recent work (ChemCrow, GPT-Lab, Agent Laboratory) demonstrates the feasibility of LLM-driven scientific automation, but real-time wet-lab adaptation remains an open problem.

## Hypothesis Decomposition

**H1**: An LLM-based agent can generate wet-lab protocols with >70% accuracy on protocol quality assessment tasks (BioProBench error correction).

**H2**: Iterative feedback adaptation (multi-round LLM refinement) produces protocols with higher accuracy than single-shot generation.

**H3**: A tool-augmented LLM outperforms a vanilla LLM on wet-lab protocol tasks, justifying the modular agent design.

**H4**: The agent can identify protocol errors (wrong concentrations, temperatures, steps) with measurable precision/recall.

## Proposed Methodology

### Approach
We implement a **WetLabAgent** — a modular LLM-based system with:
1. **Literature Context Module**: Provides relevant protocol background to the LLM
2. **Protocol Generation Tool**: Structured protocol generation with parameter validation
3. **Error Detection Tool**: Identifies protocol errors using domain heuristics + LLM
4. **Feedback Loop**: Iterative refinement based on simulated experimental outcomes
5. **Evaluation Harness**: BioProBench-based scoring for protocol accuracy

The agent uses Claude Sonnet 4.5 or Claude claude-sonnet-4-6 as backbone (Anthropic API key available).

### Experimental Steps

1. **Setup & Data Loading** (10 min): Load BioProBench samples (N=10 available), design evaluation prompts
2. **Baseline Implementation** (15 min): Implement vanilla LLM (no tools, single-shot) as baseline
3. **Tool-Augmented Agent** (20 min): Add domain-specific tools (parameter validation, protocol structure checking)
4. **Feedback Loop Implementation** (20 min): Multi-round refinement with simulated observation feedback
5. **Evaluation** (15 min): Run all conditions on BioProBench error correction task
6. **Analysis & Visualization** (10 min): Compare conditions, statistical tests, generate plots

### Baselines
1. **Static protocol** (no AI): Human-written protocols from BioProBench as gold standard
2. **Vanilla LLM (single-shot)**: Claude without tools, one inference pass
3. **LLM with domain tools**: Claude with parameter validation + structure checking tools
4. **LLM with feedback loop (1 round)**: One refinement iteration
5. **LLM with feedback loop (3 rounds)**: Three refinement iterations ← proposed system

### Evaluation Metrics
1. **Error Detection Accuracy**: Precision, Recall, F1 for identifying protocol errors
2. **Correction Accuracy**: Whether corrected protocol matches ground truth
3. **Parameter Accuracy**: Whether numerical parameters (concentrations, temperatures) are correct
4. **Improvement Rate**: % of correct answers after N feedback rounds vs. baseline
5. **Latency**: Time per protocol evaluation (practical efficiency metric)

### Statistical Analysis Plan
- Paired t-test comparing correction accuracy across conditions (n=10 samples)
- McNemar's test for binary classification (correct/incorrect) comparisons
- Effect size (Cohen's d) for continuous metrics
- Bootstrap confidence intervals (1000 samples) given small n=10

## Expected Outcomes
- H1 supported if vanilla LLM achieves >60% correction accuracy on BioProBench
- H2 supported if multi-round feedback improves accuracy by >10% over single-shot
- H3 supported if tool-augmented agent outperforms vanilla LLM
- H4 supported if error detection F1 > 0.7

## Timeline and Milestones
- 0-10 min: Environment setup, package installation
- 10-25 min: Data loading, baseline implementation
- 25-50 min: Tool-augmented agent + feedback loop
- 50-70 min: Experiments execution (API calls)
- 70-85 min: Analysis, visualization
- 85-100 min: REPORT.md, README.md

## Potential Challenges
1. **API rate limits**: Mitigate by caching responses, using exponential backoff
2. **Small dataset (n=10)**: Use bootstrap CIs, note as limitation
3. **BioProBench format**: May need parsing; handled in data loading step
4. **API key issues**: ANTHROPIC_API_KEY is confirmed available

## Success Criteria
- At least 3 experimental conditions evaluated
- Error correction accuracy >60% for the best agent
- Clear comparison between static, single-shot, and adaptive approaches
- Complete REPORT.md with actual numerical results
