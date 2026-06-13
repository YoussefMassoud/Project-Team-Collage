import os
import json
from groq import Groq
from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("Error: GROQ_API_KEY not found in environment variables.")
    print("Get a free key at: https://console.groq.com/keys")
    exit(1)

client = Groq(api_key=API_KEY)

def is_arabic(char):
    return '؀' <= char <= 'ۿ'

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

def text_to_audio(text, output_path):
    print("Generating audio...")
    segments = split_text_by_language(text)
    combined_audio = BytesIO()

    for i, seg in enumerate(segments):
        seg_text = seg['text']
        seg_lang = seg['lang']

        if not seg_text.strip():
            continue

        try:
            tts = gTTS(text=seg_text, lang=seg_lang)
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            combined_audio.write(fp.read())
        except Exception as e:
            print(f"Error processing audio segment {i}: {e}")

    try:
        with open(output_path, "wb") as f:
            f.write(combined_audio.getvalue())
        print(f"Audio saved to {output_path}")
    except Exception as e:
        print(f"Error saving audio file: {e}")

def analyze_json_with_groq(json_file_path, output_file_path, audio_file_path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        json_str = json.dumps(data, indent=2, ensure_ascii=False)

        prompt = f"""
        Act as a social media analyst. Analyze the following JSON data.
        Provide a detailed human-like analysis.
        You MUST structure your response with exactly these three section headers (include the "Part" prefixes):

        Part One: The Negatives
        [Describe negative aspects, friction points, or complaints here]

        Part Two: The Positives
        [Describe positive aspects, high engagement, or good things here]

        Part Three: How to Improve
        [Provide actionable advice and suggestions here]

        Data:
        {json_str}
        """

        print("Sending request to Groq (Llama 3)...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7,
        )
        analysis_text = response.choices[0].message.content or ""

        post_author = data.get("post_author", "Client")
        intro = f"Hello {post_author}, in this video we will summarize your post data in three parts.\n\n"
        full_analysis = intro + analysis_text

        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(full_analysis)
        print(f"Analysis text saved to {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    analyze_json_with_groq('BazookaFriedChicken.json', 'file.txt', 'analysis_audio.mp3')
