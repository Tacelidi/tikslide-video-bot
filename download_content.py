import requests
from bs4 import BeautifulSoup
import os
from PIL import Image

def get_links(tiktok_url):
    api_url = "https://snaptik.net/api/ajaxSearch"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://snaptik.net"
    }
    data = {
        "q": tiktok_url,
        "lang": "ru"
    }
    response = requests.post(api_url, headers=headers, data=data)
    soup = BeautifulSoup(response.text, "html.parser")
    images = [img["src"] for img in soup.find_all("img") if 'src' in img.attrs]
    sound = soup.find("a")['data-audiourl']
    sound = sound[2:-2]
    for i in range(len(images)):
        images[i] = images[i][2:-2]
    return [images, sound]

def get_images_and_sound(links,id):
    images = links[0]
    sound = links[1]
    headers = {
        "User-Agent": "Mozilla/5.0",
    }
    for i,url in enumerate(images,start=1):
        os.makedirs(f"content{id}",exist_ok=True)
        os.makedirs(os.path.join(f"content{id}","img"),exist_ok=True)
        save_dir = f"content{id}/img"
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        filename = f"file{i}.webp"
        path = os.path.join(save_dir, filename)
        with open(path, "wb") as f:
            f.write(r.content)
    r = requests.get(sound, headers=headers)
    r.raise_for_status()
    save_dir = f"content{id}"
    path = os.path.join(save_dir, "music.mp3")
    with open(path, "wb") as f:
        f.write(r.content)

def convert_images(id):
    image_dir = f"content{id}/img"
    image_files = sorted(
        [os.path.join(image_dir, f) for f in os.listdir(image_dir)]
    )
    os.makedirs(os.path.join(f"content{id}", "converted_img"), exist_ok=True)
    for i,j in enumerate(image_files):
        myimage = Image.open(j)
        myimage.save(f"content{id}/converted_img/file{i + 1}.png")

def download(tiktok_url,id):
    links = get_links(tiktok_url)
    get_images_and_sound(links,id)
    convert_images(id)

