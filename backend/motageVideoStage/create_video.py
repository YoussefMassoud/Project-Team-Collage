"""
Video Montage Creator
This script creates a professional video montage from images, audio, and script.

Features:
- Intro title card
- 4 main sections with title cards
- Smooth transitions (fade in/out)
- Styled subtitles with semi-transparent backgrounds
- Gradient backgrounds for section titles
- Professional fonts and styling

Usage:
    python app.py

Output:
    output/final_montage.mp4
"""

from app import VideoMontageMaker

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 BAZOOKA FRIED CHICKEN - VIDEO MONTAGE CREATOR")
    print("=" * 60)
    print()

    maker = VideoMontageMaker()

    try:
        output_file = maker.create_montage()
        print()
        print("=" * 60)
        print(f"✅ SUCCESS! Video saved to: {output_file}")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERROR: {str(e)}")
        print("=" * 60)
        raise
