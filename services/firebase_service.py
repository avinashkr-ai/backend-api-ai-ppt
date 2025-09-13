import firebase_admin
from firebase_admin import credentials, db
import os

class FirebaseService:
    def __init__(self):
        database_url = os.environ.get('FIREBASE_DATABASE_URL')
        if not database_url:
            raise ValueError("Missing Firebase database URL")
        
        if not firebase_admin._apps:
            # The SDK will automatically use the GOOGLE_APPLICATION_CREDENTIALS environment
            # variable if it's set. Otherwise, it will look for a default credential.
            cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })

    def save_analysis(self, video_id: str, analysis: dict):
        try:
            ref = db.reference(f'/video_analysis/{video_id}')
            ref.set(analysis)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    def get_analysis(self, video_id: str):
        try:
            ref = db.reference(f'/video_analysis/{video_id}')
            return ref.get()
        except Exception as e:
            return {"error": str(e)}

    def save_presentation(self, video_id: str, presentation: dict):
        try:
            ref = db.reference(f'/presentations/{video_id}')
            ref.set(presentation)
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    def get_presentation(self, video_id: str):
        try:
            ref = db.reference(f'/presentations/{video_id}')
            return ref.get()
        except Exception as e:
            return {"error": str(e)}

    def get_all_presentations(self):
        try:
            ref = db.reference('/presentations')
            return ref.get()
        except Exception as e:
            return {"error": str(e)}
