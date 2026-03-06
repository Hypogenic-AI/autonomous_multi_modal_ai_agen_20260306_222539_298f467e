# Datasets for Autonomous Multi-Modal AI Agent Research

This directory contains datasets for the research project on autonomous AI agents for wet-lab
experiment design and execution. Data files are NOT committed to git due to size. Follow the
download instructions below.

## Dataset 1: BioProBench

### Overview
- **Source**: HuggingFace - `GreatCaptainNemo/BioProBench`
- **Size**: 27K protocols, 556K structured instances, 1K test examples per task
- **Format**: HuggingFace Dataset
- **Task**: Biological protocol understanding and reasoning
- **Splits**: test (5 tasks × 1K examples each)
- **License**: Open (research use)

### Relevance to Research
BioProBench is highly relevant because it:
1. Evaluates AI models on biological protocol understanding - directly applicable to wet-lab experiment design
2. Covers 5 tasks: Protocol QA, Step Ordering, Error Correction, Protocol Generation, Protocol Reasoning
3. Built on 27K real biological protocols - represents the domain of wet-lab protocols
4. Enables evaluation of how well an AI agent understands and generates lab protocols

### Download Instructions

**Using HuggingFace (recommended):**
```python
from datasets import load_dataset

# Error Correction task (most relevant for wet-lab quality control)
dataset = load_dataset("GreatCaptainNemo/BioProBench", split="test")
dataset.save_to_disk("datasets/bioprobench")
```

**Alternative datasets (same source):**
```python
# Full benchmark with all 5 tasks
dataset = load_dataset("BioProBench/BioProBench")
```

### Loading the Dataset

Once downloaded, load with:
```python
from datasets import load_from_disk
dataset = load_from_disk("datasets/bioprobench")
```

### Sample Data

Example record from this dataset (Error Correction task):
```json
{
  "context": {"next_step": "Daily medium exchange", "prior_step": "Preparation of vitronectin-coated plates", "purpose": "Maintain hESCs"},
  "corrupted_text": "Maintain hESCs in Nutristem medium on 0.5u/cm^2 vitronectin... (37°C, 10% CO2)",
  "corrected_text": "Maintain hESCs in Nutristem medium on 0.5u/cm^2 vitronectin... (37°C, 5% CO2)",
  "is_correct": false,
  "type": "parameter",
  "error_description": "CO2 concentration is critical for maintaining pH balance"
}
```

### Notes
- The Error Correction task is most directly relevant to validating AI-generated protocols
- Protocol Generation task tests ability to generate lab protocols from scratch
- Small sample files available in `datasets/bioprobench/samples.json`

---

## Dataset 2: ScienceAgentBench

### Overview
- **Source**: HuggingFace - `osunlp/ScienceAgentBench`
- **Size**: 102 tasks from 44 peer-reviewed publications
- **Format**: HuggingFace Dataset
- **Task**: Scientific data analysis programming tasks
- **Splits**: validation (102 tasks)
- **License**: CC Attribution 4.0 (most tasks); MIT (code)
- **Paper**: arXiv:2410.05080 (ICLR 2025)

### Relevance to Research
ScienceAgentBench is relevant because it:
1. Evaluates AI agents on end-to-end scientific discovery tasks
2. Tasks span Computational Chemistry, Bioinformatics, and other scientific domains
3. Validates agent ability to write reproducible scientific code
4. Represents the current state-of-the-art benchmark for scientific AI agents

### Download Instructions

**Using HuggingFace (annotation sheet only):**
```python
from datasets import load_dataset
dataset = load_dataset("osunlp/ScienceAgentBench", split="validation")
dataset.save_to_disk("datasets/scienceagentbench")
```

**Full benchmark (including datasets and gold programs):**
```bash
# From: https://github.com/OSU-NLP-Group/ScienceAgentBench
git clone https://github.com/OSU-NLP-Group/ScienceAgentBench
# Then download full benchmark data separately (see their README)
```

### Loading the Dataset

```python
from datasets import load_from_disk
dataset = load_from_disk("datasets/scienceagentbench")
```

### Sample Data

Example task from this dataset:
```json
{
  "instance_id": 1,
  "domain": "Computational Chemistry",
  "subtask_categories": "Feature Engineering, Deep Learning",
  "task_inst": "Train a multitask model on the Clintox dataset to predict drug toxicity and FDA approval status...",
  "domain_knowledge": "The ClinTox dataset contains drugs approved by the FDA..."
}
```

### Notes
- The validation split has 102 tasks across 4 scientific domains
- Computational Chemistry tasks are most relevant to our wet-lab research
- Full benchmark requires password `scienceagentbench` to extract
- Small sample files available in `datasets/scienceagentbench/samples.json`

---

## Dataset 3: LAB-Bench (Recommended for Future Use)

### Overview
- **Source**: Laurent et al., 2024
- **Size**: Large multiple-choice benchmark
- **Format**: Biology research skills evaluation
- **Task**: Literature reasoning, database navigation, figure interpretation, sequence manipulation
- **Relevance**: Tests practical biology research skills needed for wet-lab automation

### Download Instructions

```python
# Paper: https://arxiv.org/abs/2407.10362
# Check for HuggingFace release or contact authors
from datasets import load_dataset
dataset = load_dataset("futurehouse/lab-bench")
```

---

## Recommendations for Experiment Design

Based on gathered datasets:

1. **Primary dataset**: **BioProBench** - Directly tests biological protocol understanding/generation which is core to wet-lab experiment design
   - Focus on Protocol Generation task to test AI's ability to create lab protocols
   - Use Error Correction task to test quality control capabilities
   - Dataset available immediately via HuggingFace

2. **Secondary dataset**: **ScienceAgentBench** - Tests end-to-end scientific task completion including code generation
   - Provides standardized evaluation framework
   - Covers computational chemistry relevant to wet-lab workflows

3. **Baseline comparison**: Use BioProBench results from 12 existing LLMs as baselines to compare against our multi-modal agent system
