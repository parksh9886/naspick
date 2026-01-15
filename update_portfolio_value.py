import sys
import os

# Ensure scripts directory is in path (if running from root)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.core.portfolio import PortfolioManager

if __name__ == "__main__":
    print("🔄 Portfolio Facade: Hitting PortfolioManager...")
    manager = PortfolioManager()
    manager.update_daily()
