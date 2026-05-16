# --------------------------------------------------------------------------------------------------------------
#
# Filename: SEMetrics.py
# Author: Shahid Alam (sha.alam@uoh.edu.sa)
# Dated: Feb, 03, 2026
# SEMetrics => Software Engineering Metrics for Sifting Android Malicious Applications
#
# --------------------------------------------------------------------------------------------------------------

from __future__ import print_function
import os, sys, argparse
import pandas as pd

from Classify import *

__DEBUG__ = True
CLASS_LABEL = "Class"
__WITH_APK__ = False

# Classes
classes = ['benign', 'malware']


if __name__ == "__main__":
	print("--- SEMetrics START ---")

	parser = argparse.ArgumentParser()

	parser.add_argument("-f", type=str)
	parser.add_argument("-csv", type=str)
	args = parser.parse_args()

	if args.csv == None:
		print("ERROR:SEMetrics: Missing arguments\nUsage:\n")
		print("   python SEMetrics.py -csv <csv_filename>")
		sys.exit(1)

	csv_filename = args.csv.strip()

	if csv_filename is None:
		print("Please enter the filename of the csv file list")
		print("   python SEMetrics.py -csv <csv_filename>")
		sys.exit(1)

	# If the features have not already been extracted,
	# extract the features from the generated CSV files.
	# It assumes that the method level features for APKs
	# have already been collected in respective APK CSV
	# files. It then calculates different metrics for each
	# APK and combines them all in one CSV file for classification.
	if args.f == None:
		print("ERROR:SEMetrics: Missing arguments\nUsage:\n")
		print("   python SEMetrics.py -f <file_containing_csv_files> -csv <csv_filename>")
		sys.exit(1)

	file_containing_csv_files = args.f.strip()

	if file_containing_csv_files is None:
		print("Please enter the filename containing the list of CSV files")
		print("   python SEMetrics.py -f <file_containing_csv_files> -csv <csv_filename>")
		sys.exit(1)

	if not os.path.isfile(file_containing_csv_files):
		print("File '%s' does not exist" % file_containing_csv_files)
		print("   python SEMetrics.py -f <file_containing_csv_files> -csv <csv_filename>")
		sys.exit(1)

	file_containing_csv_files = os.path.abspath(file_containing_csv_files)
	print("Reading list of files from %s" % file_containing_csv_files)

	f = open(file_containing_csv_files, 'r')
	files = f.readlines()
	f.close()

	df = pd.DataFrame()  # Original dataframe that will hold the final CSV

	for csv_file in files:
		try:
			csv_file = csv_file.strip()

			if csv_file == "":
				continue

			print("------ Processing file: " + csv_file)

			if not os.path.isfile(csv_file):
				print("ERROR: File does not exist: " + csv_file)
				continue

			data = pd.read_csv(csv_file)

			dict = {}

			apk_filename = os.path.basename(csv_file)
			apk_filename = apk_filename.replace(".csv", "")

			if __WITH_APK__:
				dict["APK"] = apk_filename  # Name of the APK file

			# Number of rows i.e., methods in the APK
			dict["Number-Of-Methods"] = len(data.index)

			# Class label: 0 = benign, 1 = malware
			dict[CLASS_LABEL] = 0
			if "malware" in csv_file.lower():
				dict[CLASS_LABEL] = 1

			# Select only numeric columns and ignore non-numeric columns such as Method
			numeric_data = data.select_dtypes(include=['number'])

			# Compute statistical measurements for each numeric feature
			for h in numeric_data.columns:
				dict["Max-" + h] = numeric_data[h].max()
				dict["Mean-" + h] = numeric_data[h].mean()
				dict["Median-" + h] = numeric_data[h].median()
				dict["Min-" + h] = numeric_data[h].min()
				dict["Range-" + h] = numeric_data[h].max() - numeric_data[h].min()
				dict["Std-" + h] = numeric_data[h].std()
				dict["Sum-" + h] = numeric_data[h].sum()
				dict["Var-" + h] = numeric_data[h].var()

			# Add this APK/sample row to the final dataframe
			df = pd.concat([df, pd.DataFrame([dict])], ignore_index=True)

		except Exception as error:
			print("ERROR: Processing file: " + csv_file)
			print(error)

	if df.empty != True:
		df[CLASS_LABEL] = df[CLASS_LABEL].astype(int)

		if __DEBUG__:
			print(df)

		df.to_csv(csv_filename, index=False)
		print("Final dataset created: " + csv_filename)
	else:
		print("ERROR: Dataframe empty")

	# Classification
	if not os.path.isfile(csv_filename):
		print("File '%s' does not exist" % csv_filename)
		sys.exit(1)

	CL = Classifier(CLASS_LABEL, classes)
	dataset = pd.read_csv(csv_filename)

	if len(dataset) >= 29:  # more than 29 samples
		if dataset.isna().any(axis=None) == True:
			dataset.interpolate(method='linear', inplace=True)

		if dataset.isna().any(axis=None) == True:
			print("Missing values still present in the dataset")
			sys.exit(1)

		dataset.to_csv(csv_filename, index=False)

		# Call the classify method of the Classifier class
		CL.classify(dataset, csv_filename)

	else:
		print("ERROR:Nothing to classify in file %s" % csv_filename)

	print("--- SEMetrics END ---")