document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const fileInfo = document.getElementById('file-info');
    const filenameDisplay = document.getElementById('filename-display');
    const removeFileBtn = document.getElementById('remove-file');
    const dropZoneContent = document.querySelector('.drop-zone-content');
    const uploadBtn = document.getElementById('upload-btn');
    const expirySelect = document.getElementById('expiry-select');
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const resultSection = document.getElementById('result-section');
    const shareUrlInput = document.getElementById('share-url');
    const copyBtn = document.getElementById('copy-btn');
    const expiryDisplay = document.getElementById('expiry-display');
    const newUploadBtn = document.getElementById('new-upload-btn');
    const themeToggle = document.getElementById('theme-toggle');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const whatsappBtn = document.getElementById('whatsapp-btn');
    const emailBtn = document.getElementById('email-btn');
    const historySection = document.getElementById('history-section');
    const historyList = document.getElementById('history-list');
    const clearHistoryBtn = document.getElementById('clear-history');

    let selectedFiles = [];

    // --- Theme Logic ---
    const loadTheme = () => {
        const theme = localStorage.getItem('theme') || 'dark';
        if (theme === 'light') {
            document.body.classList.add('light-theme');
            themeToggle.querySelector('i').classList.replace('fa-moon', 'fa-sun');
        }
    };

    themeToggle.addEventListener('click', () => {
        const isLight = document.body.classList.toggle('light-theme');
        const icon = themeToggle.querySelector('i');
        if (isLight) {
            icon.classList.replace('fa-moon', 'fa-sun');
            localStorage.setItem('theme', 'light');
        } else {
            icon.classList.replace('fa-sun', 'fa-moon');
            localStorage.setItem('theme', 'dark');
        }
    });

    loadTheme();

    // --- History Logic ---
    const getHistory = () => JSON.parse(localStorage.getItem('share_history') || '[]');
    
    const saveToHistory = (item) => {
        const history = getHistory();
        history.unshift(item); // Add to beginning
        localStorage.setItem('share_history', JSON.stringify(history.slice(0, 10))); // Keep last 10
        renderHistory();
    };

    const renderHistory = () => {
        const history = getHistory();
        if (history.length === 0) {
            historySection.classList.add('hidden');
            return;
        }

        historySection.classList.remove('hidden');
        historyList.innerHTML = '';

        history.forEach((item, index) => {
            const expiry = new Date(item.expires_at);
            const isExpired = expiry < new Date();

            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            if (isExpired) historyItem.style.opacity = '0.5';

            historyItem.innerHTML = `
                <div class="history-meta">
                    <span class="history-filename">${item.name}</span>
                    <span class="history-expiry">${isExpired ? 'Expired' : 'Expires ' + expiry.toLocaleString()}</span>
                </div>
                <div class="history-actions">
                    <div class="history-link-box">
                        <span>${item.url}</span>
                    </div>
                    <button class="icon-btn copy-history-btn" data-url="${item.url}" title="Copy Link">
                        <i class="far fa-copy"></i>
                    </button>
                </div>
            `;
            historyList.appendChild(historyItem);
        });

        // Add copy listeners
        historyList.querySelectorAll('.copy-history-btn').forEach(btn => {
            btn.onclick = () => {
                const url = btn.getAttribute('data-url');
                navigator.clipboard.writeText(url);
                showToast('Link copied from history!', 'success');
            };
        });
    };

    clearHistoryBtn.addEventListener('click', () => {
        if (confirm('Clear all sharing history?')) {
            localStorage.removeItem('share_history');
            renderHistory();
        }
    });

    renderHistory();

    // --- Drag and Drop Handlers ---
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'));
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'));
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        handleFileSelect(Array.from(files));
    });

    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        handleFileSelect(Array.from(e.target.files));
    });

    function handleFileSelect(files) {
        if (files.length === 0) return;
        
        // Limit to 5 files
        if (files.length > 5) {
            showToast('Only 5 files allowed at once!', 'error');
            return;
        }

        // Total size limit check (approx 500MB)
        const totalSize = files.reduce((acc, f) => acc + f.size, 0);
        if (totalSize > 500 * 1024 * 1024) {
            showToast('Total size exceeds 500MB!', 'error');
            return;
        }

        selectedFiles = files;
        renderFileList();
        
        dropZoneContent.classList.add('hidden');
        fileList.classList.remove('hidden');
        uploadBtn.disabled = false;
        resultSection.classList.add('hidden');
    }

    function renderFileList() {
        fileList.innerHTML = '';
        selectedFiles.forEach((file, index) => {
            const item = document.createElement('div');
            item.className = 'file-item';
            item.innerHTML = `
                <i class="fas fa-file"></i>
                <div class="file-name-text">${file.name}</div>
                <div style="font-size: 0.7rem; color: var(--text-muted); margin-right: 10px;">${(file.size / 1024).toFixed(1)} KB</div>
                <button class="remove-single-file" data-index="${index}" title="Remove this file">
                    <i class="fas fa-times"></i>
                </button>
            `;
            fileList.appendChild(item);
        });

        // Add event listeners to individual remove buttons
        document.querySelectorAll('.remove-single-file').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const index = parseInt(btn.getAttribute('data-index'));
                selectedFiles.splice(index, 1);
                if (selectedFiles.length === 0) {
                    resetUpload();
                } else {
                    renderFileList();
                }
            });
        });
        
        // Add a "Clear All" button
        const clearBtn = document.createElement('button');
        clearBtn.className = 'secondary-btn';
        clearBtn.style.padding = '8px';
        clearBtn.style.marginTop = '10px';
        clearBtn.innerHTML = '<i class="fas fa-trash"></i> Remove All';
        clearBtn.onclick = (e) => {
            e.stopPropagation();
            resetUpload();
        };
        fileList.appendChild(clearBtn);
    }

    function resetUpload() {
        selectedFiles = [];
        fileInput.value = '';
        dropZoneContent.classList.remove('hidden');
        fileList.classList.add('hidden');
        fileList.innerHTML = '';
        uploadBtn.disabled = true;
        progressContainer.classList.add('hidden');
        resultSection.classList.add('hidden');
    }

    // --- Upload Logic ---
    uploadBtn.addEventListener('click', async () => {
        if (selectedFiles.length === 0) return;

        const formData = new FormData();
        const customAlias = document.getElementById('custom-alias').value.trim();
        const isOneTime = document.getElementById('one-time-check').checked;
        const password = document.getElementById('file-password').value;

        // Append all files
        selectedFiles.forEach(file => {
            formData.append('files[]', file);
        });
        
        formData.append('expiry', expirySelect.value);
        if (customAlias) formData.append('custom_alias', customAlias);
        formData.append('is_one_time', isOneTime);
        if (password) formData.append('password', password);

        // UI State
        uploadBtn.disabled = true;
        uploadBtn.querySelector('.loader').classList.remove('hidden');
        progressContainer.classList.remove('hidden');

        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressFill.style.width = percent + '%';
                progressText.textContent = percent + '%';
            }
        });

        xhr.onload = () => {
            uploadBtn.querySelector('.loader').classList.add('hidden');

            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                showResult(response.file_url, response.network_file_url, response.expires_at);
                showToast('Upload successful!', 'success');
            } else {
                let errorMsg = 'Upload failed';
                try {
                    const error = JSON.parse(xhr.responseText);
                    errorMsg = error.detail || errorMsg;
                } catch(e) {}
                showToast(errorMsg, 'error');
                uploadBtn.disabled = false;
            }
        };

        xhr.onerror = () => {
            uploadBtn.querySelector('.loader').classList.add('hidden');
            showToast('Network error.', 'error');
            uploadBtn.disabled = false;
        };

        const backendUrl = window.location.protocol === 'file:' ? 'http://localhost:8000/upload' : '/upload';
        xhr.open('POST', backendUrl, true);
        xhr.send(formData);
    });

    function showResult(url, networkUrl, expiry) {
        shareUrlInput.value = url;
        const networkUrlInput = document.getElementById('network-url');
        if (networkUrlInput) networkUrlInput.value = networkUrl;

        const expiryDate = new Date(expiry);
        expiryDisplay.textContent = expiryDate.toLocaleString();
        
        generateQRCode(networkUrl);
        
        // Setup Social Sharing
        const message = `Check out this file on DropShare: ${url}`;
        whatsappBtn.onclick = () => {
            window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(message)}`, '_blank');
        };
        emailBtn.onclick = () => {
            window.location.href = `mailto:?subject=File Shared&body=${encodeURIComponent(message)}`;
        };
        
        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth' });

        // Save to History
        const password = document.getElementById('file-password').value;
        saveToHistory({
            name: selectedFiles.length > 1 ? `Package (${selectedFiles.length} files)` : selectedFiles[0].name,
            url: url,
            expires_at: expiry,
            created_at: new Date().toISOString()
        });
    }

    function generateQRCode(url) {
        const qrContainer = document.getElementById('qrcode');
        qrContainer.innerHTML = ''; // Clear previous
        
        // Create a canvas for QRious to draw on
        const canvas = document.createElement('canvas');
        qrContainer.appendChild(canvas);

        const qr = new QRious({
            element: canvas,
            value: url,
            size: 250,
            level: 'H', // High error correction for better scanning
            background: 'white',
            foreground: '#6366f1' // Branded color
        });
    }

    // --- Aux Logic ---
    copyBtn.addEventListener('click', () => {
        shareUrlInput.select();
        document.execCommand('copy');
        showToast('Link copied!', 'success');
    });

    newUploadBtn.addEventListener('click', () => {
        resetUpload();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    function showToast(message, type = 'success') {
        toastMessage.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.remove('hidden');
        setTimeout(() => toast.classList.add('hidden'), 3000);
    }
});
