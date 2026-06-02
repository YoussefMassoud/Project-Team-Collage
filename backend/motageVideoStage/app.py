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

        self.post_author = "Bazooka Fried Chicken"
        json_path = os.path.join(self.base_dir, "..", "AnalyzeHumanStage", "BazookaFriedChicken.json")
        json_path = os.path.normpath(json_path)
        if os.path.exists(json_path):
            try:
                import json
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "post_author" in data:
                    self.post_author = data["post_author"]
            except Exception:
                pass

    def load_best_font(self, font_size, bold=False):
        """Try modern system fonts in priority order, fall back gracefully."""
        if bold:
            candidates = [
                "bahnschrift.ttf",
                "segoeuib.ttf",
                "calibrib.ttf",
                "Candarab.ttf",
                "trebucbd.ttf",
                "arialbd.ttf",
                "arial.ttf",
            ]
        else:
            candidates = [
                "bahnschrift.ttf",
                "segoeui.ttf",
                "calibri.ttf",
                "Candara.ttf",
                "trebuc.ttf",
                "arial.ttf",
            ]
        for name in candidates:
            try:
                return ImageFont.truetype(name, font_size)
            except (OSError, IOError):
                continue
        return ImageFont.load_default()

    def create_text_image(
        self,
        text,
        font_size,
        color=(255, 255, 255),
        bg_color=None,
        max_width=1600,
        align="center",
        bold=False,
        shadow=True,
    ):
        font = self.load_best_font(font_size, bold=bold)
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
        shadow_offset = max(2, font_size // 30)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]

            if align == "center":
                x_offset = (img_width - line_width) // 2
            elif align == "right":
                x_offset = img_width - line_width - 20
            else:
                x_offset = 20

            if shadow:
                draw.text((x_offset + shadow_offset, y_offset + shadow_offset), line, font=font, fill=(0, 0, 0, 160))
            draw.text((x_offset, y_offset), line, font=font, fill=color)
            y_offset += line_height

        return np.array(img)

    def create_intro_card(self, duration=4.0):
        w, h = self.video_size
        dur = duration

        # ─── Animated gradient background ───
        n_steps = 60
        step_dur = dur / n_steps
        clips = []
        for s in range(n_steps):
            t = s / n_steps
            angle = t * np.pi * 2
            c1 = (15, 5, 35)
            c2 = (55, 15, 80)
            c3 = (100, 30, 130)
            c4 = (124, 58, 180)

            img = Image.new("RGBA", (w, h))
            draw = ImageDraw.Draw(img)
            for y in range(h):
                p = y / h
                wave = np.sin(angle + p * np.pi * 3) * 0.15
                mix = p + wave
                r = int(c1[0] * (1-mix) + c2[0] * mix) if mix < 0.5 else int(c2[0] * (2-2*mix) + c3[0] * (2*mix-1))
                g = int(c1[1] * (1-mix) + c2[1] * mix) if mix < 0.5 else int(c2[1] * (2-2*mix) + c3[1] * (2*mix-1))
                b = int(c1[2] * (1-mix) + c2[2] * mix) if mix < 0.5 else int(c2[2] * (2-2*mix) + c3[2] * (2*mix-1))
                draw.line([(0, y), (w, y)], fill=(r, g, b))

            # ─── Grid overlay ───
            grid_color = (80, 50, 120, 12)
            for y in range(0, h, 70):
                draw.line([(0, y), (w, y)], fill=grid_color)
            for x in range(0, w, 70):
                draw.line([(x, 0), (x, h)], fill=grid_color)

            # ─── Scan line glow ───
            scan_y = int(((t * 1.2) % 1.0) * h)
            for dy in range(-3, 4):
                sy = scan_y + dy
                if 0 <= sy < h:
                    alpha = max(0, 60 - abs(dy) * 15)
                    draw.line([(0, sy), (w, sy)], fill=(180, 130, 255, alpha))

            clip = ImageClip(np.array(img), duration=step_dur).with_start(s * step_dur)
            clips.append(clip)

        bg = concatenate_videoclips(clips, method="compose")

        # ─── Vignette overlay ───
        yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
        dx = (xx - w / 2) / (w / 2)
        dy = (yy - h / 2) / (h / 2)
        dist = np.sqrt(dx * dx + dy * dy)
        vig_alpha = np.clip((dist - 0.4) * 300, 0, 200).astype(np.uint8)
        vig_array = np.zeros((h, w, 4), dtype=np.uint8)
        vig_array[:, :, 3] = vig_alpha
        vignette_clip = ImageClip(vig_array, duration=dur)

        # ─── Corner brackets ───
        def make_corner_bracket(cx, cy, flip_x, flip_y):
            bracket_size = 60
            bracket_thick = 4
            bracket_gap = 30
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            mx = 1 if flip_x else -1
            my = 1 if flip_y else -1
            x0 = cx + mx * bracket_gap
            y0 = cy + my * bracket_gap
            x1 = cx + mx * (bracket_gap + bracket_size)
            y1 = cy + my * (bracket_gap + bracket_size)
            color = (180, 130, 255, 180)
            d.line([(x0, y0), (x1, y0)], fill=color, width=bracket_thick)
            d.line([(x0, y0), (x0, y1)], fill=color, width=bracket_thick)
            return ImageClip(np.array(img), duration=dur)

        corners = ["tl", "tr", "bl", "br"]
        corner_positions = {
            "tl": (80, 80, False, False),
            "tr": (w-80, 80, True, False),
            "bl": (80, h-80, False, True),
            "br": (w-80, h-80, True, True),
        }
        corner_clips = []
        for pos in corners:
            cx, cy, fx, fy = corner_positions[pos]
            corner_clips.append(make_corner_bracket(cx, cy, fx, fy))

        # ─── Author name with glow ───
        author_font = self.load_best_font(120, bold=True)
        author_text = self.post_author.upper()

        def make_author_layer():
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            temp = Image.new("RGBA", (1, 1))
            td = ImageDraw.Draw(temp)
            bbox = td.textbbox((0, 0), author_text, font=author_font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            ax = (w - tw) // 2
            ay = h // 2 - th // 2 - 40

            # glow layers
            for radius in range(8, 0, -1):
                glow_color = (124, 58, 237, 40 - radius * 4)
                d.text((ax + 0, ay + 0), author_text, font=author_font, fill=glow_color,
                       stroke_width=radius+2, stroke_fill=(124, 58, 237, 20-radius*2))
            # main text
            d.text((ax, ay), author_text, font=author_font, fill=(255, 255, 255))
            return ImageClip(np.array(img), duration=dur)

        author_clip = make_author_layer()

        # ─── Subtitle ───
        sub_img = self.create_text_image(
            "SOCIAL MEDIA ANALYSIS",
            font_size=45,
            color=(255, 215, 0),
            max_width=w - 300,
            bold=True,
        )
        sub_clip = ImageClip(sub_img, duration=dur).with_position(("center", h // 2 + 50))

        # ─── Accent bar ───
        bar = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bar_d = ImageDraw.Draw(bar)
        bar_color = (255, 215, 0, 220)
        bar_d.rectangle([(w//2 - 120, h//2 + 95), (w//2 + 120, h//2 + 100)], fill=bar_color)
        bar_clip = ImageClip(np.array(bar), duration=dur)

        # ─── Sensor ring animation ───
        ring_clips = []
        for phase in range(3):
            start_offset = phase * 0.3
            ring_dur = dur - start_offset
            if ring_dur <= 0:
                continue
            r_steps = max(1, int(ring_dur / 0.05))
            step_d = ring_dur / r_steps
            for rs in range(r_steps):
                rp = rs / r_steps
                ring_r = int(50 + rp * 500)
                ring_alpha = int(max(0, 120 * (1 - rp)))
                ring = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                rd = ImageDraw.Draw(ring)
                rd.ellipse(
                    [(w//2 - ring_r, h//2 - ring_r), (w//2 + ring_r, h//2 + ring_r)],
                    outline=(124, 58, 237, ring_alpha),
                    width=2,
                )
                rc = ImageClip(np.array(ring), duration=step_d)
                rc = rc.with_start(start_offset + rs * step_d)
                ring_clips.append(rc)

        elements = [bg, vignette_clip, author_clip, sub_clip, bar_clip] + corner_clips + ring_clips
        composite = CompositeVideoClip(elements)
        composite = composite.with_effects([vfx.FadeIn(0.5), vfx.FadeOut(0.8)])

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
            bold=True,
        )

        main_title = ImageClip(main_title_img, duration=duration).with_position(
            ("center", self.video_size[1] // 3 - main_title_img.shape[0] // 2)
        )

        sub_title_img = self.create_text_image(
            subtitle,
            font_size=50,
            color=(255, 255, 255),
            max_width=self.video_size[0] - 400,
            bold=True,
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
            font_size=60,
            color=(255, 255, 255),
            bg_color=None,
            max_width=video_size[0] - 300,
            bold=True,
        )

        txt_clip = (
            ImageClip(subtitle_img, duration=duration)
            .with_position("center")
            .with_start(start_time)
        )

        return [txt_clip]

    def add_section_label_overlay(self, label, start_time, duration, video_size):
        bar_height = 60
        bar = np.zeros((bar_height, video_size[0], 4), dtype=np.uint8)
        bar[:, :, :3] = (10, 10, 30)
        bar[:, :, 3] = 200

        overlay_img = Image.new("RGBA", (video_size[0], bar_height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay_img)
        font = self.load_best_font(28, bold=True)
        label_text = label.upper()
        bbox = overlay_draw.textbbox((0, 0), label_text, font=font)
        text_x = 30
        text_y = (bar_height - (bbox[3] - bbox[1])) // 2
        overlay_draw.text((text_x + 1, text_y + 1), label_text, font=font, fill=(0, 0, 0, 180))
        overlay_draw.text((text_x, text_y), label_text, font=font, fill=(180, 180, 255))

        overlay_np = np.array(overlay_img)
        bar_with_text = bar.copy()
        text_mask = overlay_np[:, :, 3] > 0
        bar_with_text[text_mask] = overlay_np[text_mask]

        bar_clip = (
            ImageClip(bar_with_text, duration=duration)
            .with_position(("center", video_size[1] - bar_height))
            .with_start(start_time)
        )

        accent_line = np.zeros((3, video_size[0], 4), dtype=np.uint8)
        accent_line[:, :, :3] = (124, 58, 237)
        accent_line[:, :, 3] = 255
        line_clip = (
            ImageClip(accent_line, duration=duration)
            .with_position(("center", video_size[1] - bar_height - 3))
            .with_start(start_time)
        )

        return [bar_clip, line_clip]

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
        label_overlay_clips = []

        # Phase 1: compute all timings and collect audio
        section_audios = {}
        section_durations = {}
        section_title_durations = {}
        section_titles = {
            "intro": self.post_author,
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
                label_overlay_clips.extend(
                    self.add_section_label_overlay(section_titles[section_name], t, d, self.video_size)
                )
                t += d
            else:
                # --- Generate spoken audio for the section title ---
                section_title_audio_text = section_titles[section_name]
                if section_name == "intro":
                    section_title_audio_text = f"{self.post_author} Social Media Analysis"
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
                label_overlay_clips.extend(
                    self.add_section_label_overlay(section_titles[section_name], section_start, t - section_start, self.video_size)
                )

        final_audio = concatenate_audioclips(audio_clips) if audio_clips else None

        # Phase 2: build video clips
        clips = []
        for section_name in content_sections:
            text = sections[section_name].strip()
            if not text:
                continue

            dur = section_durations.get(section_name, 1.0)

            if use_recorded:
                clip = self.create_image_clip_with_zoom(images[section_name], dur)
                clip = clip.with_effects([vfx.FadeIn(1), vfx.FadeOut(1)])
                clips.append(clip)
            else:
                title_dur = section_title_durations.get(section_name, 1.4)
                if section_name == "intro":
                    card = self.create_intro_card(duration=title_dur)
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
        if subtitle_clips or label_overlay_clips:
            final_video = CompositeVideoClip([final_video] + subtitle_clips + label_overlay_clips)

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
