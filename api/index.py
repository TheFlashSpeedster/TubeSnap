from flask import Flask, request, send_file
import yt_dlp
import os
import uuid
import tempfile
import shutil
import traceback

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
    <title>TubeSnap</title>
    <style>
        body { margin:0; height:100vh; display:flex; align-items:center; justify-content:center; font-family:system-ui; background:#0f172a; color:#e5e7eb; }
        .box { padding:2rem; border-radius:0.75rem; background:#020617; box-shadow:0 20px 40px rgba(0,0,0,0.6); min-width:320px; }
        h1 { margin:0 0 1rem; font-size:1.25rem; text-align:center; }
        form { display:flex; gap:0.5rem; }
        input[type="text"] { flex:1; padding:0.6rem 0.8rem; border-radius:0.5rem; border:1px solid #1f2937; background:#020617; color:#e5e7eb; }
        button { padding:0.6rem 1rem; border-radius:0.5rem; border:none; background:#2563eb; color:#e5e7eb; cursor:pointer; }
        button:hover { background:#1d4ed8; }
    </style>
</head>
<body>
    <div class="box">
        <h1>TubeSnap</h1>
        <form method="post">
            <input type="text" name="url" placeholder="Paste YouTube URL" required>
            <button type="submit">Download</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url:
            return "Invalid URL", 400

        try:
            temp_dir = tempfile.mkdtemp()
            temp_id = str(uuid.uuid4())
            output_template = os.path.join(temp_dir, f"{temp_id}.%(ext)s")

            ydl_opts = {
                "outtmpl": output_template,
                "format": "best[ext=mp4]/best",
                "noplaylist": True,
                "extractor_args": {"youtube": {"skip": ["hls", "dash"]}},
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                files = ydl.prepare_filename(info)
                filepath = files.rsplit(".", 1)[0] + ".mp4"
                if not os.path.exists(filepath):
                    filepath = files.rsplit(".", 1)[0] + ".webm"

            if os.path.exists(filepath):
                return send_file(filepath, as_attachment=True, download_name="video.mp4")
            return "Download failed", 500

        except Exception as e:
            return f"Error: {str(e)}", 500
        finally:
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)

    return HTML

if __name__ == "__main__":
    app.run()