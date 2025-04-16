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
        if request.is_json:
            data = request.get_json()
        else:
            data = json.loads(request.get_data(as_text=True))
    except Exception as e:
        return jsonify({"error": f"Failed to parse request body: {str(e)}"}), 400

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
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = ' '.join([entry['text'] for entry in transcript]).lower()
            mentions_tree_care = any(keyword in full_text for keyword in keywords)

            quotes = []
            for entry in transcript:
                line = entry['text'].lower()
                if any(keyword in line for keyword in keywords):
                    quotes.append({
                        "time": format_time(entry['start']),
                        "text": entry['text']
                    })

            publish_date = get_publish_date(video_id)

            results.append({
                'url': url,
                'published': publish_date,
                'mentions_tree_care': mentions_tree_care,
                'quotes': quotes,
                'summary': "Mentions found: tree care or forestry" if mentions_tree_care else "No mentions found."
            })

        except (TranscriptsDisabled, NoTranscriptFound):
            results.append({
                'url': url,
                'published': "Unknown",
                'transcript': None,
                'mentions_tree_care': False,
                'quotes': [],
                'summary': 'Transcript not available.'
            })
        except Exception as e:
            results.append({
                'url': url,
                'published': "Unknown",
                'error': str(e)
            })

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
