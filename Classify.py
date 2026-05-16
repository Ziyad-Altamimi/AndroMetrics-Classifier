# --------------------------------------------------------------------------------------------------------------
#
# Filename: Classify.py
# Author: Shahid Alam (sha.alam@uoh.edu.sa)
# Dated: Feb, 03, 2026
#
# Classifier wrapper used by SEMetrics.py. Trains five supervised classifiers
# on the consolidated dataset, prints a readable confusion matrix per
# classifier, and saves one ROC PNG per classifier into the results/ folder.
# --------------------------------------------------------------------------------------------------------------

from __future__ import print_function
import os, sys, math, time
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_curve, auc, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

import warnings
from sklearn import preprocessing
from sklearn.exceptions import UndefinedMetricWarning
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

__DEBUG__  = True

#
#
#
class Classifier:
	def __init__(self, CLASS_LABEL, file_types):
		self.CLASS_LABEL = CLASS_LABEL
		self.n_classes = 0
		self.file_types = file_types

	#
	# --- TASK TO COMPLETE ---
	# Complete this function. Follow the instruction given below to complete the function.
	#
	def classify(self, dataset, dataset_filename, testSize=20):
		# Separate the data into features (X) and class label (y).
		# X is everything except the Class column; y is 0 (benign) or 1 (malware).
		y = dataset[self.CLASS_LABEL]
		X = dataset.drop(columns=[self.CLASS_LABEL])
		feature_names_all = list(X.columns)

		# Split: testSize is a percentage (e.g. 20 -> 0.20). Stratification keeps
		# the same benign/malware ratio in train and test, which makes accuracy
		# numbers comparable across runs and prevents lopsided test sets.
		try:
			train_X, test_X, train_y, test_y = train_test_split(
				X, y, test_size=testSize/100.0, random_state=42, stratify=y)
		except ValueError:
			# Fallback if a class has too few samples to stratify
			train_X, test_X, train_y, test_y = train_test_split(
				X, y, test_size=testSize/100.0, random_state=42)

		# --- Feature selection (mutual information) ---
		# Keep the top-K features ranked by mutual information with the label.
		# Fit the selector on the training data only to avoid leakage.
		k = min(30, train_X.shape[1])
		selector = SelectKBest(score_func=mutual_info_classif, k=k)
		train_X_sel = selector.fit_transform(train_X, train_y)
		test_X_sel = selector.transform(test_X)
		selected_features = [feature_names_all[i] for i, keep in enumerate(selector.get_support()) if keep]

		# --- Scaling ---
		# Only distance- and margin-based models (KNN, LinearSVC) need scaling.
		# Tree-based models are scale-invariant, so we feed them unscaled features.
		scaler = StandardScaler()
		train_X_scaled = scaler.fit_transform(train_X_sel)
		test_X_scaled = scaler.transform(test_X_sel)

		# Six classifiers spanning different model families. Tree-based models
		# get light caps (max_depth=10) to prevent overfitting on 206 samples.
		# Each tuple: (name, estimator, needs_scaling).
		classifiers = [
			("NaiveBayes",   GaussianNB(),                                                                False),
			("DecisionTree", DecisionTreeClassifier(max_depth=10, random_state=42),                       False),
			("RandomForest", RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),     False),
			("KNN",          KNeighborsClassifier(),                                                      True),
			("AdaBoost",     AdaBoostClassifier(n_estimators=200, random_state=42),                       False),
			# LinearSVC has no predict_proba on its own; CalibratedClassifierCV
			# wraps it to produce probability scores for the ROC curve.
			("LinearSVC",    CalibratedClassifierCV(LinearSVC(max_iter=5000, random_state=42), cv=5),     True),
		]

		# Keep all reports and plots inside results/ so the project root stays
		# clean and the graded deliverables are easy to find.
		results_dir = "results"
		os.makedirs(results_dir, exist_ok=True)

		# Open the results file inside results/
		base_name = os.path.basename(dataset_filename)
		result_filename = os.path.join(results_dir, base_name + ".results.txt")
		file_result = open(result_filename, "w")

		# Provenance header in the results file
		file_result.write("=== SEMetrics classification report ===\n")
		file_result.write("Dataset: %s\n" % dataset_filename)
		file_result.write("Samples: %d total | %d train | %d test\n" % (len(X), len(train_X), len(test_X)))
		file_result.write("Selected features (top %d by mutual information):\n  %s\n\n"
		                  % (k, ", ".join(selected_features)))

		# Train each classifier, write its report, save its ROC, and (for
		# tree-based models only) save a Top-10 feature importance chart.
		for cn, clf, needs_scaling in classifiers:
			t_X  = train_X_scaled if needs_scaling else train_X_sel
			te_X = test_X_scaled  if needs_scaling else test_X_sel
			filename_roc = os.path.join(results_dir, "ROC_" + cn + ".png")
			self.classify_with_split(cn, t_X, te_X, train_y, test_y, clf, file_result, filename_roc)

			# Feature importance is only available on tree-based models.
			if hasattr(clf, "feature_importances_"):
				self._save_feature_importance(cn, clf.feature_importances_, selected_features, results_dir, file_result)

		# --- 10-fold cross-validation ---
		# Wrap each classifier in a Pipeline so feature selection (and scaling
		# where applicable) is refit inside every fold. Avoids leakage and
		# gives an honest stability estimate alongside the single 80/20 split.
		file_result.write("\n=== 10-fold cross-validation (accuracy) ===\n")
		print("\n=== 10-fold cross-validation (accuracy) ===")
		for cn, clf, needs_scaling in classifiers:
			steps = [("select", SelectKBest(score_func=mutual_info_classif, k=k))]
			if needs_scaling:
				steps.append(("scale", StandardScaler()))
			steps.append(("clf", clf))
			pipe = Pipeline(steps)
			try:
				scores = cross_val_score(pipe, X, y, cv=10, scoring="accuracy")
				line = "%-12s  mean = %.4f   std = %.4f\n" % (cn, scores.mean(), scores.std())
			except Exception as e:
				line = "%-12s  CV failed: %s\n" % (cn, str(e))
			file_result.write(line)
			print(line.rstrip())

		# Close the file
		file_result.close()

	def _save_feature_importance(self, cn, importances, feature_names, results_dir, file_result):
		# Save a horizontal bar chart of the top-10 features for tree-based
		# classifiers. Helps interpret which software-engineering metrics
		# drive the benign-vs-malware decision.
		idx = np.argsort(importances)[::-1][:10]
		top_names = [feature_names[i] for i in idx]
		top_vals  = [importances[i]   for i in idx]

		fig, ax = plt.subplots(figsize=(8, 5))
		ax.barh(range(len(top_names)), top_vals, color="#4C72B0")
		ax.set_yticks(range(len(top_names)))
		ax.set_yticklabels(top_names)
		ax.invert_yaxis()
		ax.set_xlabel("Importance")
		ax.set_title("Top 10 Feature Importances - " + cn)
		ax.grid(True, axis="x", alpha=0.3)
		fig.tight_layout()
		out = os.path.join(results_dir, "FeatureImportance_" + cn + ".png")
		fig.savefig(out)
		plt.close(fig)

		file_result.write("Top 10 features (%s):\n" % cn)
		for n, v in zip(top_names, top_vals):
			file_result.write("  %-30s %.4f\n" % (n, v))
		file_result.write("(chart saved to %s)\n\n" % out)

	#
	# It's not an n-fold cross validation but a %age split,
	# e.g., 80% training and 20% testing
	# clf is the classifier passed
	# e.g., NaiveBayes, RandomForest etc
	#
	def classify_with_split(self, cn, train_X, test_X, train_y, test_y, clf, file_result, filename_roc):
		try:
			result = cn
			print(result)
			warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

			class_labels = set(test_y)               # Extract the class labels from the test_y
			class_labels = list(class_labels)        # Confusion matrix requires class labels in a list
			cl = list()
			for names in class_labels:
				cl.append(str(self.file_types[names]))
			clf.fit(train_X, train_y)
			predicted = clf.predict(test_X)
			expected = test_y
			class_labels = set(expected)      # Extract the class labels from the true_y
			class_labels = list(class_labels) # Confusion matrix requires class labels in a list
			cm = confusion_matrix(expected, predicted, labels=class_labels)
			# Confusion matrix of 2 classes
			#   |_A__|_B__
			# A |_TP_|_FN_
			# B |_FP_|_TN_
			# --- BONUS: print confusion matrix in a readable form ---
			# Render the matrix as a small aligned text table so it appears in
			# the results file directly above the classification report.
			cm_text = "\n=== " + cn + " ===\n"
			cm_text += "Confusion Matrix (rows=actual, cols=predicted):\n"
			cm_text += "            " + "  ".join("%-10s" % t for t in cl) + "\n"
			for i, row in enumerate(cm):
				cm_text += "%-12s" % cl[i] + "  ".join("%-10d" % v for v in row) + "\n"
			print(cm_text)
			result += cm_text + "\n"
			report = classification_report(expected, predicted, target_names=cl)
			print("--- Report ---\n", report)
			result += "--- Report ---\n" + str(report) + "\n"
			result += self.classification_results(cm, class_labels)

			# --- BONUS: ROC curve + AUC (only for classifiers with predict_proba) ---
			# ROC needs probability scores. Classifiers without predict_proba
			# (e.g. LinearSVC) are skipped gracefully instead of raising.
			if hasattr(clf, "predict_proba"):
				try:
					proba = clf.predict_proba(test_X)
					if proba.shape[1] == 2:
						pos_proba = proba[:, 1]
						fpr, tpr, _ = roc_curve(test_y, pos_proba)
						roc_auc = auc(fpr, tpr)
						fig, ax = plt.subplots(figsize=(6, 5))
						ax.plot(fpr, tpr, label="%s (AUC = %.3f)" % (cn, roc_auc))
						ax.plot([0, 1], [0, 1], "k--", label="Random")
						ax.set_xlabel("False Positive Rate")
						ax.set_ylabel("True Positive Rate")
						ax.set_title("ROC Curve - " + cn)
						ax.legend(loc="lower right")
						ax.grid(True, alpha=0.3)
						fig.tight_layout()
						fig.savefig(filename_roc)
						plt.close(fig)
						result += "ROC AUC = %.4f  (saved to %s)\n\n" % (roc_auc, filename_roc)
					else:
						result += "ROC skipped: not a binary classification.\n\n"
				except Exception as e:
					result += "ROC skipped due to error: " + str(e) + "\n\n"
			else:
				result += "ROC skipped: " + cn + " has no predict_proba.\n\n"

			file_result.write(result)
			if __DEBUG__:
				print(result)
		except ValueError:
			print("--- Data ERROR ---")
			print("Error:Classify::classify_with_split: Value Error!")
			pass

	#
	#
	#
	def classification_results(self, cm, class_labels):
		result = ""

		tp = np.diag(cm)
		fn = cm.sum(axis=1) - np.diag(cm)
		fp = cm.sum(axis=0) - np.diag(cm)
		tn = cm.sum() - (tp + fn + fp)
		classes = len(cm[0])
		tpr = np.empty(classes, dtype=float)
		fpr = np.empty(classes, dtype=float)
		accuracy = np.empty(classes, dtype=float)
		f1_score = np.empty(classes, dtype=float)
		precision = np.empty(classes, dtype=float)
		mean_tpr = mean_fpr = mean_accuracy = mean_f1_score = mean_precision = 0.0
		for i in range(classes):
			tpr[i] = 0
			if (tp[i] + fn[i]) > 0:
				tpr[i] = tp[i] / (tp[i] + fn[i])   #tp / (tp + fn)
			mean_tpr = mean_tpr + tpr[i]
			fpr[i] = 0
			if (fp[i] + tn[i]) > 0:
				fpr[i] = fp[i] / (fp[i] + tn[i])   #fp / (fp + tn)
			mean_fpr = mean_fpr + fpr[i]
			accuracy[i] = 0
			if (tp[i] + tn[i] + fp[i] + fn[i]) > 0:
				accuracy[i] = (tp[i] + tn[i]) / (tp[i] + tn[i] + fp[i] + fn[i])   #(tp + tn) / (tp + tn + fp + fn)
			mean_accuracy = mean_accuracy + accuracy[i]
			f1_score[i] = 0
			if ((2 * tp[i]) + fp[i] + fn[i]) > 0:
				f1_score[i] = (2 * tp[i]) / ((2 * tp[i]) + fp[i] + fn[i])   #(2 * tp) / ((2 * tp) + fp + fn)
			mean_f1_score = mean_f1_score + f1_score[i]
			precision[i] = 0
			if (tp[i] + fp[i]) > 0:
				precision[i] = tp[i] / (tp[i] + fp[i])   #tp / tp + fp
			mean_precision = mean_precision + precision[i]
			n = class_labels[i]     # Get the specific class label (int) from the confusion matrix class labels
			c = self.file_types[n]  # Get the type (string label) of the file from the stored file types
			result += "Reporting results for Class " + c + "\n"
			result += "   TPR = " + str(tpr[i]) + "\n"
			result += "   FPR = " + str(fpr[i]) + "\n"
			result += "   Accuracy = " + str(accuracy[i]) + "\n"
			result += "   F1 Score = " + str(f1_score[i]) + "\n"
			result += "   Precision = " + str(precision[i]) + "\n"
		mean_tpr = mean_tpr / classes
		mean_fpr = mean_fpr / classes
		mean_accuracy = mean_accuracy / classes
		mean_f1_score = mean_f1_score / classes
		mean_precision = mean_precision / classes
		result += "Average TPR = " + str(mean_tpr) + "\n"
		result += "Average FPR = " + str(mean_fpr) + "\n"
		result += "Average Accuracy = " + str(mean_accuracy) + "\n"
		result += "Average F1 Score = " + str(mean_f1_score) + "\n"
		result += "Average Precision = " + str(mean_precision) + "\n\n"

		return result

	#
	#
	#
	def plot_df(self, df, fn, label_y="Mean SHAP Values", title="Feature Importance (SHAP)", step=3):
		fig,ax = plt.subplots()
		plt.title(title, fontsize=100)
		fig.set_size_inches(120, 60)
		df.plot.bar(ax=ax)
		plt.yticks(fontsize=40)
		plt.xticks(fontsize=40)

		ax.set_ylabel(label_y, size=80)
		ax.set_xlabel('Features', size=80)
		f = list()
		n = 0
		for i in fn:
			if n%step == 0:
				f.append(i)
			else:
				f.append('')
			n += 1
		f[n-1] = fn[n-1]
		ax.set_xticklabels(f, rotation=90)
		ax.legend(fontsize=80)
		if len(df.columns) <= 1:
			ax.get_legend().remove()
		if "SHAP" in title:
			plt.savefig("fi_SHAP.png")
			plt.savefig("fi_SHAP.pdf")
		elif "LIME" in title:
			plt.savefig("fi_LIME.png")
			plt.savefig("fi_LIME.pdf")
		else:
			plt.savefig("fi_RF.png")
			plt.savefig("fi_RF.pdf")
