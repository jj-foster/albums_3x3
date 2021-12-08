import coverpy
import pytube
import cv2
import requests
import numpy as np
import os
import shutil
import ffmpeg
from coverpy import CoverPy

class Song():
    def __init__(self,url,title,artwork=None, artwork_url=None, length=None, audio=None):
        self.title=title
        self.url=url
        self.artwork=artwork
        self.artwork_url=artwork_url
        self.length=length
        self.audio=audio

def search(album):
    """
    Searches youtube for songs, takes first result.
    """

    s=pytube.Search(album).results[0]
    song=Song(url="https://www.youtube.com/watch?v="+str(s).split("=")[1][:-1],title=album)

    return song

def get_audio(song):
    """
    Downloads audio & gets video title.
    """

    video=pytube.YouTube(song.url)
    song.length=video.length    #   video length [s]
    audio=video.streams.filter(only_audio=True) #   gets audio streams from video

    bitrate=list()
    for i,stream in enumerate(audio):
        bitrate.append((i,int(str(stream).split(" ")[3][5:-5])))    #   Gets bitrate value from stream data
    bitrate.sort(reverse=True,key=lambda x: x[1])   #   Sorts
    audio=audio[bitrate[0][0]]

    audio.download(filename=song.title+'.webm')    #   Downloads stream with highest bitrate as .webm
    audio=ffmpeg.input(song.title+'.webm',ss=int(song.length*0.25),t=10,noaccurate_seek=None)   #   sets ffmpeg input to trim 10s at 1/4 song length.
    audio=ffmpeg.output(audio,song.title+'.mp3')
    ffmpeg.run(audio,quiet=True)
    os.remove(song.title+'.webm')

    song.audio=ffmpeg.input(song.title+'.mp3')

def video_stitch(songs,background):

    stitch=ffmpeg.concat(songs[0].audio,songs[1].audio,v=1,a=1)
    stitch=ffmpeg.concat(stitch,songs[2].audio,v=1,a=1)
    img=ffmpeg.input(background)
    stitch=ffmpeg.overlay(stitch,img)
    stitch=ffmpeg.output(stitch,'3x3.webm')
    ffmpeg.run(stitch)

def img_crop(song):
    """
    Gets image & center crops to square.
    """

    try:
        song.artwork_url=CoverPy().get_cover(song.title,1).artwork(300) #   Gets album art (apple music api)
        response=requests.get(song.artwork_url).content
        img=np.frombuffer(response,np.uint8)    #   Converts image to np int array (readable by opencv)
        img=cv2.imdecode(img,cv2.IMREAD_UNCHANGED)  #   Decodes image

        song.artwork=img

    except coverpy.exceptions.NoResultsException:
        print(f"!    No result for '{song.title}'   !") 

def img_stack(songs):
    """
    Stitches artworks in 3x3 grid.
    """
    img_list=[[songs[0].artwork,songs[1].artwork,songs[2].artwork],
            [songs[3].artwork,songs[4].artwork,songs[5].artwork],
            [songs[6].artwork,songs[7].artwork,songs[8].artwork]
            ]
        
    img=cv2.vconcat([cv2.hconcat(row) for row in img_list]) #   Stacks images
    filename='background.jpg'
    cv2.imwrite(filename,img)

    return filename

def main():
    #3x3 selections go here v
    albums=(
        "beach house - levitation",
        "lomelda - hannah sun",
        "the microphones - microphones in 2020",
        "sufjan stevens - carrie and lowell",
        "adrianne lenker - songs",
        "a beacon school - cola",
        "chris christodoulou - coalescence",
        "club kuru - meet your maker",
        "this is the kit - off off on"
    )
    if len(albums)!=9:
        print("!    3x3 selection must contain 9 songs  !")
        exit()

    songs=[]
    for album in albums:
        songs.append(search(album))

    for song in songs:
        get_audio(song)
        img_crop(song)
        
    background=img_stack(songs)
    video_stitch(songs,background)

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
