from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables from .env file
load_dotenv()

from services.twelvelabs_service import TwelveLabsService
from services.gemini_service import GeminiService
from services.firebase_service import FirebaseService
from routes.presentations import presentations_bp

# Initialize services
tl_service = TwelveLabsService()
gemini_service = GeminiService()
firebase_service = FirebaseService()

app = Flask(__name__)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
CORS(app, resources={r"/*": {"origins": allowed_origins}})


# Register blueprints
app.register_blueprint(presentations_bp)

def wake_up_app():
    """Pings the Moody Bomb website to prevent it from sleeping."""
    try:
        app_url = os.getenv('APP_URL')
        if app_url:
            response = requests.get(app_url)
            if response.status_code == 200:
                print(f"Successfully pinged {app_url} at {datetime.now()}")
            else:
                print(f"Failed to ping {app_url} (status code: {response.status_code}) at {datetime.now()}")
        else:
            print("APP_URL environment variable not set.")
    except Exception as e:
        print(f"Error occurred while pinging app: {e}")

# Create a background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(wake_up_app, 'interval', minutes=9)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@app.route('/health/twelvelabs', methods=['GET'])
def twelvelabs_health_check():
    status = tl_service.check_connection()
    return jsonify(status)

@app.route('/health/gemini', methods=['GET'])
def gemini_health_check():
    status = gemini_service.check_connection()
    return jsonify(status)

@app.route('/indexes', methods=['GET'])
def get_indexes():
    indexes = tl_service.get_indexes()
    return jsonify(indexes)

@app.route('/indexes/<index_id>/videos', methods=['GET'])
def get_videos(index_id):
    videos = tl_service.get_videos(index_id)
    return jsonify(videos)

@app.route('/videos/<video_id>/analyze', methods=['POST'])
def analyze_video(video_id):
    # 1. Get video analysis from Twelve Labs
    video_analysis = tl_service.analyze_video(video_id)
    if "error" in video_analysis:
        return jsonify(video_analysis), 500

    # 2. Save analysis to Firebase
    saved_data = {"analysis": video_analysis}
    firebase_service.save_analysis(video_id, saved_data)

    return jsonify(saved_data)

@app.route('/videos/<video_id>/presentation', methods=['POST'])
def generate_presentation(video_id):
    # 1. Get video analysis from Firebase
    firebase_data = firebase_service.get_analysis(video_id)
    if not firebase_data:
        return jsonify({"error": "Video analysis not found. Please analyze the video first."}), 404
    
    video_analysis = firebase_data.get("analysis")
    if not video_analysis:
        return jsonify({"error": "Video analysis data not found in the Firebase record."}), 404

    # 2. Get the number of slides from the request, with a default of 5
    data = request.get_json() or {}
    num_slides = data.get('num_slides', 5)

    # 3. Generate presentation with Gemini
    presentation_prompt = f"Generate a presentation from the provided video analysis. The presentation should have a title and {num_slides} slides with bullet points."
    slides = gemini_service.generate_slides(video_analysis, presentation_prompt)
    
    # 4. Save the presentation to a separate presentations collection in Firebase
    firebase_service.save_presentation(video_id, slides)

    return jsonify(slides)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']
    index_id = request.form.get('index_id')
    if not index_id:
        return jsonify({"error": "Index ID is required"}), 400

    # Save the file temporarily
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file_path = os.path.join(upload_folder, video_file.filename)
    video_file.save(file_path)

    # Upload to Twelve Labs
    result = tl_service.upload_video_file(index_id, file_path)

    # Clean up the temporary file
    os.remove(file_path)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
