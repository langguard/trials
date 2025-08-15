# Trial 001: HackAPrompt Baseline Evaluation

This trial evaluates LangGuard's baseline performance against successful prompt injection attacks from the HackAPrompt dataset.

## Objective

Test LangGuard's default configuration (without custom specifications) against known successful attacks to establish a baseline detection rate and identify areas for improvement.

## Dataset

- **Source**: HackAPrompt successful attacks dataset
- **Sample Size**: 145 attacks (stratified sample) or 77,936 attacks (full dataset)
- **Attack Types**: Proven successful prompt injection attacks from competitive testing
- **Difficulty Levels**: 0-9 (0 = easiest, 9 = hardest)

## Configuration

- **LangGuard Version**: Uses pip-installed langguard library
- **Provider**: OpenAI (gpt-5-nano) or TestLLM for testing
- **Specification**: Default LangGuard security specification
- **Temperature**: 1.0 (required for GPT-5 models), 0.1 (default for other models)
- **Concurrency**: 8 concurrent workers (configurable)

## Usage

### Prerequisites

1. Install dependencies:
```bash
pip install langguard
```

2. Set up OpenAI API key (optional, will use test mode without it):
```bash
export GUARD_LLM_API_KEY="your-openai-api-key"
export GUARD_LLM_PROVIDER="openai"
```

### Running the Trial

```bash
# Run with sample dataset (recommended for initial testing)
python run_trial.py

# Run with full dataset (77k+ attacks, requires API)
python run_trial.py --full

# Run in test mode (no API calls, always fails for safety)
python run_trial.py --test

# Run with limited attacks for quick testing
python run_trial.py --limit 10

# Run with custom number of concurrent workers
python run_trial.py --workers 16

# Run with combination of options
python run_trial.py --limit 50 --workers 4
```

### Command Line Options

- `--full`: Use full dataset instead of sample (default: sample)
- `--test`: Use test mode without API calls (default: auto-detect based on API key)
- `--limit N`: Only evaluate first N attacks (useful for testing)
- `--workers N`: Number of concurrent workers (default: 8, max recommended: 16 for Tier 1)

## Expected Results

This trial will generate:

1. **`results/DD-MMM-YYYY-HH:MM:SS-results.json`** - Complete timestamped results including:
   - Trial metadata and configuration
   - Summary statistics (detection rates, timing)
   - Individual attack evaluation results
   - Breakdown by difficulty level and model

2. **Console output** - Real-time progress and summary statistics

## Evaluation Metrics

- **Overall Detection Rate**: Percentage of attacks successfully blocked
- **Detection Rate by Level**: Performance across difficulty levels (0-9)
- **Detection Rate by Level**: Performance across difficulty levels (0-9)
- **Average Evaluation Time**: Time taken to screen each prompt
- **False Positive Rate**: N/A (all test cases are known attacks)

## Results Format

```json
{
  "trial_metadata": {
    "name": "HackAPrompt Baseline Evaluation",
    "version": "001",
    "timestamp": "2025-01-15T...",
    "dataset_type": "sample",
    "test_mode": false,
    "langguard_config": {...}
  },
  "summary": {
    "total_attacks_tested": 145,
    "attacks_blocked": 120,
    "attacks_allowed": 25,
    "overall_detection_rate": 0.827,
    "detection_rate_by_level": {...},
    "detection_rate_by_level": {...},
    "average_evaluation_time_seconds": 0.45
  },
  "individual_results": [
    {
      "attack_id": "...",
      "level": 3,
      "level": 3,
      "user_input": "...",
      "langguard_response": {
        "safe": false,
        "reason": "Detected prompt injection attempt..."
      },
      "blocked": true,
      "evaluation_time_seconds": 0.42
    }
  ]
}
```

## Analysis

After running the trial, analyze the results to:

1. **Identify baseline performance** - What percentage of known attacks does LangGuard catch?
2. **Find difficulty patterns** - Do harder attacks (higher levels) bypass detection more often?
3. **Attack complexity patterns** - Are certain types of attacks harder to detect?
4. **Performance characteristics** - How fast is the evaluation process?
5. **Failure analysis** - What types of attacks slip through most often?

## Files

- `run_trial.py` - Main trial execution script
- `README.md` - This documentation  
- `results/` - Directory containing timestamped result files
  - `DD-MMM-YYYY-HH:MM:SS-results.json` - Generated results (after running)