#!/usr/bin/env python3
"""
Trial Registry System

Maintains a centralized record of all trial runs including dates, results summaries,
and LangGuard versions used.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Try to import langguard to get version
try:
    import langguard
    LANGGUARD_VERSION = langguard.__version__
except ImportError:
    LANGGUARD_VERSION = "unknown"


class TrialRegistry:
    """Manages the trial registry file and entries."""
    
    def __init__(self, registry_file: str = "trial_registry.json"):
        self.registry_file = Path(__file__).parent / registry_file
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load existing registry or create new one."""
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "registry_metadata": {
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "total_trials": 0
                },
                "trials": []
            }
    
    def _save_registry(self):
        """Save registry to file."""
        self.registry["registry_metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
    
    def add_trial_entry(self, trial_results_file: str) -> str:
        """Add a new trial entry from results file."""
        # Load trial results
        results_path = Path(trial_results_file)
        if not results_path.exists():
            raise FileNotFoundError(f"Trial results file not found: {trial_results_file}")
        
        with open(results_path, 'r', encoding='utf-8') as f:
            trial_data = json.load(f)
        
        # Extract key information for registry
        trial_metadata = trial_data.get("trial_metadata", {})
        summary = trial_data.get("summary", {})
        
        # Create registry entry
        registry_entry = {
            "trial_id": f"trial-{len(self.registry['trials']) + 1:03d}",
            "trial_name": trial_metadata.get("name", "Unknown Trial"),
            "trial_version": trial_metadata.get("version", "unknown"),
            "date_run": trial_metadata.get("timestamp", datetime.now().isoformat()),
            "langguard_version": LANGGUARD_VERSION,
            "configuration": {
                "dataset_type": trial_metadata.get("dataset_type", "unknown"),
                "test_mode": trial_metadata.get("test_mode", False),
                "langguard_config": trial_metadata.get("langguard_config", {})
            },
            "results_summary": {
                "total_attacks_tested": summary.get("total_attacks_tested", 0),
                "attacks_blocked": summary.get("attacks_blocked", 0),
                "overall_detection_rate": summary.get("overall_detection_rate", 0.0),
                "average_evaluation_time_seconds": summary.get("average_evaluation_time_seconds", 0.0)
            },
            "results_file": str(results_path.relative_to(Path(__file__).parent)),
            "trial_directory": str(results_path.parent.relative_to(Path(__file__).parent))
        }
        
        # Add to registry
        self.registry["trials"].append(registry_entry)
        self.registry["registry_metadata"]["total_trials"] = len(self.registry["trials"])
        
        # Save registry
        self._save_registry()
        
        return registry_entry["trial_id"]
    
    def get_trial_by_id(self, trial_id: str) -> Optional[Dict[str, Any]]:
        """Get trial entry by ID."""
        for trial in self.registry["trials"]:
            if trial["trial_id"] == trial_id:
                return trial
        return None
    
    def list_trials(self, recent_first: bool = True) -> list:
        """List all trials, optionally sorted by date."""
        trials = self.registry["trials"].copy()
        if recent_first:
            trials.sort(key=lambda x: x["date_run"], reverse=True)
        return trials
    
    def get_trials_by_version(self, langguard_version: str) -> list:
        """Get all trials run with a specific LangGuard version."""
        return [trial for trial in self.registry["trials"] 
                if trial["langguard_version"] == langguard_version]
    
    def print_registry_summary(self):
        """Print a summary of the trial registry."""
        print("🗂️  LangGuard Trial Registry")
        print("=" * 50)
        
        metadata = self.registry["registry_metadata"]
        print(f"📅 Created: {metadata['created'][:10]}")
        print(f"🔄 Last Updated: {metadata['last_updated'][:10]}")
        print(f"📊 Total Trials: {metadata['total_trials']}")
        
        if metadata['total_trials'] > 0:
            print(f"\n📋 Recent Trials:")
            for trial in self.list_trials()[:5]:  # Show last 5 trials
                date = trial["date_run"][:10]
                name = trial["trial_name"]
                version = trial["trial_version"]
                detection_rate = trial["results_summary"]["overall_detection_rate"]
                langguard_ver = trial["langguard_version"]
                
                print(f"   {trial['trial_id']} | {date} | {name} v{version}")
                print(f"      Detection Rate: {detection_rate:.1%} | LangGuard: {langguard_ver}")
                print()
    
    def export_summary_csv(self, output_file: str = "trial_summary.csv"):
        """Export trial summary to CSV."""
        import csv
        
        output_path = Path(__file__).parent / output_file
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'trial_id', 'trial_name', 'trial_version', 'date_run', 
                'langguard_version', 'dataset_type', 'total_attacks_tested',
                'attacks_blocked', 'overall_detection_rate', 'average_evaluation_time_seconds'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for trial in self.registry["trials"]:
                row = {
                    'trial_id': trial['trial_id'],
                    'trial_name': trial['trial_name'],
                    'trial_version': trial['trial_version'],
                    'date_run': trial['date_run'][:10],
                    'langguard_version': trial['langguard_version'],
                    'dataset_type': trial['configuration']['dataset_type'],
                    'total_attacks_tested': trial['results_summary']['total_attacks_tested'],
                    'attacks_blocked': trial['results_summary']['attacks_blocked'],
                    'overall_detection_rate': trial['results_summary']['overall_detection_rate'],
                    'average_evaluation_time_seconds': trial['results_summary']['average_evaluation_time_seconds']
                }
                writer.writerow(row)
        
        print(f"📄 Trial summary exported to {output_path}")


def main():
    """Command line interface for trial registry."""
    import argparse
    
    parser = argparse.ArgumentParser(description="LangGuard Trial Registry Management")
    parser.add_argument("--add", help="Add trial results file to registry")
    parser.add_argument("--list", action="store_true", help="List all trials")
    parser.add_argument("--summary", action="store_true", help="Show registry summary")
    parser.add_argument("--export-csv", action="store_true", help="Export summary to CSV")
    parser.add_argument("--version", help="List trials by LangGuard version")
    
    args = parser.parse_args()
    
    registry = TrialRegistry()
    
    if args.add:
        try:
            trial_id = registry.add_trial_entry(args.add)
            print(f"✅ Added trial {trial_id} to registry")
        except Exception as e:
            print(f"❌ Error adding trial: {e}")
    
    elif args.list:
        trials = registry.list_trials()
        if trials:
            print("📋 All Trials:")
            for trial in trials:
                date = trial["date_run"][:10]
                print(f"   {trial['trial_id']} | {date} | {trial['trial_name']} v{trial['trial_version']}")
        else:
            print("📋 No trials found in registry")
    
    elif args.version:
        trials = registry.get_trials_by_version(args.version)
        if trials:
            print(f"📋 Trials using LangGuard {args.version}:")
            for trial in trials:
                date = trial["date_run"][:10]
                print(f"   {trial['trial_id']} | {date} | {trial['trial_name']} v{trial['trial_version']}")
        else:
            print(f"📋 No trials found using LangGuard {args.version}")
    
    elif args.export_csv:
        registry.export_summary_csv()
    
    else:
        registry.print_registry_summary()


if __name__ == "__main__":
    main()