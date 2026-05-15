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

__DEBUG__  = True
CLASS_LABEL = "Class"
__WITH_APK__ = False
# Classes
classes = ['benign', 'malware']

if __name__=="__main__":
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
	# APK and combines them all in one CSV file for clasification.
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
		print("File '%s' does not exist"%file_containing_csv_files)
		print("   python SEMetrics.py -f <file_containing_csv_files> -csv <csv_filename>")
		sys.exit(1)

	file_containing_csv_files = os.path.abspath(file_containing_csv_files)
	print("Reading list of files from %s"%file_containing_csv_files)
	f = open(file_containing_csv_files, 'r')
	files = f.readlines()
	f.close()

	df = pd.DataFrame()    # Original dataframe that will hold the final CSV
	for csv_file in files:
		try:
			csv_file = csv_file.strip()
			print("------ Processing file: " + csv_file)
			data = pd.read_csv(csv_file)
			dict = {}
			apk_filename = os.path.basename(csv_file)
			apk_filename = apk_filename.replace(".csv", "")
			if __WITH_APK__:
				dict["APK"] = apk_filename                  # Name of the APK file
			dict["Number-Of-Methods"] = len(data.index)     # Number of rows i.e., methods in the APK
			dict[CLASS_LABEL] = 0                           # Benign
			if "malware" in csv_file:
				dict[CLASS_LABEL] = 1                       # Malware
			headers = list(data.columns)
            #
            # --- TASK TO COMPLETE ---
            # Compute the following metrics:
            # Sum, Variance, Standard Deviation, Mean, Max, Min, Range
            # These are statisitical measurements about data, you can more info from Google/chatGPT
            # Store them in dict and then concat the dict to the dataframe df
            #
		except Exception as error:
			print("ERROR: Processing file: " + csv_file)
			print(error)
	if df.empty != True:
		df[CLASS_LABEL] = df[CLASS_LABEL].astype(int)           # Changing the type of column CLASS_LABEL to int
		if __DEBUG__:
			print(df)
		df.to_csv(csv_filename, index=False)
	else:
		print("ERROR: Dataframe empty")

	# Classification
	if not os.path.isfile(csv_filename):
		print("File '%s' does not exist"%csv_filename)
		sys.exit(1)
	CL = Classifier(CLASS_LABEL, classes)
	dataset = pd.read_csv(csv_filename)
	if len(dataset) >= 29:   # more than 29 samples
		if dataset.isna().any(axis=None) == True:
			dataset.interpolate(method='linear', inplace=True)
		if dataset.isna().any(axis=None) == True:
			print("Missing values still present in the dataset")
			sys.exit(1)
		dataset.to_csv(csv_filename, index=False)
        #
        # --- TASK TO COMPLETE ---
        # Call the method classify of the class Classifier for classification
        #
	else:
		print("ERROR:Nothing to classify in file %s"%csv_filename)

	print("--- SEMetrics END ---")
