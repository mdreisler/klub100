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


duration = 100  
signal, sampling_rate = librosa.load(dst, duration=duration)

display(Audio(data=signal, rate=sampling_rate))

def gentempspecgram(signal, sampling_rate, type, plot=False):
    hop_length_tempo = 256
    oenv = librosa.onset.onset_strength(
        y=signal, sr=sampling_rate, hop_length=hop_length_tempo
    )
    if type == "temp":
        tempogram = librosa.feature.tempogram(
            onset_envelope=oenv, sr=sampling_rate, hop_length=hop_length_tempo,
        )
        if plot:
            fig, ax = plt.subplots()
            _ = librosa.display.specshow(
                tempogram,
                ax=ax,
                hop_length=hop_length_tempo,
                sr=sampling_rate,
                x_axis="s",
                y_axis="tempo",
            )
        return tempogram
    if type == "spec":
        S = librosa.feature.melspectrogram(
            y=signal, sr=sampling_rate, n_mels=128, fmax=sampling_rate / 2
        )
        S_dB = librosa.power_to_db(S, ref=np.max)
        if plot:
            fig, ax = plt.subplots()
            img = librosa.display.specshow(
                S_dB,
                x_axis="time",
                y_axis="mel",
                sr=sampling_rate,
                fmax=sampling_rate / 2,
                ax=ax,
            )
            fig.colorbar(img, ax=ax, format="%+2.0f dB")
            ax.set(title="Mel-frequency spectrogram")
        return S_dB


def detect(tempspecgram, plot=False):
    algo = rpt.KernelCPD(kernel="linear").fit(tempspecgram.T)

    n_bkps_max = 20
    _ = algo.predict(n_bkps_max)

    array_of_n_bkps = np.arange(1, n_bkps_max + 1)

    def get_sum_of_cost(algo, n_bkps) -> float:
        """Return the sum of costs for the change points `bkps`"""
        bkps = algo.predict(n_bkps=n_bkps)
        return algo.cost.sum_of_costs(bkps)

    if plot:
        fig, ax = plt.subplots()
        ax.plot(
            array_of_n_bkps,
            [get_sum_of_cost(algo=algo, n_bkps=n_bkps) for n_bkps in array_of_n_bkps],
            "-*",
            alpha=0.5,
        )
        ax.set_xticks(array_of_n_bkps)
        ax.set_xlabel("Number of change points")
        ax.set_title("Sum of costs")
        ax.grid(axis="x")
        ax.set_xlim(0, n_bkps_max + 1)
        n_bkps = 7

        _ = ax.scatter([5], [get_sum_of_cost(algo=algo, n_bkps=5)], color="r", s=100)
    return algo


def segmentate(n_bkps, tempspecgram, algo, sampling_rate, type, plot=False):
    bkps = algo.predict(n_bkps=n_bkps)
    bkps_times = librosa.frames_to_time(
        bkps, sr=sampling_rate, hop_length=hop_length_tempo
    )
    if type == "temp":
        y_axis = "tempo"
    if type == "spec":
        y_axis = "mel"
    fig, ax = plt.subplots()
    _ = librosa.display.specshow(
        tempspecgram,
        ax=ax,
        x_axis="s",
        y_axis=y_axis,
        sr=sampling_rate,
    )
    for b in bkps_times[:-1]:
        ax.axvline(b, ls="--", color="white", lw=4)
    ax.set(xlim=(0, 100))
    return


display(Audio(data=signal, rate=sampling_rate))

signal, sampling_rate = librosa.load(dst, duration=100)
type_ = "temp"
tempogramtemp = gentempspecgram(signal, sampling_rate, type=type_, plot=True)
algo_ = detect(tempogramtemp, plot=True)
segmentate(13, tempogramtemp, algo_, sampling_rate, type=type_, plot=True)
