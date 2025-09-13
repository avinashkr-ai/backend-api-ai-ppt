from flask import Blueprint, jsonify
from services.firebase_service import FirebaseService

presentations_bp = Blueprint('presentations', __name__)
firebase_service = FirebaseService()

@presentations_bp.route('/presentations', methods=['GET'])
def get_all_presentations():
    presentations = firebase_service.get_all_presentations()
    if presentations:
        return jsonify(presentations)
    return jsonify({})
