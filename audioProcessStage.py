import os
from gtts import gTTS
from io import BytesIO

def is_arabic(char):
    return '\u0600' <= char <= '\u06FF'

def is_english(char):
    return 'a' <= char.lower() <= 'z'

def split_text_by_language(text):
    segments = []
    if not text:
        return segments

    current_lang = None  # 'ar' or 'en'
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
                # Switch detected
                # Save previous segment
                segments.append({'text': "".join(current_text), 'lang': current_lang})
                # Start new
                current_text = [char]
                current_lang = char_lang

    if current_text:
        # Default to 'en' if still None (e.g. all numbers), or keep current
        lang = current_lang if current_lang else 'en'
        segments.append({'text': "".join(current_text), 'lang': lang})

    return segments

def process_tts(input_file, output_folder):
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    if not text.strip():
        print("File is empty.")
        return

    segments = split_text_by_language(text)
    combined_audio = BytesIO()

    print(f"Found {len(segments)} segments.")

    for i, seg in enumerate(segments):
        seg_text = seg['text']
        seg_lang = seg['lang']
        
        # Skip empty or whitespace-only segments if they don't add value, 
        # but sometimes pauses are good. gTTS might fail on empty.
        if not seg_text.strip():
            continue

        print(f"Processing segment {i+1}/{len(segments)} ({seg_lang}): {seg_text[:30]}...")
        
        try:
            tts = gTTS(text=seg_text, lang=seg_lang)
            # Write to memory
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            combined_audio.write(fp.read())
        except Exception as e:
            print(f"Error processing segment {i+1}: {e}")

    output_path = os.path.join(output_folder, "output.mp3")
    try:
        with open(output_path, "wb") as f:
            f.write(combined_audio.getvalue())
        print(f"Successfully saved combined audio to {output_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    process_tts("file.txt", "audio")
