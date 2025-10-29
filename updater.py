import requests
import os
import sys
import time
import subprocess
import ctypes

# ----------------------
# Konfiguration
# ----------------------
EXE_URL = "https://github.com/LordRaspy/garmin/raw/main/dist/main.exe"

# Garmin-Ordner (muss mit main.py übereinstimmen)
GARMIN_DIR = os.path.join(os.environ["APPDATA"], "Garmin")
MAIN_EXE = os.path.join(GARMIN_DIR, "main.exe")

# ----------------------
# Funktion für Popup-Nachricht
# ----------------------
def notify_user(message, title="Garmin Update"):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)  # 0x40 = Info-Icon

# ----------------------
# Hauptfunktion
# ----------------------
def main():
    # Kurze Pause, damit main.exe beendet ist
    time.sleep(2)

    try:
        # Neue main.exe herunterladen
        r = requests.get(EXE_URL)
        r.raise_for_status()  # Fehler, wenn Download fehlschlägt
        with open(MAIN_EXE, "wb") as f:
            f.write(r.content)

        # Benutzer benachrichtigen
        notify_user("✅ Garmin wurde erfolgreich aktualisiert!")

        # Neue main.exe starten
        subprocess.Popen([MAIN_EXE])
        sys.exit(0)

    except Exception as e:
        notify_user(f"❌ Update fehlgeschlagen:\n{e}", "Garmin Updater Fehler")
        sys.exit(1)

# ----------------------
# Script ausführen
# ----------------------
if __name__ == "__main__":
    main()
