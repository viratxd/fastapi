document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const submitBtn = document.getElementById('submitBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const processingOverlay = document.getElementById('processingOverlay');
    const timeLeft = document.getElementById('timeLeft');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const uploadTab = document.getElementById('uploadTab');
    const howItWorksTab = document.getElementById('howItWorksTab');
    const uploadSection = document.getElementById('uploadSection');
    const howItWorksSection = document.getElementById('howItWorksSection');
    const recentUploads = document.getElementById('recentUploads');
    const searchUploads = document.getElementById('searchUploads');

    // Tab Switching
    uploadTab.addEventListener('click', () => {
        uploadTab.classList.add('bg-yellow-600');
        uploadTab.classList.remove('bg-gray-700');
        howItWorksTab.classList.add('bg-gray-700');
        howItWorksTab.classList.remove('bg-yellow-600');
        uploadSection.classList.remove('hidden');
        howItWorksSection.classList.add('hidden');
    });

    howItWorksTab.addEventListener('click', () => {
        howItWorksTab.classList.add('bg-yellow-600');
        howItWorksTab.classList.remove('bg-gray-700');
        uploadTab.classList.add('bg-gray-700');
        uploadTab.classList.remove('bg-yellow-600');
        howItWorksSection.classList.remove('hidden');
        uploadSection.classList.add('hidden');
    });

    // Drag and Drop
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-yellow-600');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('border-yellow-600'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-yellow-600');
        fileInput.files = e.dataTransfer.files;
        displayFileName();
    });

    fileInput.addEventListener('change', () => {
        displayFileName();
    });

    // Submit Handler
    submitBtn.addEventListener('click', () => {
        if (!fileInput.files.length) {
            showError('Please select a file');
            return;
        }

        const file = fileInput.files[0];
        const processType = document.querySelector('input[name="process"]:checked').value;
        const formData = new FormData();
        formData.append('file', file);

        progressContainer.classList.remove('hidden');
        progressText.textContent = 'Uploading...';

        const xhr = new XMLHttpRequest();
        xhr.open('POST', `/process/${processType}`, true);

        // Ensure headers are set for proper progress tracking
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
                const percent = Math.round((event.loaded * 100) / event.total);
                console.log(`Upload progress: ${percent}%`); // Debug log
                progressBar.style.width = `${percent}%`;
                progressText.textContent = `Uploading: ${percent}%`;

                if (percent === 100) {
                    setTimeout(() => {
                        progressContainer.classList.add('hidden');
                        processingOverlay.classList.remove('hidden');
                        startTimer();
                    }, 500);
                }
            } else {
                console.log('Upload progress: lengthComputable is false');
            }
        };

        xhr.upload.onloadstart = () => {
            console.log('Upload started');
        };

        xhr.upload.onloadend = () => {
            console.log('Upload finished');
        };

        xhr.onload = () => {
            if (xhr.status === 200) {
                clearInterval(timerInterval);
                processingOverlay.classList.add('hidden');

                const blob = new Blob([xhr.response], { type: 'application/vnd.android.package-archive' });
                const url = window.URL.createObjectURL(blob);
                const filename = xhr.getResponseHeader('content-disposition')?.split('filename=')[1] || `${file.name}_processed`;
                addRecentUpload(file.name, filename, url);
            } else {
                const error = JSON.parse(xhr.responseText);
                showError(error.detail || 'Failed to process file');
            }
        };

        xhr.onerror = () => {
            showError('An error occurred while uploading the file');
            resetUI();
        };

        xhr.responseType = 'blob';
        xhr.send(formData);
    });

    // Timer function
    let timerInterval;
    function startTimer() {
        let time = 120; // 2 minutes
        timerInterval = setInterval(() => {
            const minutes = Math.floor(time / 60);
            const seconds = time % 60;
            timeLeft.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            time--;
            if (time < 0) clearInterval(timerInterval);
        }, 1000);
    }

    // Display file name
    function displayFileName() {
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = `Selected file: ${fileInput.files[0].name}`;
        } else {
            fileNameDisplay.textContent = '';
        }
    }

    // Add to recent uploads
    function addRecentUpload(originalName, processedName, downloadUrl) {
        const uploadItem = document.createElement('div');
        uploadItem.className = 'bg-gray-700 p-3 rounded flex justify-between items-center';
        const date = new Date().toLocaleDateString('en-US', { month: 'numeric', day: 'numeric', year: 'numeric' });
        uploadItem.innerHTML = `
            <div class="flex items-center">
                <img src="https://img.icons8.com/color/40/000000/android-os.png" alt="Android Icon" class="w-10 h-10 mr-3">
                <div>
                    <p class="text-gray-300">${originalName}</p>
                    <p class="text-gray-500 text-sm">Uploaded on ${date}</p>
                </div>
            </div>
            <a href="${downloadUrl}" download="${processedName}" class="bg-yellow-600 text-white px-3 py-1 rounded text-sm">
                Download
            </a>
        `;
        recentUploads.prepend(uploadItem);

        // Limit to 5 recent uploads
        const items = recentUploads.children;
        if (items.length > 5) {
            recentUploads.removeChild(items[items.length - 1]);
        }
    }

    // Search uploads
    searchUploads.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const items = recentUploads.children;
        for (let item of items) {
            const fileName = item.querySelector('p').textContent.toLowerCase();
            item.style.display = fileName.includes(searchTerm) ? '' : 'none';
        }
    });

    // UI Helpers
    function showError(message) {
        errorAlert.classList.remove('hidden');
        errorMessage.textContent = message;
        setTimeout(() => errorAlert.classList.add('hidden'), 5000);
    }

    function resetUI() {
        progressContainer.classList.add('hidden');
        processingOverlay.classList.add('hidden');
        progressBar.style.width = '0%';
        progressText.textContent = '';
        fileNameDisplay.textContent = '';
    }
});