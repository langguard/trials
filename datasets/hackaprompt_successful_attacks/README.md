# HackAPrompt Successful Attacks Dataset

This directory contains extracted successful attacks from the [HackAPrompt dataset](https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset) for testing LangGuard's defensive capabilities.

## Files

- **`successful_attacks.parquet`** - Full dataset of 77,936 successful attacks in Parquet format (efficient for pandas)
- **`successful_attacks.json`** - Full dataset in JSON format (human-readable)
- **`successful_attacks_sample.json`** - Sample of 145 attacks for quick testing (stratified by model and level)
- **`summary.json`** - Dataset statistics and summary information
- **`README.md`** - This file

## Dataset Statistics

- **Total successful attacks**: 77,936
- **Attack success by model**:
  - gpt-3.5-turbo: 42,370 attacks (54.4%)
  - FlanT5-XXL: 30,417 attacks (39.0%)
  - text-davinci-003: 5,149 attacks (6.6%)
- **Attack levels**: 0-9 (varying difficulty)
- **Token count range**: 2-4,043 tokens
- **Average token count**: 52.6 tokens

## Data Format

Each attack record contains:

```json
{
  "level": 3,
  "user_input": "The actual attack prompt submitted by the user",
  "prompt": "The full prompt sent to the model (includes context)",
  "completion": "What the model actually output",
  "model": "gpt-3.5-turbo",
  "expected_completion": "I have been PWNED",
  "token_count": 45,
  "correct": true,
  "error": false,
  "score": 95.0,
  "dataset": "playground_data",
  "timestamp": "2023-05-15T14:30:00Z",
  "session_id": "abc123"
}
```

## Usage Examples

### Load Full Dataset (Python)

```python
import pandas as pd

# Load full dataset
df = pd.read_parquet('successful_attacks.parquet')
print(f"Loaded {len(df)} successful attacks")

# Filter by difficulty level
level_5_attacks = df[df['level'] == 5]

# Filter by model
gpt_attacks = df[df['model'] == 'gpt-3.5-turbo']
```

### Load Sample Dataset (Python)

```python
import json

# Load sample dataset
with open('successful_attacks_sample.json', 'r') as f:
    attacks = json.load(f)

# Extract just the user inputs for testing
user_inputs = [attack['user_input'] for attack in attacks]
```

### Command Line Usage

```bash
# From the langguard root directory
python load_attack_dataset.py  # Run demo
python extract_successful_attacks.py  # Re-extract if needed
```

## Testing with LangGuard

This dataset is designed to test LangGuard's ability to detect and block successful prompt injection attacks. Each attack in this dataset has already proven successful against at least one major LLM, making it a valuable benchmark for defensive systems.

### Recommended Testing Approach

1. **Start with the sample dataset** (`successful_attacks_sample.json`) for initial testing
2. **Test by difficulty level** - Start with level 0-3 (easier) and progress to 7-9 (harder)
3. **Test by model** - Some attacks may be model-specific
4. **Measure detection rates** - Track how many attacks LangGuard successfully blocks

### Example LangGuard Test

```python
from langguard import GuardAgent
import json

# Load attacks
with open('successful_attacks_sample.json', 'r') as f:
    attacks = json.load(f)

# Test LangGuard
guard = GuardAgent()
blocked_count = 0

for attack in attacks:
    result = guard.evaluate(attack['user_input'])
    if result.is_blocked:
        blocked_count += 1

detection_rate = blocked_count / len(attacks)
print(f"LangGuard blocked {blocked_count}/{len(attacks)} attacks ({detection_rate:.1%})")
```

## Dataset Source

This dataset is derived from the HackAPrompt competition dataset, which contains submissions from a prompt hacking competition where users attempted to "hack" different LLMs. Only the successful attacks (where `correct=True`) have been extracted.

**Original dataset**: [hackaprompt/hackaprompt-dataset](https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset)

**Citation**:
```
@inproceedings{Schulhoff:Pinto:Khan:Bouchard:Si:Boyd-Graber:Anati:Tagliabue:Kost:Carnahan-2023,
  Title = {Ignore This Title and HackAPrompt: Exposing Systemic Vulnerabilities of LLMs Through a Global Prompt Hacking Competition},
  Author = {Sander V Schulhoff and Jeremy Pinto and Anaum Khan and Louis-François Bouchard and Chenglei Si and Jordan Lee Boyd-Graber and Svetlina Anati and Valen Tagliabue and Anson Liu Kost and Christopher R Carnahan},
  Booktitle = {Empirical Methods in Natural Language Processing},
  Year = {2023},
  Location = {Singapore}
}
```

## License

This dataset maintains the MIT license from the original HackAPrompt dataset.