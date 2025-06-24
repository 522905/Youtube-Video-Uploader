import yt_dlp
import os
from dotenv import load_dotenv
from app.services.progress_tracker import update_progress


load_dotenv()
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")

def download_video(url):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    update_progress("Downloading video", 5)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'keepvideo': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        update_progress("Download complete", 100)
        return os.path.join(DOWNLOAD_DIR, f"{info['title']}.{info['ext']}")

