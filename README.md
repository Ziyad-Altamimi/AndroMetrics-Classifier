
# AndroMetrics-Classifier

Android Malware Detection using Software Engineering Metrics and Machine Learning

## Overview

This project detects Android malware using software engineering metrics extracted from APK files through static analysis. Method-level features are statistically aggregated into APK-level feature vectors and classified using multiple machine learning algorithms.

The project is developed for the **ISEC363 — Secure Software Development** course.

## Pipeline

```text
APK Samples
    |
    v
DroidASAT Static Analysis
    |
    v
Per-method CSV Feature Files
    |
    v
SEMetrics.py
    |
    v
final_dataset.csv
    |
    v
Classify.py
    |
    v
Classification Results + Bonus Visualizations
````

## Repository Structure

```text
.
|-- SEMetrics.py
|-- Classify.py
|-- SEMetricsBonus.py
|-- pipeline.py
|-- run.sh / run.bat
|-- requirements.txt
|-- DroidASAT.jar
|
|-- final_dataset.csv
|-- final_dataset_results.txt
|-- final_dataset_cv_results.txt
|
|-- final_dataset_roc_*.png
|-- final_dataset_cm_*.png
|
\-- README.md
```

> Note: APK samples, Android SDK libraries, and generated intermediate CSV outputs are excluded from the repository due to repository size and security considerations.

## Requirements

* Java JDK 8 or later
* Python 3.7 or later
* Cygwin on Windows (optional)
* Python dependencies from `requirements.txt`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Dataset

| Class   | Description                    | Label |
| ------- | ------------------------------ | ----- |
| Benign  | Normal Android applications    | 0     |
| Malware | Android malware/adware samples | 1     |

The final machine learning dataset is stored in:

```text
final_dataset.csv
```

## Extracted Features

| Feature              | Description             |
| -------------------- | ----------------------- |
| LOC                  | Lines of Code           |
| Fan-In               | Number of callers       |
| Fan-Out              | Number of callees       |
| CFG-Size             | Control Flow Graph size |
| Number-Of-Branches   | Branch count            |
| Number-Of-Invokes    | Method invocation count |
| Number-Of-Parameters | Parameter count         |
| Is-Static            | Static method flag      |
| Is-Public            | Public method flag      |
| Is-Private           | Private method flag     |
| Is-Protected         | Protected method flag   |

## Feature Aggregation

For each APK, the following statistical measures are calculated:

* Sum
* Variance
* Standard Deviation
* Mean
* Maximum
* Minimum
* Range
* Median

Example columns:

```text
Sum-LOC
Mean-LOC
Max-Fan-Out
Median-CFG-Size
```

## Usage

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run static analysis

Linux:

```bash
bash run.sh
```

Windows:

```bat
run.bat
```

### 3. Build aggregated dataset

```bash
python SEMetrics.py
```

### 4. Run classification

```bash
python Classify.py
```

Generated outputs:

```text
final_dataset_results.txt
final_dataset_cv_results.txt
final_dataset_roc_*.png
final_dataset_cm_*.png
```

## Machine Learning Pipeline

```text
X
|
v
VarianceThreshold
|
v
SelectKBest
|
v
StandardScaler
|
v
Train/Test Split
|
v
Classification
```

## Classifiers

| Classifier           | Parameters           |
| -------------------- | -------------------- |
| Gaussian Naive Bayes | `var_smoothing=1e-9` |
| Decision Tree        | `max_depth=5`        |
| Random Forest        | `n_estimators=100`   |
| AdaBoost             | `n_estimators=50`    |
| Linear SVC           | `C=1.0`              |

## Experimental Results

| Classifier           | Accuracy | F1-Score |
| -------------------- | -------- | -------- |
| Gaussian Naive Bayes | 0.95     | 0.95     |
| Decision Tree        | 0.93     | 0.93     |
| Random Forest        | 0.98     | 0.98     |
| AdaBoost             | 0.98     | 0.98     |
| Linear SVC           | 0.95     | 0.95     |

Random Forest and AdaBoost achieved the best performance with approximately 98% accuracy.

## Bonus Features

### ROC Curves

Generated ROC curve visualizations for all classifiers.

### 10-Fold Cross Validation

Implemented stratified 10-fold cross-validation using Random Forest.

### Confusion Matrix Heatmaps

Generated confusion matrix heatmaps for all classifiers.



## Output Files

| File                           | Description              |
| ------------------------------ | ------------------------ |
| `final_dataset.csv`            | Final dataset            |
| `final_dataset_results.txt`    | Classification results   |
| `final_dataset_cv_results.txt` | Cross-validation results |
| `final_dataset_roc_*.png`      | ROC curve plots          |
| `final_dataset_cm_*.png`       | Confusion matrix plots   |

## Limitations

* APK files are not included in the repository.
* Android SDK libraries are excluded due to size.
* Dynamic malware analysis is not implemented.

## Project Summary
This project demonstrates how software engineering metrics combined with machine learning can classify Android applications as benign or malicious using static analysis techniques.

---
---

## Authors

**Course:** ISEC363 — Secure Software Development 

**Instructor:** Dr. Shahid Alam (sha.alam@uoh.edu.sa) — University of Hail, Saudi Arabia

