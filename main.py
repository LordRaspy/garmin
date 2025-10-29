import os
import sys
import shutil
import subprocess
import threading
import time
import ctypes

import pygame
import requests
import speech_recognition as sr

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

    # Musik-Dateien aus EXE extrahieren
    for file in ["bibibip.mp3", "hymne.mp3"]:
        src = os.path.join(getattr(sys, "_MEIPASS", "."), file)
        dst = os.path.join(GARMIN_DIR, file)
        if os.path.exists(src):
            shutil.copy2(src, dst)

    # Updater herunterladen
    updater_url = "https://github.com/LordRaspy/garmin/raw/main/dist/updater.exe"
    updater_path = os.path.join(GARMIN_DIR, "updater.exe")
    if not os.path.exists(updater_path):
        r = requests.get(updater_url)
        with open(updater_path, "wb") as f:
            f.write(r.content)

    # EXE in Garmin-Ordner kopieren und Neustart
    main_exe = os.path.join(GARMIN_DIR, "main.exe")
    shutil.copy2(sys.argv[0], main_exe)

    # Autostart-Verknüpfung erstellen
    try:
        import winshell
        from win32com.client import Dispatch

        def create_startup_shortcut():
            startup = winshell.startup()
            path = os.path.join(startup, "Garmin.lnk")
            target = main_exe
            wDir = GARMIN_DIR
            icon = target

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()

        create_startup_shortcut()
    except:
        pass

    # Neustart der EXE aus Garmin-Ordner
    subprocess.Popen([main_exe])
    sys.exit(0)

# ----------------------
# Pfad Helfer
# ----------------------
def resource_path(filename):
    """Pfad zu Ressourcen (EXE oder Garmin-Ordner)"""
    base_path = getattr(sys, "_MEIPASS", GARMIN_DIR)
    return os.path.join(base_path, filename)

# ----------------------
# User Notification
# ----------------------
def notify_user(message, title="Garmin"):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)  # Info

# ----------------------
# Musik-System
# ----------------------
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

def play_music(file):
    try:
        filepath = resource_path(file)
        if not os.path.exists(filepath):
            print(f"❌ Datei nicht gefunden: {filepath}")
            return
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
    flag_file = os.path.join(GARMIN_DIR, "installed.flag")
    if not os.path.exists(flag_file):
        notify_user("🎉 Garmin wurde erfolgreich installiert! Du kannst jetzt Befehle geben.")
        play_music("bibibip.mp3")
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
            play_music("bibibip.mp3")
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
            play_music("bibibip.mp3")

            while True:
                command = listen()

                if "spiele deine hymne" in command.lower():
                    print("🎵 Spiele Hymne...")
                    play_music("bibibip.mp3")
                    time.sleep(1)
                    play_music("hymne.mp3")
                    break

                elif "schicht starten" in command.lower():
                    print("Schicht wird gestartet...")
                    play_music("bibibip.mp3")
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
