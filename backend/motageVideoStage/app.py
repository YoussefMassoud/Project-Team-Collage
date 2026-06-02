from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    concatenate_audioclips,
    ColorClip,
)
import moviepy.video.fx as vfx
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from gtts import gTTS
import uuid

def is_arabic(char):
    return '\u0600' <= char <= '\u06FF'

def is_english(char):
    return 'a' <= char.lower() <= 'z'

def split_text_by_language(text):
    segments = []
    if not text:
        return segments

    current_lang = None
    current_text = []

    for char in text:
        if is_arabic(char):
            char_lang = 'ar'
        elif is_english(char):
            char_lang = 'en'
        else:
            char_lang = 'neutral'

        if char_lang == 'neutral':
            current_text.append(char)
        else:
            if current_lang is None:
                current_lang = char_lang
                current_text.append(char)
            elif char_lang == current_lang:
                current_text.append(char)
            else:
                segments.append({'text': "".join(current_text), 'lang': current_lang})
                current_text = [char]
                current_lang = char_lang

    if current_text:
        lang = current_lang if current_lang else 'en'
        segments.append({'text': "".join(current_text), 'lang': lang})

    return segments


class VideoMontageMaker:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_path = os.path.join(self.base_dir, "assets")
        self.output_path = os.path.join(self.base_dir, "output")
        os.makedirs(self.output_path, exist_ok=True)

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
        total_height = int(len(lines) * line_height + 40)
        max_line_width = 0
        for line in lines:
            bbox = temp_draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            max_line_width = max(max_line_width, line_width)

        img_width = int(max_line_width + 80)
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

    def create_title_card(self, title, duration=3.0, bg_color=(20, 20, 40)):
        bg = ColorClip(size=self.video_size, color=bg_color, duration=duration)
        title_img = self.create_text_image(
            title,
            font_size=80,
            color=(255, 255, 255),
            max_width=self.video_size[0] - 200,
        )
        
        title_clip = ImageClip(title_img, duration=duration).with_position("center")

        composite = CompositeVideoClip([bg, title_clip])
        composite = composite.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.5)])

        return composite

    def create_section_title(self, section_title, subtitle, duration=4.0, image_path=None):
        if image_path and os.path.exists(image_path):
            bg_img = ImageClip(image_path, duration=duration).resized(width=self.video_size[0])
            if bg_img.h > self.video_size[1]:  # type: ignore
                bg_img = bg_img.with_effects([vfx.Crop(y_center=bg_img.h/2, height=self.video_size[1])])  # type: ignore

            dark_bg = ColorClip(size=self.video_size, color=(0, 0, 0), duration=duration)
            bg_img = bg_img.with_opacity(0.7)  # type: ignore
            bg_img = bg_img.with_position("center")  # type: ignore
            elements = [dark_bg, bg_img]
        else:
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
        duration = end_time - start_time
        subtitle_img = self.create_text_image(
            text.upper(),
            font_size=65,
            color=(255, 255, 255),
            bg_color=None,
            max_width=video_size[0] - 300,
        )

        txt_clip = (
            ImageClip(subtitle_img, duration=duration)
            .with_position("center")
            .with_start(start_time)
        )

        return [txt_clip]

    def create_image_clip_with_zoom(self, image_path, duration):
        img_clip = ImageClip(image_path, duration=duration)

        w_ratio = self.video_size[0] / img_clip.w  # type: ignore
        h_ratio = self.video_size[1] / img_clip.h  # type: ignore
        fill_ratio = max(w_ratio, h_ratio)

        img_clip = img_clip.resized(fill_ratio)
        img_clip = img_clip.with_effects([vfx.Crop(
            x_center=img_clip.w / 2,  # type: ignore
            y_center=img_clip.h / 2,  # type: ignore
            width=self.video_size[0],
            height=self.video_size[1]
        )])
        img_clip = img_clip.with_position("center")  # type: ignore

        return img_clip

    def parse_script(self, script_path):
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

    def _recorded_audio_paths(self):
        paths = {}
        for name in ["intro", "negatives", "positives", "improvements"]:
            p = os.path.join(self.assets_path, f"{name}_narration.mp3")
            if os.path.exists(p):
                paths[name] = p
        return paths

    def generate_recording_guide(self):
        script_path = os.path.join(self.assets_path, "script.txt")
        sections = self.parse_script(script_path)
        labels = {
            "intro": "Introduction",
            "negatives": "Part One: The Negatives",
            "positives": "Part Two: The Positives",
            "improvements": "Part Three: How to Improve",
        }
        print("\n" + "=" * 60)
        print("RECORDING GUIDE")
        print("=" * 60)
        print("Record 4 separate MP3 files and place them in 'assets/':")
        print()
        for name in ["intro", "negatives", "positives", "improvements"]:
            text = sections.get(name, "").strip()
            if not text:
                continue
            filename = f"{name}_narration.mp3"
            print(f"  File: {filename}")
            print(f"  Say:  {labels[name]}. {text}")
            print(f"       (speak naturally, include the section title)")
            print()
        print("The video timing will match your recording exactly.")
        print("No gTTS will be used. No sync delays.")
        print("=" * 60)

    def create_montage(self, recorded_mode=False):
        print("Starting video creation...")
        script_path = os.path.join(self.assets_path, "script.txt")

        images = {
            "intro": os.path.join(self.assets_path, "intro.png"),
            "negatives": os.path.join(self.assets_path, "negative.png"),
            "positives": os.path.join(self.assets_path, "positive.png"),
            "improvements": os.path.join(self.assets_path, "How to improved.png"),
        }
        sections = self.parse_script(script_path)
        content_sections = ["intro", "negatives", "positives", "improvements"]

        recorded_audio = self._recorded_audio_paths()
        has_all_recorded = len(recorded_audio) == len(content_sections)
        use_recorded = recorded_mode and has_all_recorded

        if recorded_mode and not has_all_recorded:
            missing = [s for s in content_sections if s not in recorded_audio]
            print(f"WARNING: Recorded mode but missing: {missing}")
            self.generate_recording_guide()

        if use_recorded:
            print("RECORDED MODE: using your voice narration")
        else:
            print("TTS MODE: generating synthetic speech")

        subtitle_clips = []
        audio_clips = []
        temp_audio_files = []

        # Phase 1: compute all timings and collect audio
        section_audios = {}
        section_durations = {}
        section_title_durations = {}
        section_titles = {
            "intro": "Introduction",
            "negatives": "Part One: The Negatives",
            "positives": "Part Two: The Positives",
            "improvements": "Part Three: How to Improve",
        }
        t = 0.0

        for section_name in content_sections:
            text = sections[section_name].strip()
            if not text:
                section_durations[section_name] = 0.1
                section_audios[section_name] = None
                t += 0.1
                continue

            if use_recorded:
                ac = AudioFileClip(recorded_audio[section_name])
                d = ac.duration
                if d is None:
                    print(f"WARNING: Could not read duration from {recorded_audio[section_name]}, using 3.0s fallback")
                    d = 3.0
                section_audios[section_name] = ac
                section_durations[section_name] = d
                audio_clips.append(ac)

                subtitle_text = f"{section_titles[section_name]}\n{text}"
                subtitle_clips.extend(
                    self.add_subtitle(subtitle_text, t, t + d, self.video_size)
                )
                t += d
            else:
                # --- Generate spoken audio for the section title ---
                section_title_audio_text = section_titles[section_name]
                if section_name == "intro":
                    section_title_audio_text = "Bazooka Fried Chicken Social Media Analysis"
                title_segments = split_text_by_language(section_title_audio_text)
                title_chunk_clips = []
                for seg in title_segments:
                    if not seg['text'].strip():
                        continue
                    try:
                        tts = gTTS(text=seg['text'], lang=seg['lang'])
                        tmp = os.path.join(self.output_path, f"temp_title_{uuid.uuid4().hex}.mp3")
                        tts.save(tmp)
                        temp_audio_files.append(tmp)
                        title_chunk_clips.append(AudioFileClip(tmp))
                    except Exception as e:
                        print(f"Error generating title audio: {e}")
                if title_chunk_clips:
                    title_audio = concatenate_audioclips(title_chunk_clips) if len(title_chunk_clips) > 1 else title_chunk_clips[0]
                    title_dur = title_audio.duration
                    if title_dur is None:
                        title_dur = len(section_title_audio_text.split()) * 0.3
                    audio_clips.append(title_audio)
                    section_title_durations[section_name] = title_dur
                    t += title_dur
                else:
                    section_title_durations[section_name] = 1.4

                # --- Content chunks ---
                words = text.split()
                chunk_size = 7
                chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
                section_start = t
                for chunk_text in chunks:
                    if not chunk_text.strip():
                        continue
                    segments = split_text_by_language(chunk_text)
                    chunk_clips = []
                    for seg in segments:
                        if not seg['text'].strip():
                            continue
                        try:
                            tts = gTTS(text=seg['text'], lang=seg['lang'])
                            tmp = os.path.join(self.output_path, f"temp_seg_{uuid.uuid4().hex}.mp3")
                            tts.save(tmp)
                            temp_audio_files.append(tmp)
                            chunk_clips.append(AudioFileClip(tmp))
                        except Exception as e:
                            print(f"Error generating audio for segment: {e}")
                    if not chunk_clips:
                        continue
                    chunk_audio = concatenate_audioclips(chunk_clips) if len(chunk_clips) > 1 else chunk_clips[0]
                    audio_clips.append(chunk_audio)
                    d = chunk_audio.duration
                    if d is None:
                        d = len(chunk_text.split()) * 0.25
                    subtitle_clips.extend(self.add_subtitle(chunk_text, t, t + d, self.video_size))
                    t += d
                section_durations[section_name] = t - section_start
                section_audios[section_name] = None

        final_audio = concatenate_audioclips(audio_clips) if audio_clips else None

        # Phase 2: build video clips
        clips = []
        for section_name in content_sections:
            text = sections[section_name].strip()
            if not text:
                continue

            dur = section_durations.get(section_name, 1.0)

            if use_recorded:
                # No title cards; narration includes the title
                clip = self.create_image_clip_with_zoom(images[section_name], dur)
                clip = clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
                clips.append(clip)
            else:
                # Title card + content image
                # Title card duration matches the spoken title audio
                title_dur = section_title_durations.get(section_name, 1.4)
                if section_name == "intro":
                    card = self.create_title_card("Bazooka Fried Chicken Social Media Analysis", duration=title_dur)
                    clips.append(card)
                else:
                    title_map = {
                        "negatives": ("Part One", "The Negatives"),
                        "positives": ("Part Two", "The Positives"),
                        "improvements": ("Part Three", "How to Improve"),
                    }
                    title_text, sub_text = title_map[section_name]
                    card = self.create_section_title(title_text, sub_text, duration=title_dur, image_path=images[section_name])
                    clips.append(card)
                img = self.create_image_clip_with_zoom(images[section_name], dur)
                img = img.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
                clips.append(img)

        print("Concatenating clips...")
        final_video = concatenate_videoclips(clips, method="compose")

        if final_audio:
            print("Adding audio...")
            final_video = final_video.with_audio(final_audio)

        print("Adding subtitles...")
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

        for f in temp_audio_files:
            try:
                os.remove(f)
            except:
                pass

        print(f"Video created successfully: {output_file}")
        return output_file


if __name__ == "__main__":
    recorded_mode = "--recorded" in sys.argv

    if "--guide" in sys.argv:
        maker = VideoMontageMaker()
        maker.generate_recording_guide()
        sys.exit(0)

    maker = VideoMontageMaker()
    if recorded_mode:
        print("RECORDED MODE from command line")
    maker.create_montage(recorded_mode=recorded_mode)
