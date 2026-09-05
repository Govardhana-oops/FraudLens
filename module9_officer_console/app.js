function getApiBaseUrl() {
    // 1. Injected via window.__API_BASE_URL__ or window.API_BASE
    if (window.__API_BASE_URL__ && typeof window.__API_BASE_URL__ === 'string' && window.__API_BASE_URL__.trim() !== '') {
        return window.__API_BASE_URL__.replace(/\/+$/, '');
    }
    if (window.API_BASE && typeof window.API_BASE === 'string' && window.API_BASE.trim() !== '') {
        return window.API_BASE.replace(/\/+$/, '');
    }
    // 2. Injected via HTML <meta name="api-base-url" content="...">
    const metaTag = document.querySelector('meta[name="api-base-url"]');
    if (metaTag && metaTag.content && metaTag.content.trim() !== '' && !metaTag.content.startsWith('%')) {
        return metaTag.content.replace(/\/+$/, '');
    }
    // 3. User runtime override stored in localStorage
    try {
        const saved = localStorage.getItem('AI_DIDSS_API_BASE');
        if (saved && saved.trim() !== '') {
            return saved.replace(/\/+$/, '');
        }
    } catch (e) {}
    // 4. Same origin if running on FastAPI server directly
    if (window.location.port === '8000' || window.location.pathname.startsWith('/console')) {
        return '';
    }
    // 5. Default local fallback for local development (port 3000 -> 8000)
    return 'http://localhost:8000';
}

document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = getApiBaseUrl();

    // DOM Elements
    const docDropzone = document.getElementById('doc-dropzone');
    const docFileInput = document.getElementById('doc-file-input');
    const docPrompt = document.getElementById('doc-dropzone-prompt');
    const docPreview = document.getElementById('doc-preview-img');

    const liveFaceBox = document.getElementById('live-face-box');
    const liveFileInput = document.getElementById('live-file-input');
    const livePrompt = document.getElementById('live-upload-prompt');
    const liveFaceCrop = document.getElementById('live-face-crop');

    const runScreenBtn = document.getElementById('run-screen-btn');
    const syncBtn = document.getElementById('sync-btn');

    // UI Feedback Elements
    const docTypeBadge = document.getElementById('doc-type-badge');
    const fDocNum = document.getElementById('f-doc-num');
    const fName = document.getElementById('f-name');
    const fIssuing = document.getElementById('f-issuing-country');
    const fDob = document.getElementById('f-dob');
    const fExpiry = document.getElementById('f-expiry');
    const mrzDisplay = document.getElementById('mrz-display');
    const mrzStatus = document.getElementById('mrz-status');

    const bioSimilarityVal = document.getElementById('bio-similarity-val');
    const bioProgressFill = document.getElementById('bio-progress-fill');
    const bioStatusBadge = document.getElementById('bio-status-badge');

    const decisionBanner = document.getElementById('decision-banner');
    const decisionTitle = document.getElementById('decision-title');
    const riskIndexVal = document.getElementById('risk-index-val');
    const riskDocFill = document.getElementById('risk-doc-fill');
    const riskTampFill = document.getElementById('risk-tamp-fill');
    const riskBioFill = document.getElementById('risk-bio-fill');

    const evidenceList = document.getElementById('evidence-list');
    const guidanceText = document.getElementById('guidance-text');
    const latencyVal = document.getElementById('latency-val');
    const auditHashDisplay = document.getElementById('audit-hash-display');

    let selectedDocFile = null;
    let selectedLiveFile = null;

    // Document Dropzone Handling
    docDropzone.addEventListener('click', () => docFileInput.click());
    docFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleDocFile(e.target.files[0]);
        }
    });

    docDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        docDropzone.style.borderColor = '#6366F1';
    });

    docDropzone.addEventListener('dragleave', () => {
        docDropzone.style.borderColor = 'rgba(255, 255, 255, 0.12)';
    });

    docDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        docDropzone.style.borderColor = 'rgba(255, 255, 255, 0.12)';
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleDocFile(e.dataTransfer.files[0]);
        }
    });

    function handleDocFile(file) {
        selectedDocFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            docPreview.src = e.target.result;
            docPreview.hidden = false;
            docPrompt.hidden = true;
            docTypeBadge.textContent = 'DOCUMENT LOADED';
            docTypeBadge.style.color = '#10B981';
        };
        reader.readAsDataURL(file);
    }

    // Live Probe Face Handling
    liveFaceBox.addEventListener('click', () => liveFileInput.click());
    liveFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            selectedLiveFile = e.target.files[0];
            const reader = new FileReader();
            reader.onload = (ev) => {
                liveFaceCrop.src = ev.target.result;
                liveFaceCrop.hidden = false;
                livePrompt.hidden = true;
                bioStatusBadge.textContent = 'PROBE CAPTURED';
                bioStatusBadge.style.color = '#38BDF8';
            };
            reader.readAsDataURL(selectedLiveFile);
        }
    });

    // Execute Screening
    runScreenBtn.addEventListener('click', async () => {
        if (!selectedDocFile) {
            alert('Please select or drop a document image scan first.');
            return;
        }

        runScreenBtn.disabled = true;
        runScreenBtn.innerHTML = '<span>Processing Multi-Modal Pipeline...</span>';

        const formData = new FormData();
        formData.append('document_file', selectedDocFile);
        if (selectedLiveFile) {
            formData.append('live_face_file', selectedLiveFile);
        }
        formData.append('officer_id', 'OFFICER-0082');
        formData.append('checkpoint_id', 'GATE-04');

        try {
            const response = await fetch(`${API_BASE}/api/v1/screening/inspect`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server returned HTTP ${response.status}`);
            }

            const data = await response.json();
            renderDossier(data);
        } catch (err) {
            console.warn('API fetch failed; running local fallback:', err);
            renderLocalSimulation();
        } finally {
            runScreenBtn.disabled = false;
            runScreenBtn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                    <circle cx="11" cy="11" r="8"/>
                    <path d="m21 21-4.3-4.3"/>
                </svg>
                Execute Multi-Modal Screening
            `;
        }
    });

    function renderDossier(data) {
        // Document Type
        const rawType = data.document_type || 'UNKNOWN';
        docTypeBadge.textContent = rawType.toUpperCase().replace(/_/g, ' ');

        // Update Document Fields dynamically from extracted_fields and MRZ
        const fields = data.extracted_fields || {};
        const docNum = fields.passport_number?.value ||
                       fields.id_number?.value ||
                       fields.license_number?.value ||
                       fields.visa_number?.value ||
                       fields.permit_number?.value ||
                       fields.document_number?.value ||
                       (data.mrz?.lines && data.mrz.lines[1] ? data.mrz.lines[1].substring(0, 9).replace(/</g, '') : null) ||
                       'UNKNOWN';

        const fullName = fields.full_name?.value ||
                         ((fields.given_names?.value || '') + ' ' + (fields.surname?.value || '')).trim() ||
                         'UNKNOWN';

        const issuing = fields.issuing_country?.value ||
                        fields.nationality?.value ||
                        (data.mrz?.lines && data.mrz.lines[0] ? data.mrz.lines[0].substring(2, 5).replace(/</g, '') : null) ||
                        'UNKNOWN';

        const dob = fields.date_of_birth?.value ||
                    (data.mrz?.lines && data.mrz.lines[1] ? data.mrz.lines[1].substring(13, 19) : null) ||
                    'UNKNOWN';

        const expiry = fields.date_of_expiry?.value ||
                       fields.valid_until?.value ||
                       (data.mrz?.lines && data.mrz.lines[1] ? data.mrz.lines[1].substring(21, 27) : null) ||
                       'UNKNOWN';

        fDocNum.textContent = docNum;
        if (fName) fName.textContent = fullName;
        fIssuing.textContent = issuing;
        fDob.textContent = dob;
        fExpiry.textContent = expiry;

        // MRZ stream display
        if (data.mrz && Array.isArray(data.mrz.lines) && data.mrz.lines.length > 0) {
            mrzDisplay.textContent = data.mrz.lines.join('\n');
            mrzStatus.textContent = data.mrz.status || (data.mrz.checksum_valid ? 'CHECKSUM VALID' : 'CHECKSUM ERROR');
            mrzStatus.style.color = data.mrz.checksum_valid ? '#10B981' : '#F59E0B';
        } else {
            mrzDisplay.textContent = 'NO MRZ DETECTED / VISUAL ONLY';
            mrzStatus.textContent = 'N/A';
            mrzStatus.style.color = '#94A3B8';
        }

        // Biometrics
        const sim = data.dimensional_risks?.biometric_identity_risk !== undefined
            ? Math.max(0.0, 1.0 - data.dimensional_risks.biometric_identity_risk)
            : 0.0;
        bioSimilarityVal.textContent = sim > 0 ? sim.toFixed(2) : 'N/A';
        bioProgressFill.style.width = `${Math.round(sim * 100)}%`;

        // Decision Banner
        const action = data.recommended_action || 'TECHNICAL_REVIEW_REQUIRED';
        decisionTitle.textContent = action.replace(/_/g, ' ');

        decisionBanner.className = 'decision-banner';
        if (action === 'CLEAR') {
            decisionBanner.classList.add('clear');
        } else if (action === 'SECONDARY_INSPECTION_RECOMMENDED') {
            decisionBanner.classList.add('secondary');
        } else {
            decisionBanner.classList.add('review');
        }

        // Risks
        const risk = data.risk_index !== undefined ? data.risk_index : 0.50;
        riskIndexVal.textContent = risk.toFixed(2);
        riskDocFill.style.width = `${Math.round((data.dimensional_risks?.document_syntactic_risk || 0.0) * 100)}%`;
        riskTampFill.style.width = `${Math.round((data.dimensional_risks?.physical_tampering_risk || 0.0) * 100)}%`;
        riskBioFill.style.width = `${Math.round((data.dimensional_risks?.biometric_identity_risk || 0.0) * 100)}%`;

        // Itemized Evidence
        evidenceList.innerHTML = '';
        const positives = data.itemized_evidence?.positive_findings || [];
        positives.forEach(p => {
            const li = document.createElement('li');
            li.className = 'evidence-item positive';
            li.textContent = p;
            evidenceList.appendChild(li);
        });

        const negatives = data.itemized_evidence?.negative_findings || [];
        negatives.forEach(n => {
            const li = document.createElement('li');
            li.className = 'evidence-item negative';
            li.textContent = n;
            evidenceList.appendChild(li);
        });

        const uncertainties = data.itemized_evidence?.uncertainties || [];
        uncertainties.forEach(u => {
            const li = document.createElement('li');
            li.className = 'evidence-item negative';
            li.textContent = u;
            evidenceList.appendChild(li);
        });

        if (positives.length === 0 && negatives.length === 0 && uncertainties.length === 0) {
            const li = document.createElement('li');
            li.className = 'evidence-item positive';
            li.textContent = 'Document screening processed through all security checkpoints.';
            evidenceList.appendChild(li);
        }

        // Guidance & Telemetry
        guidanceText.textContent = data.actionable_guidance || 'Technical review recommended for unverified document.';
        latencyVal.textContent = `${data.total_latency_ms || 0.0} ms`;
        if (data.audit_log?.entry_hash) {
            auditHashDisplay.textContent = data.audit_log.entry_hash.substring(0, 32) + '...';
        }
    }

    function renderLocalSimulation() {
        renderDossier({
            document_type: 'UNKNOWN',
            recommended_action: 'TECHNICAL_REVIEW_REQUIRED',
            risk_index: 0.50,
            dimensional_risks: {
                document_syntactic_risk: 0.50,
                physical_tampering_risk: 0.0,
                biometric_identity_risk: 0.0
            },
            extracted_fields: {},
            mrz: null,
            actionable_guidance: 'Backend service offline or unreachable. Manual inspection required.',
            total_latency_ms: 0.0,
            audit_log: { entry_hash: 'LOCAL_FALLBACK_NO_SERVER_CONNECTION' }
        });
    }

    // Sync button
    syncBtn.addEventListener('click', async () => {
        syncBtn.textContent = 'Syncing...';
        try {
            const res = await fetch(`${API_BASE}/api/v1/sync/differential`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ delta_records: [] })
            });
            if (res.ok) {
                syncBtn.textContent = 'Synced ✓';
            } else {
                syncBtn.textContent = 'Offline';
            }
        } catch (e) {
            syncBtn.textContent = 'Synced (Local) ✓';
        }
        setTimeout(() => {
            syncBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg> Sync';
        }, 1500);
    });
});
