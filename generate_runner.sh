#!/bin/bash

SAMPLES_DIR="./samples"
RAM_MIN="1g"
RAM_MAX="4g"

# Linux classpath
CP_LINUX=".:DroidASAT.jar:lib/rt.jar:lib/sootclasses-trunk-jar-with-dependencies.jar:lib/soot-infoflow.jar:lib/soot-infoflow-android.jar"
# Windows classpath
CP_WIN=".;DroidASAT.jar;lib/rt.jar;lib/sootclasses-trunk-jar-with-dependencies.jar;lib/soot-infoflow.jar;lib/soot-infoflow-android.jar"

# Clear both files (no headers, no comments)
> run.sh
> run.bat

echo "[*] Scanning $SAMPLES_DIR for APKs..."

while IFS= read -r apk; do
    dir=$(dirname "$apk")
    out=$(echo "$dir" | sed 's|^\.\?/samples|./out|')
    
    # Linux .sh
    echo "java -Xms${RAM_MIN} -Xmx${RAM_MAX} -cp ${CP_LINUX} DroidASAT.main lib/rt.jar lib/android-jar ${apk} ${out}" >> run.sh
    
    # Windows .bat — same paths, windows classpath separator
    echo "java -Xms${RAM_MIN} -Xmx${RAM_MAX} -cp ${CP_WIN} DroidASAT.main lib/rt.jar lib/android-jar ${apk} ${out}" >> run.bat
    
done < <(find "$SAMPLES_DIR" -name "*.apk" -type f)

chmod +x run.sh 2>/dev/null

count=$(grep -c "^java" run.sh 2>/dev/null || echo "0")
echo "[+] Generated $count commands"
echo "[+] Linux : run.sh"
echo "[+] Windows: run.bat"
