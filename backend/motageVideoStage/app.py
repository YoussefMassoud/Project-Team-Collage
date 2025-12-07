from flask import Flask, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from montage_manager import VideoMontageMaker
import tempfile

app = Flask(__name__)
montage_maker = VideoMontageMaker()

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/create-montage', methods=['POST'])
def create_montage():
    try:
        # 1. Handle Files
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        audio_filename = secure_filename(audio_file.filename)
        audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
        audio_file.save(audio_path)
        
        image_paths = []
        if 'images' not in request.files:
             # Allow passing paths if running locally and files are already there?
             # Or maybe multiple files with same key 'images'
             return jsonify({'error': 'No images provided'}), 400
        
        files = request.files.getlist('images')
        for file in files:
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            image_paths.append(path)
            
        # 2. Handle Subtitles
        # Expecting JSON string or file? Let's assume JSON for now for simplicity
        # Format: [{"start": 0, "end": 2, "text": "Hello"}, ...]
        subtitles = []
        if 'subtitles' in request.form:
            import json
            subtitles_raw = json.loads(request.form['subtitles'])
            for item in subtitles_raw:
                subtitles.append((item['start'], item['end'], item['text']))
        
        # 3. Generate Video
        output_filename = f"montage_{os.urandom(4).hex()}.mp4"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        montage_maker.create_montage(image_paths, audio_path, subtitles, output_path)
        
        # 4. Return Result
        # Return the file directly or the path?
        # Let's return the file for download
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
