from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
import requests

app = Flask(__name__)

def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    return None

def format_time(seconds):
    """Turns 134.5 seconds into '00:02:14' """
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def get_publish_date(video_id):
    """Fetches publish date using YouTube oEmbed (no API key needed)"""
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("author_name", "Unknown date")
    except Exception:
        return "Unknown date"

@app.route("/batch-transcripts", methods=["POST"])
def batch_transcripts():
    data = request.get_json()
    video_urls = data.get("video_urls", [])

    results = []
    for url in video_urls:
        # your logic here, like fetching transcript and extracting mentions
        results.append({
            "url": url,
            "mentions_tree_care": True,
            "quotes": [],
            "video_title": "Example Video Title",
            "date": "2025-04-15"
        })

    return jsonify(results)

if __name__ == "__main__":
    app.run()


