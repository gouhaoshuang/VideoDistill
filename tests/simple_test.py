# -*- coding: utf-8 -*-
"""
VideoDistill Simple Test - No Emojis
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ["PYTHONIOENCODING"] = "utf-8"

from src.gemini_client import GeminiClient


def test_api():
    """Test API connection"""
    print("=" * 60)
    print("VideoDistill API Test")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyAAamFsC_TahLyPPlK5gnZF_m1bFkaY0m4")

    try:
        print("\n[1/2] Initializing Gemini client...")
        client = GeminiClient(api_key=api_key)
        print("[OK] Client initialized")

        print("\n[2/2] Testing text generation...")
        response = client.generate_content(
            "Please introduce Gemini AI in one sentence.",
            temperature=0.7
        )
        print("[OK] API Response:")
        print(f"     {response[:200]}...")

        print("\n" + "=" * 60)
        print("Test PASSED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[FAILED] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_video():
    """Test video note generation"""
    print("=" * 60)
    print("VideoDistill Video Test")
    print("=" * 60)

    video_path = r"C:\Users\tianyi\Downloads\Claude_Code+Tmux,并行跑Agent军团.mp4"
    api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyAAamFsC_TahLyPPlK5gnZF_m1bFkaY0m4")

    if not os.path.exists(video_path):
        print(f"\n[ERROR] Video file not found: {video_path}")
        return False

    print(f"\n[Video] {os.path.basename(video_path)}")
    print(f"[Size] {os.path.getsize(video_path) / 1024 / 1024:.2f} MB")

    # Create temp copy with ASCII name to avoid encoding issues
    import shutil
    temp_dir = Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    temp_video_path = temp_dir / "test_video.mp4"

    print(f"\n[Prep] Creating temp copy...")
    shutil.copy(video_path, temp_video_path)
    print(f"[OK] Temp copy: {temp_video_path}")

    try:
        from src.note_generator import NoteGenerator

        print("\n[1/5] Initializing client...")
        client = GeminiClient(api_key=api_key)
        print("[OK]")

        print("\n[2/5] Uploading video...")
        video_file = client.upload_video(str(temp_video_path))
        print(f"[OK] File: {video_file.name}")

        print("\n[3/5] Generating notes...")
        generator = NoteGenerator(client)

        def progress(current, total, msg):
            pct = current / total * 100
            print(f"      [{pct:.0f}%] {msg}")

        notes = generator.generate_all_notes(video_file, progress_callback=progress)
        print("[OK] Notes generated")

        print("\n[4/5] Saving notes...")
        output_dir = Path(__file__).parent.parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "test_notes.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(notes)
        print(f"[OK] Saved to: {output_path}")

        print("\n[Preview] First 300 chars:")
        print("-" * 60)
        print(notes[:300] + "..." if len(notes) > 300 else notes)
        print("-" * 60)

        print("\n[5/5] Cleanup...")
        client.delete_file(video_file.name)
        print("[OK] Deleted uploaded file")
        os.remove(temp_video_path)
        print("[OK] Deleted temp copy")

        print("\n" + "=" * 60)
        print("Test PASSED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[FAILED] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Cleanup temp file on error
        try:
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
        except:
            pass
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--test", choices=["api", "video"], default="api")
    args = parser.parse_args()

    if args.test == "api":
        success = test_api()
    else:
        success = test_video()

    sys.exit(0 if success else 1)
