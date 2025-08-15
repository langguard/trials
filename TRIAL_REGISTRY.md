# LangGuard Trial Registry

The trial registry system maintains a centralized record of all trial runs, tracking dates, results summaries, and LangGuard versions used.

## Overview

Each trial run is automatically registered with:
- **Trial ID**: Unique identifier (trial-001, trial-002, etc.)
- **Date/Time**: When the trial was executed
- **LangGuard Version**: Version of LangGuard used
- **Configuration**: Dataset type, model settings, etc.
- **Results Summary**: Key metrics (detection rate, timing, etc.)
- **File References**: Path to detailed results

## Usage

### View Registry Summary
```bash
python trial_registry.py
```

### List All Trials
```bash
python trial_registry.py --list
```

### Add Trial Manually
```bash
python trial_registry.py --add trial-001-hackaprompt-baseline/trial_results.json
```

### Filter by LangGuard Version
```bash
python trial_registry.py --version 0.3.0
```

### Export to CSV
```bash
python trial_registry.py --export-csv
```

## Registry File Format

The registry is stored in `trial_registry.json`:

```json
{
  "registry_metadata": {
    "created": "2025-01-15T...",
    "last_updated": "2025-01-15T...",
    "total_trials": 3
  },
  "trials": [
    {
      "trial_id": "trial-001",
      "trial_name": "HackAPrompt Baseline Evaluation",
      "trial_version": "001",
      "date_run": "2025-01-15T14:30:00",
      "langguard_version": "0.3.0",
      "configuration": {
        "dataset_type": "sample",
        "test_mode": false,
        "langguard_config": {
          "provider": "openai",
          "model": "gpt-5-nano",
          "temperature": 1.0
        }
      },
      "results_summary": {
        "total_attacks_tested": 145,
        "attacks_blocked": 120,
        "overall_detection_rate": 0.827,
        "average_evaluation_time_seconds": 0.45
      },
      "results_file": "trial-001-hackaprompt-baseline/trial_results.json",
      "trial_directory": "trial-001-hackaprompt-baseline"
    }
  ]
}
```

## Automatic Registration

Trial scripts automatically register themselves when they complete successfully. If auto-registration fails, you'll see a warning with manual registration instructions.

## Benefits

- **Track Progress**: See how LangGuard performance evolves over time
- **Version Comparison**: Compare results across different LangGuard versions
- **Experiment Management**: Maintain organized records of all trials
- **Data Export**: Generate reports and summaries for analysis