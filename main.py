import subprocess
import speech_recognition as sr
import pygame
import os
import time
import shutil
import requests
import sys

VERSION_URL = "https://dein-server.com/version.txt"
EXE_URL = "https://dein-server.com/main.exe"

current_version = "1.0"

r = requests.get(VERSION_URL)
if r.text.strip() != current_version:
    # Neue Version verfügbar
    exe_path = os.path.abspath(sys.argv[0])
    r = requests.get(EXE_URL)
    with open(exe_path, "wb") as f:
        f.write(r.content)
    # Neustart
    os.execv(exe_path, [exe_path])

#Autostart
startup = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
shutil.copy2("main.exe", startup)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Musik-System initialisieren
pygame.mixer.init()

def play_music(file):
    try:
        filepath = os.path.join(SCRIPT_DIR, file)
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print("❌ Fehler beim Abspielen:", e)


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

def main():
    while True:
        text = listen()

        if "okay garmin" in text:
            print("✅ Hotword erkannt!")
            print("Bitte gib einen Befehl.")
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
                    print("-> " + exe_file)
                    subprocess.Popen(
                        exe_file,
                        stdout=subprocess.DEVNULL,  # stdout ignorieren
                        stderr=subprocess.DEVNULL,  # stderr ignorieren
                        creationflags=subprocess.DETACHED_PROCESS
                    )
                    time.sleep(1)
                    break

                else:
                    print("Befehl nicht erkannt.")
                    print("->" + command)

if __name__ == "__main__":
    main()