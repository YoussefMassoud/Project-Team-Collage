from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
)
import moviepy.video.fx as vfx
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np


class VideoMontageMaker:
    def __init__(self):
        self.assets_path = "assets"
        self.output_path = "output"
        os.makedirs(self.output_path, exist_ok=True)

        # Video settings
        self.video_size = (1920, 1080)
        self.fps = 30

    def create_text_image(
        self,
        text,
        font_size,
        color=(255, 255, 255),
        bg_color=None,
        max_width=1600,
        align="center",
    ):
        """Create an image with text using PIL (no ImageMagick needed)"""
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except (OSError, IOError):
                font = ImageFont.load_default()
        temp_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))
        line_height = font_size + 20
        total_height = len(lines) * line_height + 40
        max_line_width = 0
        for line in lines:
            bbox = temp_draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            max_line_width = max(max_line_width, line_width)

        img_width = max_line_width + 80
        if bg_color:
            img = Image.new("RGBA", (img_width, total_height), bg_color)
        else:
            img = Image.new("RGBA", (img_width, total_height), (0, 0, 0, 0))

        draw = ImageDraw.Draw(img)
        y_offset = 20
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]

            if align == "center":
                x_offset = (img_width - line_width) // 2
            elif align == "right":
                x_offset = img_width - line_width - 20
            else:
                x_offset = 20

            draw.text((x_offset, y_offset), line, font=font, fill=color)
            y_offset += line_height

        return np.array(img)

    def create_title_card(self, title, duration=3, bg_color=(20, 20, 40)):
        """Create a title card with nice background and text"""
        bg = ColorClip(size=self.video_size, color=bg_color, duration=duration)
        title_img = self.create_text_image(
            title,
            font_size=80,
            color=(255, 255, 255),
            max_width=self.video_size[0] - 200,
        )
        shadow_img = self.create_text_image(
            title, font_size=80, color=(0, 0, 0), max_width=self.video_size[0] - 200
        )
        shadow_clip = ImageClip(shadow_img, duration=duration).with_position(
            lambda t: (
                self.video_size[0] // 2 - shadow_img.shape[1] // 2 + 3,
                self.video_size[1] // 2 - shadow_img.shape[0] // 2 + 3,
            )
        )

        title_clip = ImageClip(title_img, duration=duration).with_position("center")

        composite = CompositeVideoClip([bg, shadow_clip, title_clip])
        composite = composite.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])

        return composite

    def create_section_title(self, section_title, subtitle, duration=4, image_path=None):
        """Create section title card with full image background"""
        if image_path and os.path.exists(image_path):
            # Use image as background
            bg_img = ImageClip(image_path, duration=duration).resized(width=self.video_size[0])
            if bg_img.h > self.video_size[1]:
                bg_img = bg_img.cropped(y_center=bg_img.h/2, height=self.video_size[1])
            
            # Add a slight dark tint so text is readable
            dark_bg = ColorClip(size=self.video_size, color=(0, 0, 0), duration=duration)
            bg_img = bg_img.with_opacity(0.7).with_position("center")
            elements = [dark_bg, bg_img]
        else:
            # Fallback to gradient if no image
            bg = self.create_gradient_background((30, 50, 80), (60, 80, 120), duration)
            elements = [bg]

        main_title_img = self.create_text_image(
            section_title,
            font_size=90,
            color=(255, 215, 0),
            max_width=self.video_size[0] - 200,
        )

        main_title = ImageClip(main_title_img, duration=duration).with_position(
            ("center", self.video_size[1] // 3 - main_title_img.shape[0] // 2)
        )
        
        sub_title_img = self.create_text_image(
            subtitle,
            font_size=50,
            color=(255, 255, 255),
            max_width=self.video_size[0] - 400,
        )

        sub_title = ImageClip(sub_title_img, duration=duration).with_position(
            ("center", self.video_size[1] // 2 + 50)
        )

        elements.extend([main_title, sub_title])
        composite = CompositeVideoClip(elements)
        composite = composite.with_effects([vfx.FadeIn(0.8), vfx.FadeOut(0.8)])

        return composite

    def create_gradient_background(self, color1, color2, duration):
        """Create a gradient background"""
        gradient = np.zeros((self.video_size[1], self.video_size[0], 3), dtype=np.uint8)

        for i in range(self.video_size[1]):
            ratio = i / self.video_size[1]
            color = tuple(
                int(color1[j] * (1 - ratio) + color2[j] * ratio) for j in range(3)
            )
            gradient[i, :] = color
        clip = ImageClip(gradient, duration=duration)
        return clip

    def add_subtitle(self, text, start_time, end_time, video_size):
        """Create pro subtitle in the center without a background box"""
        duration = end_time - start_time
        subtitle_img = self.create_text_image(
            text.upper(), # Pro style: Uppercase
            font_size=65,
            color=(255, 255, 255),
            bg_color=None, # No background box
            max_width=video_size[0] - 300,
        )
        
        # Add a shadow for better visibility in center
        shadow_img = self.create_text_image(
            text.upper(),
            font_size=65,
            color=(0, 0, 0),
            bg_color=None,
            max_width=video_size[0] - 300,
        )

        shadow_clip = (
            ImageClip(shadow_img, duration=duration)
            .with_position(("center", video_size[1] // 2 + 5))
            .with_start(start_time)
            .with_opacity(0.6)
        )

        txt_clip = (
            ImageClip(subtitle_img, duration=duration)
            .with_position("center")
            .with_start(start_time)
        )

        return [shadow_clip, txt_clip]

    def create_image_clip_with_zoom(self, image_path, duration, text=None):
        """Create image clip that always fills the screen (no black bars)"""
        img_clip = ImageClip(image_path, duration=duration)
        
        # Calculate scaling to cover the screen
        w_ratio = self.video_size[0] / img_clip.w
        h_ratio = self.video_size[1] / img_clip.h
        fill_ratio = max(w_ratio, h_ratio)
        
        # Resize and center crop
        img_clip = img_clip.resized(fill_ratio)
        img_clip = img_clip.cropped(
            x_center=img_clip.w / 2,
            y_center=img_clip.h / 2,
            width=self.video_size[0],
            height=self.video_size[1]
        ).with_position("center")
        
        return img_clip

    def parse_script(self, script_path):
        """Parse the script file into sections"""
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        sections = {"intro": "", "negatives": "", "positives": "", "improvements": ""}

        lines = content.split("\n")
        current_section = "intro"

        for line in lines:
            line = line.strip()
            if "Part One: The Negatives" in line:
                current_section = "negatives"
            elif "Part Two: The Positives" in line:
                current_section = "positives"
            elif "Part Three: How to Improve" in line:
                current_section = "improvements"
            elif line and not line.startswith("Part"):
                sections[current_section] += line + " "

        return sections

    def create_montage(self):
        """Create the complete video montage"""
        print("Starting video creation...")
        audio_path = os.path.join(self.assets_path, "output.mp3")
        script_path = os.path.join(self.assets_path, "script.txt")

        images = {
            "intro": os.path.join(self.assets_path, "intro.png"),
            "negatives": os.path.join(self.assets_path, "negative.png"),
            "positives": os.path.join(self.assets_path, "positive.png"),
            "improvements": os.path.join(self.assets_path, "How to improved.png"),
        }
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        sections = self.parse_script(script_path)
        title_card_duration = 3.0
        if total_duration < 30:
            title_card_duration = 2.0
            
        # Calculate section durations based on word count for better synchronization
        content_sections = ["intro", "negatives", "positives", "improvements"]
        word_counts = {sec: len(sections[sec].split()) for sec in content_sections}
        total_words = sum(word_counts.values())
        
        # Avoid division by zero
        if total_words == 0:
            total_words = 1
            word_counts = {sec: 1 for sec in content_sections}
            
        remaining_time = total_duration - (4 * title_card_duration)
        
        t = 0
        timings = {}
        
        # Intro
        timings["intro_title"] = (t, t + title_card_duration)
        t += title_card_duration
        intro_dur = (word_counts["intro"] / total_words) * remaining_time
        timings["intro"] = (t, t + intro_dur)
        t += intro_dur
        
        # Negatives
        timings["negatives_title"] = (t, t + title_card_duration)
        t += title_card_duration
        neg_dur = (word_counts["negatives"] / total_words) * remaining_time
        timings["negatives"] = (t, t + neg_dur)
        t += neg_dur
        
        # Positives
        timings["positives_title"] = (t, t + title_card_duration)
        t += title_card_duration
        pos_dur = (word_counts["positives"] / total_words) * remaining_time
        timings["positives"] = (t, t + pos_dur)
        t += pos_dur
        
        # Improvements
        timings["improvements_title"] = (t, t + title_card_duration)
        t += title_card_duration
        timings["improvements"] = (t, total_duration)

        clips = []

        print("Creating intro title...")
        intro_title = self.create_title_card(
            "Bazooka Fried Chicken Social Media Analysis",
            duration=timings["intro_title"][1] - timings["intro_title"][0],
        )
        clips.append(intro_title)

        print("Creating intro section...")
        intro_clip = self.create_image_clip_with_zoom(
            images["intro"],
            duration=timings["intro"][1] - timings["intro"][0],
            text=sections["intro"],
        )
        intro_clip = intro_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
        clips.append(intro_clip)
        print("Creating negatives section...")
        neg_title = self.create_section_title(
            "Part One",
            "The Negatives",
            duration=timings["negatives_title"][1] - timings["negatives_title"][0],
            image_path=images["negatives"],
        )
        clips.append(neg_title)

        neg_clip = self.create_image_clip_with_zoom(
            images["negatives"],
            duration=timings["negatives"][1] - timings["negatives"][0],
            text=sections["negatives"],
        )
        neg_clip = neg_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
        clips.append(neg_clip)
        print("Creating positives section...")
        pos_title = self.create_section_title(
            "Part Two",
            "The Positives",
            duration=timings["positives_title"][1] - timings["positives_title"][0],
            image_path=images["positives"],
        )
        clips.append(pos_title)

        pos_clip = self.create_image_clip_with_zoom(
            images["positives"],
            duration=timings["positives"][1] - timings["positives"][0],
            text=sections["positives"],
        )
        pos_clip = pos_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
        clips.append(pos_clip)
        print("Creating improvements section...")
        imp_title = self.create_section_title(
            "Part Three",
            "How to Improve",
            duration=timings["improvements_title"][1]
            - timings["improvements_title"][0],
            image_path=images["improvements"],
        )
        clips.append(imp_title)

        imp_clip = self.create_image_clip_with_zoom(
            images["improvements"],
            duration=timings["improvements"][1] - timings["improvements"][0],
            text=sections["improvements"],
        )
        imp_clip = imp_clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
        clips.append(imp_clip)
        print("Concatenating clips...")
        final_video = concatenate_videoclips(clips, method="compose")
        print("Adding audio...")
        final_video = final_video.with_audio(audio)
        print("Adding subtitles...")
        # Dynamic Subtitles will be generated based on the script content
        
        # Dynamic Subtitle Generation
        subtitle_clips = []
        
        for section_name in content_sections:
            start_t, end_t = timings[section_name]
            text = sections[section_name].strip()
            if not text:
                continue
                
            # Split text into chunks (approx 7 words each for pro look)
            words = text.split()
            chunk_size = 7
            chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
            
            section_dur = end_t - start_t
            if not chunks:
                continue
                
            chunk_dur = section_dur / len(chunks)
            
            for i, chunk_text in enumerate(chunks):
                c_start = start_t + (i * chunk_dur)
                c_end = c_start + chunk_dur
                
                # Add the subtitle
                subtitle_clips.extend(
                    self.add_subtitle(chunk_text, c_start, c_end, self.video_size)
                )

        if subtitle_clips:
            final_video = CompositeVideoClip([final_video] + subtitle_clips)
        output_file = os.path.join(self.output_path, "final_montage.mp4")
        print(f"Exporting video to {output_file}...")

        final_video.write_videofile(
            output_file,
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            threads=4,
            preset="medium",
        )

        print(f"Video created successfully: {output_file}")
        return output_file


if __name__ == "__main__":
    maker = VideoMontageMaker()
    maker.create_montage()
