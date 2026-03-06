# Cloned Repositories

## Summary
3 repositories cloned covering autonomous AI research agents and scientific discovery benchmarks.

---

## Repo 1: ChemCrow
- **URL**: https://github.com/ur-whitelab/chemcrow-public
- **Purpose**: Tool-augmented LLM agent for autonomous chemistry tasks; baseline implementation
- **Location**: `code/chemcrow-public/`
- **Key Files**:
  - `chemcrow/agents/chemcrow.py` — Main agent class
  - `chemcrow/tools/` — 18 chemistry tools (molecular properties, retrosynthesis, etc.)
  - `setup.py` — Installation
- **Notes**:
  - Built on LangChain with GPT-4 backend
  - Requires OpenAI API key and optionally RXN4Chem API key
  - Public repo excludes some paper tools due to API restrictions
  - Use as baseline for tool-augmented LLM performance without robotic integration
  - Can be installed: `pip install chemcrow`

## Repo 2: Agent Laboratory
- **URL**: https://github.com/SamuelSchmidgall/AgentLaboratory
- **Purpose**: End-to-end autonomous research pipeline (Literature Review → Experiment → Report Writing)
- **Location**: `code/agent-laboratory/`
- **Key Files**:
  - `agents.py` — Specialized research agents (PhD, Postdoc)
  - `ai_lab_repo.py` — Main pipeline orchestration
  - `mlesolver.py` — ML experimentation solver
  - `papersolver.py` — Paper writing solver
  - `tools.py` — Agent tools
  - `requirements.txt` — Dependencies
- **Notes**:
  - Supports OpenAI (o1, gpt-4o) and DeepSeek backends
  - Three-stage pipeline: Literature Review → Experimentation → Report Writing
  - Also includes AgentRxiv for multi-agent research sharing
  - Key baseline: shows how autonomous research pipeline works for computational experiments
  - Relevant adaptation: extend experimentation stage to interface with physical lab robotics

## Repo 3: ScienceAgentBench
- **URL**: https://github.com/OSU-NLP-Group/ScienceAgentBench
- **Purpose**: Benchmark for evaluating AI agents on data-driven scientific discovery tasks (ICLR 2025)
- **Location**: `code/science-agent-bench/`
- **Key Files**:
  - `agent.py` — Agent evaluation harness
  - `run_eval.py` — Evaluation runner
  - `benchmark/` — Benchmark tasks (102 tasks across 4 disciplines)
  - `engine/` — Evaluation engine
  - `requirements.txt` — Dependencies
- **Notes**:
  - 102 tasks from 44 peer-reviewed publications
  - Disciplines: Computational Chemistry, Bioinformatics, Computational Physics, Neuroinformatics
  - Each task target: self-contained Python program
  - Evaluation metrics: code correctness, execution success
  - Use for evaluating our agent's scientific coding capabilities

---

## How to Use These Repositories

### ChemCrow (as baseline):
```python
from chemcrow.agents import ChemCrow
import os
os.environ["OPENAI_API_KEY"] = "your-key"

chem_model = ChemCrow(model="gpt-4o", temp=0.1)
result = chem_model.run("What is the optimal synthesis protocol for aspirin?")
```

### Agent Laboratory (as template):
```bash
cd code/agent-laboratory
pip install -r requirements.txt
python ai_lab_repo.py --research-topic "Your research idea here" --llm-backend "gpt-4o"
```

### ScienceAgentBench (for evaluation):
```bash
cd code/science-agent-bench
pip install -r requirements.txt
python run_eval.py --agent your_agent --benchmark benchmark/
```
