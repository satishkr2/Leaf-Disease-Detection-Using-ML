"""Print image counts for leaf vs non-leaf dataset (no training)."""
from pathlib import Path

from train import DATA_DIR, count_images, print_dataset_summary

if __name__ == "__main__":
    print_dataset_summary()
