import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import whisper
from datetime import datetime
import subprocess
import tempfile
import shutil
import torch

print("CUDA available:", torch.cuda.is_available())
print("CUDA device name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] =None #500 * 1024 * 1024  500MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Load Whisper model (you can change to 'small', 'medium', 'large' for better accuracy)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = whisper.load_model("medium").to(device)
print("Running Whisper on device:", model.device)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_audio(video_path):
    """Extract audio from video file using ffmpeg"""
    audio_path = video_path.rsplit('.', 1)[0] + '.wav'
    
    # Try different FFmpeg locations
    ffmpeg_paths = [
        'ffmpeg',  # System PATH
        r'C:\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe',  # Your installation
        r'C:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe',  # Alternative location
        r'C:\ffmpeg-7.0-essentials_build\bin\ffmpeg.exe',  # Different version
    ]
    
    ffmpeg_cmd = None
    for path in ffmpeg_paths:
        if path == 'ffmpeg':
            ffmpeg_in_path = shutil.which('ffmpeg')
            if ffmpeg_in_path:
                ffmpeg_cmd = ffmpeg_in_path
                break
        elif os.path.exists(path):
            ffmpeg_cmd = path
            break
    
    if not ffmpeg_cmd:
        print("FFmpeg not found in any expected location")
        return None
    
    try:
        # Try to run ffmpeg
        result = subprocess.run([
            ffmpeg_cmd, '-i', video_path, '-ab', '160k', '-ac', '2', '-ar', '44100', 
            '-vn', audio_path, '-y'
        ], check=True, capture_output=True, text=True)
        print(f"Audio extracted successfully using {ffmpeg_cmd}")
        return audio_path
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg and add it to your system PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        print(f"FFmpeg stderr: {e.stderr}")
        return None

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_timestamp_srt(seconds):
    """Convert seconds to SRT format HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    whole_seconds = int(secs)
    milliseconds = int((secs - whole_seconds) * 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{milliseconds:03d}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    results = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)
            
            try:
                # Extract audio from video
                print(f"Extracting audio from {filename}")
                audio_path = extract_audio(video_path)
                if not audio_path:
                    results.append({
                        'filename': filename,
                        'status': 'error',
                        'message': 'Failed to extract audio from video - check if FFmpeg is installed'
                    })
                    continue
                
                # Transcribe audio
                print(f"Transcribing audio for {filename}")
                result = model.transcribe(audio_path)
                detected_language = result.get('language', 'unknown')
                
                # Save transcripts
                base_filename = os.path.splitext(filename)[0]
                
                # Save transcript with timestamps
                with_timestamps_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_filename}_with_timestamps.txt")
                with open(with_timestamps_path, 'w', encoding='utf-8') as f:
                    for segment in result['segments']:
                        start_time = format_timestamp(segment['start'])
                        end_time = format_timestamp(segment['end'])
                        text = segment['text'].strip()
                        f.write(f"[{start_time} - {end_time}] {text}\n")
                
                # Save transcript without timestamps
                without_timestamps_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_filename}_transcript.txt")
                with open(without_timestamps_path, 'w', encoding='utf-8') as f:
                    f.write(result['text'].strip())

                # Save SRT file
                srt_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_filename}.srt")
                with open(srt_path, 'w', encoding='utf-8') as srt_file:
                    for i, segment in enumerate(result['segments'], start=1):
                        start_time = format_timestamp_srt(segment['start'])
                        end_time = format_timestamp_srt(segment['end'])
                        text = segment['text'].strip()
                        srt_file.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")

                # Clean up temporary files
                os.remove(video_path)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'transcript': result['text'][:200] + '...' if len(result['text']) > 200 else result['text'],
                    'language': detected_language,
                    'with_timestamps': f"{base_filename}_with_timestamps.txt",
                    'without_timestamps': f"{base_filename}_transcript.txt",
                    'srt_file': f"{base_filename}.srt",
                    'translation': None,
                    'translation_srt': None
                })
                
            except Exception as e:
                import traceback
                print(f"Error processing {filename}: {str(e)}")
                print(traceback.format_exc())
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'message': str(e)
                })
                # Clean up on error
                if os.path.exists(video_path):
                    os.remove(video_path)
    
    return jsonify({'results': results})

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_file(
            os.path.join(app.config['OUTPUT_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)