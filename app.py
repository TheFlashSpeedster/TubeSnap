from flask import Flask, render_template, request, send_file, redirect, url_for
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url:
            return redirect(url_for("index"))

        temp_id = str(uuid.uuid4())
        output_template = os.path.join(DOWNLOAD_DIR, f"{temp_id}.%(ext)s")

        ydl_opts = {
            "outtmpl": output_template,
            "format": "bestvideo+bestaudio/best",  # best quality with audio. [web:5][web:12]
            "merge_output_format": "mp4",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get("ext", "mp4")
            filename = f"{temp_id}.{ext}"
            filepath = os.path.join(DOWNLOAD_DIR, filename)

        return send_file(filepath, as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)