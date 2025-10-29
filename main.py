import subprocess
import threading
import speech_recognition as sr
import pygame
import os
import time
import shutil
import requests
import sys
import ctypes  # Für Windows-Popup

# ----------------------
# Versions-Check & Update
# ----------------------
VERSION_URL = "https://raw.githubusercontent.com/LordRaspy/garmin/main/version.txt"
EXE_URL     = "https://github.com/LordRaspy/garmin/raw/main/dist/main.exe"
current_version = "1.0"

# Pfad zur laufenden EXE oder Skript
exe_path = os.path.abspath(sys.argv[0])

def resource_path(relative_path):
    """Pfad zu Ressourcen, funktioniert in EXE und Skript"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def notify_user(message):
    """Windows-Popup Nachricht"""
    ctypes.windll.user32.MessageBoxW(0, message, "Garmin Update", 0x40)  # 0x40 = Info-Icon

def check_update():
    try:
        r = requests.get(VERSION_URL)
        latest_version = r.text.strip()
        if latest_version != current_version:
            # User benachrichtigen
            notify_user("🔄 Neue Version gefunden! Garmin wird jetzt aktualisiert...")
            play_music(resource_path("bibibip.mp3"))  # optional Sound
            time.sleep(1)

            r = requests.get(EXE_URL)
            with open(exe_path, "wb") as f:
                f.write(r.content)

            notify_user("✅ Update abgeschlossen! Garmin wird neu gestartet...")
            os.execv(exe_path, [exe_path])
    except Exception as e:
        print("⚠️ Update-Check fehlgeschlagen:", e)

    # Timer für nächsten Check in 30 Minuten
    threading.Timer(1800, check_update).start()

# ----------------------
# Autostart einrichten
# ----------------------
startup = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
if not os.path.exists(os.path.join(startup, os.path.basename(exe_path))):
    shutil.copy2(exe_path, startup)

# ----------------------
# Musik-System initialisieren
# ----------------------
pygame.mixer.init()

def play_music(file):
    try:
        filepath = resource_path(file)
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print("❌ Fehler beim Abspielen:", e)

# ----------------------
# Spracherkennung
# ----------------------
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Garmin hört zu...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="de-DE").lower()
        print("Du sagtest:", text)
        return text
    except:
        return ""

# ----------------------
# Update-Thread starten
# ----------------------
check_update()

# ----------------------
# Haupt-Loop
# ----------------------
def main():
    while True:
        text = listen()

        if "okay garmin" in text:
            print("✅ Hotword erkannt! Bitte gib einen Befehl.")
            play_music(resource_path("bibibip.mp3"))

            while True:
                command = listen()

                if "spiele deine hymne" in command.lower():
                    print("🎵 Spiele Hymne...")
                    play_music(resource_path("bibibip.mp3"))
                    time.sleep(1)
                    play_music(resource_path("hymne.mp3"))
                    break

                elif "schicht starten" in command.lower():
                    print("Schicht wird gestartet...")
                    play_music(resource_path("bibibip.mp3"))
                    curseforge_path = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "CurseForge Windows")
                    exe_file = os.path.join(curseforge_path, "CurseForge.exe")
                    print("-> " + exe_file)
                    subprocess.Popen(
                        exe_file,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.DETACHED_PROCESS
                    )
                    time.sleep(1)
                    break

                else:
                    print("Befehl nicht erkannt:", command)

if __name__ == "__main__":
    main()
