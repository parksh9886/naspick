import sys
import os

# Ensure scripts directory is in path (if running from root)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.core.consensus import ConsensusManager

if __name__ == "__main__":
    print("🔄 Consensus Facade: Hitting ConsensusManager...")
    manager = ConsensusManager()
    manager.fetch_all_consensus()
