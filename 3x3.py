import coverpy
import pytube
import cv2
import requests
import numpy as np
import os
import shutil
import ffmpeg
from pydub import AudioSegment

class Song():
    def __init__(self,url,title,artwork=None, artwork_url=None, length=None, audio=None):
        self.title=title
        self.url=url
        self.artwork=artwork
        self.artwork_url=artwork_url
        self.length=length
        self.audio=audio

####################################    Audio   ####################################

def search(track):
    """
    Searches youtube for songs, takes first result.
    """

    s=pytube.Search(track).results[0]
    song=Song(url="https://www.youtube.com/watch?v="+str(s).split("=")[1][:-1],title=track)

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
    
    audio=AudioSegment.from_file(song.title+'.webm',format='webm')
    t=int(song.length*0.25)
    audio=audio[t*1000:t*1000+10*1000]
    audio.export(song.title+'.mp3',format='mp3')
    
    os.remove(song.title+'.webm')

    song.audio=AudioSegment.from_file(song.title+'.mp3',format='mp3')

    return None

####################################    Visual   ####################################

def video_stitch(songs,background):
    i=0
    stitch=songs[0].audio
    for i,song in enumerate(songs):  
        stitch=stitch.append(songs[i+1].audio,crossfade=500)
        if i+1==len(songs)-1:
            break
    stitch.export('stitch.mp3',format='mp3')
    stitch=ffmpeg.input('stitch.mp3')
    img=ffmpeg.input(background,t=90,loop=True)
    av=ffmpeg.concat(img,stitch,v=1,a=1)
    av=ffmpeg.output(av,'3x3.webm')
    av.run()

    return '3x3.webm'

def img_crop(song):
    """
    Gets image & center crops to square.
    """

    try:
        song.artwork_url=coverpy.CoverPy().get_cover(song.title,1).artwork(300) #   Gets track art (apple music api)
        response=requests.get(song.artwork_url).content
        img=np.frombuffer(response,np.uint8)    #   Converts image to np int array (readable by opencv)
        img=cv2.imdecode(img,cv2.IMREAD_UNCHANGED)  #   Decodes image

        song.artwork=img

    except coverpy.exceptions.NoResultsException:
        print(f"!    No result for '{song.title}'   !") 

    return None

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
    os.system('cls')
    
    path=os.path.abspath(os.getcwd())
    try:
        if os.path.isdir(path+"/tmp")==True:
            shutil.rmtree(path+"/tmp")
    except PermissionError:
        print("!    Close all tmp files    !")
    os.mkdir(path+"/tmp")
    os.chdir(path+'/tmp')

    #3x3 selections go here v
    tracks=(
        "beach house - levitation",
        "lomelda - hannah sun",
        "the microphones - microphones in 2020",
        "sufjan stevens - death with dignity",
        "adrianne lenker - songs",
        "a beacon school - cola",
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
    print("Searching for tracks complete...")

    for song in songs:
        get_audio(song)
        img_crop(song)
    print("Downloading & trimming tracks complete...")

    background=img_stack(songs)
    vid=video_stitch(songs,background)
    shutil.move(f"{path}/tmp/{vid}",f"{path}/{vid}")

    os.chdir(path)
    shutil.rmtree(path+"/tmp")

if __name__=="__main__":
    main()
