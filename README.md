# 🎬 YouTube Shorts Uploader (Flask-Based Automation Tool)

This project is a **web-based Python tool** that allows users to **automate the creation and uploading of YouTube Shorts** from any public YouTube video. It's built using **Flask**, **yt-dlp**, **moviepy**, and the **YouTube Data API**.

---

## ✅ Features

- 🔗 Input a YouTube video URL through the web interface
- ⬇️ Automatically download the video in best quality using `yt-dlp`
- ✂️ Split the full video into **vertical 9:16 shorts** (29s by default)
- 🎥 Upload each short directly to your **YouTube Shorts section**
- 🔄 Handles OAuth2 authentication and token refresh for upload
- 🌐 Simple, clean web UI built with Flask + Jinja

---

## 🚀 How It Works

1. **User submits a YouTube video URL**
2. `yt-dlp` downloads the full video (merged best video+audio)
3. `moviepy` splits the video into **< 60s vertical clips (1080x1920)**
4. Each short is given a `#Shorts` tag in title/description
5. Videos are uploaded using the YouTube Data API
6. Final videos appear in your **YouTube Shorts** section (not regular videos tab)

---

## 🛠️ Project Structure

project/
├── run.py
├── .env
├── requirements.txt
├── app/
│ ├── init.py
│ ├── routes.py
│ ├── templates/
│ │ └── index.html
│ ├── services/
│ │ ├── downloader.py
│ │ ├── video_splitter.py
│ │ └── youtube_uploader.py
│ └── credentials/
│ └── client_secrets.json
├── downloads/
├── shorts/



---

## 🔧 Setup Instructions

1. **Install Python 3.10.13** (strongly recommended)
2. Clone this repo
3. Create `.env` file with:
   ```env
   CLIENT_SECRET_PATH=app/credentials/client_secrets.json
   DOWNLOAD_DIR=downloads
   SHORTS_DIR=shorts
   OAUTH_TOKEN_PATH=app/credentials/token.json
   FLASK_SECRET=your_secret_key
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run the Flask server:

bash
Copy
Edit
python run.py
Open http://localhost:5000 in your browser.

⚠️ Notes & Gotchas
Shorts upload requires:

Vertical resolution: 1080x1920

Duration: ≤ 60s

Tag: #Shorts in title or description

If you get:

pgsql
Copy
Edit
Authorized user info was not in the expected format, missing fields refresh_token
→ Delete token.json and re-authenticate.

If yt-dlp gives 403 errors → update it:

bash
Copy
Edit
yt-dlp -U
💡 Next Steps (Future Ideas)
🎨 Overlay text/hashtags on video clips

🎚️ Crop/trim interface for manual editing

📅 Upload scheduler or batch automation

📱 Telegram Bot or REST API wrapper

☁️ Deploy on Render or Railway

🧪 Tech Stack
Python 3.10+

Flask

yt-dlp

moviepy

Google OAuth + YouTube Data API