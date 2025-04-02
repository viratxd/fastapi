document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const submitBtn = document.getElementById('submitBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const timer = document.getElementById('timer');
    const timeLeft = document.getElementById('timeLeft');
    const response = document.getElementById('response');
    const downloadLink = document.getElementById('downloadLink');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    // Drag and Drop
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-blue-500');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('border-blue-500'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-500');
        fileInput.files = e.dataTransfer.files;
    });

    // Submit Handler
    submitBtn.addEventListener('click', async () => {
        if (!fileInput.files.length) {
            showError('Please select a file');
            return;
        }

        const file = fileInput.files[0];
        const processType = document.querySelector('input[name="process"]:checked').value;
        const formData = new FormData();
        formData.append('file', file);

        // Show progress and timer
        progressContainer.classList.remove('hidden');
        timer.classList.remove('hidden');
        startTimer();

        try {
            const response = await fetch(`/process/${processType}`, {
                method: 'POST',
                body: formData,
                onUploadProgress: (progressEvent) => {
                    const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    progressBar.style.width = `${percent}%`;
                    progressText.textContent = `Uploading: ${percent}%`;
                }
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                downloadLink.href = url;
                downloadLink.download = response.headers.get('content-disposition')?.split('filename=')[1] || `${file.name}_processed`;
                showResponse();
            } else {
                const error = await response.json();
                showError(error.detail);
            }
        } catch (error) {
            showError('An error occurred while processing the file');
        } finally {
            resetUI();
        }
    });

    // Timer Function
    function startTimer() {
        let time = 120; // 2 minutes
        const interval = setInterval(() => {
            const minutes = Math.floor(time / 60);
            const seconds = time % 60;
            timeLeft.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            time--;
            if (time < 0) clearInterval(interval);
        }, 1000);
    }

    // UI Helpers
    function showResponse() {
        response.classList.remove('hidden');
        timer.classList.add('hidden');
    }

    function showError(message) {
        errorAlert.classList.remove('hidden');
        errorMessage.textContent = message;
        setTimeout(() => errorAlert.classList.add('hidden'), 5000);
    }

    function resetUI() {
        progressContainer.classList.add('hidden');
        timer.classList.add('hidden');
        progressBar.style.width = '0%';
        progressText.textContent = '';
    }
});
