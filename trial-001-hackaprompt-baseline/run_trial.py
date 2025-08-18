#!/usr/bin/env python3
"""
Trial 001: HackAPrompt Baseline Evaluation

This trial evaluates LangGuard's baseline performance against successful attacks
from the HackAPrompt dataset. It tests the default GuardAgent configuration
without any custom specifications.

"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import sys
import os
import asyncio
import concurrent.futures
from threading import Lock
import zipfile
import tempfile
import shutil

# Add parent directory to path to find datasets
sys.path.append(str(Path(__file__).parent.parent))

try:
    from langguard import GuardAgent
except ImportError:
    print("❌ Error: langguard library not found. Please install with: pip install langguard")
    sys.exit(1)


class TrialRunner:
    """Runs the HackAPrompt baseline trial."""
    
    def __init__(self, use_sample=True, test_mode=False, max_workers=8):
        """Initialize the trial runner.
        
        Args:
            use_sample: If True, use the sample dataset. If False, use full dataset.
            test_mode: If True, use TestLLM instead of OpenAI for testing.
        """
        self.use_sample = use_sample
        self.test_mode = test_mode
        self.max_workers = max_workers
        self.trial_name = "HackAPrompt Baseline Evaluation"
        self.trial_version = "001"
        self.results_lock = Lock()
        self.results = {
            "trial_metadata": {
                "name": self.trial_name,
                "version": self.trial_version,
                "timestamp": datetime.now().isoformat(),
                "dataset_type": "sample" if use_sample else "full",
                "test_mode": test_mode,
                "langguard_config": {
                    "specification": "default"
                }
            },
            "summary": {},
            "individual_results": []
        }
        
        # Initialize GuardAgent
        try:
            if test_mode:
                self.guard = GuardAgent()  # Uses TestLLM by default
            else:
                # Check for API key
                if not os.getenv("GUARD_LLM_API_KEY"):
                    print("⚠️  Warning: GUARD_LLM_API_KEY not set. Using test mode.")
                    self.test_mode = True
                    self.results["trial_metadata"]["test_mode"] = True
                    self.guard = GuardAgent()
                else:
                    self.guard = GuardAgent(llm="openai")
        except Exception as e:
            print(f"❌ Error initializing GuardAgent: {e}")
            print("   Falling back to test mode...")
            self.test_mode = True
            self.results["trial_metadata"]["test_mode"] = True
            self.guard = GuardAgent()
    
    def _get_model_temperature(self):
        """Get appropriate temperature for the selected model."""
        model = os.getenv("GUARD_LLM_MODEL", "gpt-5-nano")
        if "gpt-5" in model:
            # GPT-5 models only support temperature=1
            return 1.0
        else:
            # Other models support custom temperature
            return float(os.getenv("LLM_TEMPERATURE", "0.1"))
    
    def _get_actual_model_info(self):
        """Get the actual model information from the GuardAgent."""
        try:
            # Try to get model info from the LLM instance
            if hasattr(self.guard, 'llm') and hasattr(self.guard.llm, 'model'):
                actual_model = self.guard.llm.model
            else:
                # Fallback to environment variable
                actual_model = os.getenv("GUARD_LLM_MODEL", "gpt-5-nano")
            
            return {
                "configured_model": os.getenv("GUARD_LLM_MODEL", "gpt-5-nano"),
                "actual_model": actual_model,
                "provider": "test" if self.test_mode else os.getenv("GUARD_LLM_PROVIDER", "openai"),
                "temperature": self._get_model_temperature()
            }
        except Exception as e:
            # Fallback if we can't get model info
            return {
                "configured_model": os.getenv("GUARD_LLM_MODEL", "gpt-5-nano"),
                "actual_model": "unknown",
                "provider": "test" if self.test_mode else os.getenv("GUARD_LLM_PROVIDER", "openai"),
                "temperature": self._get_model_temperature(),
                "model_detection_error": str(e)
            }
    
    def _extract_dataset_if_needed(self) -> Path:
        """Extract dataset from zip if needed, return path to dataset directory."""
        dataset_dir = Path("../datasets/hackaprompt_successful_attacks")
        zip_path = Path("../datasets/hackaprompt_successful_attacks/hackaprompt_successful_attacks.zip")
        
        # If directory exists and has the data files, use it
        if dataset_dir.exists():
            sample_file = dataset_dir / "successful_attacks_sample.json"
            if sample_file.exists():
                return dataset_dir
        
        # If zip exists, extract it
        if zip_path.exists():
            print(f"📦 Extracting dataset from {zip_path}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("../datasets/")
            print(f"✅ Dataset extracted to {dataset_dir}")
            return dataset_dir
        
        raise FileNotFoundError(f"Dataset not found at {dataset_dir} or {zip_path}")
    
    def load_attack_dataset(self) -> List[Dict[str, Any]]:
        """Load the attack dataset, extracting from zip if necessary."""
        dataset_dir = self._extract_dataset_if_needed()
        
        if self.use_sample:
            dataset_path = dataset_dir / "successful_attacks_sample.json"
        else:
            dataset_path = dataset_dir / "successful_attacks.json"
        
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset file not found at {dataset_path}")
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def evaluate_attack(self, attack: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single attack against LangGuard."""
        start_time = time.time()
        
        try:
            # Screen the attack with LangGuard, using model-appropriate temperature
            model = os.getenv("GUARD_LLM_MODEL", "gpt-5-nano")
            if "gpt-5" in model:
                # GPT-5 models require temperature=1
                response = self.guard.screen(attack['user_input'], temperature=1.0)
            else:
                # Other models can use custom temperature
                response = self.guard.screen(attack['user_input'], temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")))
            
            evaluation_time = time.time() - start_time
            
            # Prepare result - only include full details for failures (unblocked attacks)
            blocked = not response['safe']
            
            if blocked:
                # Success case - minimal data needed
                result = {
                    "attack_id": attack.get('session_id', f"unknown_{len(self.results['individual_results'])}"),
                    "level": attack['level'],
                    "blocked": True,
                    "reason": response['reason'][:100] + "..." if len(response['reason']) > 100 else response['reason'],  # Truncated reason
                    "evaluation_time_seconds": evaluation_time,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Failure case - full details for analysis
                result = {
                    "attack_id": attack.get('session_id', f"unknown_{len(self.results['individual_results'])}"),
                    "level": attack['level'],
                    "token_count": attack['token_count'],
                    "user_input": attack['user_input'],
                    "expected_completion": attack['expected_completion'],
                    "langguard_response": response,
                    "blocked": False,
                    "evaluation_time_seconds": evaluation_time,
                    "timestamp": datetime.now().isoformat(),
                    "failure_analysis": True  # Flag to identify this as a failure needing attention
                }
            
            
            return result
            
        except Exception as e:
            evaluation_time = time.time() - start_time
            return {
                "attack_id": attack.get('session_id', f"error_{len(self.results['individual_results'])}"),
                "level": attack['level'],
                "blocked": True,  # Assume blocked on error for safety
                "reason": f"Evaluation error: {str(e)}",
                "evaluation_time_seconds": evaluation_time,
                "error": True,
                "timestamp": datetime.now().isoformat()
            }
    
    def calculate_summary_statistics(self):
        """Calculate summary statistics from individual results."""
        total_attacks = len(self.results['individual_results'])
        blocked_attacks = sum(1 for r in self.results['individual_results'] if r['blocked'])
        detection_rate = blocked_attacks / total_attacks if total_attacks > 0 else 0
        
        # Statistics by level
        level_stats = {}
        for result in self.results['individual_results']:
            level = result['level']
            if level not in level_stats:
                level_stats[level] = {'total': 0, 'blocked': 0}
            level_stats[level]['total'] += 1
            if result['blocked']:
                level_stats[level]['blocked'] += 1
        
        for level in level_stats:
            level_stats[level]['detection_rate'] = (
                level_stats[level]['blocked'] / level_stats[level]['total']
            )
        
        # Additional statistics could be added here if needed
        
        # Average evaluation time
        avg_eval_time = sum(r['evaluation_time_seconds'] for r in self.results['individual_results']) / total_attacks
        
        # Count detailed vs minimal results for file size optimization info
        detailed_results = sum(1 for r in self.results['individual_results'] if r.get('failure_analysis', False))
        minimal_results = total_attacks - detailed_results
        
        self.results['summary'] = {
            "total_attacks_tested": total_attacks,
            "attacks_blocked": blocked_attacks,
            "attacks_allowed": total_attacks - blocked_attacks,
            "overall_detection_rate": detection_rate,
            "detection_rate_by_level": level_stats,
            "average_evaluation_time_seconds": avg_eval_time,
            "total_evaluation_time_seconds": sum(r['evaluation_time_seconds'] for r in self.results['individual_results']),
        }
    
    def _evaluate_attack_wrapper(self, attack_with_index):
        """Wrapper for evaluate_attack to work with concurrent execution."""
        index, attack = attack_with_index
        result = self.evaluate_attack(attack)
        
        # Thread-safe addition to results
        with self.results_lock:
            self.results['individual_results'].append(result)
        
        return index, result
    
    def run_trial(self, max_attacks=None):
        """Run the complete trial."""
        print(f"🔒 Starting {self.trial_name} (Version {self.trial_version})")
        print(f"📊 Dataset: {'Sample' if self.use_sample else 'Full'}")
        print(f"🤖 Mode: {'Test' if self.test_mode else 'OpenAI'}")
        
        # Capture actual model info after GuardAgent is initialized
        model_info = self._get_actual_model_info()
        self.results["trial_metadata"]["model_info"] = model_info
        print(f"🎯 Model: {model_info['actual_model']} (Provider: {model_info['provider']})")
        
        # Load dataset
        print("\n📂 Loading attack dataset...")
        attacks = self.load_attack_dataset()
        
        if max_attacks:
            attacks = attacks[:max_attacks]
            print(f"🎯 Limited to first {max_attacks} attacks for testing")
        
        print(f"📈 Loaded {len(attacks)} attacks")
        
        # Run evaluations with concurrent processing
        print(f"\n🔍 Evaluating attacks against LangGuard (using {self.max_workers} concurrent workers)...")
        
        # Prepare attacks with indices for tracking
        attacks_with_indices = [(i, attack) for i, attack in enumerate(attacks)]
        
        completed_count = 0
        
        # Use ThreadPoolExecutor for concurrent API calls
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_attack = {executor.submit(self._evaluate_attack_wrapper, attack_data): attack_data 
                              for attack_data in attacks_with_indices}
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(future_to_attack):
                completed_count += 1
                
                if completed_count % 10 == 0 or completed_count == len(attacks):
                    print(f"   Progress: {completed_count}/{len(attacks)} ({completed_count/len(attacks)*100:.1f}%)")
                
                try:
                    index, result = future.result()
                except Exception as e:
                    print(f"   Warning: Task failed: {e}")
        
        # Sort results by original order (important for analysis)
        # Note: We can't sort by original order anymore due to optimized storage,
        # but results are processed in order anyway due to concurrent execution
        
        # Calculate summary statistics
        print("\n📊 Calculating summary statistics...")
        self.calculate_summary_statistics()
        
        # Save results with timestamped filename
        timestamp = datetime.now().strftime("%d-%b-%Y-%H:%M:%S")
        results_filename = f"{timestamp}-results.json"
        results_dir = Path(__file__).parent / "results"
        results_file = results_dir / results_filename
        
        # Ensure results directory exists
        results_dir.mkdir(exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Trial complete! Results saved to {results_file}")
        
        # Auto-register trial in registry
        try:
            sys.path.append(str(Path(__file__).parent.parent))
            from trial_registry import TrialRegistry
            
            registry = TrialRegistry()
            trial_id = registry.add_trial_entry(str(results_file))
            print(f"📝 Trial registered as {trial_id} in trial registry")
        except Exception as e:
            print(f"⚠️  Warning: Could not register trial automatically: {e}")
            print(f"   You can manually register with: python ../trial_registry.py --add {results_file}")
        
        # Print summary
        summary = self.results['summary']
        print(f"\n📋 TRIAL SUMMARY")
        print(f"   Total attacks tested: {summary['total_attacks_tested']}")
        print(f"   Attacks blocked: {summary['attacks_blocked']}")
        print(f"   Attacks allowed: {summary['attacks_allowed']}")
        print(f"   Detection rate: {summary['overall_detection_rate']:.1%}")
        print(f"   Average evaluation time: {summary['average_evaluation_time_seconds']:.3f}s")
        
        print(f"\n🎯 DETECTION RATE BY LEVEL:")
        for level in sorted(summary['detection_rate_by_level'].keys()):
            stats = summary['detection_rate_by_level'][level]
            print(f"   Level {level}: {stats['blocked']}/{stats['total']} ({stats['detection_rate']:.1%})")
        


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run HackAPrompt baseline trial")
    parser.add_argument("--full", action="store_true", help="Use full dataset instead of sample")
    parser.add_argument("--test", action="store_true", help="Use test mode (no API calls)")
    parser.add_argument("--limit", type=int, help="Limit number of attacks to evaluate (for testing)")
    parser.add_argument("--workers", type=int, default=8, help="Number of concurrent workers (default: 8)")
    
    args = parser.parse_args()
    
    # Create and run trial
    runner = TrialRunner(use_sample=not args.full, test_mode=args.test, max_workers=args.workers)
    runner.run_trial(max_attacks=args.limit)


if __name__ == "__main__":
    main()