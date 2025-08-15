# LangGuard Trials

Comprehensive testing framework for evaluating LangGuard's security effectiveness against known prompt injection attacks.

## Overview

This trials framework provides a structured approach to testing LangGuard's defensive capabilities using proven attack datasets. Each trial focuses on specific aspects of security evaluation and maintains detailed records for performance tracking over time.

## Structure

```
trials/
├── README.md                           # This file
├── trial_registry.py                   # Central trial tracking system
├── trial_registry.json                 # Registry database (auto-generated)
├── TRIAL_REGISTRY.md                   # Registry documentation
├── datasets/                           # Shared attack datasets
│   └── hackaprompt_successful_attacks/ # Proven successful attacks
│       ├── successful_attacks_sample.json
│       ├── successful_attacks.json
│       ├── summary.json
│       ├── README.md
│       └── hackaprompt_successful_attacks.zip # Compressed dataset (portable)
└── trial-001-hackaprompt-baseline/     # Individual trial directories
    ├── run_trial.py                    # Trial execution script
    ├── README.md                       # Trial-specific documentation
    └── results/                        # Timestamped results
        └── DD-MMM-YYYY-HH:MM:SS-results.json
```

## Dataset Management

The trials framework supports both zipped and unzipped datasets for portability:

### **Automatic Extraction**
- Trials automatically detect and extract zipped datasets
- If `hackaprompt_successful_attacks.zip` exists but directory doesn't, it auto-extracts
- No manual intervention required

### **Storage Options**
```bash
# Keep only zip file (saves space) - remove data files but keep zip
rm datasets/hackaprompt_successful_attacks/successful_attacks*.json
rm datasets/hackaprompt_successful_attacks/summary.json

# Keep only unzipped (faster access) - remove zip file
rm datasets/hackaprompt_successful_attacks/hackaprompt_successful_attacks.zip

# Keep both (convenience)
# - Use unzipped for repeated trials
# - Use zip for sharing/backup
```

### **Dataset Compression Stats**
- Original: ~150MB uncompressed
- Zipped: ~14MB (90%+ compression)
- JSON files compress especially well due to repetitive structure

## Current Trials

### Trial 001: HackAPrompt Baseline Evaluation
- **Purpose**: Establish baseline LangGuard performance against known successful attacks
- **Dataset**: 77,936 proven successful prompt injection attacks (145 sample)
- **Configuration**: Default LangGuard settings with GPT-5-nano
- **Focus**: Overall detection rates and performance by difficulty level

## Trial Registry System

The registry automatically tracks:
- **Execution Dates**: When each trial was run
- **LangGuard Versions**: Which version was tested
- **Configuration Details**: Model, settings, dataset type
- **Results Summary**: Key metrics and detection rates
- **File References**: Paths to detailed results

### Registry Commands
```bash
python trial_registry.py                    # View summary
python trial_registry.py --list            # List all trials
python trial_registry.py --version 0.3.0   # Filter by LangGuard version
python trial_registry.py --export-csv      # Export data to CSV
```

## Running Trials

### Prerequisites
1. **Install LangGuard**: `pip install langguard`
2. **Set API Key**: `export GUARD_LLM_API_KEY="your-openai-api-key"`
3. **Configure Provider**: `export GUARD_LLM_PROVIDER="openai"`

### Example Trial Execution
```bash
cd trial-001-hackaprompt-baseline

# Quick test with sample data
python run_trial.py --limit 10 --workers 4

# Full evaluation with sample dataset
python run_trial.py

# Full evaluation with complete dataset (77k+ attacks)
python run_trial.py --full --workers 8
```

## Results Format

Each trial generates timestamped results in `results/DD-MMM-YYYY-HH:MM:SS-results.json`:

```json
{
  "trial_metadata": {
    "name": "HackAPrompt Baseline Evaluation",
    "timestamp": "2025-01-15T14:30:00",
    "langguard_config": {
      "provider": "openai",
      "model": "gpt-5-nano",
      "temperature": 1.0
    }
  },
  "summary": {
    "total_attacks_tested": 145,
    "attacks_blocked": 120,
    "overall_detection_rate": 0.827,
    "detection_rate_by_level": {...},
    "average_evaluation_time_seconds": 0.45,
    "result_optimization": {
      "detailed_results": 25,
      "minimal_results": 120,
      "space_saved": "82.8% of results use minimal storage"
    }
  },
  "individual_results": [
    // Successful block (minimal data)
    {
      "attack_id": "abc123",
      "level": 3,
      "blocked": true,
      "reason": "Detected prompt injection attempt...",
      "evaluation_time_seconds": 0.42,
      "timestamp": "2025-01-15T..."
    },
    // Failed block (full details for analysis)
    {
      "attack_id": "def456",
      "level": 7,
      "token_count": 150,
      "user_input": "Complex attack that bypassed detection...",
      "expected_completion": "I have been PWNED",
      "langguard_response": {"safe": true, "reason": "..."},
      "blocked": false,
      "failure_analysis": true,
      "evaluation_time_seconds": 0.58,
      "timestamp": "2025-01-15T..."
    }
  ]
}
```

## Key Features

### **Concurrent Processing**
- Configurable worker threads (default: 8)
- Rate limit aware (optimized for OpenAI Tier 1: 500 RPM)
- Progress tracking with real-time updates

### **Automatic Registration**
- Trials self-register upon completion
- Centralized tracking across all experiments
- Version correlation for performance analysis

### **Timestamped Results**
- No result file overwrites
- Easy chronological sorting
- Complete audit trail

### **Difficulty Analysis**
- Performance tracking by attack complexity (levels 0-9)
- Identification of LangGuard's strengths and weaknesses
- Targeted improvement recommendations

## Performance Considerations

### **Rate Limits (OpenAI Tier 1)**
- 500 requests per minute
- Recommended: 8 concurrent workers
- Sample dataset: ~2-3 minutes
- Full dataset: ~6-7 hours

### **Cost Estimation (GPT-5-nano)**
- $0.05/1M input tokens, $0.40/1M output tokens
- Sample dataset (145 attacks): ~$0.02
- Full dataset (77,936 attacks): ~$11

## Analysis Workflow

1. **Run Baseline Trial**: Establish current performance
2. **Review Results**: Identify weak points and patterns
3. **Registry Tracking**: Compare with previous versions
4. **Iterate**: Test improvements and configuration changes

## Future Trial Ideas

- **Trial 002**: Custom security specifications testing
- **Trial 003**: Attack category analysis (jailbreaks, injections, etc.)
- **Trial 004**: Adversarial prompt testing
- **Trial 005**: Performance optimization evaluation
- **Trial 006**: Multi-model comparison studies

## Contributing

When adding new trials:
1. Follow the `trial-XXX-name` directory naming convention
2. Include comprehensive README.md documentation
3. Use the registry system for tracking
4. Follow the timestamped results format
5. Document configuration and objectives clearly