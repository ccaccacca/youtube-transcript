import logging
import os
import requests
from flask import Flask, request, jsonify, Response, render_template
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from youtube_transcript_api.proxies import WebshareProxyConfig
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
CORS(app)

# Add configuration for production
app.config['JSON_SORT_KEYS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

# Configure YouTube Transcript API with proxy
ytt_api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username="quoofpkh",
        proxy_password="k481zfbrv2ki",
    )
)

def format_time(seconds, format_type="srt"):
    """Formats time to HH:MM:SS,MMM (SRT) or HH:MM:SS.MMM (TXT)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    if format_type == "srt":
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
    return f"{hours:02}:{minutes:02}:{secs:02}.{millis:03}"

def format_transcript(transcript, format_type="txt"):
    """Formats transcript into SRT or TXT format."""
    formatted_text = ""
    for index, t in enumerate(transcript, start=1):
        start_time = format_time(t['start'], format_type)
        if format_type == "srt":
            formatted_text += f"{index}\n{start_time} --> {format_time(t['start'] + t.get('duration', 0.5), format_type)}\n{t['text']}\n\n"
        else:
            formatted_text += f"{start_time} {t['text']}\n"

    return formatted_text.strip()

@app.route('/', methods=['GET'])
def home():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    """Health check route to confirm the server is running."""
    return jsonify({"status": "running"}), 200

@app.route('/transcript', methods=['GET'])
def get_transcript():
    """Fetches and returns YouTube transcript in the requested format."""
    video_id = request.args.get('videoId')
    format_type = request.args.get('format', 'txt').lower()

    if not video_id:
        return jsonify({"error": "Missing videoId parameter"}), 400

    if format_type not in ["txt", "srt"]:
        return jsonify({"error": "Invalid format. Use 'txt' or 'srt'."}), 400

    try:
        transcript = ytt_api.get_transcript(video_id)
        content = format_transcript(transcript, format_type)
        filename = f"transcript.{format_type}"

        return Response(
            content,
            mimetype="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )

    except TranscriptsDisabled:
        logger.error(f"Transcripts are disabled for video ID: {video_id}")
        return jsonify({"error": "Transcripts are disabled for this video"}), 400
    except NoTranscriptFound:
        logger.error(f"No transcript found for video ID: {video_id}")
        return jsonify({"error": "No transcript available for this video"}), 404
    except VideoUnavailable:
        logger.error(f"Video unavailable: {video_id}")
        return jsonify({"error": "This video is unavailable"}), 404
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
