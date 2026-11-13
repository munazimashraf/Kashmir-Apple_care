"""Master Orchestrator for Ensemble Learning (VGG-16, VGG-19, ResNet-50, XGBoost).

Executes the two stages in separate isolated Python processes to prevent
macOS OpenMP ABI contention between PyTorch and XGBoost:
- Stage 1: Feature extraction & CNN head training (PyTorch)
- Stage 2: XGBoost training, Voting & Stacking ensembles, and benchmark evaluation
"""
import subprocess
import sys
from pathlib import Path


def main():
    repo_root = Path(__file__).resolve().parent.parent
    python_bin = sys.executable

    print("\n=======================================================")
    print("STAGE 1: Deep Feature Extraction (VGG-16, VGG-19, ResNet-50)")
    print("=======================================================\n")
    step1_script = repo_root / "ml" / "extract_and_train_cnns.py"
    res1 = subprocess.run([python_bin, str(step1_script)])
    if res1.returncode != 0:
        print(f"Stage 1 failed with exit code {res1.returncode}")
        sys.exit(res1.returncode)

    print("\n=======================================================")
    print("STAGE 2: XGBoost, Soft-Voting, Hard-Voting & Stacking")
    print("=======================================================\n")
    step2_script = repo_root / "ml" / "train_xgboost_and_ensemble.py"
    res2 = subprocess.run([python_bin, str(step2_script)])
    if res2.returncode != 0:
        print(f"Stage 2 failed with exit code {res2.returncode}")
        sys.exit(res2.returncode)

    print("\nEnsemble Learning Pipeline completed successfully!\n")


if __name__ == "__main__":
    main()
