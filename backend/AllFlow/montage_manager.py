import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from moviepy.video.fx.all import fadein, fadeout
import numpy as np

class VideoMontageMaker:
    def __init__(self):
        pass

    def create_montage(self, image_paths, audio_path, subtitles, output_path):
        """
        Creates a video montage from images and audio with subtitles.
        
        :param image_paths: List of paths to images.
        :param audio_path: Path to the audio file (mp3).
        :param subtitles: List of tuples (start_time, end_time, text) or path to SRT file (not implemented yet).
        :param output_path: Path to save the output video.
        """
        try:
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            
            if not image_paths:
                raise ValueError("No images provided")
            
            num_images = len(image_paths)
            duration_per_image = audio_duration / num_images
            
            # 3. Create Image Clips with Transitions
            clips = []
            transition_duration = 0.5  # 0.5 second crossfade between images
            
            for i, img_path in enumerate(image_paths):
                # Each clip gets the base duration
                clip = ImageClip(img_path).set_duration(duration_per_image)
                
                # Add fade in for first clip, fade out for last clip
                # All clips get fade in/out for smooth transitions
                if i == 0:
                    # First clip: fade in
                    clip = clip.fx(fadein, transition_duration)
                elif i == num_images - 1:
                    # Last clip: fade out
                    clip = clip.fx(fadeout, transition_duration)
                else:
                    # Middle clips: fade in and out
                    clip = clip.fx(fadein, transition_duration).fx(fadeout, transition_duration)
                    
                clips.append(clip)
            
            # 4. Concatenate Clips
            # For a smooth crossfade effect, we'll use overlap via padding
            video = concatenate_videoclips(clips, method="compose")


            video = video.set_audio(audio_clip)
            
            # 5. Add Subtitles with Enhanced Styling and Animations
            # subtitles argument is expected to be a list of (start, end, text)
            subtitle_clips = []
            if subtitles:
                from PIL import Image, ImageDraw, ImageFont
                import tempfile
                
                for start, end, text in subtitles:
                    # Create text image using PIL (no ImageMagick needed)
                    # Calculate text size and create image
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
                    except:
                        font = ImageFont.load_default()
                    
                    # Create a temporary image to measure text size
                    temp_img = Image.new('RGBA', (1, 1))
                    draw = ImageDraw.Draw(temp_img)
                    
                    # Get text bounding box
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # Add padding
                    padding = 20
                    img_width = min(text_width + padding * 2, video.w - 100)
                    img_height = text_height + padding * 2
                    
                    # Create actual text image with semi-transparent black background
                    txt_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 180))
                    draw = ImageDraw.Draw(txt_img)
                    
                    # Draw text centered
                    text_x = (img_width - text_width) // 2
                    text_y = (img_height - text_height) // 2
                    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))
                    
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        txt_img.save(tmp_file.name, 'PNG')
                        temp_path = tmp_file.name
                    
                    # Create ImageClip from the text image
                    txt_clip = ImageClip(temp_path).set_duration(end - start)
                    
                    # Position at bottom with 50px margin from the bottom edge
                    # This ensures subtitles are in the "bottom 5" area and clearly visible
                    txt_clip = txt_clip.set_position(('center', video.h - img_height - 50))
                    
                    # Add fade-in and fade-out transitions for smooth appearance
                    # 0.3 seconds fade in at the start, 0.3 seconds fade out at the end
                    fade_duration = 0.3
                    txt_clip = txt_clip.set_start(start)
                    txt_clip = txt_clip.fx(fadein, fade_duration).fx(fadeout, fade_duration)
                    
                    subtitle_clips.append(txt_clip)
            
            if subtitle_clips:
                final_video = CompositeVideoClip([video] + subtitle_clips)
            else:
                final_video = video

            # 6. Write Output
            final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
            
            return output_path

        except Exception as e:
            print(f"Error creating montage: {e}")
            raise e
