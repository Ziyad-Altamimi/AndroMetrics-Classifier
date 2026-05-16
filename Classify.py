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
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_curve, auc, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.feature_selection import VarianceThreshold, SelectKBest, mutual_info_classif

import warnings
from sklearn import preprocessing
from sklearn.exceptions import UndefinedMetricWarning
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

from SEMetricsBonus import Bonus

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
		X = dataset.drop(columns=[self.CLASS_LABEL])
		y = dataset[self.CLASS_LABEL]

		selector = VarianceThreshold(threshold=0.01)
		X = selector.fit_transform(X)
		retained = sum(selector.get_support())
		print("Features retained after variance threshold: %d / %d" % (retained, X.shape[1]))

		k_best = SelectKBest(mutual_info_classif, k=30)
		X = k_best.fit_transform(X, y)
		print("Features retained after SelectKBest: %d" % X.shape[1])

		scaler = preprocessing.StandardScaler()
		X = pd.DataFrame(scaler.fit_transform(X))

		clf_names = [
			"GaussianNB",
			"DecisionTreeClassifier",
			"RandomForestClassifier",
			"AdaBoostClassifier",
			"LinearSVC"
		]
		classifiers = [
			GaussianNB(var_smoothing=1e-9),
			DecisionTreeClassifier(max_depth=5, min_samples_split=5, min_samples_leaf=2, class_weight='balanced', random_state=42),
			RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=5, min_samples_leaf=2, class_weight='balanced', random_state=42),
			AdaBoostClassifier(n_estimators=50, learning_rate=0.5, random_state=42),
			LinearSVC(C=1.0, max_iter=2000, dual='auto', class_weight='balanced', random_state=42)
		]

		test_size = testSize / 100.0
		train_X, test_X, train_y, test_y = train_test_split(
			X, y, test_size=test_size, random_state=42, stratify=y
		)

		result_filename = dataset_filename.replace(".csv", "_results.txt")
		file_result = open(result_filename, "w")

		for i, clf in enumerate(classifiers):
			cn = clf_names[i]
			roc_filename = dataset_filename.replace(".csv", "_roc_" + cn + ".png")
			cm_filename = dataset_filename.replace(".csv", "_cm_" + cn + ".png")
			self.classify_with_split(cn, train_X, test_X, train_y, test_y, clf, file_result, roc_filename, cm_filename)

		file_result.close()

	#
	# It's not an n-fold cross validation but a %age split,
	# e.g., 80% training and 20% testing
	# clf is the classifier passed
	# e.g., NaiveBayes, RandomForest etc
	#
	def classify_with_split(self, cn, train_X, test_X, train_y, test_y, clf, file_result, filename_roc, filename_cm=""):
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
			optimal_threshold = 0.5
			try:
				if hasattr(clf, 'predict_proba'):
					scores = clf.predict_proba(test_X)[:, 1]
				else:
					scores = clf.decision_function(test_X)
				if len(class_labels) == 2:
					fpr_curve, tpr_curve, thresholds = roc_curve(test_y, scores)
					youden_idx = np.argmax(tpr_curve - fpr_curve)
					optimal_threshold = thresholds[youden_idx]
					predicted = (scores >= optimal_threshold).astype(int)
				else:
					predicted = clf.predict(test_X)
			except:
				predicted = clf.predict(test_X)
			expected = test_y
			class_labels = set(expected)      # Extract the class labels from the true_y
			class_labels = list(class_labels) # Confusion matrix requires class labels in a list
			cm = confusion_matrix(expected, predicted, labels=class_labels)
			# Confusion matrix of 2 classes
			#   |_A__|_B__
			# A |_TP_|_FN_
			# B |_FP_|_TN_
			#print(cm)
			report = classification_report(expected, predicted, target_names=cl)
			print("--- Report ---\n", report)
			result += "--- Report ---\n" + str(report) + "\n"
			result += self.classification_results(cm, class_labels)
			if optimal_threshold != 0.5:
				result += "Optimized threshold: %.4f\n\n" % optimal_threshold

			# BONUS: Generate ROC curve visualization
			try:
				if hasattr(clf, 'predict_proba'):
					scores_bonus = clf.predict_proba(test_X)[:, 1]
				else:
					scores_bonus = clf.decision_function(test_X)
				fpr_bonus, tpr_bonus, _ = roc_curve(test_y, scores_bonus)
				roc_auc_bonus = auc(fpr_bonus, tpr_bonus)
				if filename_roc:
					Bonus.plot_roc_curve(fpr_bonus, tpr_bonus, roc_auc_bonus, cn, filename_roc)
			except:
				pass

			# BONUS: Generate confusion matrix heatmap
			if filename_cm:
				Bonus.plot_confusion_matrix(cm, cl, cn, filename_cm)

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
