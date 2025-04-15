from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs

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

@app.route('/')
def home():
    return "I'm alive!"

@app.route('/batch-transcripts', methods=['POST'])
def batch_transcripts():
    data = request.get_json()
    video_urls = data.get('video_urls', [])
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

            # Find all matching lines with timestamps
            quotes = []
            for entry in transcript:
                line = entry['text'].lower()
                if any(keyword in line for keyword in keywords):
                    quotes.append({
                        "time": format_time(entry['start']),
                        "text": entry['text']
                    })

            summary = "Mentions found: tree care or forestry" if mentions_tree_care else "No mentions found."
            results.append({
                'url': url,
                'mentions_tree_care': mentions_tree_care,
                'quotes': quotes,
                'summary': summary
            })

        except (TranscriptsDisabled, NoTranscriptFound):
            results.append({
                'url': url,
                'transcript': None,
                'mentions_tree_care': False,
                'quotes': [],
                'summary': 'Transcript not available.'
            })
        except Exception as e:
            results.append({
                'url': url,
                'error': str(e)
            })

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
