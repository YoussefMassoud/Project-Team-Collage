from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
)
import moviepy.video.fx.all as vfx
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
        shadow_clip = ImageClip(shadow_img, duration=duration).set_position(
            lambda t: (
                self.video_size[0] // 2 - shadow_img.shape[1] // 2 + 3,
                self.video_size[1] // 2 - shadow_img.shape[0] // 2 + 3,
            )
        )

        title_clip = ImageClip(title_img, duration=duration).set_position("center")

        composite = CompositeVideoClip([bg, shadow_clip, title_clip])
        composite = vfx.fadein(composite, 0.5)
        composite = vfx.fadeout(composite, 0.5)

        return composite

    def create_section_title(self, section_title, subtitle, duration=4):
        """Create section title card with gradient background"""
        bg = self.create_gradient_background((30, 50, 80), (60, 80, 120), duration)

        main_title_img = self.create_text_image(
            section_title,
            font_size=90,
            color=(255, 215, 0),
            max_width=self.video_size[0] - 200,
        )

        main_title = ImageClip(main_title_img, duration=duration).set_position(
            ("center", self.video_size[1] // 3 - main_title_img.shape[0] // 2)
        )
        sub_title_img = self.create_text_image(
            subtitle,
            font_size=50,
            color=(255, 255, 255),
            max_width=self.video_size[0] - 400,
        )

        sub_title = ImageClip(sub_title_img, duration=duration).set_position(
            ("center", self.video_size[1] // 2 + 50)
        )

        composite = CompositeVideoClip([bg, main_title, sub_title])
        composite = vfx.fadein(composite, 0.8)
        composite = vfx.fadeout(composite, 0.8)

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
        """Create subtitle with nice background box"""
        duration = end_time - start_time
        subtitle_img = self.create_text_image(
            text,
            font_size=45,
            color=(255, 255, 255),
            bg_color=(0, 0, 0, 180), 
            max_width=video_size[0] - 250,
        )
        txt_clip = (
            ImageClip(subtitle_img, duration=duration)
            .set_position(("center", video_size[1] - 200))
            .set_start(start_time)
        )

        return [txt_clip]

    def create_image_clip_with_zoom(self, image_path, duration, text=None):
        """Create image clip with proper sizing and optional text overlay"""
        img_clip = ImageClip(image_path, duration=duration)
        img_clip = img_clip.resize(height=self.video_size[1])
        if img_clip.w > self.video_size[0]:
            img_clip = img_clip.crop(
                x_center=img_clip.w / 2,
                width=self.video_size[0],
                height=self.video_size[1],
            )
        else:
            img_clip = img_clip.set_position("center")
            bg = ColorClip(size=self.video_size, color=(0, 0, 0), duration=duration)
            img_clip = CompositeVideoClip([bg, img_clip])

        if text and text.strip():
            # Create centered text overlay
            text_img = self.create_text_image(
                text.strip(),
                font_size=60,
                color=(255, 255, 255),
                bg_color=(0, 0, 0, 160),  # Semi-transparent black background
                max_width=self.video_size[0] - 300,
                align="center",
            )
            text_clip = ImageClip(text_img, duration=duration).set_position("center")
            img_clip = CompositeVideoClip([img_clip, text_clip])

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
        timings = {
            "intro_title": (0, 3),
            "intro": (3, 17),
            "negatives_title": (17, 21),
            "negatives": (21, 41),
            "positives_title": (41, 45),
            "positives": (45, 65),
            "improvements_title": (65, 69),
            "improvements": (69, total_duration),
        }

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
        intro_clip = vfx.fadein(vfx.fadeout(intro_clip, 1), 1)
        clips.append(intro_clip)
        print("Creating negatives section...")
        neg_title = self.create_section_title(
            "Part One",
            "The Negatives",
            duration=timings["negatives_title"][1] - timings["negatives_title"][0],
        )
        clips.append(neg_title)

        neg_clip = self.create_image_clip_with_zoom(
            images["negatives"],
            duration=timings["negatives"][1] - timings["negatives"][0],
            text=sections["negatives"],
        )
        neg_clip = vfx.fadein(vfx.fadeout(neg_clip, 1), 1)
        clips.append(neg_clip)
        print("Creating positives section...")
        pos_title = self.create_section_title(
            "Part Two",
            "The Positives",
            duration=timings["positives_title"][1] - timings["positives_title"][0],
        )
        clips.append(pos_title)

        pos_clip = self.create_image_clip_with_zoom(
            images["positives"],
            duration=timings["positives"][1] - timings["positives"][0],
            text=sections["positives"],
        )
        pos_clip = vfx.fadein(vfx.fadeout(pos_clip, 1), 1)
        clips.append(pos_clip)
        print("Creating improvements section...")
        imp_title = self.create_section_title(
            "Part Three",
            "How to Improve",
            duration=timings["improvements_title"][1]
            - timings["improvements_title"][0],
        )
        clips.append(imp_title)

        imp_clip = self.create_image_clip_with_zoom(
            images["improvements"],
            duration=timings["improvements"][1] - timings["improvements"][0],
            text=sections["improvements"],
        )
        imp_clip = vfx.fadein(vfx.fadeout(imp_clip, 1), 1)
        clips.append(imp_clip)
        print("Concatenating clips...")
        final_video = concatenate_videoclips(clips, method="compose")
        print("Adding audio...")
        final_video = final_video.set_audio(audio)
        print("Adding subtitles...")
        subtitle_clips = []
        subtitles_data = [
            (3, 10, "Today we're breaking down Bazooka Fried Chicken"),
            (10, 17, "Looking at what works and what doesn't"),
            (21, 28, "No price listed created major friction"),
            (28, 35, "Over 1000 comments asking 'how much?'"),
            (35, 41, "Generic replies provided zero value"),
            (45, 52, "Strong initial interest with 1100 comments"),
            (52, 59, "Hundreds of likes and positive reactions"),
            (59, 65, "Brand was active and engaging"),
            (69, 76, "Always include price in the post"),
            (76, 83, "Replace vague replies with clear answers"),
            (83, 90, "Add clear call to action for conversions"),
        ]

        for start, end, text in subtitles_data:
            if end <= total_duration:
                subtitle_clips.extend(
                    self.add_subtitle(text, start, end, self.video_size)
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
