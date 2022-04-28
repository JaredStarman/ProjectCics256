import keyboard
import pyaudio
import wave
import time
import numpy as np
from os.path import exists
from pydub import AudioSegment
from pydub.playback import play

# represent key presses to 
keys = [ ['q','a'], ['w','s'], ['e','d'], ['r','f'], ['t','g'] ]

pitch = [0]
uploaded_recording_status = [0]
current_file_recording = [-1]
flag = []
flag_previous = []

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024*2
device_index = 2
audio_input = pyaudio.PyAudio()
stream_input = audio_input.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

Recordframes = []
WAVE_OUTPUT_FILENAME = ''


for i in range(len(keys)):
    flag.append(False)
    flag_previous.append(False)

def start_record(num):
    val = True
    for i in range(len(flag)):
        val = val and not flag[i]
    if(val):
        flag[num] = True
        current_file_recording[0] = num


def end_record(num):
    val = True
    for i in range(len(flag)):
        if(i == num):
            val = val and flag[i]
        else:
            val = val and not flag[i]
    if(val):
        flag[num] = False
        uploaded_recording_status[0] = 2

def adjust_pitch(val):
    if(pitch[0] + val < 0.5 and pitch[0] + val > -0.5):
        pitch[0] += val
    print(pitch[0])

def reset_pitch():
    pitch[0] = 0

def playback_recording(num):
    file_name = "recording_"+str(num)+".wav"
    file_exists = exists(file_name)
    if(file_exists):
        print("Playing: \'"+file_name+"\'")
        sound = AudioSegment.from_wav(file_name) + 10
        play(sound)
        print("Finished Playing: \'"+file_name+"\'")
    else:
        print("File: (\'"+file_name+"\') does not exist")


for i in range(len(keys)):
    keyboard.add_hotkey(keys[i][0], start_record, args=[i])
    keyboard.add_hotkey('shift+'+keys[i][0], playback_recording, args=[i])
    keyboard.add_hotkey(keys[i][1], end_record, args=[i])
    keyboard.add_hotkey('up', adjust_pitch, args=[0.01])
    keyboard.add_hotkey('down', adjust_pitch, args=[-0.01])
    keyboard.add_hotkey('space', reset_pitch)


while True:
    # functionality to run 
    num = current_file_recording[0]
    if(num != -1):
        if(uploaded_recording_status[0] == 0):
            WAVE_OUTPUT_FILENAME = "recording_"+str(num)+".wav"
            print("Now recording to file: \'"+WAVE_OUTPUT_FILENAME+"\'")
            print("press \'"+str(keys[num][1])+"\' to stop recording")
            Recordframes = []
            uploaded_recording_status[0] = 1

        data = stream_input.read(CHUNK)
        Recordframes.append(data)

        if(uploaded_recording_status[0] == 2):
            waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(audio_input.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(Recordframes))
            waveFile.close()
            print("Finished recording to file: \'"+WAVE_OUTPUT_FILENAME+"\'")
            uploaded_recording_status[0] = 0
            current_file_recording[0] = -1