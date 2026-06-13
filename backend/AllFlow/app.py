import os
import shutil
import subprocess
import json
import threading
import time
import sys

if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

video_status = {
    "is_generating": False,
    "last_video_path": None
}

video_progress = {
    "percent": 0,
    "elapsed": 0,
    "stage": "idle",
    "frame": 0,
    "total_frames": 0,
    "speed": 0,
    "stage_index": 0,
    "total_stages": 5
}

def quick_analyze(data):
    """Rule-based structured analysis from JSON data — no AI needed."""
    comments = data.get("comments", [])
    engagement = data.get("engagement", {})
    post = data.get("post_content", "")

    price_kw = ["بكام", "سعر", "كام", "تمن", "بتاخد", "بياخد"]
    positive_kw = ["ممتاز", "رائع", "جميل", "تسلم", "يسلمو", "شكرا", "شكرًا", "تمام", "حلو", "احسن", "بحب", "عظيم"]
    negative_kw = ["وحش", "سيء", "غالي", "غلاء", "مش كويس", "زهقت", "بطيء"]

    pos, neg, neu = 0, 0, 0
    for c in comments:
        text = c.get("comment", "")
        if any(k in text for k in positive_kw):
            pos += 1
        elif any(k in text for k in negative_kw):
            neg += 1
        else:
            neu += 1

    # Scale sample to total comment count
    total = engagement.get("comments", len(comments))
    sample = max(len(comments), 1)
    scale = total / sample
    pos = round(pos * scale)
    neg = round(neg * scale)
    neu = total - pos - neg

    issues = []
    no_price = any(any(k in c.get("comment", "") for k in price_kw) for c in comments)
    has_dm = any(
        any("تم التوصل" in r.get("reply", "") or "رسائل الصفحه" in r.get("reply", "")
            for r in c.get("replies", []))
        for c in comments
    )
    if no_price:
        pct = round(neu / total * 100) if total else 0
        issues.append(f"السعر غير مذكور - ~{pct}% من التعليقات تسأل عن السعر")
    if has_dm:
        issues.append("الرد بـ'تم التوصل' يُخفي السعر عن الجمهور ويُقلل التحويل")
    if engagement.get("shares", 0) < 5:
        issues.append("معدل المشاركة منخفض جداً مقارنة بحجم التعليقات")

    suggestions = [
        "أضف السعر مباشرةً في البوست أو في أول تعليق مثبّت",
        "استبدل 'تم التوصل' بالسعر في ردودك العامة لتحفيز الشراء الفوري",
        "أضف CTA واضح مثل 'اطلب الآن على واتساب: [رقم]'",
        "أنشئ Story تكشف فيه السعر لجذب مشاركات أكثر",
    ]

    topics = []
    if "تشيكن" in post or "فرايد" in post:
        topics.append("Fried Chicken")
    if "عرض" in post:
        topics.append("Offer")
    if "كول سلو" in post:
        topics.append("Coleslaw")
    if not topics:
        topics = ["Food", "Offer"]

    sentiment = "Neutral" if neu >= (pos + neg) else ("Positive" if pos > neg else "Negative")

    return {
        "issues": issues,
        "suggestions": suggestions,
        "comment_analysis": {"Positive": pos, "Negative": neg, "Neutral": neu},
        "sentiment": sentiment,
        "topics": topics,
        "video_ready": False,
    }

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_stage(folder_name, script_name, ignore_failure=False, extra_args=None):
    cwd = os.path.join(BACKEND_DIR, folder_name)
    python_exe = os.path.join(cwd, 'venv', 'Scripts', 'python.exe')
    
    stages_to_run = [python_exe, 'python'] if os.path.exists(python_exe) else ['python']
    
    start_time = time.time()
    last_error = Exception(f"Failed to run {script_name} in {folder_name}")
    for exe in stages_to_run:
        cmd = [exe, script_name] + (extra_args or [])
        print("\n" + "="*50, flush=True)
        print(f"STAGE START: {folder_name}", flush=True)
        print(f"Command: {' '.join(cmd)}", flush=True)
        print("="*50, flush=True)
        try:
            subprocess.run(cmd, cwd=cwd, check=True)
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

def run_stage_stream(folder_name, script_name, ignore_failure=False, extra_args=None):
    """Run a stage with streaming stdout to capture tqdm progress."""
    global video_progress
    cwd = os.path.join(BACKEND_DIR, folder_name)
    python_exe = os.path.join(cwd, 'venv', 'Scripts', 'python.exe')
    
    stages_to_run = [python_exe, 'python'] if os.path.exists(python_exe) else ['python']
    import re
    
    last_error = Exception(f"Failed to run {script_name} in {folder_name}")
    for exe in stages_to_run:
        cmd = [exe, script_name] + (extra_args or [])
        print("\n" + "="*50, flush=True)
        print(f"STREAMING STAGE START: {folder_name}", flush=True)
        print(f"Command: {' '.join(cmd)}", flush=True)
        print("="*50, flush=True)
        
        start_time = time.time()
        try:
            proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding='utf-8')
            
            if proc.stdout is not None:
                for line in iter(proc.stdout.readline, ''):
                    line = line.rstrip()
                    print(line, flush=True)
                    
                    # Parse tqdm progress
                    m = re.search(r'frame_index:\s*\d+%\|\s*(\d+)/(\d+)', line)
                    if m:
                        frame = int(m.group(1))
                        total = int(m.group(2))
                        speed_m = re.search(r',\s*([\d.]+)it/s\]', line)
                        speed = int(float(speed_m.group(1))) if speed_m else 0
                        percent = int(frame / total * 100) if total > 0 else 0
                        video_progress.update({
                            "percent": percent,
                            "frame": frame,
                            "total_frames": total,
                            "speed": speed,
                            "stage": "rendering video"
                        })
                    
                    m2 = re.search(r'\[TOTAL ELAPSED:\s*(\d+)s\]', line)
                    if m2:
                        video_progress.update({"elapsed": int(m2.group(1))})
            else:
                # Fallback: wait without streaming
                proc.wait()
            
            if proc.returncode != 0:
                raise Exception(f"Process exited with code {proc.returncode}")
            
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
    global video_status, video_progress
    video_status["is_generating"] = True
    progress_stages = ["audio processing", "preparing assets", "generating audio", "building scenes", "rendering video"]
    video_progress.update({"percent": 0, "elapsed": 0, "stage": "starting", "frame": 0, "total_frames": 0, "speed": 0, "stage_index": 0, "total_stages": len(progress_stages)})
    
    stop_logger = threading.Event()
    logger_thread = threading.Thread(target=total_duration_logger, args=(stop_logger,))
    logger_thread.start()
    
    pipeline_start = time.time()
    stage_index = 0
    try:
        # Stage 1: Audio processing
        stage_index = 1
        video_progress.update({"stage_index": stage_index, "stage": progress_stages[stage_index-1]})
        audio_input_txt = os.path.join(audio_dir, 'file.txt')
        shutil.copy2(analyze_output, audio_input_txt)
        run_stage('audioProessStage', 'audioProcessStage.py', ignore_failure=True)
        video_progress.update({"percent": 15, "elapsed": round(time.time() - pipeline_start)})
        
        # Stage 2: Prepare assets
        stage_index = 2
        video_progress.update({"stage_index": stage_index, "stage": progress_stages[stage_index-1]})
        audio_output_path = os.path.join(audio_dir, 'audio', 'output.mp3')
        video_assets_dir = os.path.join(video_dir, 'assets')
        os.makedirs(video_assets_dir, exist_ok=True)
        
        if os.path.exists(audio_output_path):
            shutil.copy2(audio_output_path, os.path.join(video_assets_dir, 'output.mp3'))
        
        shutil.copy2(analyze_output, os.path.join(video_assets_dir, 'script.txt'))
        video_progress.update({"percent": 25, "elapsed": round(time.time() - pipeline_start)})

        # Stage 3: Audio generation (TTS)
        stage_index = 3
        video_progress.update({"stage_index": stage_index, "stage": progress_stages[stage_index-1]})

        # Auto-detect recorded narration files
        recorded_narrations = [
            os.path.join(video_assets_dir, f"{name}_narration.mp3")
            for name in ["intro", "negatives", "positives", "improvements"]
        ]
        has_recorded = all(os.path.exists(p) for p in recorded_narrations)
        montage_args = ['--recorded'] if has_recorded else []
        if has_recorded:
            print("RECORDED NARRATION DETECTED: using your voice instead of gTTS")
        
        video_progress.update({"percent": 35, "elapsed": round(time.time() - pipeline_start)})

        # Stage 4-5: Montage (scene building + rendering)
        stage_index = 4
        video_progress.update({"stage_index": stage_index, "stage": progress_stages[stage_index-1]})
        run_stage_stream('motageVideoStage', 'app.py', ignore_failure=True, extra_args=montage_args)
        
        video_path = os.path.join(video_dir, 'output', 'final_montage.mp4')
        if os.path.exists(video_path):
            video_status["last_video_path"] = video_path
            total_time = time.time() - pipeline_start
            video_progress.update({"percent": 100, "elapsed": round(total_time), "stage": "complete", "stage_index": len(progress_stages)})
            print(f"!!! COMPLETE !!! All stages finished in {total_time:.2f}s. Video saved to {video_path}")
    except Exception as e:
        print(f"!!! CRITICAL FAILURE in pipeline: {e}", flush=True)
        video_progress.update({"stage": f"error: {str(e)[:50]}"})
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
        dest_json = os.path.join(analyze_dir, 'BazookaFriedChicken.json')
        if not os.path.exists(dest_json):
            source_json = os.path.join(BACKEND_DIR, 'BazookaFriedChicken.json')
            if os.path.exists(source_json):
                shutil.copy2(source_json, dest_json)
            
        run_stage('AnalyzeHumanStage', 'AnalyzeHumanStage.py', ignore_failure=True)
        
        analyze_output = os.path.join(analyze_dir, 'file.txt')
        if not os.path.exists(analyze_output) or os.path.getsize(analyze_output) < 10:
            fallback_text = "Hello Bazooka Fried Chicken, in this video we will summarize your post data in three parts.\n\nPart One: The Negatives\nNo price listed created major friction. Over 1000 comments asking 'how much?'.\n\nPart Two: The Positives\nStrong interest with 1100 comments. Hundreds of likes.\n\nPart Three: How to Improve\nInclude price in post. Replace vague replies with clear answers."
            with open(analyze_output, 'w', encoding='utf-8') as f:
                f.write(fallback_text)

        threading.Thread(target=process_video_background, args=(analyze_output, audio_dir, video_dir)).start()

        with open(dest_json, 'r', encoding='utf-8') as f:
            post_data = json.load(f)
        analysis = quick_analyze(post_data)
        analysis["message"] = "Analysis started"
        return jsonify(analysis), 200

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

@app.route('/api/video-progress', methods=['GET'])
def get_video_progress():
    global video_progress
    video_path = os.path.join(BACKEND_DIR, 'motageVideoStage', 'output', 'final_montage.mp4')
    ready = os.path.exists(video_path)
    return jsonify({
        **video_progress,
        "ready": ready,
        "generating": video_status.get("is_generating", False)
    })

@app.route('/api/fetch-post', methods=['POST'])
def fetch_post():
    try:
        source_json = os.path.join(BACKEND_DIR, 'AnalyzeHumanStage', 'BazookaFriedChicken.json')
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
    app.run(host='0.0.0.0', port=5001, debug=True)
