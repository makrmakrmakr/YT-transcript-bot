from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "🎉 It's alive!"

@app.route("/batch-transcripts", methods=["POST"])
def batch_transcripts():
    data = request.get_json()
    video_urls = data.get("video_urls", [])

    # Temporary dummy response to confirm it works
    return jsonify({
        "message": "Received your list!",
        "video_urls": video_urls
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080
