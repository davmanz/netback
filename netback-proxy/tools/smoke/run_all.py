import subprocess
import sys

MODULES = [
    "tools.smoke.test_vaultcredentials",
    "tools.smoke.test_users",
    "tools.smoke.test_devices",
    "tools.smoke.test_locations",
    "tools.smoke.test_classification_rules",
    "tools.smoke.test_zabbix",
]


def main():
    for m in MODULES:
        print(f"\n=== Running {m} ===")
        res = subprocess.run([sys.executable, "-m", m], capture_output=True, text=True)
        print(res.stdout)
        if res.returncode != 0:
            print(res.stderr)
            sys.exit(res.returncode)
    print("\nAll smoke tests OK")


if __name__ == "__main__":
    main()
