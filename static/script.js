let selectedFiles = [];

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const transcribeBtn = document.getElementById('transcribeBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const results = document.getElementById('results');

// Drag and drop functionality
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
});

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    for (let file of files) {
        if (isVideoFile(file)) {
            selectedFiles.push(file);
        }
    }
    updateFileList();
}

function isVideoFile(file) {
    const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 
                         'video/x-flv', 'video/x-ms-wmv', 'video/webm'];
    return allowedTypes.includes(file.type) || file.name.match(/\.(mp4|avi|mov|mkv|flv|wmv|webm)$/i);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function updateFileList() {
    fileList.innerHTML = '';
    
    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div>
                <div class="file-name">${file.name}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
            <button class="remove-btn" onclick="removeFile(${index})">Remove</button>
        `;
        fileList.appendChild(fileItem);
    });
    
    transcribeBtn.style.display = selectedFiles.length > 0 ? 'block' : 'none';
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
}

transcribeBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;
    
    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('files[]', file);
    });
    
    transcribeBtn.disabled = true;
    progressContainer.style.display = 'block';
    results.innerHTML = '';
    
    try {
        progressText.textContent = 'Uploading and processing videos...';
        progressFill.style.width = '50%';
        
        const response = await fetch('/transcribe', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Transcription failed');
        }
        
        const data = await response.json();
        progressFill.style.width = '100%';
        progressText.textContent = 'Transcription complete!';
        
        displayResults(data.results);
        
        // Reset
        selectedFiles = [];
        updateFileList();
        fileInput.value = '';
        
        setTimeout(() => {
            progressContainer.style.display = 'none';
            progressFill.style.width = '0%';
        }, 2000);
        
    } catch (error) {
        alert('Error: ' + error.message);
        progressContainer.style.display = 'none';
    } finally {
        transcribeBtn.disabled = false;
    }
});

function displayResults(resultsList) {
    results.innerHTML = '<h2>Transcription Results</h2>';
    
    resultsList.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        
        if (result.status === 'success') {
            let downloadLinks = `
                <a href="/download/${result.with_timestamps}" class="download-btn">Download with timestamps</a>
                <a href="/download/${result.without_timestamps}" class="download-btn">Download without timestamps</a>
                <a href="/download/${result.srt_file}" class="download-btn">Download SRT subtitles</a>
            `;
            
            // Add translation links if available
            if (result.translation) {
                downloadLinks += `
                    <a href="/download/${result.translation}" class="download-btn">Download English translation</a>
                    <a href="/download/${result.translation_srt}" class="download-btn">Download English SRT</a>
                `;
            }
            
            resultItem.innerHTML = `
                <div class="result-header">
                    <div class="result-filename">${result.filename}</div>
                    <div class="result-status status-success">Success (${result.language})</div>
                </div>
                <div class="result-preview">${result.transcript}</div>
                <div class="download-links">
                    ${downloadLinks}
                </div>
            `;
        } else {
            resultItem.innerHTML = `
                <div class="result-header">
                    <div class="result-filename">${result.filename}</div>
                    <div class="result-status status-error">Error</div>
                </div>
                <div class="result-preview">Error: ${result.message}</div>
            `;
        }
        
        results.appendChild(resultItem);
    });
}

// Make removeFile globally accessible
window.removeFile = removeFile;