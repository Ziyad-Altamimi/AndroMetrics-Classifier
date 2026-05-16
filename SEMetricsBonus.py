# --------------------------------------------------------------------------------------------------------------
#
# Filename: SEMetricsBonus.py
# Author: Shahid Alam (sha.alam@uoh.edu.sa) — Extended by Students
# Dated: 2026
# SEMetrics => Software Engineering Metrics — Bonus Features
#
# This module provides three bonus analysis methods:
#   1. ROC curve visualization
#   2. Confusion matrix heatmap visualization
#   3. Stratified 10-fold cross-validation with Random Forest
#
# --------------------------------------------------------------------------------------------------------------

from __future__ import print_function
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
	confusion_matrix,
	roc_auc_score,
	accuracy_score,
	precision_score,
	recall_score,
	f1_score,
	roc_curve,
	auc
)
from sklearn.feature_selection import VarianceThreshold, SelectKBest, mutual_info_classif
from sklearn import preprocessing

__DEBUG__ = True


class Bonus:
	"""
	Bonus analysis methods for the SEMetrics project.

	All methods are static — call as Bonus.method_name(...)
	"""

	# ------------------------------------------------------------------
	# BONUS 1: ROC Curve Visualization
	# ------------------------------------------------------------------
	@staticmethod
	def plot_roc_curve(fpr, tpr, roc_auc, classifier_name, filename):
		"""
		Plots and saves a Receiver Operating Characteristic (ROC) curve to a PNG file.

		Parameters
		----------
		fpr : array-like
			False positive rate values.
		tpr : array-like
			True positive rate values.
		roc_auc : float
			Area Under the Curve value.
		classifier_name : str
			Name of the classifier (for the plot title).
		filename : str
			Output file path (must end with .png or .pdf).
		"""
		try:
			plt.figure(figsize=(6, 6))
			plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC (AUC = %.3f)' % roc_auc)
			plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Guess')
			plt.xlim([0.0, 1.0])
			plt.ylim([0.0, 1.05])
			plt.xlabel('False Positive Rate', fontsize=12)
			plt.ylabel('True Positive Rate', fontsize=12)
			plt.title('ROC Curve — %s' % classifier_name, fontsize=14)
			plt.legend(loc='lower right', fontsize=10)
			plt.grid(alpha=0.3)
			plt.tight_layout()
			plt.savefig(filename, dpi=150)
			plt.close()
			if __DEBUG__:
				print("[Bonus] ROC curve saved: %s" % filename)
		except Exception as e:
			print("[Bonus] WARNING: Could not save ROC curve for %s — %s" % (classifier_name, str(e)))

	# ------------------------------------------------------------------
	# BONUS 3: Confusion Matrix Heatmap
	# ------------------------------------------------------------------
	@staticmethod
	def plot_confusion_matrix(cm, class_names, classifier_name, filename):
		"""
		Plots and saves a confusion matrix heatmap to a PNG file.

		Cells show TPR / FPR / FNR / TNR rates instead of raw counts.
		Positive class = Malware, Negative class = Benign.

		Parameters
		----------
		cm : ndarray of shape (2, 2)
			Confusion matrix from sklearn (order matches class_names).
		class_names : list of str
			List of class label strings (e.g., ['benign', 'malware']).
		classifier_name : str
			Name of the classifier (for the plot title).
		filename : str
			Output file path (must end with .png or .pdf).
		"""
		try:
			malware_idx = class_names.index('malware') if 'malware' in class_names else 1
			benign_idx = 1 - malware_idx

			tp = cm[malware_idx, malware_idx]
			fn = cm[malware_idx, benign_idx]
			fp = cm[benign_idx, malware_idx]
			tn = cm[benign_idx, benign_idx]

			tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
			fnr = fn / (tp + fn) if (tp + fn) > 0 else 0.0
			fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
			tnr = tn / (fp + tn) if (fp + tn) > 0 else 0.0

			rate_matrix = np.array([
				[tpr, fnr],
				[fpr, tnr],
			])

			labels = ["Malware\n(Positive)", "Benign\n(Negative)"]
			cell_texts = [
				["TPR: %.3f" % tpr, "FNR: %.3f" % fnr],
				["FPR: %.3f" % fpr, "TNR: %.3f" % tnr],
			]

			fig, ax = plt.subplots(figsize=(6, 5.5))
			cax = ax.matshow(rate_matrix, cmap=plt.cm.Blues, vmin=0, vmax=1, alpha=0.85)
			cbar = fig.colorbar(cax, ticks=[0, 0.25, 0.5, 0.75, 1.0])
			cbar.set_label("Rate", fontsize=10)

			ax.set_xticks(np.arange(2))
			ax.set_yticks(np.arange(2))
			ax.set_xticklabels(labels, fontsize=10)
			ax.set_yticklabels(labels, fontsize=10)
			ax.xaxis.set_ticks_position('bottom')

			for i in range(2):
				for j in range(2):
					bright = rate_matrix[i, j] > 0.65
					ax.text(j, i, cell_texts[i][j],
					        ha='center', va='center',
					        fontsize=15, fontweight='bold',
					        color='white' if bright else 'black')

			ax.set_xlabel('Predicted', fontsize=12)
			ax.set_ylabel('True', fontsize=12)
			ax.set_title('Confusion Matrix Rates — %s' % classifier_name, fontsize=13, pad=20)
			plt.tight_layout()
			plt.savefig(filename, dpi=150)
			plt.close()
			if __DEBUG__:
				print("[Bonus] Confusion matrix saved: %s" % filename)
		except Exception as e:
			print("[Bonus] WARNING: Could not save confusion matrix for %s — %s" % (classifier_name, str(e)))

	# ------------------------------------------------------------------
	# BONUS 2: 10-Fold Stratified Cross-Validation with Random Forest
	# ------------------------------------------------------------------
	@staticmethod
	def cross_validate_rf(dataset, class_label, file_types, results_filename):
		"""
		Performs stratified 10-fold cross-validation using Random Forest.
		Applies the same preprocessing pipeline used in classify():
		  1. VarianceThreshold (remove near-constant features)
		  2. SelectKBest (keep top 30 features by mutual information)
		  3. StandardScaler

		Parameters
		----------
		dataset : pandas DataFrame
			The consolidated feature matrix (last column = class label).
		class_label : str
			Name of the class column (e.g., 'Class').
		file_types : list of str
			List mapping integer class labels to string names (e.g., ['benign', 'malware']).
		results_filename : str
			Output file path for CV results.

		Notes
		-----
		The README specifies using WEKA for 10-fold CV. This method provides
		an equivalent implementation directly in Python using scikit-learn.
		"""
		try:
			print("\n[Bonus] --- 10-Fold Cross-Validation with Random Forest ---")

			# Separate features and labels
			X = dataset.drop(columns=[class_label])
			y = dataset[class_label]

			# Apply preprocessing — same pipeline as classify()
			selector_var = VarianceThreshold(threshold=0.01)
			X = selector_var.fit_transform(X)
			if __DEBUG__:
				print("[Bonus] Features after VarianceThreshold: %d" % X.shape[1])

			selector_kbest = SelectKBest(mutual_info_classif, k=30)
			X = selector_kbest.fit_transform(X, y)
			if __DEBUG__:
				print("[Bonus] Features after SelectKBest: %d" % X.shape[1])

			scaler = preprocessing.StandardScaler()
			X = scaler.fit_transform(X)

			# Stratified 10-fold split
			skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

			# Per-fold metrics accumulators
			fold_accuracies   = []
			fold_precisions   = {0: [], 1: []}
			fold_recalls      = {0: [], 1: []}
			fold_f1s          = {0: [], 1: []}
			fold_tprs         = {0: [], 1: []}
			fold_fprs         = {0: [], 1: []}
			aggregate_cm      = np.zeros((2, 2), dtype=int)

			clf_rf = RandomForestClassifier(
				n_estimators=100, max_depth=10,
				min_samples_split=5, min_samples_leaf=2,
				class_weight='balanced', random_state=42
			)

			fold_num = 1
			for train_idx, test_idx in skf.split(X, y):
				X_train, X_test = X[train_idx], X[test_idx]
				y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

				clf_rf.fit(X_train, y_train)
				y_pred = clf_rf.predict(X_test)

				# Per-fold metrics
				acc = accuracy_score(y_test, y_pred)
				fold_accuracies.append(acc)

				for c in [0, 1]:
					pr = precision_score(y_test, y_pred, pos_label=c, zero_division=0)
					re = recall_score(y_test, y_pred, pos_label=c, zero_division=0)
					f1 = f1_score(y_test, y_pred, pos_label=c, zero_division=0)
					fold_precisions[c].append(pr)
					fold_recalls[c].append(re)
					fold_f1s[c].append(f1)

				# Per-fold CM and derived TPR / FPR
				cm_fold = confusion_matrix(y_test, y_pred, labels=[0, 1])
				aggregate_cm += cm_fold

				# TPR = TP / (TP + FN)
				tp = np.diag(cm_fold)
				fn = cm_fold.sum(axis=1) - tp
				fp = cm_fold.sum(axis=0) - tp
				tn = cm_fold.sum() - (tp + fn + fp)

				for i, c in enumerate([0, 1]):
					tpr_val = tp[i] / (tp[i] + fn[i]) if (tp[i] + fn[i]) > 0 else 0.0
					fpr_val = fp[i] / (fp[i] + tn[i]) if (fp[i] + tn[i]) > 0 else 0.0
					fold_tprs[c].append(tpr_val)
					fold_fprs[c].append(fpr_val)

				fold_num += 1

			# ------------------------------------------------------------------
			# Build results string
			# ------------------------------------------------------------------
			result = ""
			result += "=" * 60 + "\n"
			result += "BONUS: 10-Fold Stratified Cross-Validation Results\n"
			result += "Classifier: Random Forest (100 trees, max_depth=10)\n"
			result += "=" * 60 + "\n\n"

			def mean_std_str(values):
				arr = np.array(values)
				return "%.4f ± %.4f" % (arr.mean(), arr.std())

			result += "--- Per-Fold Metrics ---\n\n"
			result += "%-35s %s\n" % ("Metric", "Mean ± Std")
			result += "-" * 55 + "\n"
			result += "%-35s %s\n" % ("Accuracy", mean_std_str(fold_accuracies))

			for c in [0, 1]:
				label = file_types[c]
				result += "%-35s %s\n" % ("Precision (%s)" % label, mean_std_str(fold_precisions[c]))
				result += "%-35s %s\n" % ("Recall / TPR (%s)" % label, mean_std_str(fold_recalls[c]))
				result += "%-35s %s\n" % ("F1 Score (%s)" % label, mean_std_str(fold_f1s[c]))

			for c in [0, 1]:
				label = file_types[c]
				result += "%-35s %s\n" % ("TPR (%s)" % label, mean_std_str(fold_tprs[c]))
				result += "%-35s %s\n" % ("FPR (%s)" % label, mean_std_str(fold_fprs[c]))

			# Aggregate confusion matrix (sum over folds)
			result += "\n--- Aggregate Confusion Matrix (sum over 10 folds) ---\n"
			result += "Predicted:  %6s  %6s\n" % (file_types[0], file_types[1])
			result += "Actual %-4s: %6d  %6d\n" % (file_types[0], aggregate_cm[0, 0], aggregate_cm[0, 1])
			result += "Actual %-4s: %6d  %6d\n" % (file_types[1], aggregate_cm[1, 0], aggregate_cm[1, 1])

			# Compute aggregate TPR / FPR from aggregate CM
			tp_agg = np.diag(aggregate_cm)
			fn_agg = aggregate_cm.sum(axis=1) - tp_agg
			fp_agg = aggregate_cm.sum(axis=0) - tp_agg
			tn_agg = aggregate_cm.sum() - (tp_agg + fn_agg + fp_agg)

			result += "\n--- Aggregate Per-Class Metrics ---\n\n"
			for i, c in enumerate([0, 1]):
				label = file_types[c]
				tpr_agg = tp_agg[i] / (tp_agg[i] + fn_agg[i]) if (tp_agg[i] + fn_agg[i]) > 0 else 0.0
				fpr_agg = fp_agg[i] / (fp_agg[i] + tn_agg[i]) if (fp_agg[i] + tn_agg[i]) > 0 else 0.0
				acc_agg = (tp_agg[i] + tn_agg[i]) / aggregate_cm.sum() if aggregate_cm.sum() > 0 else 0.0
				result += "Class %s:\n" % label
				result += "  TPR      = %.4f\n" % tpr_agg
				result += "  FPR      = %.4f\n" % fpr_agg
				result += "  Accuracy = %.4f\n" % acc_agg

			result += "\n" + "=" * 60 + "\n"
			print(result)

			# Write to file
			with open(results_filename, 'w') as f_out:
				f_out.write(result)
			print("[Bonus] CV results saved to: %s" % results_filename)

		except Exception as e:
			print("[Bonus] ERROR during cross-validation: %s" % str(e))
