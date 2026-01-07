# api/index.py (rename your app.py here)
from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid
import tempfile

app = Flask(__name__)

DOWNLOAD_DIR = tempfile.gettempdir()  # Use temp dir for serverless []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url:
            return "Invalid URL", 400

        temp_id = str(uuid.uuid4())
        output_template = os.path.join(DOWNLOAD_DIR, f"{temp_id}.%(ext)s")

        ydl_opts = {
            "outtmpl": output_template,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get("ext", "mp4")
            filename = f"{temp_id}.{ext}"
            filepath = os.path.join(DOWNLOAD_DIR, filename)

        return send_file(filepath, as_attachment=True, download_name=filename)

    return render_template("index.html")  # templates/ still works []