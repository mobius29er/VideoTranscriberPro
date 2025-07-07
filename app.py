import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import whisper
from datetime import datetime
import subprocess
import tempfile
import shutil

# Add FFmpeg to PATH for this process
import sys
ffmpeg_dir = r'C:\ffmpeg-7.1.1-essentials_build\bin'
if ffmpeg_dir not in os.environ['PATH']:
    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = None # removed limit for local running large batches
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Load Whisper model (you can change to 'small', 'medium', 'large' for better accuracy)
model = whisper.load_model("medium")

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
        if (path != 'ffmpeg' and os.path.exists(path)) or path == 'ffmpeg':
            ffmpeg_cmd = path
            break
    
    if not ffmpeg_cmd:
        print("FFmpeg not found in any expected location")
        return None
    
    try:
    # Use the full path to ffmpeg
        if os.path.exists(r'C:\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe'):
            ffmpeg_cmd = r'C:\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe'
        
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
                result = model.transcribe(
                    audio_path,
                    language="en",  # Specify English for better accuracy
                    fp16=False,     # Use FP32 for CPU compatibility
                    verbose=True    # Show progress
                )
                
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
                
                # Clean up temporary files
                os.remove(video_path)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'transcript': result['text'][:200] + '...' if len(result['text']) > 200 else result['text'],
                    'with_timestamps': f"{base_filename}_with_timestamps.txt",
                    'without_timestamps': f"{base_filename}_transcript.txt"
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