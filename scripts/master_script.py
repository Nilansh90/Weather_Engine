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


with open(log_file, "a", encoding="utf-8") as log:

    for script in scripts:

        print(f"\n========== Running {script} ==========")

        log.write(f"\n\n{'=' * 60}\n")
        log.write(f"Running {script}\n")
        log.write(f"{'=' * 60}\n")


        try:

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / script)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True
            )


            print(result.stdout)

            log.write(result.stdout)


            print(f"✓ {script} completed")


        except subprocess.CalledProcessError as e:

            print(e.stdout)

            log.write(e.stdout)


            print(f"✗ {script} failed")

            raise e


print("\nPipeline finished successfully.")