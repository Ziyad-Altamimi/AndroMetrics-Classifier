--- Course Project ---

The purpose of the project is to extract software engineering metrics from
Android APKs and then use them to classify if an APK is malware or benign.

This course project is to be completed in a group of 3 - 4 students.
At the end, students will demonstrate their project to the instructor and
also submit a project report with their complete code.
The Python programming language will be used to complete the project.
Students are advised to install the Anaconda environment on their PCs to complete the project.
The instructor will explain the project in detail to students in the class/lab.

The following is provided to you:

run.bat is a shell script that runs the DroidASAT with associated libs to extract features from the APK files, both benign and malware. To run the script, you will need to change the directories to match your settings/environments.
There are ~200 samples, so you need to update the run.bat so that it runs all the samples/APKs.

HINT: Install Cygwin on Windows and use 'find' and 'awk', the two LINUX commands, to update run.bat 

It will create a CSV file for each APK in the same directory as the APK. For example, in the run.bat file provided, this dir is "out/benign" for all the benign files, and the dir for malware is "out/malware/adware".

The Classify.py file contains different helper methods to be used for classification. Here is the Python code to use Classify.py:

import pandas as pd
from Classify import *

CLASS_LABEL = "Class"
classes = ['benign', 'malware']

csv_filename = "name_of_the_final_csv_file.csv"
CL = Classifier(CLASS_LABEL, classes)
dataset = pd.read_csv(csv_filename)
CL.classify(dataset, csv_filename)


The students will develop and write the SEMetrics.py file:

The SEMetrics.py file takes a list of all these csv files (you will have to create and provide this file - you can look at the file, list_of_csv_files.txt, created for this purpose) generated above to create more features and generate a consolidated CSV file containing features extracted from all the samples, which can be used for classification.

Students will also complete the function 'classify' in the file Classify.py.

HINT: Use find to create the list_of_csv_files.txt file

Here is the workflow of the Project:

1. DATA COLLECTION

The students will be provided with ~200 benign and malware samples.

2. FEATURE EXTRACTION

They should create the run.bat file to run the tool that generates the CSV files for each sample.
A sample run.bat file is provided to the students.
After generating all the csv files, students need to compute the statistical data for each sample from these csv files.

The tool extracts some of the software engineering metrics from a sample. The list is given below.
A csv file contains the following extracted features:

Method,LOC,Is-Protected,Fan-In,Is-Static,Number-Of-Branches,CFG-Size,Number-Of-Parameters,Is-Public,Fan-Out,Number-Of-Invokes,Is-Private
<test.app.InstallService: void tryCountEnd(android.os.PowerManager$WakeLock)>,34,0,1,0,2,32,1,0,20,13,1
<test.app.DbSms: test.app.DbSmsItem loadItem(android.database.Cursor)>,35,0,2,0,0,35,1,0,9,19,1
<test.app.MainService: test.app.CommandResult executeCommand(test.app.Command)>,738,0,1,0,105,633,1,1,195,219,0
<test.app.InstallService: void startInstall()>,64,0,2,0,7,57,0,0,36,23,1

In this csv file, there are four methods.
The feature values of the first method 'tryCountEnd':
LOC (Lines of code) = 34
Fan-In = 0
Is-Static = 1 (Yes)
Number-Of-Branches = 2
CFG-Size = 32
Number-Of-Parameters = 1
Is-Public = 0 (No)
Fan-Out = 20
Number-Of-Invokes = 13
Is-Private = 1 (Yes)

These features are extracted for each method in the sample.
Now we need to compute the statistical measures of these metrics for each sample.
The following statistical measurements will be computed:
Number of methods in the sample.
Mean, median, range, minimum, maximum, standard deviation, variance, and sum of each feature.
After this we get 81 features for each sample/APK.
A final csv file is created with these features for each sample. This csv file will have 82 columns, the last column with be the class label, either benign or sample. If the name (e.g., ./samples/malware/adware/caed8a52a079ea0679071d976c698f35.apk) of the csv file contains malware in it then the class label for that sample/APK will be 1 (malware); otherwise the label will be 0 (benign).

A sample final csv file is listed below, containing 2 benign and 2 malware samples/APKs:

Class,Max-CFG-Size,Max-Fan-In,Max-Fan-Out,Max-Is-Private,Max-Is-Protected,Max-Is-Public,Max-Is-Static,Max-LOC,Max-Number-Of-Branches,Max-Number-Of-Invokes,Max-Number-Of-Parameters,Mean-CFG-Size,Mean-Fan-In,Mean-Fan-Out,Mean-Is-Private,Mean-Is-Protected,Mean-Is-Public,Mean-Is-Static,Mean-LOC,Mean-Number-Of-Branches,Mean-Number-Of-Invokes,Mean-Number-Of-Parameters,Median-CFG-Size,Median-Fan-In,Median-Fan-Out,Median-Is-Private,Median-Is-Protected,Median-Is-Public,Median-Is-Static,Median-LOC,Median-Number-Of-Branches,Median-Number-Of-Invokes,Median-Number-Of-Parameters,Min-CFG-Size,Min-Fan-In,Min-Fan-Out,Min-Is-Private,Min-Is-Protected,Min-Is-Public,Min-Is-Static,Min-LOC,Min-Number-Of-Branches,Min-Number-Of-Invokes,Min-Number-Of-Parameters,Number-Of-Methods,Range-CFG-Size,Range-Fan-In,Range-Fan-Out,Range-Is-Private,Range-Is-Protected,Range-Is-Public,Range-Is-Static,Range-LOC,Range-Number-Of-Branches,Range-Number-Of-Invokes,Range-Number-Of-Parameters,Std-CFG-Size,Std-Fan-In,Std-Fan-Out,Std-Is-Private,Std-Is-Protected,Std-Is-Public,Std-Is-Static,Std-LOC,Std-Number-Of-Branches,Std-Number-Of-Invokes,Std-Number-Of-Parameters,Sum-CFG-Size,Sum-Fan-In,Sum-Fan-Out,Sum-Is-Private,Sum-Is-Protected,Sum-Is-Public,Sum-Is-Static,Sum-LOC,Sum-Number-Of-Branches,Sum-Number-Of-Invokes,Sum-Number-Of-Parameters,Var-CFG-Size,Var-Fan-In,Var-Fan-Out,Var-Is-Private,Var-Is-Protected,Var-Is-Public,Var-Is-Static,Var-LOC,Var-Number-Of-Branches,Var-Number-Of-Invokes,Var-Number-Of-Parameters
0,553.0,1145.0,98.0,1.0,1.0,1.0,1.0,678.0,125.0,120.0,9.0,16.590862246650637,3.410511851597389,4.46891102713844,0.16763998625901752,0.06698728959120577,0.6499484713156991,0.24287186533837168,19.13156990724837,2.389213328753006,4.162487117828925,1.0144280316042598,9.0,1.0,2.0,0.0,0.0,1.0,0.0,9.0,0.0,1.0,1.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,2911.0,552.0,1145.0,98.0,1.0,1.0,1.0,1.0,677.0,125.0,120.0,9.0,25.613568387574094,23.392383099152287,7.986477756687267,0.3736104549711904,0.2500429368830989,0.47706775195517676,0.42889195973943245,31.46222634918354,5.735463360978616,8.051811253689456,1.1317647355903906,48296.0,9928.0,13009.0,488.0,195.0,1892.0,707.0,55692.0,6955.0,12117.0,2953.0,656.054885544935,547.2035870575055,63.78382695806049,0.13958477206377987,0.06252147028512538,0.22759363995556606,0.18394831312913096,989.871686847259,32.89553996512812,64.83166446504018,1.2808914167259866
0,733.0,116.0,83.0,1.0,1.0,1.0,1.0,955.0,222.0,161.0,29.0,17.687453600593912,2.455827765404603,3.4773570898292503,0.1588715664439495,0.06533036377134373,0.6540460282108389,0.2479584261321455,20.6369710467706,2.8507795100222717,3.9591685226429103,1.2605790645879733,9.0,1.0,2.0,0.0,0.0,1.0,0.0,10.0,1.0,1.0,1.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1347.0,732.0,116.0,83.0,1.0,1.0,1.0,1.0,954.0,222.0,161.0,29.0,33.70924337815482,5.1867159266768,6.567065118668908,0.36569204557912866,0.2471996624121338,0.4758549427686897,0.4319879456588452,41.90892161435393,8.499585108374298,8.584980936126723,1.684104681942215,23825.0,3308.0,4684.0,214.0,88.0,881.0,334.0,27798.0,3840.0,5333.0,1698.0,1136.3130891276744,26.902022104042775,43.12634427283788,0.13373067219984752,0.06110767309667293,0.22643792655739295,0.18661358519454938,1756.3577108780617,72.24294701449813,73.70189767365925,2.8362085797396888
1,838.0,95.0,241.0,1.0,1.0,1.0,1.0,1185.0,347.0,303.0,7.0,13.011583011583012,2.806949806949807,3.386100386100386,0.08494208494208494,0.1583011583011583,0.6447876447876448,0.2277992277992278,15.274131274131275,2.189189189189189,4.2007722007722,1.0424710424710424,5.0,1.0,1.0,0.0,0.0,1.0,0.0,5.0,0.0,1.0,1.0,1.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,259.0,837.0,94.0,241.0,1.0,1.0,1.0,1.0,1184.0,347.0,303.0,7.0,53.466535402525174,7.886881338615973,15.42867937113123,0.27933527222186616,0.36572987717804606,0.4795041985592038,0.42022440276782114,75.09094064516003,21.877542353234222,19.58756525399952,0.9971525711380399,3370.0,727.0,877.0,22.0,41.0,167.0,59.0,3956.0,567.0,1088.0,270.0,2858.670407949478,62.202897249408885,238.04414713717037,0.07802819430726408,0.13375834306066864,0.22992427643590432,0.17658854868157198,5638.649366974948,478.6268594175572,383.6727125796894,0.9943132501272037
1,201.0,308.0,98.0,1.0,1.0,1.0,1.0,231.0,50.0,138.0,7.0,16.756704980842912,2.861111111111111,4.5201149425287355,0.16187739463601533,0.12547892720306514,0.48084291187739464,0.29693486590038315,18.511494252873565,1.5335249042145593,5.669540229885057,1.0316091954022988,7.0,1.0,1.0,0.0,0.0,0.0,0.0,7.0,0.0,1.0,1.0,1.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1044.0,200.0,307.0,98.0,1.0,1.0,1.0,1.0,230.0,50.0,138.0,7.0,24.172125715701146,12.811520354657581,9.310793208365354,0.36851483473460867,0.33141993900443184,0.4998723310041249,0.4571265788383158,27.624118265412235,3.9684550280961433,11.426743260149639,1.0841651583839145,17494.0,2987.0,4719.0,169.0,131.0,502.0,310.0,19326.0,1601.0,5919.0,1077.0,584.2916616156607,164.1350537978055,86.69087016894238,0.13580318341947592,0.10983917596970132,0.24987234730349744,0.20896470908042297,763.0919099414818,15.748635310021562,130.57046153337518,1.1754140906536183

3. CLASSIFICATION

Now this csv file will become the input to a classifier for training and testing.
Students will be provided with a classifier file written in Python that they can
use in their code for training and testing different classifiers.

4. SUBMISSION

The students will submit their complete Python code and the results. --- 2 marks
They will also write a short project report. --- 2 marks
The report will contain the following:
All the steps were performed to complete the project. --- 2 marks
Include images of these steps in the report. --- 2 marks
Explain each step in detail. List the how, what, and why of each step. --- 2 marks

5. BONUS
Print the Confusion Matrix   --- 1 mark
Perform 10-fold cross-validation on the saved CSV file with Random Forest using WEKA   --- 2 marks
Read about ROC and visualize it as a graph   --- 2 marks


NOTE:
THE REST OF THE MARKS WILL BE ASSIGNED BASED ON YOUR PERFORMANCE, INCLUDING THE VIVA DURING THE PROJECT DEMONSTRATION
