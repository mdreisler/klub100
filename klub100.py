from os import path
from pydub import AudioSegment
import numpy as np
import wave
import matplotlib.pyplot as plt
import librosa
from IPython.display import Audio, display
import librosa.display
import ruptures as rpt
import os
from pydub import AudioSegment, effects

def read_normalize(filepath):
    ## takes path to file either mp3 or wav and converts to a normalized wav
    if filepath.endswith(".m4a"):
        sound = AudioSegment.from_file(filepath)
        filepath = filepath.replace(".m4a", ".wav")
        sound.export(filepath, format="wav")
        sound = AudioSegment.from_wav(filepath)
        normsound = effects.normalize(sound)
    if filepath.endswith(".mp3"):
        sound = AudioSegment.from_mp3(filepath)
        filepath = filepath.replace(".mp3", ".wav")
        sound.export(filepath, format="wav")
        sound = AudioSegment.from_wav(filepath)
        normsound = effects.normalize(sound)
    elif filepath.endswith(".wav"):
        print(filepath)
        sound = AudioSegment.from_wav(filepath)
        normsound = effects.normalize(sound)
    else:
        return AudioSegment.empty()
    return normsound


def stitch(df, exportdir, speakfolderpath):
    initsound = AudioSegment.empty()
    for i,file in enumerate(df["Songs"]):
        file = file + ".mp3"
        print(file)
        f = os.path.join(exportdir, file)
        fspeak = os.path.join(speakfolderpath, df["Associated speak"][i])
        normspeak = read_normalize(fspeak)
        speakduration = normspeak.duration_seconds
        songduration = df["Duration"][i] - speakduration
        delay = df["Delayed start"][i]
        normsound = read_normalize(f)[delay * 1000 : songduration * 1000]
        initsound = initsound + normsound + normspeak
    initsound.export(os.path.join(os.getcwd(), "klub100mix.mp3"),format = "mp3")
    return initsound
