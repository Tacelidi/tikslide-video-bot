import ffmpeg
from download_content import download
import os
import cv2
from PIL import Image


def calculate_mean_size(id: str) -> tuple[int, int]:
    total_width = 0
    total_height = 0
    num_images = 0
    image_dir = f"content{id}/converted_img"
    for file in os.listdir(image_dir):
        with Image.open(os.path.join(image_dir, file)) as img:
            width, height = img.size
            total_width += width
            total_height += height
            num_images += 1
    mean_width = total_width // num_images
    mean_height = total_height // num_images
    return mean_width, mean_height


def resize_images(id: str) -> None:
    mean_width, mean_height = calculate_mean_size(id)
    image_dir = f"content{id}/converted_img"
    for file in os.listdir(image_dir):
        if file.lower().endswith(".png"):
            with Image.open(os.path.join(image_dir, file)) as img:
                img_resized = img.resize(
                    (mean_width, mean_height), Image.Resampling.LANCZOS
                )
                img_resized.save(os.path.join(image_dir, file), "JPEG", quality=95)


def create_video(tiktok_url: str, id: str, fps: int = 0.5) -> None:
    download(tiktok_url, id)
    resize_images(id)
    video_name = f"content{id}/video.mp4"
    images_dir = f"content{id}/converted_img"
    images = [img for img in os.listdir(images_dir) if img.lower().endswith(".png")]
    images = sorted(images, key=lambda x: int("".join(filter(str.isdigit, x))))
    first_image_path = os.path.join(images_dir, images[0])
    frame = cv2.imread(first_image_path)
    height, width, layers = frame.shape
    video = cv2.VideoWriter(
        video_name, cv2.VideoWriter_fourcc("m", "p", "4", "v"), fps, (width, height)
    )
    for image in images:
        img_path = os.path.join(images_dir, image)
        video.write(cv2.imread(img_path))
    video.release()
    video = ffmpeg.input(video_name)
    audio = ffmpeg.input(f"content{id}/music.mp3")
    (ffmpeg.output(video, audio, f"content{id}/output.mp4", shortest=None).run())
