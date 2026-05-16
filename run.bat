@echo off
REM ============================================================
REM  SEMetrics - Feature extraction with DroidASAT (Soot)
REM
REM  Processes every APK under:
REM     samples\benign            -> out\benign
REM     samples\malware\adware    -> out\malware\adware
REM
REM  Output: one CSV per APK (created by DroidASAT)
REM  Log:    run.log (all Soot/Java stdout + stderr)
REM ============================================================

setlocal

REM --- 1. Run from this script's own directory (handles spaces) ---
cd /d "%~dp0"

REM --- 2. Make sure the output folders exist --------------------
if not exist "out\benign"         mkdir "out\benign"
if not exist "out\malware\adware" mkdir "out\malware\adware"

REM --- 3. Reset the log file ------------------------------------
echo Run started at %DATE% %TIME% > run.log

REM --- 4. Common variables --------------------------------------
set "CP=.;DroidASAT.jar;lib/rt.jar;lib/sootclasses-trunk-jar-with-dependencies.jar;lib/soot-infoflow.jar;lib/soot-infoflow-android.jar"
set "MAIN=DroidASAT.main"
set "RT=lib/rt.jar"
set "APIS=lib/android-jar"
set "JVM_OPTS=-Xms2048m -Xmx4096m"

REM --- 5. Process benign APKs -----------------------------------
echo Processing benign samples...
for %%f in (samples\benign\*.apk) do (
    echo   %%~nxf
    echo --- %%f --- >> run.log
    java %JVM_OPTS% -cp "%CP%" %MAIN% %RT% %APIS% "%%f" "out\benign" >> run.log 2>&1
)

REM --- 6. Process malware APKs ----------------------------------
echo Processing malware samples...
for %%f in (samples\malware\adware\*.apk) do (
    echo   %%~nxf
    echo --- %%f --- >> run.log
    java %JVM_OPTS% -cp "%CP%" %MAIN% %RT% %APIS% "%%f" "out\malware\adware" >> run.log 2>&1
)

echo.
echo Done. Output CSVs are in out\benign and out\malware\adware.
echo See run.log for per-APK details.

endlocal
