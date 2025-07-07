# 🎬 VideoTranscriberPro

**VideoTranscriberPro** is a lightweight web application that allows users to upload video files and receive automatic transcriptions using OpenAI's Whisper model. With a sleek frontend, Whisper-powered backend, and support for multiple file formats, it’s the perfect tool for fast, high-quality video transcription.

![screenshot](https://your-screenshot-url-if-available)

---

## 🚀 Features

- 🎥 Upload multiple videos at once (drag & drop interface)
- 🧠 Automatic transcription with OpenAI Whisper
- 📝 Output with and without timestamps
- 🌐 Downloadable SRT subtitle support
- 📁 Local file handling for privacy and performance
- 🎨 Clean, responsive frontend UI (HTML/CSS/JS)
- 🧪 Optional English translation support (when configured)

---

## 🗂 Project Structure

VideoTranscriberPro/

├── app.py # Flask backend

├── requirements.txt # Python dependencies

├── templates/

│ └── index.html # Frontend UI

├── static/

│ ├── style.css # Styles

│ └── script.js # Frontend logic

├── uploads/ # Temporary video uploads

└── output/ # Transcription results

yaml
Copy
Edit

---

## ⚙️ Installation & Setup

### 1. Prerequisites

- **Python 3.8+**
- **FFmpeg** installed and available in your system's PATH

```bash
# Windows: Add FFmpeg to PATH after downloading from https://ffmpeg.org
# macOS:   brew install ffmpeg
# Ubuntu:  sudo apt-get install ffmpeg
2. Installation Steps
bash
Copy
Edit
# Clone the repository
git clone git@github.com:mobius29er/VideoTranscriberPro.git
cd VideoTranscriberPro

# (Recommended) Create a virtual environment
python -m venv venv
# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
Open your browser to http://localhost:5000

```

🧪 Usage
- Open the web app
- Drag & drop or select one or more videos
- Click Start Transcription
- Wait for processing (progress bar shows status)
- Download the result (with or without timestamps, SRT) (File will autogenerate also in the output folder for with, without, .srt. language, etc.)

📄 Output Files
For each uploaded video, you’ll get:

- ✅ video_transcript.txt – raw transcript (no timestamps)
- ✅ video_with_timestamps.txt – readable transcript with [HH:MM:SS - HH:MM:SS] markers
- ✅ video.srt – subtitle file
- ✅ (Optional) English translation .txt and .srt if translation is enabled

🧠 Whisper Model Options
Whisper supports several models:

Model	Size	Speed	Accuracy
tiny	~39 MB	Very Fast	Low
base	~74 MB	Fast	Moderate
small	~244 MB	Medium	Good
medium	~769 MB	Slower	Very Good
large	~1550 MB	Slowest	Best

To change the model, edit app.py:
```
model = whisper.load_model("medium")  # or "small", "large", etc.
🛠 Configuration
UPLOAD_FOLDER and OUTPUT_FOLDER: Can be changed in app.py

MAX_CONTENT_LENGTH: Controls max upload size (default: 500MB)

ALLOWED_EXTENSIONS: Adjust to accept more/less video types

Translations: Can be enabled if you add a translation module or flag
```

🧾 Example Output (with timestamps)

```
Copy
Edit
[00:00:00 - 00:00:05] Welcome to our demo on AI-powered transcription.
[00:00:05 - 00:00:10] In this video, we’ll explore how Whisper works.
```


💻 Tech Stack
- Flask – lightweight Python web framework
- Whisper – OpenAI speech recognition model
- JavaScript/CSS – frontend interactivity and styling
- FFmpeg – video to audio conversion tool


📦 Requirements
```
txt
Copy
Edit
Flask==3.0.0
openai-whisper
torch
werkzeug==3.0.1
numpy<2
Install via:

bash
Copy
Edit
pip install -r requirements.txt
```

📌 Notes
- First-time run will auto-download the Whisper model
- FFmpeg must be correctly installed for audio extraction to work
- Your machine must support the chosen Whisper model (larger models require more memory)

📣 Future Features (Planned)
- ✅ Language detection & translation toggle
- ✅ SRT subtitle preview in browser
- ⏳ GPU support via PyTorch CUDA if available
- ⏳ User authentication (multi-user support)
- ⏳ Cloud deployment template (Render, Vercel, Heroku)

🤝 Contributing

Contributions are welcome!

Please open an issue or submit a PR with any enhancements, fixes, or ideas.

📜 License

This project is licensed under the MIT License.

👤 Author

Jeremy Foxx
