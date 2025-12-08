from montage_manager import VideoMontageMaker
import os
import re

def create_final_montage():
    maker = VideoMontageMaker()
    
    # Get downloaded images
    image_folder = 'downloaded_images'
    image_paths = []
    
    if os.path.exists(image_folder):
        # Sort images numerically
        image_files = []
        for file in os.listdir(image_folder):
            if file.endswith(('.jpg', '.png', '.jpeg')):
                match = re.search(r'image_(\d+)', file)
                if match:
                    num = int(match.group(1))
                    image_files.append((num, os.path.join(image_folder, file)))
                else:
                    image_files.append((999, os.path.join(image_folder, file)))
        
        image_files.sort(key=lambda x: x[0])
        image_paths = [path for _, path in image_files]
    
    if not image_paths:
        print("No images found. Using test images...")
        # Create test images as fallback
        os.makedirs('test_images', exist_ok=True)
        from PIL import Image
        colors = [('red', (255,0,0)), ('green', (0,255,0)), ('blue', (0,0,255))]
        for i, (color_name, color) in enumerate(colors):
            img = Image.new('RGB', (640, 480), color)
            path = f'test_images/color_{i+1}.jpg'
            img.save(path)
            image_paths.append(path)
    
    print(f"Using {len(image_paths)} images")
    
    # Audio file path
    audio_path = 'audio/output.mp3'
    if not os.path.exists(audio_path):
        print("No audio file found. Using test audio...")
        os.makedirs('test_audio', exist_ok=True)
        from gtts import gTTS
        tts = gTTS("Test audio for video montage.", lang='en')
        audio_path = 'test_audio/test.mp3'
        tts.save(audio_path)
    
    # Output path
    output_folder = 'final_output'
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, 'final_montage.mp4')
    
    # Create subtitles
    subtitles = []
    try:
        with open('script.txt', 'r', encoding='utf-8') as f:
            script_text = f.read()
        
        # Simple subtitle generation
        from moviepy.editor import AudioFileClip
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        
        # Split text into sentences
        sentences = [s.strip() for s in script_text.split('.') if s.strip()]
        sentence_duration = audio_duration / max(len(sentences), 1)
        
        current_time = 0
        for i, sentence in enumerate(sentences):
            if len(sentence) > 100:  # Too long, split further
                words = sentence.split()
                for j in range(0, len(words), 10):
                    chunk = ' '.join(words[j:j+10])
                    if chunk:
                        end_time = min(current_time + sentence_duration/2, audio_duration)
                        if end_time > current_time:
                            subtitles.append((current_time, end_time, chunk))
                            current_time = end_time
            else:
                end_time = min(current_time + sentence_duration, audio_duration)
                if end_time > current_time:
                    subtitles.append((current_time, end_time, sentence))
                    current_time = end_time
                    
    except Exception as e:
        print(f"Could not generate subtitles: {e}")
    
    print(f"Creating video with {len(image_paths)} images and {len(subtitles)} subtitles...")
    
    try:
        maker.create_montage(
            image_paths=image_paths,
            audio_path=audio_path,
            subtitles=subtitles,
            output_path=output_path
        )
        print(f"✅ Video saved to: {output_path}")
        
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"📊 File size: {size_mb:.2f} MB")
            return True
        return False
        
    except Exception as e:
        print(f"❌ Failed to create video: {e}")
        return False

if __name__ == "__main__":
    create_final_montage()
