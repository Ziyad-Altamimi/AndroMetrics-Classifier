#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# Filename: pipeline.py
# SEMetrics Unified Pipeline -- one command to rule them all
# Usage:
#   python pipeline.py                 # Full pipeline
#   python pipeline.py --classify-only # Skip extraction, just aggregate+classify
#   python pipeline.py --csv-list-only # Only regenerate list_of_csv_files.txt
# ---------------------------------------------------------------------------

from __future__ import print_function
import argparse, os, subprocess, sys, time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLES_DIR = PROJECT_ROOT / "samples"
OUT_DIR = PROJECT_ROOT / "out"
LIB_DIR = PROJECT_ROOT / "lib"

DROIDASAT_JAR = PROJECT_ROOT / "DroidASAT.jar"
RT_JAR = LIB_DIR / "rt.jar"
SOOT_JAR = LIB_DIR / "sootclasses-trunk-jar-with-dependencies.jar"
SOOT_INFOFLOW_JAR = LIB_DIR / "soot-infoflow.jar"
SOOT_INFOFLOW_ANDROID_JAR = LIB_DIR / "soot-infoflow-android.jar"
ANDROID_JAR_DIR = LIB_DIR / "android-jar"

CP_ENTRIES = [
    ".", str(DROIDASAT_JAR), str(RT_JAR), str(SOOT_JAR),
    str(SOOT_INFOFLOW_JAR), str(SOOT_INFOFLOW_ANDROID_JAR),
]

RAM_MIN = "4g"
RAM_MAX = "8g"
JAVA_TIMEOUT = 600
CSV_LIST_FILE = PROJECT_ROOT / "list_of_csv_files.txt"
DATASET_CSV = PROJECT_ROOT / "final_dataset.csv"


def check_files():
    required = {
        "DroidASAT.jar": DROIDASAT_JAR,
        "lib/rt.jar": RT_JAR,
        "lib/sootclasses-trunk-jar-with-dependencies.jar": SOOT_JAR,
        "lib/soot-infoflow.jar": SOOT_INFOFLOW_JAR,
        "lib/soot-infoflow-android.jar": SOOT_INFOFLOW_ANDROID_JAR,
        "lib/android-jar/": ANDROID_JAR_DIR,
        "samples/": SAMPLES_DIR,
    }
    for label, path in required.items():
        if not path.exists():
            print("  [FAIL] Missing: %s  (expected at %s)" % (label, path))
            sys.exit(1)
    print("  [OK] Required files: all present")


def check_java():
    try:
        result = subprocess.run(
            ["java", "-version"], capture_output=True, text=True, timeout=15
        )
        version_line = (result.stderr or result.stdout).strip().split("\n")[0]
        print("  [OK] Java detected: %s" % version_line)
    except FileNotFoundError:
        print("  [FAIL] Java not found on PATH. Install JDK 8+ and try again.")
        sys.exit(1)
    except Exception as e:
        print("  [FAIL] Java check failed: %s" % e)
        sys.exit(1)


def check_python_deps():
    deps = {
        "pandas": "pandas",
        "numpy": "numpy",
        "sklearn": "scikit-learn",
        "matplotlib": "matplotlib",
    }
    missing = []
    for module, pip_name in deps.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pip_name)
    if missing:
        print("  [FAIL] Missing Python packages: %s" % ", ".join(missing))
        requirements = PROJECT_ROOT / "requirements.txt"
        print("  Run: pip install -r %s" % requirements)
        sys.exit(1)
    print("  [OK] Python dependencies: all present")


def find_apks():
    return sorted(SAMPLES_DIR.rglob("*.apk"))


def apk_to_csv_path(apk_path):
    relative = apk_path.relative_to(SAMPLES_DIR)
    csv_name = apk_path.name + ".csv"
    return OUT_DIR / relative.parent / csv_name


def build_classpath():
    return os.pathsep.join(CP_ENTRIES)


def run_droidasat(apk_path, output_dir):
    classpath = build_classpath()
    cmd = [
        "java",
        "-Xms" + RAM_MIN,
        "-Xmx" + RAM_MAX,
        "-cp", classpath,
        "DroidASAT.main",
        str(RT_JAR),
        str(ANDROID_JAR_DIR),
        str(apk_path),
        str(output_dir),
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=JAVA_TIMEOUT,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout).strip()
            if err:
                print(" " * 9 + "stderr: %s" % err[:200])
            return False
        return True
    except subprocess.TimeoutExpired:
        print(" " * 9 + "TIMEOUT after %ds" % JAVA_TIMEOUT)
        return False
    except Exception as e:
        print(" " * 9 + "Error: %s" % e)
        return False


def run_extraction(apks):
    total = len(apks)
    ok = 0
    skipped = 0
    failed = 0
    start = time.time()

    for i, apk in enumerate(apks, 1):
        csv_path = apk_to_csv_path(apk)
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        prefix = "  [%3d/%d]" % (i, total)

        if csv_path.exists() and csv_path.stat().st_size > 0:
            print("%s SKIP (exists): %s" % (prefix, apk.relative_to(PROJECT_ROOT)))
            skipped += 1
            continue

        apk_size_mb = apk.stat().st_size / (1024 * 1024)
        rel = apk.relative_to(PROJECT_ROOT)
        print("%s Processing (%0.1fMB): %s" % (prefix, apk_size_mb, rel))

        success = run_droidasat(apk, csv_path.parent)

        if success and csv_path.exists() and csv_path.stat().st_size > 0:
            ok += 1
        else:
            failed += 1
            if csv_path.exists() and csv_path.stat().st_size == 0:
                csv_path.unlink()

    elapsed = time.time() - start
    print()
    print("  Extraction: %d OK, %d skipped, %d failed" % (ok, skipped, failed))
    print("  Elapsed: %s" % time.strftime("%H:%M:%S", time.gmtime(elapsed)))
    print()
    return (ok + skipped) > 0


def generate_csv_list():
    csv_files = sorted(OUT_DIR.rglob("*.csv"))
    with open(str(CSV_LIST_FILE), "w") as f:
        for csv_path in csv_files:
            rel = csv_path.relative_to(PROJECT_ROOT)
            f.write("./%s\n" % rel)
    print("  Generated %s  (%d entries)" % (CSV_LIST_FILE.name, len(csv_files)))
    return len(csv_files)


def run_semetrics():
    print()
    print("=" * 70)
    print("  Running SEMetrics (aggregation + classification)")
    print("=" * 70)
    print()

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "SEMetrics.py"),
        "-f", str(CSV_LIST_FILE),
        "-csv", str(DATASET_CSV),
    ]
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print()
        print("  [WARN] SEMetrics exited with code %d" % result.returncode)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="SEMetrics Unified Pipeline -- single-command workflow"
    )
    parser.add_argument(
        "--classify-only", action="store_true",
        help="Skip DroidASAT extraction; aggregate + classify existing CSVs"
    )
    parser.add_argument(
        "--csv-list-only", action="store_true",
        help="Only (re)generate list_of_csv_files.txt and exit"
    )
    args = parser.parse_args()

    os.chdir(str(PROJECT_ROOT))

    print()
    print("=" * 70)
    print("  SEMetrics Unified Pipeline")
    print("=" * 70)
    print()

    print("[1/3] Checking prerequisites...")
    check_files()
    check_java()
    check_python_deps()
    print()

    if args.classify_only:
        print("[2/3] Skipping feature extraction (--classify-only)")
        print()
    else:
        print("[2/3] Feature extraction (DroidASAT)")
        apks = find_apks()
        if not apks:
            print("  [FAIL] No APK files found in samples/")
            sys.exit(1)
        print("  Found %d APK files" % len(apks))
        print()
        ok = run_extraction(apks)
        if not ok:
            print("  [FAIL] No CSV files were produced. Check the errors above.")
            sys.exit(1)

    if args.csv_list_only:
        print("[*] Generating CSV list only...")
        generate_csv_list()
        return

    print("[3/3] Aggregation + Classification")
    n_csvs = generate_csv_list()
    if n_csvs == 0:
        print("  [FAIL] No CSV files found in out/")
        print("  Run the full pipeline (without --classify-only) first.")
        sys.exit(1)

    run_semetrics()

    print()
    print("=" * 70)
    print("  Pipeline complete!")
    print("=" * 70)
    print()
    for label, pattern in [
        ("Dataset", "final_dataset.csv"),
        ("Results", "final_dataset_results.txt"),
        ("CV results", "final_dataset_cv_results.txt"),
        ("ROC curves", "final_dataset_roc_*.png"),
        ("Confusion matrices", "final_dataset_cm_*.png"),
    ]:
        matches = sorted(PROJECT_ROOT.glob(pattern))
        if matches:
            print("  %s:" % label)
            for m in matches:
                print("    %s" % m.name)
    print()


if __name__ == "__main__":
    main()
