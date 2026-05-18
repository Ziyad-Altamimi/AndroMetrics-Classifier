# SEMetrics — Software Engineering Metrics for Sifting Android Malicious Applications

ISEC363 Course Project — Android malware detection using software engineering metrics and machine learning.

## Overview

This project classifies Android APKs as **benign** or **malware** using software engineering metrics extracted via static analysis. Method-level features (LOC, cyclomatic complexity, fan-in/fan-out, etc.) are aggregated into per-APK statistical profiles, then fed to five machine learning classifiers.

## Pipeline

```
samples/*.apk
    |
    v
DroidASAT (Java/Soot/FlowDroid)
    |
    v
out/benign/*.csv  +  out/malware/adware/*.csv   (per-method features)
    |
    v
SEMetrics.py   <--  list_of_csv_files.txt
    |
    v
final_dataset.csv   (89 aggregate features + Class label)
    |
    v
Classify.py   -->   final_dataset_results.txt
```

## Project Structure

```
.
|-- SEMetrics.py               # Feature aggregation: per-method -> per-APK statistics
|-- Classify.py                # ML classification with 5 classifiers
|-- SEMetricsBonus.py          # Bonus: ROC, CM heatmaps, 10-fold CV
|-- run.sh / run.bat           # Runs DroidASAT on all APK samples
|-- requirements.txt           # Python dependencies
|-- DroidASAT.jar              # Static analysis engine
|-- AndroidCallbacks.txt       # Android listener interfaces for Soot
|-- list_of_csv_files.txt      # Paths to all per-APK CSV files
|
|-- samples/
|   |-- benign/                # 103 benign APK files
|   \-- malware/adware/        # 103 malware APK files
|
|-- out/
|   |-- benign/                # Per-method CSV output (benign)
|   \-- malware/adware/        # Per-method CSV output (malware)
|
\-- lib/
    |-- rt.jar                 # Java runtime for Soot
    |-- sootclasses-trunk-jar-with-dependencies.jar
    |-- soot-infoflow.jar
    |-- soot-infoflow-android.jar
    \-- android-jar/           # Android SDK platform jars (API 3-29)
```

## Requirements

- **Java** (JDK 8+) — for DroidASAT static analysis
- **Python 3.7+** — for feature aggregation and classification
- **Cygwin** (Windows only) — provides `find` and other Linux utilities

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Extracted Features

### Per-method features (extracted by DroidASAT)

| Feature | Description |
|---------|-------------|
| LOC | Lines of Code |
| Fan-In | Number of callers |
| Fan-Out | Number of callees |
| CFG-Size | Control Flow Graph size |
| Number-Of-Branches | Branch count |
| Number-Of-Invokes | Method invocation count |
| Number-Of-Parameters | Parameter count |
| Is-Static | Static method flag (0/1) |
| Is-Public | Public visibility flag (0/1) |
| Is-Private | Private visibility flag (0/1) |
| Is-Protected | Protected visibility flag (0/1) |

### Per-APK statistical aggregates

8 measures computed for each of the 11 features, plus method count:

**Sum, Var, Std, Mean, Max, Min, Range, Median**

Example column names: `Sum-LOC`, `Var-LOC`, `Std-LOC`, `Mean-LOC`, etc.

The final CSV has `Class` as the last column (0 = benign, 1 = malware).

## Usage

### Step 1: Run pipeline.py

```bash
py pipeline.py
```

### Step 2: Extract features from all APKs

```bash
bash run.sh        # Linux
# or
run.bat            # Windows (Cygwin)
```

DroidASAT processes each APK and writes a per-method CSV to `out/benign/` or `out/malware/adware/`. The script's last line generates `list_of_csv_files.txt`.

### Step 2: View results

- Classification results: `final_dataset_results.txt`
- Cross-validation results: `final_dataset_cv_results.txt`
- ROC curves: `final_dataset_roc_*.png` (5 files)
- Confusion matrix heatmaps: `final_dataset_cm_*.png` (5 files)

## Classifiers

Five classifiers trained and evaluated with an 80/20 stratified split and standardized features (StandardScaler):

| Classifier | Hyperparameters |
|------------|----------------|
| Gaussian Naive Bayes | `var_smoothing=1e-9` |
| Decision Tree | `max_depth=5`, `min_samples_split=5`, `min_samples_leaf=2` |
| Random Forest | `n_estimators=100`, `max_depth=10`, `min_samples_split=5` |
| AdaBoost | `n_estimators=50`, `learning_rate=0.5` |
| Linear SVC | `C=1.0`, `max_iter=2000`, `dual='auto'` |

All use `random_state=42` for reproducibility.

### Preprocessing Pipeline

```
X → VarianceThreshold(0.01) → SelectKBest(k=30, mutual_info) → StandardScaler → train_test_split
```

- **VarianceThreshold** removes near-constant features (noise)
- **SelectKBest** keeps the top 30 most informative features via mutual information
- **StandardScaler** standardizes features to zero mean and unit variance

### Class Weighting & Threshold Optimization

- `class_weight='balanced'` on DecisionTree, RandomForest, and LinearSVC to penalize minority-class errors
- ROC-based threshold calibration via **Youden's index** (maximizes `TPR - FPR`)

## Bonus Features (`SEMetricsBonus.py`)

Three bonus analysis features are implemented in a separate module and called automatically during classification:

### 1. ROC Curve Visualization (2 bonus marks)

Five ROC curves are generated (one per classifier) showing the trade-off between TPR and FPR. The AUC value is displayed on each plot.

**Output:** `final_dataset_roc_GaussianNB.png` through `final_dataset_roc_LinearSVC.png`

### 2. 10-Fold Cross-Validation with Random Forest (2 bonus marks)

Stratified 10-fold cross-validation using the same preprocessing pipeline. Reports per-fold mean ± standard deviation for Accuracy, Precision, Recall, F1, TPR, and FPR across both classes, plus an aggregate confusion matrix.

**Output:** `final_dataset_cv_results.txt`

### 3. Confusion Matrix Heatmap (1 bonus mark)

Five confusion matrix heatmaps are generated (one per classifier) with annotated cell values (TP, FP, FN, TN).

**Output:** `final_dataset_cm_GaussianNB.png` through `final_dataset_cm_LinearSVC.png`

## Output Files

| File | Description |
|------|-------------|
| `final_dataset.csv` | Consolidated feature matrix |
| `final_dataset_results.txt` | Per-classifier metrics (confusion matrix, precision, recall, F1, accuracy, TPR, FPR) |
| `final_dataset_roc_*.png` | ROC curves (5 files — one per classifier) |
| `final_dataset_cm_*.png` | Confusion matrix heatmaps (5 files) |
| `final_dataset_cv_results.txt` | 10-fold cross-validation results |

## Authors

**Instructor:** Dr. Shahid Alam (sha.alam@uoh.edu.sa) — University of Hail, Saudi Arabia

**Course:** ISEC363 — Secure Software Development
