from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services.downloader import download_video
from app.services.video_splitter import split_video_into_shorts
from app.services.youtube_uploader import authenticate_youtube, upload_all_shorts, upload_short
from app.services.progress_tracker import get_progress
import os
import shutil

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("video_url")
        short_duration = int(request.form.get("short_duration", 29))
        try:
            video_path = download_video(url)
            flash("✅ Video downloaded successfully", "success")
            return render_template("index.html", video_path=video_path, short_duration=short_duration)
        except Exception as e:
            flash(f"❌ Download error: {e}", "danger")
    return render_template("index.html")


@main.route("/split", methods=["POST"])
def split():
    video_file = request.files.get("video_file")
    short_duration = int(request.form.get("short_duration", 29))
    overlay_text = "overlay_text" in request.form

    if not video_file:
        flash("❌ No video uploaded!", "danger")
        return redirect(url_for("main.index"))

    try:
        os.makedirs("uploads", exist_ok=True)
        save_path = os.path.join("uploads", video_file.filename)
        video_file.save(save_path)

        output_folder = split_video_into_shorts(
            video_path=save_path,
            duration=short_duration,
            overlay_text=overlay_text
        )

        # ✅ Delete uploaded full video after splitting
        if os.path.exists(save_path):
            os.remove(save_path)

        flash("✅ Shorts created and original video cleaned!", "success")
        return render_template("index.html", split_path=output_folder, short_duration=short_duration)
    except Exception as e:
        flash(f"❌ Splitting error: {e}", "danger")
        return redirect(url_for("main.index"))


@main.route("/upload_shorts", methods=["POST"])
def upload_shorts():
    folder = request.form.get("shorts_folder", "shorts")
    title_base = request.form.get("base_title", "Short Clip")
    description = request.form.get("description", "#Shorts")
    tags_raw = request.form.get("tags", "")
    tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]

    try:
        youtube = authenticate_youtube()
        msg = upload_all_shorts(youtube, folder, title_base, description, tags)

        # ✅ Clean up shorts and uploads folder after upload
        shutil.rmtree("shorts", ignore_errors=True)
        shutil.rmtree("uploads", ignore_errors=True)
        os.makedirs("shorts", exist_ok=True)
        os.makedirs("uploads", exist_ok=True)

        flash(msg, "success")
    except Exception as e:
        flash(f"❌ Upload failed: {e}", "danger")
    return redirect(url_for("main.index"))


@main.route("/upload_video", methods=["POST"])
def upload_video():
    video_path = request.form.get("video_path")
    if not video_path or not os.path.exists(video_path):
        flash("❌ Video file not found.", "danger")
        return redirect(url_for("main.index"))

    try:
        youtube = authenticate_youtube()
        title = os.path.basename(video_path).split('.')[0]
        description = "Full video uploaded from tool."
        tags = ["upload", "full", "video"]
        upload_short(youtube, video_path, title, description, tags)

        # ✅ Optionally delete full video after upload
        os.remove(video_path)

        flash("✅ Full video uploaded and cleaned.", "success")
    except Exception as e:
        flash(f"❌ Upload failed: {e}", "danger")

    return redirect(url_for("main.index"))


@main.route("/progress", methods=["GET"])
def progress():
    return jsonify(get_progress())
