@echo off

echo ================================
echo SEMetrics Feature Extraction
echo ================================

REM Use Java 17 because DroidASAT requires a newer Java runtime
set PATH=C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot\bin;%PATH%

echo.
echo Checking Java version...
java -version

echo.
echo Creating output directories...
if not exist out mkdir out
if not exist out\benign mkdir out\benign
if not exist out\malware mkdir out\malware
if not exist out\malware\adware mkdir out\malware\adware

echo.
echo Extracting features from benign APKs...
for %%f in (samples\benign\*.apk) do (
    echo Processing benign APK: %%f
    java -Xms512m -Xmx1024m -cp .;DroidASAT.jar;lib/rt.jar;lib/android-jar;lib/sootclasses-trunk-jar-with-dependencies.jar;lib/soot-infoflow.jar;lib/soot-infoflow-android.jar DroidASAT.main lib/rt.jar lib/android-jar "%%f" out\benign
)

echo.
echo Extracting features from malware APKs...
for %%f in (samples\malware\adware\*.apk) do (
    echo Processing malware APK: %%f
    java -Xms512m -Xmx1024m -cp .;DroidASAT.jar;lib/rt.jar;lib/android-jar;lib/sootclasses-trunk-jar-with-dependencies.jar;lib/soot-infoflow.jar;lib/soot-infoflow-android.jar DroidASAT.main lib/rt.jar lib/android-jar "%%f" out\malware\adware
)

echo.
echo Creating list_of_csv_files.txt...
dir /s /b out\*.csv > list_of_csv_files.txt

echo.
echo Feature extraction completed.
echo CSV list created: list_of_csv_files.txt

pause