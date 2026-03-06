# Resources Catalog

## Summary
This document catalogs all resources gathered for the research project on **Autonomous Multi-Modal AI Agent for Wet-Lab Experiment Design and Execution**.

---

## Papers
Total papers downloaded: 12

| Title | Authors | Year | File | Key Info |
|-------|---------|------|------|----------|
| ChemCrow: Augmenting LLMs with Chemistry Tools | Bran et al. (EPFL) | 2023 | `papers/2304.05376_chemcrow.pdf` | 18 chemistry tools, GPT-4 backbone, LangChain |
| GPT-Lab: GPT-Driven Robotic Chemistry Lab | Qin et al. (Zhejiang Lab) | 2023 | `papers/2309.16721_gpt_lab.pdf` | GPT-4 + robotic lab, 500 articles analyzed |
| LLM for Robotics: Opportunities & Challenges | Wang et al. (NPU, UGA) | 2024 | `papers/2401.04334_llm_robotics.pdf` | Survey, GPT-4V embodied tasks |
| Agent Laboratory: LLM Agents as Research Assistants | Schmidgall et al. (AMD, JHU) | 2025 | `papers/2501.04227_agent_laboratory.pdf` | 3-stage pipeline, 84% cost reduction |
| ICRA 2024 Workshop on Lab Automation | Cooper, Darvish, et al. | 2025 | `papers/2501.06847_icra_lab_automation.pdf` | Expert perspectives, practical challenges |
| LLM for Multi-Robot Systems | Multiple | 2025 | `papers/2502.03814_llm_multi_robot.pdf` | Multi-agent robotic orchestration |
| Agentic AI for Scientific Discovery (Survey) | Gridach et al. (IQVIA) | 2025 | `papers/2503.08979_agentic_ai_survey.pdf` | ICLR 2025, taxonomy, evaluation metrics |
| Scaling Laws in Scientific Discovery | Zhang et al. (Toronto) | 2025 | `papers/2503.22444_scaling_laws_discovery.pdf` | AGS concept, flywheel effect |
| Towards Scientific Intelligence (Survey) | Ren et al. (CAS) | 2025 | `papers/2503.24047_scientific_intelligence.pdf` | Agent architectures, benchmarks |
| From Automation to Autonomy (Survey) | Zheng et al. (HKUST) | 2025 | `papers/2505.13259_automation_to_autonomy.pdf` | Tool→Analyst→Scientist taxonomy |
| Autonomous Agents for Scientific Discovery | Zhou et al. (Texas A&M) | 2025 | `papers/2510.09901_autonomous_agents_discovery.pdf` | Physical world interaction bottleneck |
| MATTERIX: Digital Twin for Robotic Chemistry Lab | Darvish et al. | 2026 | `papers/2601.13232_matterix_digital_twin.pdf` | GPU sim framework, sim-to-real transfer |

See `papers/README.md` for detailed descriptions.

---

## Datasets
Total datasets explored: 2 (samples downloaded)

| Name | Source | Size | Task | Location | Notes |
|------|--------|------|------|----------|-------|
| BioProBench | HuggingFace: GreatCaptainNemo/BioProBench | 27K protocols, 556K instances | Protocol understanding & reasoning | `datasets/bioprobench/` | 5 tasks, 12 LLM baselines available |
| ScienceAgentBench | HuggingFace: osunlp/ScienceAgentBench | 102 tasks | Scientific programming | `datasets/scienceagentbench/` | ICLR 2025, 4 disciplines |

See `datasets/README.md` for detailed descriptions and download instructions.

---

## Code Repositories
Total repositories cloned: 3

| Name | URL | Purpose | Location | Notes |
|------|-----|---------|----------|-------|
| ChemCrow | github.com/ur-whitelab/chemcrow-public | Tool-augmented LLM chemistry baseline | `code/chemcrow-public/` | LangChain + 18 tools, needs OpenAI key |
| Agent Laboratory | github.com/SamuelSchmidgall/AgentLaboratory | End-to-end autonomous research pipeline | `code/agent-laboratory/` | 3-stage pipeline, Python 3.12 |
| ScienceAgentBench | github.com/OSU-NLP-Group/ScienceAgentBench | Scientific agent evaluation benchmark | `code/science-agent-bench/` | ICLR 2025, 102 tasks |

See `code/README.md` for detailed descriptions and usage instructions.

---

## Resource Gathering Notes

### Search Strategy
1. Used web search to find key papers from 2023-2025 on: autonomous AI agents for scientific discovery, LLM + robotic lab automation, wet-lab AI agents, multi-modal agents for biology
2. Cross-referenced paper-finder (service unavailable) with manual web search via Google/Semantic Scholar
3. Identified key landmark papers (Coscientist, ChemCrow) and traced forward citations to find recent work
4. Searched HuggingFace for relevant benchmarks and datasets

### Selection Criteria
- Papers directly addressing: LLM + robotic lab integration, autonomous experiment design, multi-modal scientific AI
- Survey papers covering the field comprehensively (for literature review synthesis)
- Papers with available code/datasets for direct use or adaptation
- Recent work (2023-2025) with focus on wet-lab, chemistry, or biology automation
- Datasets with biological protocol content (for wet-lab domain)

### Key Papers Not Downloaded (Paywalled/Not on arXiv)
- **Coscientist** (Boiko et al., 2023, Nature 624:570-578): Most important missing paper. GPT-4 autonomous chemistry agent with robotic integration. Key results: autonomously executed palladium cross-coupling reactions, used UV-Vis for real-time feedback. Access: institutional access required.
- **Virtual Lab** (Swanson et al., 2024): Multi-agent nanobody discovery with wet-lab validation.

### Challenges Encountered
- arxiv.org API returned HTTP 503 errors; switched to using `requests` library for direct PDF download
- wget not available in environment; used Python requests successfully
- Paper-finder service not running; used manual web search as fallback
- HuggingFace requires authentication for some rate-limit tiers; worked without token

---

## Recommendations for Experiment Design

Based on gathered resources:

1. **Primary dataset**: **BioProBench** — Use for evaluating protocol generation quality
   - Protocol Generation task: Test if our agent can generate valid wet-lab protocols
   - Error Correction task: Test if agent can identify and fix protocol errors in real-time
   - Compare against 12 existing LLM baselines already published in the paper

2. **Baseline methods** (in order of increasing capability):
   - Static pre-programmed protocol (no AI)
   - GPT-4o/Claude Sonnet without tools (language-only)
   - ChemCrow-style tool-augmented LLM (no robotic integration)
   - Agent Laboratory (computational experiments only, no physical execution)
   - Our proposed system (multi-modal AI + robotic control + real-time feedback)

3. **Evaluation metrics**:
   - Protocol quality: BioProBench scores (PQA accuracy, step ordering EM, generation BLEU)
   - Experimental efficiency: Number of iterations to converge, reagent waste
   - Feedback adaptation: Time to detect and correct deviations from expected outcomes
   - Success rate: Fraction of experiments achieving target outcome within tolerance

4. **Code to adapt/reuse**:
   - **Agent Laboratory** (`code/agent-laboratory/`): Adapt the multi-agent pipeline architecture; replace computational experiment execution with physical robotic lab interface
   - **ChemCrow** (`code/chemcrow-public/`): Reuse tool-augmented LLM pattern; add biology-specific tools (PCR design, cell culture protocols, assay readers)
   - **ScienceAgentBench** (`code/science-agent-bench/`): Use evaluation framework to assess our agent's scientific task completion

### Proposed Architecture (Based on Literature)

```
Human Research Idea
       ↓
[Literature Review Agent] ← arXiv, PubMed, lab protocol databases
       ↓
[Hypothesis Generation Agent] ← hypothesis + testable predictions
       ↓
[Protocol Design Agent] ← generates step-by-step wet-lab protocol
       ↓
[Safety Validation Agent] ← checks protocol against safety constraints
       ↓
[Robotic Execution Controller] ← controls lab instruments (liquid handler, incubator, reader)
       ↓
[Real-time Feedback Agent] ← monitors sensor data, images, OD readings
       ↓ (if deviation detected)
[Protocol Adaptation Agent] ← generates corrected protocol step
       ↓
[Analysis & Report Agent] ← interprets results, generates report
       ↑ (feedback loop)
```

Key innovation: The **real-time feedback adaptation loop** between the Robotic Execution Controller and the Feedback/Adaptation Agents. This enables the AI to dynamically adjust protocols based on observed experimental outcomes, compared to static pre-programmed robotic protocols.
