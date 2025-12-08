from montage_manager import VideoMontageMaker
import os
from PIL import Image
from gtts import gTTS

def create_dummy_assets():
    os.makedirs('test_assets', exist_ok=True)
    
    # Create dummy images
    colors = ['red', 'green', 'blue']
    image_paths = []
    for color in colors:
        img = Image.new('RGB', (640, 480), color=color)
        path = f'test_assets/{color}.png'
        img.save(path)
        image_paths.append(path)
        
    # Create dummy audio
    tts = gTTS("This is a test audio for the video montage.", lang='en')
    audio_path = 'test_assets/audio.mp3'
    tts.save(audio_path)
    
    return image_paths, audio_path

def generate_montage_video():
    maker = VideoMontageMaker()
    image_paths, audio_path = create_dummy_assets()
    
    subtitles = [
        (0, 2, "This is a test audio"),
        (2, 4, "for the video"),
        (4, 6, "montage.")
    ]
    
    # Ensure output directory exists
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'montage.mp4')
    try:
        maker.create_montage(image_paths, audio_path, subtitles, output_path)
        print(f"Success! Video saved to {output_path}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    generate_montage_video()
