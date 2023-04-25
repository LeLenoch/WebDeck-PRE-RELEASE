# import base64
import requests
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

import time
import numpy as np
import bisect

from ctypes import cast, POINTER, wintypes, WinDLL, Structure, c_char
import ctypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
import comtypes
import math

from uuid import UUID
import pygetwindow as gw
from pywinauto import Application
import mss
from PIL import Image
from deep_translator import GoogleTranslator
import pyautogui as keyboard
import keyboard as keyboard2
import webcolors
import pyaudio
from asyncio import sleep
import asyncio
import subprocess
import shutil
from shutil import copyfile
import pyperclip
import re
import sys
import random
from flask import Flask, request, jsonify, render_template, redirect, Blueprint
from flask_socketio import SocketIO, emit
from flask_sslify import SSLify
import json
import urllib.request
import zipfile
import win32api
import win32con
import win32gui
import win32com.client
from win10toast import ToastNotifier
import sounddevice as sd
import psutil
from psutil import *
import GPUtil
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.add_dll_directory(os.getcwd())
with open('config.json', encoding="utf-8") as f:
    config = json.load(f)
if config["settings"]["mp3_method"] == "vlc":
    try:
        import vlc
    except: pass
else:
    try:
        import pygame
        import pygame._sdl2.audio as sdl2_audio
    except Exception:
        pass
    pygame.init()
    pygame.mixer.init()


# def blockPrint():
#    sys.stdout = open(os.devnull, 'w')
#
#
# def enablePrint():
#    sys.stdout = sys.__stdout__


def print2(text):
    print(text)


if config["front"]["background"] and not config["front"]["background"].strip() == "":
    try:
        copyfile(config["front"]["background"].replace('/','\\\\'), "static/files/background-image")
    except:
        pass

def getarg(message, arg):
    return next((x.split(f'{arg}:', 1)[1].strip() for x in message.split() if x.startswith(f'{arg}:')), None)

def swapPositions(list, pos1, pos2):
    try:
        list[pos1], list[pos2] = list[pos2], list[pos1]
    except Exception:
        print(f"error swapping {pos1} with {pos2}")
    return list

letters = 'abcdefghijklmnopqrstuvwxyz'
def convert_position(size, position):
    position = (letters.index(position[0])*int(size.split('x')[0])) + int(position[1]) - 1
    return position


biggest_folder = {"name": "", "buttons_count": 0}
for folder_name, folder_content in config["front"]["buttons"].items():
    for button_content in folder_content:
        if 'position' in button_content.keys() and int(button_content['position'][1]) > int(config["front"]["width"]):

            index = letters.index(button_content['position'][0])
            new_letter = letters[index+1]
            button_content['position'] = new_letter + "1"
            with open('config.json', 'w', encoding="utf-8") as json_file:
                json.dump(config, json_file, indent=4)
            with open('config.json', encoding="utf-8") as f:
                config = json.load(f)

    for button_content in folder_content:
        if 'VOID' in button_content.keys():
            folder_content.pop(folder_content.index(button_content))
    total_boxes = int(config["front"]["width"]) * int(config["front"]["height"])
    while len(folder_content) < total_boxes:
        folder_content.append({"VOID": "VOID"})
    temp_folder = []
    for button_content in folder_content:
        if 'position' in button_content.keys():
            if len(button_content['position'].strip()) == 2:
                position = convert_position(f"{config['front']['width']}x{config['front']['height']}", button_content['position'])
                folder_content = swapPositions(
                    folder_content, folder_content.index(button_content), position)
                if not position == folder_content.index(button_content):
                    folder_content = swapPositions(
                        folder_content, folder_content.index(button_content), position)
                if not position == folder_content.index(button_content):
                    print(f"cant swap {button_content}")

            else:
                temp_folder.append(button_content)
                folder_content.pop(folder_content.index(button_content))
    for button_content in folder_content:
        while len(temp_folder) != 0:
            if 'VOID' in button_content.keys():
                position = folder_content.index(button_content)
                folder_content.pop(position)
                folder_content.insert(position, temp_folder[0])
                temp_folder.pop(temp_folder[0])
    for button_content in folder_content:
        if 'position' in button_content.keys():
            if len(button_content['position'].strip()) == 2:
                position = convert_position(f"{config['front']['width']}x{config['front']['height']}", button_content['position'])
                if not position == folder_content.index(button_content):
                    if not 'VOID' in button_content.keys():
                        folder_content = swapPositions(
                            folder_content, folder_content.index(button_content), position)
                        print(f'swapped {folder_content.index(button_content)} to {position}')

        if 'image' in button_content.keys():
            if not button_content['image'].strip() == '':
                if ':' in button_content['image']:
                    # il faut aussi remplacer l'espace du chemin dans la config par un _
                    if not button_content['image'].startswith('http'):
                        button_content['image'] = button_content['image'].replace('/', '\\')
                        splitted = button_content['image'].split('\\')
                        try:
                            copyfile(button_content['image'],f'static/files/images/{splitted[-1]}')
                        except Exception:
                            pass
                        
    
    if folder_content.index(folder_content[-1]) > biggest_folder["buttons_count"]:
        biggest_folder["buttons_count"] = folder_content.index(
            folder_content[-1])
        biggest_folder["name"] = folder_name

    x = int(config["front"]["width"])
    while 'VOID' in folder_content[-1].keys():
        folder_content.pop(-1)
print(biggest_folder)

with open('config.json', 'w', encoding="utf-8") as json_file:
    json.dump(config, json_file, indent=4)


def color_distance(color1, color2):
    """
    Calcule la distance entre deux couleurs en utilisant la formule Euclidienne
    """
    r1, g1, b1 = [int(color1[i:i+2], 16) for i in range(1, 7, 2)]
    r2, g2, b2 = [int(color2[i:i+2], 16) for i in range(1, 7, 2)]
    return math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)


# Ouvrir le fichier colors.json
with open('colors.json', 'r', encoding="utf-8") as f:
    try:
        data = json.load(f)
    except:
        copyfile(f"static/files/colorsbcp.json", "colors.json")
        with open('colors.json', 'r', encoding="utf-8") as f:
            data = json.load(f)

# Trier les couleurs en utilisant la distance entre chaque paire de couleurs
sorted_colors = [data[0]]  # La première couleur est toujours la même
data.pop(0)

while data:
    current_color = sorted_colors[-1]['hex_code']
    nearest_color = min(data, key=lambda c: color_distance(
        current_color, c['hex_code']))
    sorted_colors.append(nearest_color)
    data.remove(nearest_color)

# Enregistrer les couleurs triées dans un nouveau fichier colors2.json
with open('colors.json', 'w', encoding="utf-8") as f:
    json.dump(sorted_colors, f, indent=4)


if not os.path.isfile("nircmd.exe"):
    url = "http://www.nirsoft.net/utils/nircmd.zip"
    urllib.request.urlretrieve(url, "nircmd.zip")

    with zipfile.ZipFile("nircmd.zip", "r") as zip_ref:
        zip_ref.extractall("")

    os.remove("nircmd.zip")
    os.remove("NirCmd.chm")
    os.remove("nircmdc.exe")


for filename in os.listdir("static/files/images"):
    if ' ' in filename and not filename.startswith("!!"):
        new_filename = filename.replace(" ", "_")
        os.rename(f"static/files/images/{filename}",
                  f"static/files/images/{new_filename}")
        print(f"renamed {filename}")


app = Flask(__name__)
sslify = SSLify(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

toaster = ToastNotifier()

# Set up the Spotify API client
try:
    spotify_redirect_uri = 'http://localhost:8888/callback'
    spotify_scope = 'user-library-modify user-library-read user-read-currently-playing user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-follow-modify user-follow-read'
    spotify_token = util.prompt_for_user_token(config['settings']['spotify-api']['USERNAME'], spotify_scope, config['settings']['spotify-api']['CLIENT_ID'], config['settings']['spotify-api']['CLIENT_SECRET'], spotify_redirect_uri)
    sp = spotipy.Spotify(auth=spotify_token)
    spotify_current_user = sp.current_user()['id']
except:
    pass


def get_current_volume():
    comtypes.CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    comtypes.CoUninitialize()
    return volume.GetMasterVolumeLevelScalar()


def set_volume(target_volume):
    comtypes.CoInitialize()
    current_volume = get_current_volume()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    while math.isclose(current_volume, target_volume, rel_tol=0.01) == False:
        if current_volume > target_volume:
            current_volume -= 0.01
        else:
            current_volume += 0.01
        volume.SetMasterVolumeLevelScalar(current_volume, None)
        time.sleep(0.01)
    comtypes.CoUninitialize()

    return current_volume


def increase_volume(delta):
    comtypes.CoInitialize()
    win32api.keybd_event(win32con.VK_VOLUME_UP, 0)
    win32api.keybd_event(win32con.VK_VOLUME_UP, 0, win32con.KEYEVENTF_KEYUP)
    if delta != '':
        target_volume = get_current_volume() + (int(delta) / 100.0)
        comtypes.CoUninitialize()
        return set_volume(target_volume)
    else:
        comtypes.CoUninitialize()
        return get_current_volume()


def decrease_volume(delta):
    comtypes.CoInitialize()
    win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0)
    win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0, win32con.KEYEVENTF_KEYUP)
    if delta != '':
        target_volume = get_current_volume() - (int(delta) / 100.0)
        comtypes.CoUninitialize()
        return set_volume(target_volume)
    else:
        comtypes.CoUninitialize()
        return get_current_volume()


def set_current_volume():
    comtypes.CoInitialize()
    current_volume = get_current_volume()
    print(current_volume)
    comtypes.CoUninitialize()
    return current_volume


def find_color(hex_code, colors):
    try:
        # Recherche de la couleur exacte dans le fichier JSON
        for color in colors:
            if color['hex_code'] == hex_code:
                return color['name']

        # Si la couleur exacte n'est pas trouvée, recherche de la couleur la plus proche
        closest_color = None
        min_distance = float('inf')
        for color in colors:
            distance = get_color_distance(hex_code, color['hex_code'])
            if distance < min_distance:
                min_distance = distance
                closest_color = color

        return closest_color['name']
    except ValueError:
        return "Can not find color"


def get_color_distance(hex_code1, hex_code2):
    rgb1 = webcolors.hex_to_rgb(hex_code1)
    rgb2 = webcolors.hex_to_rgb(hex_code2)
    return sum([(a - b) ** 2 for a, b in zip(rgb1, rgb2)])


def translate(word, target_language):
    # Séparer les mots par des espaces avant chaque majuscule
    word = ''.join([' '+i if i.isupper() else i for i in word]).strip()

    if word == "Discord" or target_language.upper() == "EN":
        result = word
    else:
        result = GoogleTranslator(
            source='en', target=target_language).translate(word)

    return result

def bring_window_to_front(window_title):
    # Trouver la fenêtre
    hwnd = win32gui.FindWindow(None, str(window_title))
    if hwnd == 0:
        print("Fenêtre non trouvée")
        return
    # Mettre la fenêtre au premier plan
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)

def get_focused_window():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == 0:
        print("Aucune fenêtre n'a le focus")
        return None
    else:
        window_title = win32gui.GetWindowText(hwnd)
        print(f"Fenêtre focus : {window_title}")
        return window_title

def close_window(window_title):
    # Trouver la fenêtre
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd == 0:
        print("Fenêtre non trouvée")
        return
    # Fermer la fenêtre
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

# Fonction pour trouver une fenêtre avec un titre spécifique
def find_window_with_name(hwnd, name):
    window_name = win32gui.GetWindowText(hwnd)
    if name.lower().replace('.exe','') in window_name.lower().replace('.exe',''):
        return hwnd
    return None

# Fonction pour obtenir la fenêtre correspondant à un nom donné
def get_window_by_name(name):
    hwnd = win32gui.FindWindow(None, None)
    window_hwnd = None
    while hwnd != 0:
        if find_window_with_name(hwnd, name) is not None:
            window_hwnd = hwnd
            break
        hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
    return window_hwnd

p = pyaudio.PyAudio()
def set_microphone_by_name(name):
    # Rechercher le périphérique d'enregistrement avec le nom spécifié
    command = f"PowerShell -Command \"Get-WmiObject Win32_SoundDevice | Where-Object {{ $_.Name -like '*{name}*' -and $_.ConfigManagerErrorCode -eq 0 }} | Select-Object -First 1 | Invoke-CimMethod -MethodName SetDefault\""
    subprocess.run(command, shell=True)

def set_speakers_by_name(speakers_name):
    device_count = p.get_device_count()

    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info["name"].lower().find(speakers_name.lower()) != -1:
            # Sélectionne le périphérique audio trouvé
            win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_APPCOMMAND, 0, win32api.LPARAM(0x30292))
            win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_APPCOMMAND, 0, win32api.LPARAM(0x30290 + i))
            break



# try: os.remove("static/style.css")
# except OSError: pass
# try:
#    shutil.copyfile(f"themes/{config['front']['theme']}", "static/style.css")
# except:
#    shutil.copy(f"themes/{config['front']['theme']}", "static/style.css")


# p = subprocess.Popen([sys.executable, 'mic2.py'],
#                    stdout=subprocess.PIPE,
#                    stderr=subprocess.STDOUT)

# p2 = subprocess.Popen([sys.executable, 'playsound.py'],
#                      stdin=subprocess.PIPE,
#                      stdout=subprocess.PIPE,
#                      stderr=subprocess.STDOUT)
# stdout_data, stderr_data = p2.communicate(input=bytes(f"aaaaaaaaaaaaaaa", 'utf-8'))

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.event
def send(data):
    socketio.emit('json_data', data)

@app.route('/getconfig', methods=['POST'])
def getconfig():
     with open('config.json', encoding= "utf-8") as f:
        config = json.load(f)
        return jsonify(config)
    
@app.route('/usage', methods=['POST'])
def usage():
    # CPU
    cpu_percent = psutil.cpu_percent(4)
    computer_info = {'cpu': {'usage_percent': cpu_percent}}

    # Mémoire
    memory = psutil.virtual_memory()
    computer_info['memory'] = {
        'total_gb': round(memory.total / 1024**3, 2),
        'used_gb': round(memory.total / 1024**3 - memory.available / 1024**3, 2),
        'available_gb': round(memory.available / 1024**3, 2),
        'usage_percent': psutil.virtual_memory()[2]
    }

    # Disque dur
    disks = psutil.disk_partitions()
    computer_info['disks'] = {}
    for disk in disks:
        try:
            disk_name = disk.device.replace("\\", "").replace(":", "")
            disk_usage = psutil.disk_usage(disk.device)
            computer_info['disks'][disk_name] = {
                'total_gb': round(disk_usage.total / 1024**3, 2),
                'used_gb': round(disk_usage.used / 1024**3, 2),
                'free_gb': round(disk_usage.free / 1024**3, 2),
                'usage_percent': disk_usage.percent
            }
        except Exception as e:
            print('error: ', e)
            
    # Réseau
    network_io_counters = psutil.net_io_counters()
    computer_info['network'] = {
        'bytes_sent': network_io_counters.bytes_sent,
        'bytes_recv': network_io_counters.bytes_recv
    }

    # Carte graphique
    gpus = GPUtil.getGPUs()
    computer_info['gpus'] = {}
    for count, gpu in enumerate(gpus):
        computer_info['gpus'][f'GPU{count + 1}'] = {
            'name': gpu.name,
            'memory_used_mb': gpu.memoryUsed,
            'memory_total_mb': gpu.memoryTotal,
            'utilization_percent': int(gpu.load * 100),
        }

    return jsonify(computer_info)


@app.route("/")
def home():
    with open('config.json', encoding="utf-8") as f:
        config = json.load(f)

    themes = [
        file_name
        for file_name in os.listdir("static/themes/")
        if file_name.endswith(".css")
    ]
    return render_template("index.jinja",
                           config=config, themes=themes,
                           biggest_folder=biggest_folder["name"],
                           int=int, str=str, dict=dict, json=json, type=type, eval=eval, open=open
                           )


@app.route("/config")
@app.route("/settings")
def update_config():
    with open('config.json', encoding="utf-8") as f:
        config_json = json.load(f)
    return render_template("config.html", config=config_json)


@app.route("/scratch")
def scratch():
    return render_template("scratch.html")


def merge_dicts(d1, d2):
    """
    Fusionne deux dictionnaires en prenant en compte les sous-dictionnaires.
    Les clés du d2 écrasent les clés correspondantes dans le d1, sauf si elles font partie d'un sous-dictionnaire.
    """
    for key in d2:
        if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
            # Récursivement, on fusionne les sous-dictionnaires avec la méthode merge_dict.
            merge_dicts(d1[key], d2[key])
        else:
            # Si la clé existe dans d1 et qu'elle n'est pas un sous-dictionnaire, on la remplace par celle de d2.
            d1[key] = d2[key]
    return d1

@app.route('/save_config', methods=['POST'])
def save_config():
    with open('config.json', encoding="utf-8") as f:
        config = json.load(f) 
    
    # Récupère les données du formulaire
    new_config = request.get_json()
    print(new_config)
    
    config = merge_dicts(config, new_config)
    
    with open('config.json', 'w', encoding="utf-8") as json_file:
        json.dump(config, json_file, indent=4)
        
    return jsonify({'success': True})



@app.route('/send-data', methods=['POST'])
def send_data():

    try:
        os.remove('temp/mic-temp')
    except:
        pass

    data = request.get_json()
    # Do something with the name and age values received from the JavaScript client
    response_data = {"status": "success"}
    # print(response_data) # {'status': 'success'}
    # print(jsonify(response_data)) # <Response 21 bytes [200 OK]>
    print2(data)

    message = data["message"]
    # Print the received message
    if not message.replace(" ", "").replace("\n", "").replace("\r", "") == "":
        print2(message)
    if message.startswith("/debug-send"):
        data = {'message': 'Hello, world!'}
        data = json.loads(message.replace("'",'"').replace("/debug-send",""))
        send(data)
    
    elif message.startswith("/exit"):
        sys.exit("/exit received")


    elif message.startswith('/playsound '):
        if "v=" in message:
            sound_file = re.search(r'/playsound (.+?) v=', message).group(1)
            percentage = message.replace(sound_file, '').replace(
                '/playsound ', '').replace(' v=', '').replace('', '')
            sound_volume = float(percentage) / 100

        else:
            sound_file = message.replace('/playsound ', '')
            sound_volume = float(100) / 100  # max volume (default)

        if not ":" in sound_file:
            # si il est stoque directement dans static/files/sounds et pas dans C:\example
            sound_file = f"static/files/sounds/{sound_file}"

        print2("ok0")

        print2("ok1")
        if config['settings']["ear-soundboard"].lower() == "true":
            print2("ok2")
            if "v=" in message:
                sound_file = re.search(
                    r'/playsound (.+?) v=', message).group(1)
                percentage = message.replace(sound_file, '').replace(
                    '/playsound ', '').replace(' v=', '').replace('', '')
                sound_volume = float(percentage) / 100
            else:
                sound_file = message.replace('/playsound ', '')
                sound_volume = float(100) / 100  # max volume (default)

            if not ":" in sound_file:
                sound_file = "static/files/sounds/" + sound_file

            if config["settings"]["mp3_method"] == "vlc":

                try:
                    player = vlc.MediaPlayer(sound_file)
                    player.audio_set_volume(int(percentage))
                    player.play()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(
                        exc_tb.tb_frame.f_code.co_filename)[1]
                    print(
                        f"{exc_type} | {e} | {fname} | python line: {exc_tb.tb_lineno}")
                    print("ERROR:      ", e)
                    print("ERROR LINE: ", exc_tb.tb_lineno)
                    print2("Error while loading MP3 file named " + sound_file)
            else:
                try:
                    pygame.mixer.music.load(sound_file)
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_volume(sound_volume)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(
                        exc_tb.tb_frame.f_code.co_filename)[1]
                    print(
                        f"{exc_type} | {e} | {fname} | python line: {exc_tb.tb_lineno}")
                    print("ERROR:      ", e)
                    print("ERROR LINE: ", exc_tb.tb_lineno)
                    print2("Error while loading MP3 file named " + sound_file)

        asyncio.run(playsound(sound_file, sound_volume))

    elif message.startswith('/playlocalsound '):

        if "v=" in message:
            sound_file = re.search(r'/playsound (.+?) v=', message).group(1)
            percentage = message.replace(sound_file, '').replace(
                '/playsound ', '').replace(' v=', '').replace('', '')
            sound_volume = float(percentage) / 100
        else:
            sound_file = message.replace('/playsound ', '')
            sound_volume = float(100) / 100  # max volume (default)

        if config["settings"]["mp3_method"] == "vlc":

            try:
                if ":" in sound_file:
                    # si le son a un emplacement custom (ex: C:\son.mp3)
                    player = vlc.MediaPlayer(sound_file)
                else:
                    # si il est stoque directement dans static/files/sounds
                    player = vlc.MediaPlayer(
                        "static/files/sounds/" + sound_file)
                player.audio_set_volume(int(percentage))
                player.play()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(
                    f"{exc_type} | {e} | {fname} | python line: {exc_tb.tb_lineno}")
                print("ERROR:      ", e)
                print("ERROR LINE: ", exc_tb.tb_lineno)
                print2("Error while loading MP3 file named " + sound_file)
        else:
            try:
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(sound_volume)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(
                    f"{exc_type} | {e} | {fname} | python line: {exc_tb.tb_lineno}")
                print("ERROR:      ", e)
                print("ERROR LINE: ", exc_tb.tb_lineno)
                print2("Error while loading MP3 file named " + sound_file)

    elif message.startswith('/exec'):
        exec(message.replace('/exec', '').strip())

    elif message.startswith('/batch'):
        os.system(message.replace('/batch', '', 1).strip())

    elif message.startswith(('/openfile', '/start')):
        path = message.replace(
            '/openfile', '', 1).replace('/start', '', 1).strip()
        os.system(f'start {path}')

    elif message.startswith('/locksession'):
        os.system('Rundll32.exe user32.dll,LockWorkStation')

    elif message.startswith('/screensaversettings'):
        os.system('rundll32.exe desk.cpl,InstallScreenSaver toasters.scr')

    elif message.startswith('/screensaver') and not message.startswith('/screensaversettings'):
        if message.endswith(('on', '/screensaver', 'start')):
            os.system('%windir%\system32\scrnsave.scr /s')

        elif message.endswith(('hard', 'full', 'black')):
            os.system('nircmd.exe monitor off')

        elif message.endswith(('off', 'false')):
            keyboard.press('CTRL')

    elif message.startswith('/key'):
        key = message.replace('/key', '', 1).strip()
        keyboard.press(key)

    elif message.startswith('/restartexplorer'):
        os.system('taskkill /f /im explorer.exe')
        os.system('start explorer.exe')

    elif message.startswith(('/taskill', '/forceclose')):
        window_name = message.replace('/taskill', '').replace('/forceclose', '')
        hwnd = get_window_by_name(window_name)
        if hwnd:
            print(f"Fenêtre '{window_name}' trouvée avec handle : {hwnd}")
        else:
            print(f"Fenêtre '{window_name}' non trouvée")
        try:
            close_window(hwnd)
        except:
            if not '.' in window_name:
                window_name += '.exe'
            os.system(f'taskkill /f /im {window_name}')

    elif message.startswith('/restart'):
        exe = message.replace('/restart', '')
        if not '.' in exe:
            exe += '.exe'
        os.system(f'taskkill /f /im {exe}')
        os.system(f'start {exe}')

    elif message.startswith('/clearclipboard'):
        os.system('cmd /c "echo off | clip"')

    elif message.startswith('/write '):
        keyboard.write(message.replace('/write ', ''))

    elif message.startswith('/writeandsend '):
        keyboard.write(message.replace('/writeandsend ', ''))
        keyboard.press('ENTER')

    elif message.startswith('/volume +'):
        delta = message.replace('/volume +', '')
        increase_volume(delta)
    elif message.startswith('/volume -'):
        delta = message.replace('/volume -', '')
        decrease_volume(delta)
    elif message.startswith('/volume set'):
        target_volume = int(message.replace('/volume set ', '')) / 100.0
        set_volume(target_volume)

    elif message.startswith(('/appvolume +', '/appvolume -', '/appvolume set')):
        comtypes.CoInitialize()
        command = message.replace('/appvolume ', '').replace('set ', 'set').split()
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            if session.Process and session.Process.name().lower() == command[1].lower():
                print("Current volume: %s" % volume.GetMasterVolume())
                old_volume = volume.GetMasterVolume()
                old_volume_percent = round(old_volume * 100)

                if command[0].startswith('set'):
                    target_volume = int(command[0].replace('set', ''))
                    if target_volume > 100:
                        target_volume = 100
                    if target_volume < 0:
                        target_volume = 0
                elif command[0].startswith('+'):
                    if command[0].replace('+', '') == '':
                        target_volume = old_volume_percent + 1
                    else:
                        target_volume = old_volume_percent + \
                            int(command[0].replace('+', ''))
                elif command[0].startswith('-'):
                    if command[0].replace('-', '') == '':
                        target_volume = old_volume_percent - 1
                    else:
                        target_volume = old_volume_percent - \
                            int(command[0].replace('-', ''))
                target_volume_float = target_volume / 100.0

                volume.SetMasterVolume(target_volume_float, None)
                print("New volume: %s" % volume.GetMasterVolume())

        comtypes.CoUninitialize()

    elif message.startswith('/soundcontrol mute'):
        keyboard.press('volumemute')
    elif message.startswith('/soundcontrol playpause'):
        keyboard.press('playpause')
    elif message.startswith('/soundcontrol previous'):
        keyboard.press('prevtrack')
    elif message.startswith('/soundcontrol next'):
        keyboard.press('nexttrack')

    elif message.startswith('/spotify likealbum'):
        sp = spotipy.Spotify(auth=spotify_token)
        # Get information about the user's currently playing track
        track_info = sp.current_playback()

        # If a track is currently playing, like it
        if track_info is not None:
            album_id = track_info['item']['album']['id']

            is_liked = sp.current_user_saved_albums_contains(albums=[album_id])[
                0]
            # Add or remove like based on current state
            if is_liked:
                sp.current_user_saved_albums_delete(albums=[album_id])
                print(
                    f"Removed album {track_info['item']['album']['name']} by {track_info['item']['album']['artists'][0]['name']}")
            else:
                sp.current_user_saved_albums_add(albums=[album_id])
                print(
                    f"Liked album {track_info['item']['album']['name']} by {track_info['item']['album']['artists'][0]['name']}")
        else:
            print("No album currently playing.")

    elif message.startswith('/spotify likesong'):
        sp = spotipy.Spotify(auth=spotify_token)
        # Get information about the user's currently playing track
        track_info = sp.current_playback()

        # If a track is currently playing, like it
        if track_info is not None:
            track_id = track_info['item']['id']
            print(track_info)

            is_liked = sp.current_user_saved_tracks_contains(tracks=[track_id])[
                0]
            # Add or remove like based on current state
            if is_liked:
                sp.current_user_saved_tracks_delete(tracks=[track_id])
                print(
                    f"Removed track {track_info['item']['name']} by {track_info['item']['artists'][0]['name']}")
            else:
                sp.current_user_saved_tracks_add(tracks=[track_id])
                print(
                    f"Liked track {track_info['item']['name']} by {track_info['item']['artists'][0]['name']}")
        else:
            print("No track currently playing.")

    elif message.startswith(('/spotify add_to_playlist', '/spotify remove_from_playlist', '/spotify add_or_remove')):
        playlist_name = message.replace('/spotify add_to_playlist', '').replace(
            '/spotify remove_from_playlist', '').replace('/spotify add_or_remove', '').strip()
        sp = spotipy.Spotify(auth=spotify_token)
        playlists = sp.current_user_playlists()
        playlist_id = None

        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                playlist_id = playlist['id']
                break

        if playlist_id is None:
            print2(f"Playlist '{playlist_name}' non trouvée")
        else:
            playback = sp.current_playback()
            track_id = playback['item']['id']
            track_uri = playback['item']['uri']
            if 'add_or_remove' in message:
                playlist_items = sp.playlist_items(
                    playlist_id, fields='items(track(uri))')
                track_uris = [item['track']['uri']
                              for item in playlist_items['items']]

                if track_uri in track_uris:
                    sp.playlist_remove_all_occurrences_of_items(
                        playlist_id, [track_uri])
                    print("La piste a été retirée de la playlist.")
                else:
                    sp.playlist_add_items(playlist_id, [track_id])
                    print("La piste a été ajoutée à la playlist.")
            elif 'add_to_playlist' in message:
                sp.playlist_add_items(playlist_id, [track_id])
            elif 'remove_from_playlist' in message:
                sp.playlist_remove_all_occurrences_of_items(
                    playlist_id, [track_uri])

    elif message.startswith(('/spotify follow_artist', '/spotify unfollow_artist', '/spotify follow_or_unfollow_artist')):
        artist = message.replace('/spotify follow_artist', '').replace(
            '/spotify unfollow_artist', '').replace('/spotify follow_or_unfollow_artist', '').strip()
        sp = spotipy.Spotify(auth=spotify_token)
        playback = sp.current_playback()
        artist_id = playback['item']['artists'][0]['id']
        artist_name = playback['item']['artists'][0]['name']
        if 'follow_or_unfollow_artist' in message:
            results = sp.search(q=artist_name, type="artist")
            items = results["artists"]["items"]
            if len(items) > 0:
                artist_id = items[0]["id"]
            else:
                print(
                    f"Impossible de trouver l'artiste '{artist_id}' sur Spotify.")
                exit()

            # Vérifier si l'utilisateur est abonné à l'artiste correspondant
            response = sp.current_user_following_artists(ids=[artist_id])
            is_following = response[0]

            if is_following:
                print(f"L'utilisateur est abonné à l'artiste '{artist_id}'.")
                sp.user_unfollow_artists([artist_id])
                print("L'artiste a bien été retiré de la liste d'abonnements.")
            else:
                print(
                    f"L'utilisateur n'est pas abonné à l'artiste '{artist_id}'.")
                sp.user_follow_artists([artist_id])
                print("L'artiste a bien été ajouté à la liste d'abonnements.")

        elif 'unfollow_artist' in message:
            sp.user_unfollow_artists([artist_id])
            print("L'artiste a bien été retiré de la liste d'abonnements.")
        elif 'follow_artist' in message:
            sp.user_follow_artists([artist_id])
            print("L'artiste a bien été ajouté à la liste d'abonnements.")

    elif message.startswith(('/spotify volume +', '/spotify volume -', '/spotify volume set')):
        sp = spotipy.Spotify(auth=spotify_token)
        # Get the current playback information
        playback_info = sp.current_playback()

        # Check if there is an active device
        if playback_info and playback_info['is_playing'] and playback_info['device']:
            device_id = playback_info['device']['id']
        else:
            print("No active device found.")
            exit()

        # Get the current volume
        current_volume = playback_info['device']['volume_percent']
        print(f"Current volume: {current_volume}")

        if '-' in message:
            try:
                target_volume = current_volume - \
                    int(message.replace('/spotify volume -', ''))
            except:
                target_volume = current_volume - 10
        elif '+' in message:
            try:
                target_volume = current_volume + \
                    int(message.replace('/spotify volume +', ''))
            except:
                target_volume = current_volume + 10
        elif 'set' in message:
            try:
                target_volume = int(message.replace('/spotify volume set', ''))
            except:
                target_volume = current_volume
                print2('Error, unable to apply volume')
        if isinstance(target_volume, int):
            if target_volume > 100:
                target_volume = 100
            if target_volume < 0:
                target_volume = 0
            target_volume = int(target_volume)
            try:
                sp.volume(target_volume, device_id=device_id)
            except:
                print2('Error, unable to apply volume because Spotify Prenium is required')

            # Get the updated volume
            playback_info = sp.current_playback()
            current_volume = playback_info['device']['volume_percent']
            print(f"Updated volume: {current_volume}")
        else:
            print("Volume must be an integer")

    elif message.startswith('/speechrecognition'):
        keyboard.hotkey('win', 'h')

    # /colorpicker lang:en type:text|name;text-original|name-original;hex;rgb;hsl copy:text;hex;rgb;hsl copytype:raw|list showtype:raw|list remove_hex_sharp:false
    elif message.startswith('/colorpicker'):

        x, y = keyboard.position()

        # Obtient la capture d'écran de chaque moniteur et compare la position du curseur pour déterminer l'écran
        for i, monitor in enumerate(mss.mss().monitors):
            if monitor["left"] <= x < monitor["left"] + monitor["width"] and \
                    monitor["top"] <= y < monitor["top"] + monitor["height"]:
                monitor_index = i
                break

        # Capturer la capture d'écran de l'écran spécifique
        with mss.mss() as sct:
            monitor = sct.monitors[monitor_index]
            img = sct.grab(monitor)
            screenshot = np.array(Image.frombytes(
                'RGB', img.size, img.bgra, 'raw', 'BGRX'))

        # Obtient la couleur du pixel sous le curseur de la souris
        color = screenshot[y - monitor["top"], x - monitor["left"]]

        # Convertit la couleur en format HEX
        hex_color = '#{:02x}{:02x}{:02x}'.format(*color)

        # Convertit la couleur en format RGB
        rgb_color = 'rgb({},{},{})'.format(*color)

        # Convertit la couleur en format HSL
        r, g, b = [x / 255.0 for x in color]
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        delta = cmax - cmin

        if delta == 0:
            hue = 0
        elif cmax == r:
            hue = ((g - b) / delta) % 6
        elif cmax == g:
            hue = (b - r) / delta + 2
        else:
            hue = (r - g) / delta + 4

        hue = round(hue * 60)
        if hue < 0:
            hue += 360

        lightness = (cmax + cmin) / 2
        saturation = 0 if delta == 0 else delta / (1 - abs(2 * lightness - 1))

        hsl_color = 'hsl({}, {:.2f}%, {:.2f}%)'.format(
            hue, saturation * 100, lightness * 100)

        target_language = getarg(message, 'lang')
        selectedtypes = getarg(message, 'type')
        typestocopy = getarg(message, 'copy')
        copytype = getarg(message, 'copytype')
        showtype = getarg(message, 'showtype')
        try:
            remove_hex_sharp = getarg(message, 'remove_hex_sharp').capitalize()
        except AttributeError:
            remove_hex_sharp = None
        print('------------------------------------------')
        print(target_language)
        print(selectedtypes)
        print(typestocopy)
        print(copytype)
        print(showtype)
        print(remove_hex_sharp)
        print('------------------------------------------')

        with open('colors.json', 'r', encoding="utf-8") as f:
            colorsjson = json.load(f)
        if target_language is None:
            named_original = find_color(hex_color, colorsjson)
            named_color = named_original
        else:
            named_original = find_color(hex_color, colorsjson)
            named_color = translate(named_original, target_language)

        types_found = {
            "NAME":named_color,
            "TEXT":named_color,
            "NAME-ORIGINAL":named_original,
            "TEXT-ORIGINAL":named_original,
            "HEX":hex_color,
            "RGB":rgb_color,
            "HSL":hsl_color
        }
        
        
        types_found_final = {}
        if selectedtypes:
            for type in selectedtypes.split(';'):
                for type_found, value in types_found.items():
                    if type.upper() in type_found:
                        if 'HEX' in type.upper() and remove_hex_sharp == 'True':
                                types_found_final[type.upper()] = value.replace('#','')
                        else:
                            types_found_final[type.upper()] = value
            print(types_found_final)
        else:
            for type_found, value in types_found.items():
                if not any(elem in type_found for elem in ['TEXT', 'ORIGINAL']):
                    types_found_final[type_found] = value
            print(types_found_final)

        # copy:text;hex;rgb;hsl copytype:raw|list
        typestocopy_final = {}
        if typestocopy:
            for type in typestocopy.split(';'):
                for type_found, value in types_found.items():
                    if type.upper() in type_found:
                        if 'HEX' in type.upper() and remove_hex_sharp == 'True':
                            typestocopy_final[type.upper()] = value.replace('#','')
                        else:
                            typestocopy_final[type.upper()] = value
            if copytype.lower() == 'list':
                if len(typestocopy.split(';')) == 1:
                    pyperclip.copy(str(typestocopy_final)[:-2][2:].replace("'",''))
                else:
                    pyperclip.copy(str(typestocopy_final).replace("', ",',\n')[:-2][2:].replace("'",''))
            else:
                if len(typestocopy.split(';')) == 1:
                    pyperclip.copy(list(typestocopy_final.values())[0])
                else:
                    pyperclip.copy(', '.join(typestocopy_final.values()))
        
        
        title = "WebDeck Color Picker"
        icon = "static\\files\\icon.ico"
        duration = 5
        message = ''
        if showtype and showtype.lower() != 'list':
            if typestocopy and len(typestocopy.split(';')) == 1:
                message = list(types_found_final.values())[0]
            else:
                message = ', '.join(types_found_final.values())
        else:
            if typestocopy and len(typestocopy.split(';')) == 1:
                message = str(types_found_final)[:-2][2:].replace("'",'')
            else:
                message = str(types_found_final).replace("', ",',\n')[:-2][2:].replace("'",'')

        toaster.show_toast(title, message, icon_path=icon, duration=duration, threaded=True)

    elif message.startswith('/superAltF4'):
        hwnd = get_focused_window()
        if hwnd:
            close_window(hwnd)

    # A FIX
    elif message.startswith('/firstplan'):
        window_name = message.replace('/firstplan','').strip()
        
        hwnd = get_window_by_name(window_name)
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
            keyboard2.press('ENTER')
            print(f"Fenêtre '{window_name}' mise au premier plan")
        else:
            print(f"Fenêtre '{window_name}' non trouvée")

    elif message.startswith('/setmicrophone'):
        set_microphone_by_name(message.replace('/setmicrophone','').strip())
        # PAS FINI
    elif message.startswith('/setoutputdevice'):
        set_speakers_by_name(message.replace('/setoutputdevice','').strip())
        # PAS FINI

    elif message.startswith('/copy'):
        if message.strip() == 'copy':
            keyboard.hotkey('ctrl', 'c')
        else:
            msg = message.replace('/copy ','',1)
            if msg.startswith('/copy'):
                msg = message.replace('/copy','',1)
            pyperclip.copy(msg)
            
    elif message.startswith('/paste'):
        if message.strip() == '/paste':
            keyboard.hotkey('ctrl', 'v')
        else:
            msg = message.replace('/paste ','',1)
            if msg.startswith('/paste'):
                msg = message.replace('/paste','',1)
            pyperclip.copy(msg)
            keyboard.hotkey('ctrl', 'v')
            
    elif message.startswith('/clipboard'):
        keyboard.hotkey('win', 'v')


    return jsonify(response_data)


async def playsound(sound_file, sound_volume):
    def get_devices(capture_devices: bool = False) -> tuple[str, ...]:
        init_by_me = not pygame.mixer.get_init()
        if init_by_me:
            pygame.mixer.init()
        devices = tuple(sdl2_audio.get_audio_device_names(capture_devices))
        if init_by_me:
            pygame.mixer.quit()
        for d in devices:
            if "virtual cable" in d.lower():
                device = d
        return device

    def play(file_path: str, device=None):
        if device is None:
            device = get_devices()
        print("Play: {}\r\nDevice: {}".format(file_path, device))
        pygame.mixer.init(devicename=device)
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(sound_volume)
        try:
            while True:
                sleep(0.1)
        except KeyboardInterrupt:
            pass
        pygame.mixer.quit()
    play(sound_file)

try:
    os.remove('temp/mic-temp')
except:
    pass

print('main_server started')
socketio.run(app, host=config['url']['ip'], port=config['url']['port'], debug=True)