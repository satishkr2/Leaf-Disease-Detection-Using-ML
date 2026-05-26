"""
Build leaf detector: prepares dataset (if needed) and trains a small binary model.

Run from project root:
  python model/leaf_detector/create_demo_model.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    prepare = Path(__file__).parent / "prepare_dataset.py"
    train = Path(__file__).parent / "train.py"

    print("=== Preparing leaf / non-leaf dataset ===")
    subprocess.check_call([sys.executable, str(prepare)])

    print("\n=== Training leaf detector ===")
    subprocess.check_call([sys.executable, str(train)])

    print("\nDone! Restart the backend to load the new model.")


if __name__ == "__main__":
    main()
