
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
