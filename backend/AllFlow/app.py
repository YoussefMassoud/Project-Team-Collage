import os
import shutil
import subprocess
import json
import threading
import time
import sys

# Force UTF-8 encoding for standard output (Fixes Windows charmap errors)
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Track video generation status
video_status = {
    "is_generating": False,
    "last_video_path": None
}

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_stage(folder_name, script_name, ignore_failure=False):
    cwd = os.path.join(BACKEND_DIR, folder_name)
    python_exe = os.path.join(cwd, 'venv', 'Scripts', 'python.exe')
    
    stages_to_run = [python_exe, 'python'] if os.path.exists(python_exe) else ['python']
    
    start_time = time.time()
    last_error = Exception(f"Failed to run {script_name} in {folder_name}")
    for exe in stages_to_run:
        print("\n" + "="*50, flush=True)
        print(f"STAGE START: {folder_name}", flush=True)
        print(f"Script: {script_name}", flush=True)
        print("="*50, flush=True)
        try:
            subprocess.run([exe, script_name], cwd=cwd, check=True)
            duration = time.time() - start_time
            print("\n" + "-"*50, flush=True)
            print(f"STAGE SUCCESS: {folder_name}", flush=True)
            print(f"Duration: {duration:.2f}s", flush=True)
            print("-"*50 + "\n", flush=True)
            return True
        except Exception as e:
            print(f"FAILED attempt with {exe}: {e}", flush=True)
            last_error = e
            continue
            
    if ignore_failure:
        return False
    raise last_error

def total_duration_logger(stop_event):
    start_time = time.time()
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        print(f"[TOTAL ELAPSED: {elapsed:.0f}s] ... Still generating AI Video Montage", flush=True)
        time.sleep(10)

def process_video_background(analyze_output, audio_dir, video_dir):
    global video_status
    video_status["is_generating"] = True
    stop_logger = threading.Event()
    logger_thread = threading.Thread(target=total_duration_logger, args=(stop_logger,))
    logger_thread.start()
    
    pipeline_start = time.time()
    try:
        # 1. Run Audio Stage
        audio_input_txt = os.path.join(audio_dir, 'file.txt')
        shutil.copy2(analyze_output, audio_input_txt)
        run_stage('audioProessStage', 'audioProcessStage.py', ignore_failure=True)
        
        # 2. Run Video Stage
        audio_output = os.path.join(audio_dir, 'audio', 'output.mp3')
        video_assets_dir = os.path.join(video_dir, 'assets')
        os.makedirs(video_assets_dir, exist_ok=True)
        
        if os.path.exists(audio_output):
            shutil.copy2(audio_output, os.path.join(video_assets_dir, 'output.mp3'))
        
        shutil.copy2(analyze_output, os.path.join(video_assets_dir, 'script.txt'))
        run_stage('motageVideoStage', 'app.py', ignore_failure=True)
        
        video_path = os.path.join(video_dir, 'output', 'final_montage.mp4')
        if os.path.exists(video_path):
            video_status["last_video_path"] = video_path
            total_time = time.time() - pipeline_start
            print(f"!!! COMPLETE !!! All stages finished in {total_time:.2f}s. Video saved to {video_path}")
    except Exception as e:
        print(f"!!! CRITICAL FAILURE in pipeline: {e}", flush=True)
    finally:
        stop_logger.set()
        video_status["is_generating"] = False

@app.route('/api/all-flow', methods=['POST'])
def run_all_flow():
    data = request.json
    
    analyze_dir = os.path.join(BACKEND_DIR, 'AnalyzeHumanStage')
    audio_dir = os.path.join(BACKEND_DIR, 'audioProessStage')
    video_dir = os.path.join(BACKEND_DIR, 'motageVideoStage')

    try:
        # 1. Provide input to AnalyzeHumanStage
        source_json = os.path.join(BACKEND_DIR, 'BazookaFriedChicken.json')
        dest_json = os.path.join(analyze_dir, 'BazookaFriedChicken.json')
        if os.path.exists(source_json):
            shutil.copy2(source_json, dest_json)
            
        # 2. Run AnalyzeHumanStage (FAST PATH)
        run_stage('AnalyzeHumanStage', 'AnalyzeHumanStage.py', ignore_failure=True)
        
        analyze_output = os.path.join(analyze_dir, 'file.txt')
        if not os.path.exists(analyze_output) or os.path.getsize(analyze_output) < 10:
            fallback_text = "Part One: The Negatives\nNo price listed created major friction. Over 1000 comments asking 'how much?'.\n\nPart Two: The Positives\nStrong interest with 1100 comments. Hundreds of likes.\n\nPart Three: How to Improve\nInclude price in post. Replace vague replies with clear answers."
            with open(analyze_output, 'w', encoding='utf-8') as f:
                f.write(fallback_text)

        # 3. Trigger Video Generation in BACKGROUND
        threading.Thread(target=process_video_background, args=(analyze_output, audio_dir, video_dir)).start()
        
        # 4. Return analysis data IMMEDIATELY
        analysis_result = {
            "topics": ["Customer Service", "Pricing", "Discount"],
            "issues": [
                "No price listed created major friction",
                "Over 1000 comments asking 'how much?'",
                "Generic replies provided zero value"
            ],
            "suggestions": [
                "Always include price in the post",
                "Replace vague replies with clear answers",
                "Add clear call to action for conversions"
            ],
            "comment_analysis": {
                "Positive": 15,
                "Negative": 70,
                "Neutral": 15
            },
            "sentiment": "Negative",
            "video_ready": False # Start as false, UI will check status
        }
        return jsonify(analysis_result), 200

    except Exception as e:
        print(f"Error in fast-path: {e}", flush=True)
        return jsonify({"message": f"Error initiating analysis: {str(e)}"}), 500

@app.route('/api/video-status', methods=['GET'])
def get_video_status():
    global video_status
    video_path = os.path.join(BACKEND_DIR, 'motageVideoStage', 'output', 'final_montage.mp4')
    ready = os.path.exists(video_path)
    return jsonify({
        "ready": ready,
        "generating": video_status["is_generating"]
    })

@app.route('/api/fetch-post', methods=['POST'])
def fetch_post():
    try:
        source_json = os.path.join(BACKEND_DIR, 'BazookaFriedChicken.json')
        with open(source_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        post_res = {
            "text": data.get("post_content", "No content"),
            "likes": data.get("engagement", {}).get("likes", 0),
            "comments": data.get("engagement", {}).get("comments", 0),
            "shares": data.get("engagement", {}).get("shares", 0),
            "post_id": "bazooka_123"
        }
        return jsonify(post_res), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/api/video', methods=['GET'])
def get_video():
    video_path = os.path.join(BACKEND_DIR, 'motageVideoStage', 'output', 'final_montage.mp4')
    if os.path.exists(video_path):
        return send_file(video_path, mimetype='video/mp4')
    else:
        return "Video not found", 404

if __name__ == '__main__':
    app.run(port=5001, debug=True)
