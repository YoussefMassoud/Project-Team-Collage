import sys
from app import VideoMontageMaker

if __name__ == "__main__":
    recorded_mode = "--recorded" in sys.argv

    print("=" * 60)
    print("VIDEO MONTAGE CREATOR")
    print("=" * 60)
    if recorded_mode:
        print("Mode: RECORDED (using your voice narration)")
    else:
        print("Mode: TTS (synthetic speech)")
    print()

    maker = VideoMontageMaker()

    if "--guide" in sys.argv:
        maker.generate_recording_guide()
        sys.exit(0)

    try:
        output_file = maker.create_montage(recorded_mode=recorded_mode)
        print()
        print("=" * 60)
        print(f"SUCCESS! Video saved to: {output_file}")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"ERROR: {str(e)}")
        print("=" * 60)
        raise
