import pytube
import cv2
import requests
import numpy as np
import os
import shutil
import ffmpeg

class Song():
    def __init__(self,url,title=None, thumbnail=None, thumbnail_url=None, audio=None, length=None):
        self.title=title
        self.url=url
        self.thumbnail=thumbnail
        self.thumbnail_url=thumbnail_url
        self.audio=audio
        self.length=length

def search(track):
    """
    Searches youtube for songs, takes first result.
    """

    s=pytube.Search(track).results[0]
    song=Song(url="https://www.youtube.com/watch?v="+str(s).split("=")[1][:-1])

    return song

def get_video(song):
    """
    Downloads audio & gets thumbnail url.
    """

    video=pytube.YouTube(song.url)
    song.thumbnail_url=video.thumbnail_url
    song.title=video.title

    audio=video.streams.filter(only_audio=True)

    bitrate=list()
    for i,stream in enumerate(audio):
        bitrate.append((i,int(str(stream).split(" ")[3][5:-5])))    #   Gets bitrate value from stream data
    bitrate.sort(reverse=True,key=lambda x: x[1])   #   Sorts
    audio=audio[bitrate[0][0]]
    
    audio.download()

    stream=ffmpeg.input(song.title+'.webm')
    stream=ffmpeg.output(stream,song.title+'.mp3')
    ffmpeg.run(stream)
    os.remove(song.title+'.webm')
    song.audio=ffmpeg.input(song.title+'.mp3')

def img_crop(song):
    """
    Gets image & center crops to square.
    """

    response=requests.get(song.thumbnail_url).content
    img=np.frombuffer(response,np.uint8)    #   Converts image to np int array (readable by opencv)
    img=cv2.imdecode(img,cv2.IMREAD_UNCHANGED)  #   Decodes image

    img=cv2.imread('screenshot.png')
    center=tuple(int(z/2) for i,z in enumerate(img.shape) if i<2)   #   Gets center point 
    cx=center[1]
    cy=center[0]
    w=min(center)   #   Constraining dimension

    crop=img[cy-w:cy+w,cx-w:cx+w]   #   Crops image
    scale=cv2.resize(crop,(300,300))    #   Scales image to 300x300px
    song.thumbnail=scale


def main():
    #3x3 selections go here v
    tracks=(
        "beach house - levitation",
        "lomelda - hannah sun",
        "the microphones - microphones in 2020",
        "sufjan stevens - death with dignity",
        "adrianne lenker - anything",
        "a beacon school - fade into nylon",
        "chris christodoulou - coalescence",
        "club kuru - meet your maker",
        "this is the kit - keep going"
    )
    if len(tracks)!=9:
        print("!    3x3 selection must contain 9 songs  !")
        exit()

    songs=[]
    for track in tracks:
        songs.append(search(track))

    for song in songs:
        get_video(song)


if __name__=="__main__":
    os.system('cls')

    path=os.path.abspath(os.getcwd())
    try:
        if os.path.isdir(path+"/temp")==True:
            shutil.rmtree(path+"/temp")
    except PermissionError:
        print("!    Close all temp files    !")
    os.mkdir(path+"/temp")

    shutil.copyfile(path+'/ffmpeg.exe',path+'/temp'+'/ffmpeg.exe')
    os.chdir(path+'/temp')

    main()

    os.chdir(path)
    shutil.rmtree(path+"/temp")
