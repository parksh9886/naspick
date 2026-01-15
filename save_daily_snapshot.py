import sys
import os

# Ensure scripts directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.core.engine import NaspickEngine

def main():
    print("📸 Triggering Daily Snapshot via Engine...")
    eng = NaspickEngine()
    eng.save_snapshot()

if __name__ == "__main__":
    main()
