
import subprocess
import sys
import os
import time

def run_step(script_relative_path, step_name):
    """Runs a python script and handles errors."""
    print(f"\n{'='*60}")
    print(f"🚀 STARTING STEP: {step_name}")
    print(f"📂 Script: {script_relative_path}")
    print(f"{'='*60}\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, script_relative_path)
    
    if not os.path.exists(script_path):
        print(f"❌ Error: Script not found at {script_path}")
        sys.exit(1)

    start_time = time.time()
    try:
        # Force UTF-8 encoding for the subprocess to handle emojis correctly on Windows
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        # Use simple python command invocation
        cmd = [sys.executable, script_path]
        
        # Stream output to console
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True, 
            encoding='utf-8',
            errors='replace',
            env=env
        )
        
        # Read output in real-time
        for line in process.stdout:
            print(line, end='')
            
        return_code = process.wait()
        
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, cmd)
            
        duration = time.time() - start_time
        print(f"\n✅ FINISHED STEP: {step_name} (took {duration:.1f}s)")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ FAILED STEP: {step_name}")
        print(f"Error Code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR in {step_name}: {str(e)}")
        sys.exit(1)

def main():
    print("🌟 NASPICK DATA & SOCIAL AUTOMATION WORKFLOW INITIATED 🌟")
    total_start = time.time()

    # 1. Update Consensus & Calendar Data
    # This script fetches latest earnings dates and wall street targets
    # [DISABLED] Skipping API calls due to rate limits
    # run_step("update_daily_data.py", "Update Consensus & Calendar Data")

    # 2. Run Core Engine
    # Fetches prices, calculates indicators (RSI, MACD), scores stocks, updates data.json
    # [DISABLED] Skipping API calls due to rate limits
    # run_step(os.path.join("scripts", "core", "engine.py"), "Core Engine (Prices, TA, Scoring)")

    # 3. Generate Social Images
    # Reads data.json, generates ranking/oversold/golden-cross/earnings images via Playwright
    # Note: This step also fetches live 100-day data for Golden Cross calculation (top 500 stocks)
    run_step(os.path.join("scripts", "social_gen", "generator.py"), "Generate Social Media Images")

    # 4. Send to Telegram
    # Uploads generated images to Telegram channel
    # Note: Sends all images in output/ directory
    run_step(os.path.join("scripts", "social_gen", "telegram_bot.py"), "Send to Telegram")

    total_duration = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"🎉 WORKFLOW COMPLETED SUCCESSFULLY in {total_duration:.1f}s")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
