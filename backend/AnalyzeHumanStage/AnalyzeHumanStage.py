import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: GEMINI_API_KEY not found in environment variables.")
    print("Please check your .env file.")
    exit(1)

# --- Helper Functions for Audio (from audioProessStage) ---
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

# --- Main Analysis Function ---
def analyze_json_with_gemini(json_file_path, output_file_path, audio_file_path):
    try:
        # Read JSON
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)

        # Configure Gemini
        genai.configure(api_key=API_KEY)
        
        # Using a model confirmed to be available
        model = genai.GenerativeModel('gemini-2.0-flash')

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

        print("Sending request to Gemini...")
        response = model.generate_content(prompt)
        analysis_text = response.text

        # Save Text
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(analysis_text)
        print(f"Analysis text saved to {output_file_path}")

        # Generate Audio (Disabled per user request)
        # text_to_audio(analysis_text, audio_file_path)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    analyze_json_with_gemini('BazookaFriedChicken.json', 'file.txt', 'analysis_audio.mp3')
