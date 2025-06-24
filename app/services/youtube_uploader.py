import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv
from app.services.progress_tracker import update_progress

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRET_PATH")
TOKEN_FILE = os.getenv("OAUTH_TOKEN_PATH")

def authenticate_youtube():
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception:
            print("❌ Invalid token.json format. Deleting...")
            os.remove(TOKEN_FILE)
            creds = None

    if not creds or not creds.valid or not creds.refresh_token:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_local_server(port=8080, prompt='consent', access_type='offline')
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def upload_short(youtube, file_path, title, description, tags):
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"
        },
        "status": {"privacyStatus": "public"}
    }

    media = MediaFileUpload(file_path, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)

    response = None
    update_progress(f"Uploading {os.path.basename(file_path)}", 0)

    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            update_progress(f"Uploading {os.path.basename(file_path)}", pct)

    update_progress("Upload complete", 100)
    return response.get("id")

def upload_all_shorts(youtube, folder_path, title_base, description, tags):
    uploaded = 0
    errors = []

    for root, _, files in os.walk(folder_path):
        video_files = sorted([f for f in files if f.lower().endswith(".mp4")])
        total = len(video_files)

        for i, file in enumerate(video_files, start=1):
            file_path = os.path.join(root, file)
            title = f"{title_base} - Part {i} #Shorts"
            desc_full = f"{description}\nPart {i}"
            try:
                update_progress(f"Uploading Part {i} of {total}", int(((i - 1) / total) * 100))
                upload_short(youtube, file_path, title, desc_full, tags)
                uploaded += 1
                os.remove(file_path)  # ✅ delete file after successful upload
            except Exception as e:
                error_msg = f"❌ Failed to upload {file}: {e}"
                print(error_msg)
                update_progress(error_msg, 100)
                errors.append(error_msg)

        # ✅ Optional: cleanup the folder if everything succeeded
        if uploaded == total and os.path.exists(root):
            try:
                os.rmdir(root)
            except OSError:
                pass  # Folder not empty or in use

    if errors:
        return f"⚠️ Uploaded {uploaded}/{total} shorts. Some failed:\n" + "\n".join(errors)
    else:
        update_progress("All uploads complete", 100)
        return f"✅ Successfully uploaded all {uploaded} shorts."
