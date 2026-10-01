import os
import sys
from multiprocessing import freeze_support
import streamlit.web.cli as stcli

if __name__ == "__main__":
    # 1. Le verrou indispensable pour empêcher Windows de cloner le processus
    freeze_support()
    
    # 2. Résolution du chemin exact du script (compatible PyInstaller)
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    script_path = os.path.join(base_dir, 'app_devis.py')
    
    # 3. Paramètres silencieux pour stabiliser l'exécutable
    sys.argv = [
        "streamlit", 
        "run", 
        script_path, 
        "--global.developmentMode=false",
        "--server.fileWatcherType=none",    # Désactive le rechargement automatique
        "--browser.gatherUsageStats=false"
    ]
    
    sys.exit(stcli.main())