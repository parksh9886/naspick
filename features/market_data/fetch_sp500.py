import sys
import os

# Ensure scripts directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.engine import NaspickEngine

if __name__ == "__main__":
    # Facade Pattern: Delegates all logic to the core engine
    # This maintains compatibility with GitHub Actions
    
    print("🔄 Naspick Facade: Redirecting to Core Engine...")
    app = NaspickEngine()
    app.run()
