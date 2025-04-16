from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
import requests
import json

app = Flask(__name__)

def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    return None

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def get_publish_date(video_id):
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("author_name", "Unknown date")
    except Exception:
        return "Unknown date"

@app.route('/')
def home():
    return "I'm alive!"

@app.route("/batch-transcripts", methods=["POST"])
def batch_transcripts():
    try:
        data = request.get_json(force=True)
        if isinstance(data, str):
            data = json.loads(data)
    except Exception as e:
        print("❌ Failed to parse JSON:", str(e))
        return jsonify({"error": "Invalid JSON received", "details": str(e)}), 400

    print("📦 Parsed input data:", data)

    video_urls = data.get("video_urls", [])
    keywords = ['tree care', 'forestry']
    results = []

    for url in video_urls:
        video_id = extract_video_id(url)
        if not video_id:
            results.append({
                'url': url,
                'error': 'Invalid YouTube URL.'
            })
            continue

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id
