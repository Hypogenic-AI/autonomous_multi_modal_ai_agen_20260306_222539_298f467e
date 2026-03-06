# Literature Review: Autonomous Multi-Modal AI Agent for Wet-Lab Experiment Design and Execution

**Research Hypothesis**: A multi-modal AI agent integrating literature comprehension, hypothesis generation, and robotic control can autonomously design and execute simple wet-lab experiments with comparable accuracy to human-designed protocols. The agent will demonstrate improved experimental efficiency through real-time feedback adaptation compared to static pre-programmed protocols.

---

## Research Area Overview

The convergence of large language models (LLMs), multi-modal AI, and laboratory robotics has catalyzed a new paradigm of **autonomous scientific discovery**. Systems in this space range from LLMs augmented with domain-specific chemistry tools (ChemCrow, 2023) to fully integrated robotic platforms that execute physical experiments (Coscientist, 2023; GPT-Lab, 2023). Recent surveys (2024–2025) describe a progression from "AI as tool" to "AI as scientist," with the dominant trend being **closed-loop systems** where AI generates hypotheses, robots execute protocols, results are fed back, and the cycle repeats.

The specific challenge of wet-lab automation remains harder than computational/chemistry tasks due to the physical manipulation requirements, protocol complexity, safety constraints, and the need to handle real biological variability. However, recent systems (autonomous enzyme engineering platforms, Ginkgo+GPT-5 collaboration) show practical viability is approaching.

---

## Key Papers

### Paper 1: ChemCrow: Augmenting Large Language Models with Chemistry Tools
- **Authors**: Andres M. Bran, Sam Cox, Oliver Schilter, Carlo Baldassari, Andrew D. White, Philippe Schwaller
- **Year**: 2023
- **Source**: arXiv:2304.05376
- **Key Contribution**: First major demonstration of tool-augmented LLMs for autonomous chemistry. Integrated 18 expert-designed chemistry tools (RDKit, PubChem, reaction prediction APIs) into GPT-4 using a ReAct-style (Thought-Action-Observation) framework.
- **Methodology**: LangChain-based agent with GPT-4 backbone; tools include web search, molecular property prediction, retrosynthesis planning, reaction prediction, and safety checking.
- **Results**: Autonomously planned/executed synthesis of insect repellent, 3 organocatalysts, discovered novel chromophore. Evaluated on 14 chemical tasks.
- **Datasets Used**: 14 bespoke chemistry tasks; no standard benchmark
- **Code Available**: Yes — https://github.com/ur-whitelab/chemcrow-public
- **Relevance**: Establishes the tool-augmented LLM agent paradigm for laboratory tasks. Our work extends this to multi-modal wet-lab settings with robotic integration.

### Paper 2: Agent Laboratory: Using LLM Agents as Research Assistants
- **Authors**: Samuel Schmidgall, Yusheng Su, Ze Wang, et al. (AMD, Johns Hopkins, ETH Zurich)
- **Year**: 2025
- **Source**: arXiv:2501.04227 (ICLR workshop)
- **Key Contribution**: End-to-end autonomous research pipeline with three stages: Literature Review → Experimentation → Report Writing. Supports both autonomous and human-in-the-loop (co-pilot) modes.
- **Methodology**: Specialized LLM agents (PhD agent, Postdoc agent) with tools like mle-solver for ML experimentation and paper-solver for report generation. Uses arXiv, HuggingFace, Python environments.
- **Results**: o1-preview achieves best outcomes; 84% reduction in research cost vs previous methods; generated ML code achieves state-of-the-art performance; human feedback at each stage significantly improves quality.
- **Datasets Used**: Various ML benchmarks (CIFAR, etc.) depending on research idea input
- **Code Available**: Yes — https://github.com/SamuelSchmidgall/AgentLaboratory
- **Relevance**: Directly relevant as a complete autonomous research pipeline template. Our work adapts this concept from computational ML experiments to physical wet-lab experiments.

### Paper 3: Agentic AI for Scientific Discovery: A Survey of Progress, Challenges, and Future Directions
- **Authors**: Mourad Gridach, Jay Nanavati, Khaldoun Zine El Abidine, Lenon Mendes, Christina Mack (IQVIA)
- **Year**: 2025
- **Source**: arXiv:2503.08979 (ICLR 2025 conference paper)
- **Key Contribution**: Comprehensive survey of agentic AI systems for scientific discovery. Categorizes systems into autonomous and collaborative frameworks.
- **Methodology**: Survey of existing systems; defines evaluation metrics, implementation frameworks, and datasets
- **Key Findings**:
  - Agentic systems show strong performance in literature review, hypothesis generation, and computational experimentation
  - Performance drops in literature review automation (structured synthesis remains challenging)
  - Key frameworks: LangChain, AutoGen, CrewAI for multi-agent orchestration
  - Evaluation metrics: task success rates, scientific quality scores, reproducibility
- **Relevance**: Provides comprehensive taxonomy and evaluation framework applicable to our research. Identifies key challenges including system reliability and ethical governance.

### Paper 4: Accelerating Discovery in Natural Science Laboratories with AI and Robotics (IEEE ICRA 2024 Workshop)
- **Authors**: Andrew I. Cooper, Patrick Courtney, Kourosh Darvish, et al. (Multiple institutions)
- **Year**: 2025 (proceedings published)
- **Source**: arXiv:2501.06847
- **Key Contribution**: Expert perspectives on practical challenges in laboratory automation from leading researchers across materials science, biology, chemistry, and robotics.
- **Methodology**: Workshop proceedings summarizing challenges, perspectives, and research directions
- **Key Findings**:
  - Laboratory automation requires interdisciplinary collaboration (AI + robotics + domain science)
  - Key challenges: robust flexibility, reproducibility, throughput, standardization
  - Role of human scientists remains essential despite advances
  - Existing solutions often rigid (designed for specific tasks with little adaptability)
  - AI/robotics advances enable more flexible, human-centric automation
- **Relevance**: Directly addresses the practical engineering challenges our system must solve. Identifies standardization (SiLA protocol) as critical for interoperability.

### Paper 5: Towards Scientific Intelligence: A Survey of LLM-based Scientific Agents
- **Authors**: Shuo Ren, Can Xie, Pu Jian, et al. (Chinese Academy of Sciences)
- **Year**: 2025
- **Source**: arXiv:2503.24047
- **Key Contribution**: Comprehensive survey of LLM-based scientific agents with focus on architectures, design, benchmarks, and applications.
- **Methodology**: Survey with focus on why scientific agents differ from general agents (domain-specific knowledge, diverse action spaces, heterogeneous data)
- **Key Findings**:
  - Scientific agents require domain-specific tool integration
  - Validation mechanisms are critical for scientific correctness
  - Multi-modal capability (images, molecular structures, sequences) is essential
  - Key benchmarks: LAB-Bench, ScienceAgentBench, BioProBench
- **Relevance**: Provides design principles for building our multi-modal AI agent. Identifies key technical gaps in current systems.

### Paper 6: From Automation to Autonomy: A Survey on LLMs in Scientific Discovery
- **Authors**: Tianshi Zheng, Zheye Deng, Hong Ting Tsang, et al. (HKUST)
- **Year**: 2025
- **Source**: arXiv:2505.13259
- **Key Contribution**: Introduces a three-level taxonomy (Tool → Analyst → Scientist) for LLMs in science. Identifies escalating levels of autonomy and responsibility.
- **Methodology**: Survey structured around 6 stages of scientific method
- **Key Findings**:
  - Stage-by-stage analysis: observation, hypothesis, experiment, analysis, conclusions, iteration
  - Current LLMs primarily operate as "Analyst" level; "Scientist" level requires physical world interaction
  - Robotic automation is the key enabler for moving from "Analyst" to "Scientist" level
- **Relevance**: Provides conceptual framework for positioning our research contribution. Our system aims at the "Scientist" level by coupling LLM intelligence with physical robotic execution.

### Paper 7: Scaling Laws in Scientific Discovery with AI and Robot Scientists
- **Authors**: Pengsong Zhang, Heng Zhang, Huazhe Xu, et al. (Toronto, IIT, Tsinghua)
- **Year**: 2025
- **Source**: arXiv:2503.22444
- **Key Contribution**: Proposes the Autonomous Generalist Scientist (AGS) concept combining agentic AI + embodied robotics for complete research lifecycle automation. Hypothesizes new scaling laws for AI-driven scientific discovery.
- **Methodology**: Conceptual paper with empirical analysis of existing scaling behaviors
- **Key Findings**:
  - Current AI scientists are "virtual" (computational); future AGS requires embodied robotics
  - AGS could catalyze flywheel effect: more knowledge → better experiments → more knowledge
  - Key integration needed: LLM for reasoning + robot for physical execution + simulation for validation
- **Relevance**: Positions our research in the broader vision of autonomous science. Our system is a practical first step toward AGS for wet-lab biology.

### Paper 8: GPT-Lab: Next Generation of Optimal Chemistry Discovery by GPT-Driven Robotic Lab
- **Authors**: Xiaokai Qin, Mingda Song, Yangguan Chen, et al. (Zhejiang Laboratory)
- **Year**: 2023
- **Source**: arXiv:2309.16721
- **Key Contribution**: First integration of GPT-4 with a robotic chemistry lab for end-to-end materials discovery. Demonstrates literature mining → reagent identification → robotic synthesis pipeline.
- **Methodology**: GPT-4 analyzes 500 chemistry articles, identifies 18 potential reagents, then robotic platform synthesizes and tests candidates. High-throughput synthesis with real-time feedback.
- **Results**: Successfully produced humidity colorimetric sensor with RMSE of 2.68%; demonstrated feasibility of GPT-driven robotic experimentation
- **Datasets Used**: 500 chemistry articles (custom corpus)
- **Relevance**: Most directly analogous to our work - demonstrates LLM + robotic lab integration. Key difference: our work extends to wet-lab biology and incorporates real-time feedback adaptation.

### Paper 9: Autonomous Agents for Scientific Discovery (Texas A&M, Harvard, MIT)
- **Authors**: Lianhao Zhou, Hongyi Ling, Cong Fu, et al.
- **Year**: 2025
- **Source**: arXiv:2510.09901
- **Key Contribution**: Examines LLM-based agent orchestration across hypothesis discovery, experimental design/execution, and result analysis. Identifies open research challenges.
- **Methodology**: Critical survey with focus on practical achievements and limitations
- **Key Findings**:
  - Agents perform well on hypothesis generation and literature review
  - Physical world interaction remains the primary bottleneck
  - Multi-modal capabilities (vision + language + action) needed for wet-lab tasks
  - Real-time feedback adaptation is a key unsolved challenge
- **Relevance**: Directly identifies the research gap our work addresses: real-time feedback adaptation in physical lab settings.

### Paper 10: Large Language Models for Robotics: Opportunities, Challenges, and Perspectives
- **Authors**: Jiaqi Wang, Zihao Wu, et al. (Northwestern Polytechnical University, University of Georgia)
- **Year**: 2024
- **Source**: arXiv:2401.04334
- **Key Contribution**: Comprehensive survey of LLM integration into robotics, including task planning, manipulation, and human-robot interaction.
- **Methodology**: Survey + empirical evaluation using multimodal GPT-4V for embodied task planning
- **Key Findings**:
  - Text-only LLMs insufficient for embodied tasks (need visual grounding)
  - GPT-4V significantly enhances robot performance in embodied tasks
  - Key capability needed: combining language instructions with visual perception
  - Challenges: precise manipulation, long-horizon planning, safety
- **Relevance**: Provides the robotics foundation for our multi-modal agent. Justifies use of vision-language models for lab robot control.

---

## Common Methodologies

1. **Tool-augmented LLM Agents (ReAct framework)**: Used in ChemCrow, Agent Laboratory. LLM reasons about which tool to use, calls it, observes result, iterates. Standard pattern for scientific AI agents.

2. **Multi-agent Orchestration**: Used in Agent Laboratory, Virtual Lab, Tippy (drug discovery). Multiple specialized agents (planner, executor, analyzer) collaborate on complex tasks.

3. **Closed-loop Experimental Control**: Used in GPT-Lab, Coscientist. AI generates protocol → robot executes → sensor data fed back → AI adapts → repeat.

4. **Human-in-the-loop (co-pilot mode)**: Used in Agent Laboratory, most practical systems. Humans provide feedback at checkpoints; key finding: this significantly improves quality.

5. **Vision-Language-Action (VLA) Models**: Emerging paradigm for robot control combining visual perception + language reasoning + action generation.

---

## Standard Baselines

- **Human-designed protocols**: Gold standard; AI systems evaluated against expert human protocol quality
- **Static pre-programmed automation**: Rule-based robotic systems without AI adaptation
- **GPT-4/GPT-4o without tools**: Baseline language-only performance
- **ChemCrow**: Strongest tool-augmented LLM baseline for chemistry tasks
- **Agent Laboratory**: Strong baseline for autonomous research pipeline

---

## Evaluation Metrics

- **Protocol accuracy**: Comparison to expert-designed protocols (human evaluation)
- **Experimental efficiency**: Time to results, reagent consumption, number of iterations
- **Success rate**: Fraction of experiments reaching target outcomes
- **Feedback adaptation speed**: How quickly system adjusts to real-time data
- **Reproducibility**: Variance across repeated experiments
- **BioProBench tasks**: Protocol QA accuracy, step ordering EM, error correction F1, protocol generation BLEU
- **ScienceAgentBench**: Code correctness, execution success rate

---

## Datasets in the Literature

- **BioProBench** (2025): 27K biological protocols, 556K structured instances; 5 tasks for protocol understanding/reasoning. Most relevant to wet-lab protocol design.
- **ScienceAgentBench** (ICLR 2025): 102 scientific discovery tasks from peer-reviewed papers; evaluates end-to-end scientific programming.
- **LAB-Bench** (2024): Biology research skills benchmark (literature, databases, sequences).
- **ChemBench**: Chemistry reasoning benchmarks.
- **Custom corpora**: Most existing systems use custom chemistry article collections.

---

## Gaps and Opportunities

1. **Gap: Real-time feedback adaptation in physical wet-lab settings** — Current systems either (a) operate in silico only, or (b) use rigid pre-programmed robotic protocols without dynamic AI adaptation. Our research directly addresses this gap.

2. **Gap: Multi-modal integration for wet-lab tasks** — Most systems handle text or structured data. Wet-lab automation requires integrating visual feedback (microscopy images, colorimetric assays), sensor data (pH, temperature, OD measurements), and textual protocol understanding.

3. **Gap: Biology/wet-lab focus vs chemistry focus** — Most autonomous experiment systems focus on chemistry (synthesis, materials). Biology wet-lab automation (cell culture, assays, PCR) remains less developed.

4. **Gap: Protocol validation and error recovery** — Current systems rarely validate protocols against safety and feasibility constraints in real-time, and have limited error recovery capabilities.

5. **Gap: Comparable benchmarks** — No standardized benchmark for end-to-end wet-lab experiment autonomous execution exists. BioProBench covers protocol understanding but not execution.

---

## Recommendations for Our Experiment

**Recommended datasets**:
1. **BioProBench** (primary): Test our agent's protocol generation/understanding on established benchmark; compare against 12 existing LLMs as baselines
2. **ScienceAgentBench** (secondary): Evaluate scientific task completion capabilities

**Recommended baselines**:
1. Human-designed protocols (expert evaluation)
2. Static pre-programmed robotic automation (no AI adaptation)
3. GPT-4o/Claude 3.5 without tools (language-only)
4. ChemCrow-style tool-augmented LLM (without robotic integration)
5. Agent Laboratory (without physical execution, computational only)

**Recommended metrics**:
1. Protocol accuracy (vs. human expert protocols)
2. Experimental efficiency (time, iterations, reagent use)
3. Feedback adaptation latency and effectiveness
4. Success rate on simple biological assays (e.g., cell viability, pH measurement)
5. BioProBench scores for protocol quality

**Methodological considerations**:
1. Start with simple, well-characterized biological assays (pH measurement, cell counting, basic colorimetric tests) as proof-of-concept before complex protocols
2. Implement safety constraints as hard guardrails in the robotic control layer
3. Use closed-loop feedback (real sensor data → LLM → protocol adaptation) as the key differentiator
4. Multi-modal input: combine visual outputs (plate images) with numerical sensor readings for LLM context
5. Use Chain-of-Thought prompting for protocol design to enable interpretability
6. Document all adaptations to enable comparison of AI-adapted vs static protocols
