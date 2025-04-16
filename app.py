from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Hello from YouTube Transcript Bot!"

@app.route("/batch-transcripts", methods=["POST"])
def batch_transcripts():
    data = request.get_json()
    video_urls = data.get("video_urls", [])

    # Just return the list for now to test
    return jsonify({
        "status": "ok",
        "received": video_urls
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
