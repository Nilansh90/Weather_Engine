from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / "daily_pipeline.log"

scripts = [
    "recharge_actual_data.py",
    "fetch_weather.py",
    "predict.py",
    "calculate_errors.py",
    "mail_script.py",
]

print("=" * 60)
print("WEATHER ENGINE - MASTER PIPELINE")
print("=" * 60)

with open(log_file, "a", encoding="utf-8") as log:

    for script in scripts:

        print(f"\nRunning {script}")

        log.write(f"\n\n{'=' * 60}\n")
        log.write(f"Running {script}\n")
        log.write(f"{'=' * 60}\n")

        try:

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / script)
                ],
                stdout=log,
                stderr=log,
                check=True
            )

            print(f"✓ {script} completed")

        except subprocess.CalledProcessError:

            print(f"✗ {script} failed")
            print(f"Check log: {log_file}")

            break

print("\nPipeline finished.")