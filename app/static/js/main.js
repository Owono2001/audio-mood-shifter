// app/static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const submitButton = document.getElementById('submit-button');
    const fileInput = document.getElementById('file');
    const fileNameDisplay = document.getElementById('file-name-display');
    const fileDropZone = document.getElementById('file-drop-zone');

    const uploadProgressDiv = document.getElementById('upload-progress');
    const statusMessageDiv = document.getElementById('status-message');
    const progressBarInner = document.getElementById('progress-bar-inner');
    const resultLinkContainer = document.getElementById('result-link-container');
    const errorDetailsContainer = document.getElementById('error-details-container');

    let currentTaskPollInterval = null;

    // --- Effect Parameter UI Handlers ---
    function setupEffectParameterSlider(checkboxId, sliderId, valueDisplayId, unit = '', isFloat = false) {
        const checkbox = document.getElementById(checkboxId);
        const slider = document.getElementById(sliderId);
        const valueDisplay = document.getElementById(valueDisplayId);

        if (checkbox && slider && valueDisplay) {
            // Disable slider if checkbox is not checked initially
            slider.disabled = !checkbox.checked;
            
            // Initialize display based on current slider value
            let initialValue = isFloat ? parseFloat(slider.value).toFixed(slider.step.includes('.') ? slider.step.split('.')[1].length : 1) : slider.value;
            valueDisplay.textContent = initialValue + unit;


            checkbox.addEventListener('change', function() {
                slider.disabled = !this.checked;
                // Optional: if you want to reset the slider to its default when unchecked
                // if (!this.checked) {
                //     slider.value = slider.defaultValue; // Or a specific default
                //     let resetVal = isFloat ? parseFloat(slider.value).toFixed(slider.step.includes('.') ? slider.step.split('.')[1].length : 1) : slider.value;
                //     valueDisplay.textContent = resetVal + unit;
                // }
            });
            slider.addEventListener('input', function() {
                // Dynamically determine precision for floats based on step attribute
                let displayValue = isFloat ? parseFloat(this.value).toFixed(this.step.includes('.') ? this.step.split('.')[1].length : 1) : this.value;
                valueDisplay.textContent = displayValue + unit;
            });
        } else {
            console.warn(`Could not find all elements for effect setup: ${checkboxId}, ${sliderId}, ${valueDisplayId}`);
        }
    }

    // Setup for existing and new effects
    setupEffectParameterSlider('enable_gain', 'gain_db', 'gain_db_value', ' dB');
    setupEffectParameterSlider('enable_high_pass_filter', 'high_pass_cutoff_hz', 'high_pass_cutoff_hz_value', ' Hz');
    setupEffectParameterSlider('enable_low_pass_filter', 'low_pass_cutoff_hz', 'low_pass_cutoff_hz_value', ' Hz');
    setupEffectParameterSlider('enable_speed_pitch', 'speed_factor', 'speed_factor_value', 'x', true); // true for isFloat
    setupEffectParameterSlider('enable_echo', 'echo_delay_ms', 'echo_delay_ms_value', ' ms');
    setupEffectParameterSlider('enable_echo', 'echo_decay_factor', 'echo_decay_factor_value', '', true); // true for isFloat
    setupEffectParameterSlider('enable_reverb', 'reverb_wet_level', 'reverb_wet_level_value', '', true); // true for isFloat
    setupEffectParameterSlider('enable_reverb', 'reverb_room_size', 'reverb_room_size_value', '', true); // true for isFloat


    // Custom file input display
    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                fileNameDisplay.textContent = `Selected: ${fileInput.files[0].name}`;
                if(fileDropZone) fileDropZone.classList.add('file-selected-visual');
            } else {
                fileNameDisplay.textContent = 'No file selected.';
                if(fileDropZone) fileDropZone.classList.remove('file-selected-visual');
            }
        });
    }

    // Drag and drop for file input
    if (fileDropZone && fileInput) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileDropZone.addEventListener(eventName, preventDefaults, false);
        });
        function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }
        ['dragenter', 'dragover'].forEach(eventName => {
            fileDropZone.addEventListener(eventName, () => fileDropZone.classList.add('highlight-drop'), false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            fileDropZone.addEventListener(eventName, () => fileDropZone.classList.remove('highlight-drop'), false);
        });
        fileDropZone.addEventListener('drop', handleDrop, false);
        function handleDrop(e) {
            let dt = e.dataTransfer;
            let files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            }
        }
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            event.preventDefault();
            if (!fileInput.files || fileInput.files.length === 0) {
                handleError("Please select an audio file to process.", false, true);
                return;
            }

            clearPreviousStatus();
            disableForm(true, "Preparing effects...");

            const formData = new FormData();
            formData.append('file', fileInput.files[0], fileInput.files[0].name);
            
            const outputFormatSelect = document.getElementById('output_format');
            if (outputFormatSelect) {
                formData.append('output_format', outputFormatSelect.value);
            }

            // --- Collect Effect Parameters ---
            const effects_chain = [];
            // Gain
            if (document.getElementById('enable_gain').checked) {
                effects_chain.push({
                    name: 'gain',
                    gain_db: parseFloat(document.getElementById('gain_db').value)
                });
            }
            // High-Pass Filter
            if (document.getElementById('enable_high_pass_filter').checked) {
                effects_chain.push({
                    name: 'high_pass_filter',
                    cutoff_hz: parseInt(document.getElementById('high_pass_cutoff_hz').value)
                });
            }
            // Low-Pass Filter
            if (document.getElementById('enable_low_pass_filter').checked) {
                effects_chain.push({
                    name: 'low_pass_filter',
                    cutoff_hz: parseInt(document.getElementById('low_pass_cutoff_hz').value) // Changed from parseFloat
                });
            }
            // Speed/Pitch
            if (document.getElementById('enable_speed_pitch').checked) {
                effects_chain.push({
                    name: 'speed_pitch',
                    factor: parseFloat(document.getElementById('speed_factor').value)
                });
            }
            // Echo
            if (document.getElementById('enable_echo').checked) {
                effects_chain.push({
                    name: 'echo',
                    delay_ms: parseInt(document.getElementById('echo_delay_ms').value),
                    decay_factor: parseFloat(document.getElementById('echo_decay_factor').value)
                });
            }
            // Reverb
            if (document.getElementById('enable_reverb').checked) {
                effects_chain.push({
                    name: 'reverb',
                    wet_level: parseFloat(document.getElementById('reverb_wet_level').value),
                    room_size: parseFloat(document.getElementById('reverb_room_size').value)
                });
            }

            formData.append('effects_chain', JSON.stringify(effects_chain));
            // --- End Collect Effect Parameters ---

            console.log("FormData entries:");
            for (let [key, value] of formData.entries()) {
                console.log(key, value);
            }
            
            const uploadUrl = '/upload';
            console.log("Attempting to POST to URL:", uploadUrl);

            uploadProgressDiv.style.display = 'block';
            statusMessageDiv.textContent = 'Uploading your audio file... Please wait.';
            statusMessageDiv.className = 'alert alert-info text-center';
            updateProgressBar(0, 'Initiating Upload');

            fetch(uploadUrl, {
                method: 'POST',
                body: formData,
            })
            .then(response => {
                console.log("Response status from server:", response.status);
                if (!response.ok) {
                    return response.json().then(errData => {
                        console.error("Server error JSON:", errData);
                        throw new Error(errData.error || `Server error: ${response.status}`);
                    }).catch((jsonParseError) => {
                        console.error("Error parsing JSON error or non-JSON error:", jsonParseError, response.statusText, response);
                        response.text().then(text => console.error("Non-JSON response body:", text));
                        throw new Error(`Server error: ${response.status} - ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log("Data received from server:", data);
                if (data.task_id && data.status_url) {
                    statusMessageDiv.textContent = 'Upload complete! Applying audio effects...';
                    statusMessageDiv.className = 'alert alert-primary text-center';
                    updateProgressBar(5, 'Processing Queued');
                    pollTaskStatus(data.task_id, fileInput.files[0].name);
                } else if (data.error) {
                    handleError(data.error);
                } else {
                    handleError('Unexpected response from server after upload.');
                }
            })
            .catch(error => {
                console.error('Upload fetch error:', error);
                handleError(`Upload failed: ${error.message}`);
            });
        });
    }

    function pollTaskStatus(taskId, originalFileName = "your file") {
        if (currentTaskPollInterval) { clearInterval(currentTaskPollInterval); }
        currentTaskPollInterval = setInterval(() => {
            fetch(`/status/${taskId}`).then(r => r.ok ? r.json() : Promise.reject(r)).then(data => {
                const dFN = (data.info && data.info.original_filename) ? data.info.original_filename : originalFileName;
                updateStatusDisplay(data, dFN);
                if (data.state === 'SUCCESS' || data.state === 'FAILURE') {
                    clearInterval(currentTaskPollInterval); currentTaskPollInterval = null; disableForm(false);
                    if (data.state === 'SUCCESS' && data.download_url && data.result_filename) {
                        displayDownloadLink(data.result_filename, data.download_url, dFN);
                        progressBarInner.classList.remove('progress-bar-animated', 'bg-primary'); progressBarInner.classList.add('bg-success');
                    } else if (data.state === 'FAILURE') {
                        let eM = (data.info && (data.info.status_message || data.info.error_details)) || data.status_message || 'Processing failed.';
                        if (dFN) eM = `Error processing ${dFN}: ${eM}`;
                        handleError(eM, true);
                        progressBarInner.classList.remove('progress-bar-animated', 'bg-primary'); progressBarInner.classList.add('bg-danger');
                    }
                }
            }).catch(err => { console.error('Polling error:', err); statusMessageDiv.textContent = `Error fetching status. Will retry.`; statusMessageDiv.className = 'alert alert-warning text-center'; });
        }, 2500);
    }

    function updateStatusDisplay(data, fileName) {
        let sT = (data.info && data.info.status) ? data.info.status : `Task is ${data.state}`;
        let p = (data.info && typeof data.info.progress !== 'undefined') ? data.info.progress : (data.state === 'SUCCESS' ? 100 : 0);
        if (fileName && (data.state === 'PROGRESS' || data.state === 'PENDING')) sT = `${sT} for "${fileName}"`;
        statusMessageDiv.textContent = sT; updateProgressBar(p, `${p}%`);
        progressBarInner.classList.remove('bg-success', 'bg-danger', 'bg-warning'); statusMessageDiv.classList.remove('alert-success', 'alert-danger', 'alert-warning', 'alert-primary');
        if (data.state === 'SUCCESS') { statusMessageDiv.className = 'alert alert-success text-center'; progressBarInner.classList.add('bg-success'); }
        else if (data.state === 'FAILURE') { statusMessageDiv.className = 'alert alert-danger text-center'; progressBarInner.classList.add('bg-danger'); }
        else if (data.state === 'PROGRESS' || data.state === 'PENDING') { statusMessageDiv.className = 'alert alert-info text-center'; progressBarInner.classList.add('bg-primary'); }
        else { statusMessageDiv.className = 'alert alert-warning text-center'; progressBarInner.classList.add('bg-warning'); }
    }

    function updateProgressBar(percentage, textContent = null) {
        percentage = Math.max(0, Math.min(100, parseInt(percentage, 10) || 0));
        progressBarInner.style.width = percentage + '%'; progressBarInner.textContent = textContent !== null ? textContent : percentage + '%'; progressBarInner.setAttribute('aria-valuenow', percentage);
        if (percentage < 100 && percentage > 0) progressBarInner.classList.add('progress-bar-animated'); else progressBarInner.classList.remove('progress-bar-animated');
    }

    function displayDownloadLink(filename, downloadUrl, originalFilename) {
        resultLinkContainer.innerHTML = ''; const link = document.createElement('a'); link.href = downloadUrl; link.textContent = `Download Transformed Audio: ${filename}`; link.className = 'btn btn-success btn-lg'; link.setAttribute('download', filename);
        const icon = document.createElement('i'); icon.className = 'bi bi-download me-2'; link.prepend(icon);
        resultLinkContainer.appendChild(link); resultLinkContainer.style.display = 'block'; errorDetailsContainer.style.display = 'none';
    }

    function handleError(errorMessage, isProcessingError = false, isUIMessage = false) {
        if (isUIMessage) { statusMessageDiv.textContent = errorMessage; statusMessageDiv.className = 'alert alert-warning text-center'; uploadProgressDiv.style.display = 'block'; errorDetailsContainer.style.display = 'none'; resultLinkContainer.style.display = 'none'; }
        else { statusMessageDiv.textContent = isProcessingError ? 'Effect Application Error' : 'Upload Error'; statusMessageDiv.className = 'alert alert-danger text-center'; updateProgressBar(0, 'Error'); progressBarInner.classList.add('bg-danger'); errorDetailsContainer.textContent = errorMessage; errorDetailsContainer.style.display = 'block'; resultLinkContainer.style.display = 'none'; }
        if (currentTaskPollInterval) { clearInterval(currentTaskPollInterval); currentTaskPollInterval = null; } disableForm(false);
    }

    function clearPreviousStatus() {
        uploadProgressDiv.style.display = 'none'; statusMessageDiv.textContent = ''; statusMessageDiv.className = 'alert alert-info text-center'; updateProgressBar(0, '0%'); progressBarInner.classList.remove('bg-success', 'bg-danger', 'bg-warning'); progressBarInner.classList.add('bg-primary', 'progress-bar-animated');
        resultLinkContainer.innerHTML = ''; resultLinkContainer.style.display = 'none'; errorDetailsContainer.innerHTML = ''; errorDetailsContainer.style.display = 'none';
        if (currentTaskPollInterval) { clearInterval(currentTaskPollInterval); currentTaskPollInterval = null; }
    }

    function disableForm(disabled, buttonTextOverride = null) {
        if (submitButton) {
            submitButton.disabled = disabled;
            if (disabled) { const pT = buttonTextOverride || "Applying Effects..."; submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${pT}`; }
            else { submitButton.innerHTML = '<i class="bi bi-stars"></i> Apply Effects & Process'; }
        }
        if (fileInput) fileInput.disabled = disabled;
        const oFS = uploadForm.querySelector('#output_format'); if (oFS) oFS.disabled = disabled;
        document.querySelectorAll('.effect-card input, .effect-card select').forEach(el => el.disabled = disabled);
    }
});