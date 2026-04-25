/**
 * Agentic — Frontend Application Logic
 * Handles file upload, API communication, progress tracking, and result rendering.
 */

// ── DOM Elements ──────────────────────────────────────
const uploadSection = document.getElementById('upload-section');
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const filePreview = document.getElementById('file-preview');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const btnRemove = document.getElementById('btn-remove');
const btnAnalyze = document.getElementById('btn-analyze');

const progressSection = document.getElementById('progress-section');
const resultsSection = document.getElementById('results-section');

const statusIndicator = document.getElementById('status-indicator');

const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toast-message');
const toastClose = document.getElementById('toast-close');

const btnDownload = document.getElementById('btn-download');
const btnNew = document.getElementById('btn-new');

// ── State ─────────────────────────────────────────────
let selectedFile = null;
let analysisResult = null;
let timerInterval = null;
let elapsedSeconds = 0;

// ── Initialization ────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupUploadZone();
    setupTabs();
    setupButtons();
});

// ── Health Check ──────────────────────────────────────
async function checkHealth() {
    const dot = statusIndicator.querySelector('.status-dot');
    const text = statusIndicator.querySelector('.status-text');

    try {
        const res = await fetch('/api/health');
        const data = await res.json();

        if (data.ollama_connected && data.model_available) {
            dot.className = 'status-dot connected';
            text.textContent = `${data.model_name} ready`;
        } else if (data.ollama_connected) {
            dot.className = 'status-dot disconnected';
            text.textContent = `Model not found`;
            showToast(`Model "${data.model_name}" not available. Run: ollama pull ${data.model_name}`);
        } else {
            dot.className = 'status-dot disconnected';
            text.textContent = 'Ollama offline';
            showToast('Ollama is not running. Start it with: ollama serve');
        }
    } catch (e) {
        dot.className = 'status-dot disconnected';
        text.textContent = 'Server offline';
    }
}

// ── Upload Zone ───────────────────────────────────────
function setupUploadZone() {
    // Click to browse
    uploadZone.addEventListener('click', () => fileInput.click());

    // File selected via browse
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
}

function handleFile(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('Please upload a PDF file');
        return;
    }

    selectedFile = file;

    // Show file preview
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    filePreview.classList.remove('hidden');
    uploadZone.classList.add('hidden');
    btnAnalyze.classList.remove('hidden');
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ── Buttons ───────────────────────────────────────────
function setupButtons() {
    btnRemove.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUpload();
    });

    btnAnalyze.addEventListener('click', startAnalysis);

    btnNew.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        resetUpload();
    });

    btnDownload.addEventListener('click', downloadJSON);

    toastClose.addEventListener('click', () => toast.classList.add('hidden'));
}

function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    filePreview.classList.add('hidden');
    uploadZone.classList.remove('hidden');
    btnAnalyze.classList.add('hidden');
}

// ── Analysis Pipeline ─────────────────────────────────
async function startAnalysis() {
    if (!selectedFile) return;

    // Switch to progress view
    uploadSection.classList.add('hidden');
    progressSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');

    // Reset steps
    const steps = ['step-extract', 'step-clarify', 'step-testgen', 'step-complete'];
    steps.forEach(id => {
        const el = document.getElementById(id);
        el.classList.remove('active', 'done');
    });

    // Start timer
    elapsedSeconds = 0;
    updateTimer();
    timerInterval = setInterval(() => {
        elapsedSeconds++;
        updateTimer();
    }, 1000);

    // Simulate step progression
    activateStep('step-extract');

    try {
        // Upload and analyze
        const formData = new FormData();
        formData.append('file', selectedFile);

        // After a brief delay, show clarification step
        setTimeout(() => {
            completeStep('step-extract');
            activateStep('step-clarify');
        }, 2000);

        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        analysisResult = await response.json();

        // Mark all steps complete
        steps.forEach(id => {
            const el = document.getElementById(id);
            el.classList.remove('active');
            el.classList.add('done');
        });

        // Brief pause then show results
        setTimeout(() => {
            clearInterval(timerInterval);
            progressSection.classList.add('hidden');
            showResults(analysisResult);
        }, 800);

    } catch (error) {
        clearInterval(timerInterval);
        progressSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        showToast(error.message);
    }
}

function activateStep(stepId) {
    document.getElementById(stepId).classList.add('active');
}

function completeStep(stepId) {
    const el = document.getElementById(stepId);
    el.classList.remove('active');
    el.classList.add('done');
}

function updateTimer() {
    const mins = Math.floor(elapsedSeconds / 60);
    const secs = elapsedSeconds % 60;
    const timeStr = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
    document.getElementById('elapsed-time').textContent = timeStr;
}

// ── Results Rendering ─────────────────────────────────
function showResults(data) {
    resultsSection.classList.remove('hidden');

    // Summary bar
    const riskEl = document.getElementById('stat-risk');
    riskEl.textContent = data.clarification.risk_level.toUpperCase();
    riskEl.className = `stat-value risk-${data.clarification.risk_level}`;

    document.getElementById('stat-missing').textContent = data.clarification.missing_requirements.length;
    document.getElementById('stat-ambiguities').textContent = data.clarification.ambiguities.length;

    const totalTests =
        data.test_data.valid_cases.length +
        data.test_data.invalid_cases.length +
        data.test_data.edge_cases.length +
        data.test_data.boundary_values.length +
        data.test_data.security_cases.length;
    document.getElementById('stat-tests').textContent = totalTests;
    document.getElementById('stat-time').textContent = data.processing_time_seconds + 's';

    // Clarification tab
    document.getElementById('result-summary').textContent = data.clarification.summary;
    renderList('result-missing', data.clarification.missing_requirements);
    renderList('result-ambiguities', data.clarification.ambiguities);
    renderList('result-questions', data.clarification.clarification_questions);
    renderList('result-assumptions', data.clarification.assumptions);

    // Test data tab
    renderTestCases('result-valid', data.test_data.valid_cases);
    renderTestCases('result-invalid', data.test_data.invalid_cases);
    renderTestCases('result-edge', data.test_data.edge_cases);
    renderTestCases('result-boundary', data.test_data.boundary_values);
    renderTestCases('result-security', data.test_data.security_cases);

    // Extracted text tab
    document.getElementById('result-extracted-text').textContent = data.extracted_text;

    // JSON tab
    document.getElementById('result-json').textContent = JSON.stringify(data, null, 2);
}

function renderList(elementId, items) {
    const el = document.getElementById(elementId);
    el.innerHTML = '';

    if (!items || items.length === 0) {
        const li = document.createElement('li');
        li.textContent = 'None identified';
        li.style.opacity = '0.5';
        li.style.borderLeftColor = 'var(--text-muted)';
        el.appendChild(li);
        return;
    }

    items.forEach((item, i) => {
        const li = document.createElement('li');
        li.textContent = item;
        li.style.animationDelay = `${i * 0.05}s`;
        li.classList.add('fade-in-item');
        el.appendChild(li);
    });
}

function renderTestCases(elementId, cases) {
    const el = document.getElementById(elementId);
    el.innerHTML = '';

    if (!cases || cases.length === 0) {
        const div = document.createElement('div');
        div.textContent = 'No test cases generated';
        div.style.color = 'var(--text-muted)';
        div.style.padding = '12px';
        el.appendChild(div);
        return;
    }

    cases.forEach(tc => {
        const card = document.createElement('div');
        card.className = 'test-case';

        card.innerHTML = `
            <div class="test-case-scenario">${escapeHtml(tc.scenario)}</div>
            <div class="test-case-detail">
                <span class="test-case-label">Input:</span>
                <span class="test-case-value">${escapeHtml(tc.input)}</span>
            </div>
            <div class="test-case-detail">
                <span class="test-case-label">Expected:</span>
                <span class="test-case-value">${escapeHtml(tc.expected)}</span>
            </div>
        `;

        el.appendChild(card);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ── Tabs ──────────────────────────────────────────────
function setupTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Deactivate all
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            // Activate selected
            tab.classList.add('active');
            const tabId = `tab-${tab.dataset.tab}`;
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// ── Download JSON ─────────────────────────────────────
function downloadJSON() {
    if (!analysisResult) return;

    const blob = new Blob([JSON.stringify(analysisResult, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${analysisResult.pdf_filename.replace('.pdf', '')}_analysis.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// ── Toast ─────────────────────────────────────────────
function showToast(message) {
    toastMessage.textContent = message;
    toast.classList.remove('hidden');

    // Auto-hide after 8s
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 8000);
}
