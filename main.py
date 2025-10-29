import subprocess
import threading
import speech_recognition as sr
import pygame
import os
import time
import shutil
import sys
import ctypes
import requests

# ----------------------
# Versions-Check
# ----------------------
VERSION_URL = "https://raw.githubusercontent.com/LordRaspy/garmin/main/version.txt"
current_version = "1.1"

# ----------------------
# Garmin-Ordner erstellen
# ----------------------
APPDATA = os.environ["APPDATA"]
GARMIN_DIR = os.path.join(APPDATA, "Garmin")

if not os.path.exists(GARMIN_DIR):
    os.makedirs(GARMIN_DIR)

    # Musikdateien kopieren
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    for file in ["bibibip.mp3", "hymne.mp3"]:
        src = os.path.join(exe_dir, file)
        dst = os.path.join(GARMIN_DIR, file)
        if os.path.exists(src):
            shutil.copy2(src, dst)

    # Updater herunterladen
    updater_path = os.path.join(GARMIN_DIR, "updater.exe")
    updater_url = "https://github.com/LordRaspy/garmin/raw/main/dist/updater.exe"
    if not os.path.exists(updater_path):
        r = requests.get(updater_url)
        with open(updater_path, "wb") as f:
            f.write(r.content)

    # Main.exe selbst in Garmin-Ordner kopieren und neu starten
    main_exe = os.path.join(GARMIN_DIR, "main.exe")
    shutil.copy2(sys.argv[0], main_exe)
    subprocess.Popen([main_exe])
    sys.exit(0)  # Aktuellen Prozess beenden

# ----------------------
# Pfad Helfer
# ----------------------
def resource_path(relative_path):
    return os.path.join(GARMIN_DIR, relative_path)

# ----------------------
# User Notification
# ----------------------
def notify_user(message):
    ctypes.windll.user32.MessageBoxW(0, message, "Garmin", 0x40)  # Info

# ----------------------
# Autostart
# ----------------------
startup = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
startup_exe = os.path.join(startup, "Garmin.exe")
if not os.path.exists(startup_exe):
    shutil.copy2(os.path.join(GARMIN_DIR, "main.exe"), startup_exe)

# ----------------------
# Musik-System
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
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language="de-DE").lower()
    except:
        return ""

# ----------------------
# Erstinstallationsnachricht
# ----------------------
def first_run_notification():
    flag_file = resource_path("installed.flag")
    if not os.path.exists(flag_file):
        notify_user("🎉 Garmin wurde erfolgreich installiert! Du kannst jetzt Befehle geben.")
        play_music(resource_path("bibibip.mp3"))
        with open(flag_file, "w") as f:
            f.write("installed")

first_run_notification()

# ----------------------
# Update-Check via Updater.exe
# ----------------------
def check_update():
    try:
        r = requests.get(VERSION_URL)
        latest_version = r.text.strip()
        if latest_version != current_version:
            notify_user("🔄 Neue Version gefunden! Garmin wird jetzt aktualisiert...")
            play_music(resource_path("bibibip.mp3"))
            updater_exe = os.path.join(GARMIN_DIR, "updater.exe")
            subprocess.Popen([updater_exe])
            sys.exit(0)
    except Exception as e:
        print("⚠️ Update-Check fehlgeschlagen:", e)

    threading.Timer(1800, check_update).start()  # alle 30 Minuten prüfen

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
