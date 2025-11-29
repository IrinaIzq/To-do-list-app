from flask import Blueprint, jsonify, request, current_app, send_from_directory
import os

def create_routes(auth_service, task_service, category_service):
    bp = Blueprint('api', __name__)

    @bp.route('/api/hello')
    def hello():
        return jsonify({'message': 'hello from backend', 'version': current_app.config['APP_VERSION']})

    @bp.route('/api/tasks', methods=['GET', 'POST'])
    def tasks():
        if request.method == 'GET':
            # minimal demo returning empty list (to avoid depending on DB models at this point)
            return jsonify([])
        data = request.json or {}
        title = data.get('title', 'untitled')
        # for demo: not persisting here
        return jsonify({'id': 1, 'title': title, 'done': False}), 201

    # Serve frontend assets from /frontend at root
    @bp.route('/<path:filename>')
    def frontend_files(filename):
        # serve only known static files from frontend folder
        frontend_path = os.path.join(current_app.root_path, '..', 'frontend')
        return send_from_directory(frontend_path, filename)

    return bp