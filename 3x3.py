import pytube
import cv2
import requests
import numpy as np
import os
import ffmpeg

def search(song):
    """
    Searches youtube for songs, takes first result.
    """

    s=pytube.Search(song).results[0]
    url="https://www.youtube.com/watch?v="+str(s).split("=")[1][:-1]

    return url

def get_video(url):
    """
    Downloads audio & gets thumbnail url.
    """

    video=pytube.YouTube(url)
    img_url=video.thumbnail_url
    title=video.title

    audio=video.streams.filter(only_audio=True)
    bitrate=list()
    for i,stream in enumerate(audio):
        bitrate.append((i,int(str(stream).split(" ")[3][5:-5])))    #   Gets bitrate value from stream data
    bitrate.sort(reverse=True,key=lambda x: x[1])   #   Sorts
    audio=audio[bitrate[0][0]]
    
    audio.download()

    return img_url,title
    

def img_crop(img_url):
    """
    Gets image & center crops to square.
    """

    response=requests.get(img_url).content
    img=np.frombuffer(response,np.uint8)    #   Converts image to np int array (readable by opencv)
    img=cv2.imdecode(img,cv2.IMREAD_UNCHANGED)  #   Decodes image

    center=tuple(int(z/2) for i,z in enumerate(img.shape) if i<2)   #   Gets center point 
    cx=center[1]
    cy=center[0]
    w=min(center)   #   Constraining dimension

    crop=img[cy-w:cy+w,cx-w:cx+w]   #   Crops image

    return crop

def main():
    #3x3 selections go here v
    songs=(
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
    if len(songs)!=9:
        print("!    3x3 selection must contain 9 songs  !")
        exit()

    urls=[]
    for song in songs:
        urls.append(search(song))

    img_url,title=get_video(urls[0])


if __name__=="__main__":
    os.system('cls')
    main()
