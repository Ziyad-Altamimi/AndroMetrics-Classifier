# Screenshot Checklist — SEMetrics Report (Revised)

This checklist accompanies the revised
`SEMetrics_Android_Malware_Classification_Report.docx`. The report contains
12 screenshot placeholder boxes (dashed blue border, marked
**[ Insert Figure N ]**). All ROC and feature-importance figures are already
embedded directly from `results/`, so no screenshots are needed for those.

To insert a screenshot:

1. In Word, Ctrl+F for "Insert Figure N".
2. Click the placeholder cell.
3. Delete the placeholder content (one cell of a single-row table).
4. Insert > Pictures > select your screenshot.
5. The caption underneath each placeholder is already filled in.

---

## Required screenshots (12)

| # | Title | Where to capture | Suggested filename | Section |
|---|-------|------------------|--------------------|---------|
| 1 | Project folder structure | File Explorer at the project root, or `tree /F | more` | `fig01_folder_tree.png` | §4 |
| 2 | Java runtime version | cmd: `java -version` (must show Temurin 17) | `fig02_java_version.png` | §6 |
| 3 | Successful test run (run_test.bat) | cmd showing the run completes with "Test done." | `fig03_run_test_console.png` | §7.3 |
| 4 | Per-APK CSV header | A test CSV opened in Notepad++ or Excel showing 12-column header | `fig04_per_apk_csv_header.png` | §7.3 |
| 5 | Full run.bat execution | cmd at the end of `run.bat` (showing "Done.") or mid-run | `fig05_run_bat_console.png` | §7.4 |
| 6 | CSV count verification | cmd output of the two `dir /b ... | find /c /v ""` commands (103 + 103) | `fig06_csv_counts.png` | §7.4 |
| 7 | list_of_csv_files.txt generation | cmd showing `dir /s /b out\*.csv > list_of_csv_files.txt` + line count (206) | `fig07_list_generation.png` | §8.1 |
| 8 | final_dataset.csv preview | Excel or `python -c "import pandas as pd; ..."` showing (206, 90) shape | `fig08_final_dataset_preview.png` | §8.3 |
| 9 | Classification results file | `results\final_dataset.csv.results.txt` opened on the RandomForest or AdaBoost section showing CM + report + AUC + Top-10 features | `fig09_results_txt.png` | §10.1 |
| 10 | (already embedded) | Figure 10 — Random Forest feature importance is **embedded from results/**, no action needed | (n/a) | §10.4 |
| 11 | (already embedded) | Figure 11 — Random Forest ROC is **embedded from results/**, no action needed | (n/a) | §11.4 |
| 12 | results\ folder contents | File Explorer in `results\` showing all six ROC PNGs, three FeatureImportance PNGs, and the .txt file with sizes | `fig12_results_folder.png` | §11.4 |

(Figures 10 and 11 are listed for traceability — they are already embedded in
the document from `results/`, so no manual capture is needed.)

---

## Suggested capture workflow

A reproducible order that minimises context-switching:

**Pass 1 — terminal screenshots in one fresh cmd window:**
- Fig 2 (`java -version`)
- Fig 3 (run_test.bat)
- Fig 5 (run.bat — keep the window open for the run, take the screenshot at the end)
- Fig 6 (the two `dir | find /c /v ""` commands)
- Fig 7 (`dir /s /b out\*.csv > list_of_csv_files.txt` + verification)

**Pass 2 — File Explorer:**
- Fig 1 (project root)
- Fig 12 (results\ folder)

**Pass 3 — Editor / Python:**
- Fig 4 (one per-APK CSV in Notepad++)
- Fig 8 (final_dataset.csv preview in Excel or via Python)
- Fig 9 (results.txt, scrolled to RandomForest section)

Total time: roughly 15–20 minutes for all 10 manual screenshots.

---

## Notes

- All caption text is already written in the document.
- Random Forest ROC (Fig 11) and Random Forest Feature-Importance (Fig 10)
  are already embedded; the appendix also embeds AdaBoost, LinearSVC, KNN,
  Decision Tree, and Naive Bayes ROC plots and the AdaBoost and Decision Tree
  feature-importance charts. No screenshots needed for any of these.
- If you accidentally insert next to a placeholder instead of replacing it,
  simply delete the dashed-border table afterwards.
