@echo off
chcp 65001 >nul
title Dashboard Ventes — Lancement
color 0A

echo.
echo  ╔══════════════════════════════════════╗
echo  ║       Dashboard Ventes — v2          ║
echo  ╚══════════════════════════════════════╝
echo.

:: ── Vérification Python ───────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python introuvable dans le PATH.
    echo  Installez Python depuis https://python.org puis relancez.
    pause
    exit /b 1
)

:: ── Vérification des dépendances ──────────────────────────────────────
echo  [0/3] Vérification des dépendances pip...
python -c "import pandas, numpy, matplotlib" >nul 2>&1
if errorlevel 1 (
    echo  Installation des dépendances manquantes...
    python -m pip install --quiet pandas numpy matplotlib
    if errorlevel 1 (
        echo  [ERREUR] Installation pip échouée. Vérifiez votre connexion.
        pause
        exit /b 1
    )
)
echo         OK.

:: ── Génération des données et graphes ────────────────────────────────
echo.
echo  [1/3] Génération des données + graphes (produits)...
echo         Cela peut prendre 30 à 90 secondes, veuillez patienter...
echo.
python vente.py
if errorlevel 1 (
    echo.
    echo  [ERREUR] vente.py a échoué.
    echo  Consultez le message ci-dessus pour le détail.
    pause
    exit /b 1
)

:: ── Vérification que le JSON a bien été créé ─────────────────────────
if not exist "dashboard_data.json" (
    echo.
    echo  [ERREUR] dashboard_data.json introuvable après exécution.
    pause
    exit /b 1
)

:: ── Libération du port 8000 si occupé ────────────────────────────────
echo.
echo  [2/3] Vérification du port 8000...
for /f "tokens=5" %%P in (
    'netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING" 2^>nul'
) do (
    echo         Port 8000 occupé (PID %%P) — fermeture...
    taskkill /PID %%P /F >nul 2>&1
    timeout /t 1 /nobreak >nul
)
echo         Port 8000 libre.

:: ── Démarrage du serveur HTTP ─────────────────────────────────────────
echo.
echo  [3/3] Démarrage du serveur HTTP sur http://localhost:8000 ...
echo.

:: Ouvre le navigateur 2 secondes après (laisse le serveur démarrer)
start "" cmd /c "timeout /t 2 /nobreak >nul && start "" http://localhost:8000/dashboard.html"

:: Lance le serveur — Ctrl+C pour arrêter
python -m http.server 8000 --bind 127.0.0.1

echo.
echo  Serveur arrêté. Appuyez sur une touche pour fermer.
pause >nul