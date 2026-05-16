# --------------------------------------------------------------------------------------------------------------
#
# Filename: Classify.py
# Author: Shahid Alam (sha.alam@uoh.edu.sa)
# Dated: Feb, 03, 2026
#
# --------------------------------------------------------------------------------------------------------------

from __future__ import print_function
import sys, math, time
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score

import warnings
from sklearn.exceptions import UndefinedMetricWarning
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier

__DEBUG__ = True


class Classifier:
	def __init__(self, CLASS_LABEL, file_types):
		self.CLASS_LABEL = CLASS_LABEL
		self.n_classes = 0
		self.file_types = file_types

	def classify(self, dataset, dataset_filename, testSize=20):
		# Separate the data into features (X) and Classes (y)
		X = dataset.drop(self.CLASS_LABEL, axis=1)
		y = dataset[self.CLASS_LABEL]

		# ------------------------------------------------------------------
		# Bonus: 10-fold cross-validation using Random Forest
		# ------------------------------------------------------------------
		cv_result_filename = dataset_filename.replace(".csv", "_10fold_random_forest.txt")

		try:
			class_counts = y.value_counts()
			min_class_count = class_counts.min()

			if min_class_count >= 2:
				n_splits = min(10, min_class_count)

				rf_cv = RandomForestClassifier(n_estimators=100, random_state=42)

				cv = StratifiedKFold(
					n_splits=n_splits,
					shuffle=True,
					random_state=42
				)

				cv_scores = cross_val_score(
					rf_cv,
					X,
					y,
					cv=cv,
					scoring='accuracy'
				)

				with open(cv_result_filename, "w") as cv_file:
					cv_file.write("Random Forest Cross-Validation\n")
					cv_file.write("Number of folds: " + str(n_splits) + "\n")
					cv_file.write("Scores: " + str(cv_scores) + "\n")
					cv_file.write("Mean Accuracy: " + str(cv_scores.mean()) + "\n")
					cv_file.write("Standard Deviation: " + str(cv_scores.std()) + "\n")

				print("Random Forest Cross-Validation")
				print("Number of folds:", n_splits)
				print("Scores:", cv_scores)
				print("Mean Accuracy:", cv_scores.mean())
				print("Standard Deviation:", cv_scores.std())

			else:
				with open(cv_result_filename, "w") as cv_file:
					cv_file.write("Cross-validation could not be performed.\n")
					cv_file.write("Reason: At least one class has fewer than 2 samples.\n")

		except Exception as cv_error:
			with open(cv_result_filename, "w") as cv_file:
				cv_file.write("Cross-validation error:\n")
				cv_file.write(str(cv_error))

		# ------------------------------------------------------------------
		# Create the 5 classifiers
		# ------------------------------------------------------------------
		classifiers = [
			("Naive Bayes\n", GaussianNB()),
			("Decision Tree\n", DecisionTreeClassifier(random_state=42)),
			("Random Forest\n", RandomForestClassifier(n_estimators=100, random_state=42)),
			("Linear SVM\n", LinearSVC(max_iter=10000, random_state=42)),
			("KNN\n", KNeighborsClassifier(n_neighbors=5))
		]

		# Split the data into 20% testing and 80% training
		train_X, test_X, train_y, test_y = train_test_split(
			X,
			y,
			test_size=testSize / 100,
			random_state=42,
			stratify=y
		)

		# Create the result file
		result_filename = dataset_filename.replace(".csv", "_results.txt")
		file_result = open(result_filename, "w")

		# Run the classifiers
		for cn, clf in classifiers:
			filename_roc = dataset_filename.replace(
				".csv",
				"_" + cn.strip().replace(" ", "_") + "_roc.png"
			)

			self.classify_with_split(
				cn,
				train_X,
				test_X,
				train_y,
				test_y,
				clf,
				file_result,
				filename_roc
			)

		# Close the file
		file_result.close()

	def classify_with_split(self, cn, train_X, test_X, train_y, test_y, clf, file_result, filename_roc):
		try:
			result = cn
			print(result)

			warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

			# Use fixed class labels for binary classification:
			# 0 = benign, 1 = malware
			class_labels = [0, 1]
			target_names = [str(self.file_types[0]), str(self.file_types[1])]

			clf.fit(train_X, train_y)

			predicted = clf.predict(test_X)
			expected = test_y

			cm = confusion_matrix(expected, predicted, labels=class_labels)

			# ------------------------------------------------------------------
			# Bonus: Print Confusion Matrix
			# ------------------------------------------------------------------
			print("--- Confusion Matrix ---")
			print(cm)

			result += "--- Confusion Matrix ---\n"
			result += str(cm) + "\n\n"

			report = classification_report(
				expected,
				predicted,
				labels=class_labels,
				target_names=target_names,
				zero_division=0
			)

			print("--- Report ---\n", report)

			result += "--- Report ---\n" + str(report) + "\n"
			result += self.classification_results(cm, class_labels)

			# ------------------------------------------------------------------
			# Bonus: ROC Curve and AUC
			# ------------------------------------------------------------------
			try:
				y_score = None

				if hasattr(clf, "predict_proba"):
					y_score = clf.predict_proba(test_X)[:, 1]
				elif hasattr(clf, "decision_function"):
					y_score = clf.decision_function(test_X)

				if y_score is not None:
					fpr, tpr, thresholds = roc_curve(expected, y_score)
					roc_auc = auc(fpr, tpr)

					plt.figure()
					plt.plot(fpr, tpr, label="ROC curve area = %0.2f" % roc_auc)
					plt.plot([0, 1], [0, 1], linestyle="--")
					plt.xlabel("False Positive Rate")
					plt.ylabel("True Positive Rate")
					plt.title("ROC Curve - " + cn.strip())
					plt.legend(loc="lower right")
					plt.savefig(filename_roc)
					plt.close()

					result += "ROC AUC = " + str(roc_auc) + "\n"
					result += "ROC graph saved as: " + filename_roc + "\n\n"

					print("ROC AUC =", roc_auc)
					print("ROC graph saved as:", filename_roc)

				else:
					result += "ROC graph could not be generated for " + cn.strip() + "\n\n"

			except Exception as roc_error:
				result += "ROC graph could not be generated for " + cn.strip() + "\n"
				result += "ROC Error: " + str(roc_error) + "\n\n"

			file_result.write(result)

			if __DEBUG__:
				print(result)

		except ValueError as error:
			print("--- Data ERROR ---")
			print("Error:Classify::classify_with_split: Value Error!")
			print(error)
			pass

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
				tpr[i] = tp[i] / (tp[i] + fn[i])

			mean_tpr = mean_tpr + tpr[i]

			fpr[i] = 0
			if (fp[i] + tn[i]) > 0:
				fpr[i] = fp[i] / (fp[i] + tn[i])

			mean_fpr = mean_fpr + fpr[i]

			accuracy[i] = 0
			if (tp[i] + tn[i] + fp[i] + fn[i]) > 0:
				accuracy[i] = (tp[i] + tn[i]) / (tp[i] + tn[i] + fp[i] + fn[i])

			mean_accuracy = mean_accuracy + accuracy[i]

			f1_score[i] = 0
			if ((2 * tp[i]) + fp[i] + fn[i]) > 0:
				f1_score[i] = (2 * tp[i]) / ((2 * tp[i]) + fp[i] + fn[i])

			mean_f1_score = mean_f1_score + f1_score[i]

			precision[i] = 0
			if (tp[i] + fp[i]) > 0:
				precision[i] = tp[i] / (tp[i] + fp[i])

			mean_precision = mean_precision + precision[i]

			n = class_labels[i]
			c = self.file_types[n]

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

	def plot_df(self, df, fn, label_y="Mean SHAP Values", title="Feature Importance (SHAP)", step=3):
		fig, ax = plt.subplots()
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
			if n % step == 0:
				f.append(i)
			else:
				f.append('')
			n += 1

		f[n - 1] = fn[n - 1]

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