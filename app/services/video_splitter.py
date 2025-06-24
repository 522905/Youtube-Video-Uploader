import os
import subprocess
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from app.services.progress_tracker import update_progress

def split_video_into_shorts(video_path, duration=29, output_folder="shorts", overlay_text=False):
    os.makedirs(output_folder, exist_ok=True)
    base = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = os.path.join(output_folder, base)
    os.makedirs(output_dir, exist_ok=True)

    update_progress("Splitting started", 1)

    try:
        video = VideoFileClip(video_path)
    except Exception as e:
        update_progress(f"Error reading video: {e}", 100)
        return output_dir

    total_duration = int(video.duration)
    total_parts = total_duration // duration + (1 if total_duration % duration else 0)
    video.close()

    if total_parts == 0:
        update_progress("Video too short for splitting.", 100)
        return output_dir

    for i, start in enumerate(range(0, total_duration, duration), start=1):
        part_name = f"part_{i}.mp4"
        temp_path = os.path.join(output_dir, f"temp_{part_name}")
        final_path = os.path.join(output_dir, part_name)

        # FFmpeg cut + pad with 9:16 layout (no crop)
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-ss", str(start), "-t", str(duration),
            "-i", video_path,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", temp_path
        ]
        # subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"FFmpeg Error (part {i}):", result.stderr)
            update_progress(f"FFmpeg failed for part {i}: {result.stderr}", 100)
            continue


        if not os.path.exists(temp_path):
            update_progress(f"FFmpeg failed for part {i}", 100)
            continue

        if overlay_text:
            try:
                clip = VideoFileClip(temp_path)
                txt = TextClip(f"Part {i}", fontsize=70, color='white', bg_color='black', method='caption')
                txt = txt.set_position(("center", 50)).set_duration(clip.duration)
                final = CompositeVideoClip([clip, txt])
                final.audio = clip.audio
                final.write_videofile(final_path, codec="libx264", audio_codec="aac", fps=clip.fps)
                clip.close()
                os.remove(temp_path)
            except Exception as e:
                update_progress(f"Overlay failed: {e}", 100)
                continue
        else:
            os.rename(temp_path, final_path)

        percent = int((i / total_parts) * 100)
        update_progress(f"Created part {i}/{total_parts}", percent)

    update_progress("Splitting complete", 100)
    return output_dir
