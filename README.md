# Autonomous Multi-Modal AI Agent for Wet-Lab Experiment Design and Execution

Artificial Intelligence research project evaluating a modular LLM-based agent for autonomous wet-lab protocol error detection and correction. Conducted on 2026-03-06.

## Key Findings

- **Error Detection**: All agent conditions achieve 80-90% accuracy at detecting whether a protocol contains an error
- **Exact Correction**: 20-30% exact-match accuracy — the LLM correctly fixes the primary error but also modifies unrelated text ("over-correction")
- **Semantic Accuracy**: 70-80% when measuring only whether the primary error was correctly fixed; 3-round feedback loop achieves the highest at **80%**
- **Dominant failure mode**: Over-correction — the LLM normalizes units and reformats text that should remain unchanged, causing exact-match failures despite scientifically correct fixes
- **Feedback loop benefit**: Iterative 3-round adaptation outperforms single-shot generation on semantic accuracy (80% vs 70%), with medium effect size (Cohen's h=0.23)

## Environment Setup

```bash
# Requires Python 3.12+
source .venv/bin/activate

# Install dependencies
uv pip install anthropic numpy matplotlib pandas scipy

# Required environment variable
export ANTHROPIC_API_KEY=your_key_here
```

## How to Reproduce

```bash
# Run experiments (makes real API calls to Claude claude-sonnet-4-6)
python src/wetlab_agent.py

# Run statistical analysis and generate plots
python src/analysis.py
python src/semantic_analysis.py
python src/final_plots.py
```

Expected runtime: ~5 minutes (50 API calls, temperature=0.0 for determinism).

## File Structure

```
.
├── REPORT.md                  # Full research report with results
├── planning.md                # Research plan and methodology
├── src/
│   ├── wetlab_agent.py        # Main agent: 4 experimental conditions
│   ├── analysis.py            # Metrics, statistical tests, plots
│   ├── semantic_analysis.py   # Semantic accuracy analysis
│   └── final_plots.py        # Publication-quality visualizations
├── results/
│   ├── raw_results.json       # 40 result records (10 samples × 4 conditions)
│   ├── metrics.json           # Aggregated metrics + statistical tests
│   ├── semantic_metrics.json  # Semantic accuracy by condition
│   └── plots/                 # 8 visualization files
├── datasets/
│   └── bioprobench/           # BioProBench samples (10 protocol correction tasks)
├── code/                      # Reference implementations (ChemCrow, AgentLaboratory)
├── papers/                    # 12 downloaded research papers
└── literature_review.md       # Synthesized literature review

```

## Dataset

**BioProBench** (GreatCaptainNemo/BioProBench): 10 samples from the error correction task.
- 6 corrupted protocols (parameter, reagent, operation error types)
- 4 correct protocols (no error present)

## Methodology

Four conditions evaluated on Claude claude-sonnet-4-6 (temperature=0.0):
1. **Vanilla LLM**: Single-shot prompt, no tools
2. **Tool-Augmented**: Domain validation tools (parameter range checking, structural consistency) → LLM
3. **Feedback Loop (1 round)**: Tool augmentation + 1 simulated execution observation
4. **Feedback Loop (3 rounds)**: Tool augmentation + up to 3 rounds of closed-loop adaptation

For full methodology and results, see [REPORT.md](REPORT.md).
