import subprocess
import os

print("Testing FFmpeg...")

# Test paths
ffmpeg_paths = [
    'ffmpeg',
    r'C:\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe',
]

for path in ffmpeg_paths:
    print(f"\nTrying: {path}")
    if path != 'ffmpeg':
        print(f"Exists: {os.path.exists(path)}")
    
    try:
        result = subprocess.run([path, '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"SUCCESS! FFmpeg works at: {path}")
            print(result.stdout.split('\n')[0])
        else:
            print(f"Failed with return code: {result.returncode}")
    except Exception as e:
        print(f"Error: {e}")

print("\nCurrent PATH:")
print(os.environ.get('PATH', 'No PATH found'))