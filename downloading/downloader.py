import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from spotdl import __main__ as start  # To initialize
from spotdl.search.song_gatherer import from_spotify_url
from pytube import YouTube
import subprocess
import sys
from difflib import SequenceMatcher
import copy
import pandas as pd

scope = "user-library-read"

os.environ["SPOTIPY_CLIENT_ID"] = ""
os.environ["SPOTIPY_CLIENT_SECRET"] = ""
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8888"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def get_filepath_speaks(filename):
    return os.path.join(os.getcwd(),"downloading",filename)

def get_playlist_order(playlist_url):
    order = []
    formattedurl = "spotify:playlist:" + playlist_url.split("/")[-1]
    length = len(
        sp.playlist(formattedurl)["tracks"]["items"]
    )

    for i in range(length):
        name = sp.playlist(formattedurl)["tracks"][
            "items"
        ][i]["track"]["name"]
        order.append(name)
    return order


def query_download(artist, track):
    query = f"track:{track} artist:{artist}"
    results = sp.search(q=query, type="track")
    if results["tracks"]["items"] == []:
        print("Song not found")
        return
    else:
        spotify_url = results["tracks"]["items"][0]["external_urls"]["spotify"]
    track_confirmed = results["tracks"]["items"][0]["name"]
    artist_confirmed = results["tracks"]["items"][0]["artists"][0]["name"]
    spotify_url
    print(f"Found match: {track_confirmed} - {artist_confirmed}")
    prevdir = os.getcwd()
    prevdir
    os.chdir(".\klub100\downloading\mp3downloads")
    subprocess.run(f"spotdl {spotify_url}")
    os.chdir(prevdir)
    return


def download_spotify_playlist(playlist_url):
    prevdir = os.getcwd()
    os.chdir(".\downloading\mp3downloads")
    exportdir = os.getcwd()
    subprocess.run(f"spotdl {playlist_url}")
    os.chdir(prevdir)
    return exportdir


def gentable(playlist_url):
    order = get_playlist_order(playlist_url)
    ordercopy = copy.copy(order)
    df = pd.DataFrame(order,columns = ["Songs"])
    df["Downloaded"] = "No"
    exportdir = download_spotify_playlist(playlist_url)
    print(order)
    for file in os.listdir(exportdir):
        if file.endswith(".wav"):
            continue
        else:
            formattedstring = str(file.split("-",1)[-1].replace(".mp3",""))
            for i,item in enumerate(order):
                if similar(item,formattedstring) > 0.8:
                    df.at[i,"Downloaded"] = "Yes"
                    df.at[i,"Songs"] = file.replace(".mp3","")
                    print("found match for", item)
                    print(ordercopy)
                    ### .wav files may be interacting w line below, fixed
                    ordercopy.remove(item)
    print("could not find match for", ordercopy)
    df["Delayed start"] = 0
    df["Duration"] = 60
    df["Associated speak"] = ""
    return df,exportdir


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
