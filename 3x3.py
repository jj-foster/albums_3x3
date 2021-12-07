import pytube
import cv2
import requests
import numpy as np
import os

os.system('cls')

def search(songs):
    """
    Searches youtube for songs, takes first result.
    """
    urls=[]
    for song in songs:
        s=pytube.Search(song).results[0]
        urls.append("https://www.youtube.com/watch?v="+str(s).split("=")[1][:-1])

    return urls

def get_video(urls):
    """
    Downloads audio & gets thumbnail url for each video.
    """

    img_url=[]
    for url in urls:
        video=pytube.YouTube(url)
        img_url.append(video.thumbnail_url)
        

    
video=pytube.YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
img_url=video.thumbnail_url

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

#3x3 selections go here v
songs=(
    "beach house - levitation",
    "lomelda - hannah sun",
    "the microphones - microphones in 2020",
    "sujian stevens - death with dignity",
    "adrianne lenker - anything",
    "a beacon school - fade into nylon",
    "chris christodoulou - coelescence",
    "club kuru - meet your maker",
    "this is the kit - keep going"
)
if len(songs)!=9:
    print("!    3x3 selection must contain 9 songs  !")
    exit()
urls=search(songs)
print(urls)