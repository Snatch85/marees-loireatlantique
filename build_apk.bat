@echo off
echo ================================================
echo   Marees Loire-Atlantique - Construction APK
echo ================================================
echo.

REM Verifier que JAVA est dispo
java -version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Java n'est pas installe ou pas dans le PATH.
    echo Installez Android Studio depuis https://developer.android.com/studio
    echo Puis relancez ce script.
    pause
    exit /b 1
)

echo Java detecte. Construction de l'APK...
echo.

cd /d "%~dp0android"

REM Build APK debug (ne necessite pas de signature)
call gradlew.bat assembleDebug

if errorlevel 1 (
    echo.
    echo ERREUR lors de la construction.
    echo Ouvrez Android Studio et lancez Build > Make Project
    pause
    exit /b 1
)

echo.
echo ================================================
echo   APK construit avec succes !
echo ================================================
echo.
echo Fichier APK:
echo   android\app\build\outputs\apk\debug\app-debug.apk
echo.
echo Copiez ce fichier sur votre telephone Android
echo et installez-le (activez Sources inconnues dans Parametres).
echo.
pause
