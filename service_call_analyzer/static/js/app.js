/**
 * Static Site App - Renders the call analysis interface
 */

document.addEventListener('DOMContentLoaded', function() {
    if (window.CALL_DATA && window.CUSTOM_ANALYSIS) {
        renderApp();
    } else {
        console.error('Call data not found');
    }
});

function renderApp() {
    const callData = window.CALL_DATA;
    const customAnalysis = window.CUSTOM_ANALYSIS;
    
    // Process data
    const processedData = processCallData(callData);
    
    // Render the main interface
    const appContainer = document.getElementById('app');
    appContainer.innerHTML = generateMainHTML(processedData, customAnalysis);
    
    // Initialize the existing JavaScript functionality
    if (typeof initializeNavigation === 'function') {
        initializeNavigation();
    }
    if (typeof initializeScrollSpy === 'function') {
        initializeScrollSpy();
    }
    if (typeof initializeAnimations === 'function') {
        initializeAnimations();
    }
    if (typeof initializeAnalysisSync === 'function') {
        initializeAnalysisSync();
    }
}

function processCallData(data) {
    // Extract stages
    const stages = [];
    for (const check of data.compliance_check || []) {
        const stage = check.stage;
        if (stage && !stages.includes(stage)) {
            stages.push(stage);
        }
    }
    
    // Group utterances by stage
    const utterancesByStage = {};
    for (const utterance of data.utterances || []) {
        const stage = utterance.stage || 'General';
        if (!utterancesByStage[stage]) {
            utterancesByStage[stage] = [];
        }
        utterancesByStage[stage].push(utterance);
    }
    
    // Sort utterances within each stage chronologically
    for (const stage in utterancesByStage) {
        utterancesByStage[stage].sort((a, b) => (a.start || 0) - (b.start || 0));
    }
    
    // Process compliance data
    const complianceData = {};
    for (const check of data.compliance_check || []) {
        const stage = check.stage;
        if (stage) {
            complianceData[stage] = {
                score: check.score || 0,
                max_score: check.max || 5,
                evidence: check.evidence || '',
                suggestion: check.suggestion || ''
            };
        }
    }
    
    // Calculate summary
    const totalUtterances = (data.utterances || []).length;
    const totalComplianceScore = (data.compliance_check || []).reduce((sum, check) => sum + (check.score || 0), 0);
    const maxComplianceScore = (data.compliance_check || []).reduce((sum, check) => sum + (check.max || 5), 0);
    
    const callSummary = {
        call_type: data.meta?.call_type || 'Unknown',
        date_analyzed: data.meta?.date_analyzed || 'Unknown',
        total_utterances: totalUtterances,
        total_stages: stages.length,
        stages: stages,
        compliance_score: totalComplianceScore,
        max_compliance_score: maxComplianceScore,
        compliance_percentage: maxComplianceScore > 0 ? (totalComplianceScore / maxComplianceScore * 100) : 0
    };
    
    return {
        stages,
        utterancesByStage,
        complianceData,
        callSummary,
        callMeta: data.meta || {}
    };
}

function generateMainHTML(processedData, customAnalysis) {
    const { stages, utterancesByStage, complianceData, callSummary } = processedData;
    const customAnalysisStages = customAnalysis.stages || {};
    
    return `
        <div class="container-fluid">
            <!-- Call Summary Header -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="call-summary">
                        <h4><i class="bi bi-telephone-fill me-2"></i>${callSummary.call_type}</h4>
                        <p class="mb-0">Analyzed on ${callSummary.date_analyzed}</p>
                        <div class="summary-stats">
                            <div class="stat-item">
                                <span class="stat-value">${callSummary.total_stages}</span>
                                <span class="stat-label">Stages</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">${callSummary.total_utterances}</span>
                                <span class="stat-label">Utterances</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">${callSummary.compliance_score}/${callSummary.max_compliance_score}</span>
                                <span class="stat-label">Compliance Score</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">${Math.round(callSummary.compliance_percentage)}%</span>
                                <span class="stat-label">Compliance Rate</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stage Navigation Bar -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="stage-nav-horizontal">
                        <h5><i class="bi bi-list-ul me-2"></i>Call Stages</h5>
                        <nav class="nav nav-pills">
                            ${stages.map((stage, index) => `
                                <a class="nav-link" href="#stage-${index + 1}" data-stage="${stage}">
                                    ${stage}
                                </a>
                            `).join('')}
                        </nav>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Left Column: Transcript -->
                <div class="col-lg-8">
                    ${stages.map((stage, index) => generateTranscriptSection(stage, index + 1, utterancesByStage[stage] || [])).join('')}
                </div>

                <!-- Right Column: Analysis Panel -->
                <div class="col-lg-4">
                    <div class="analysis-panel">
                        <div class="analysis-panel-wrapper">
                            ${stages.map((stage, index) => generateAnalysisSection(stage, index + 1, complianceData[stage], customAnalysisStages[stage])).join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function generateTranscriptSection(stage, stageNumber, utterances) {
    return `
        <div class="transcript-section" id="stage-${stageNumber}">
            <h3 class="stage-header">
                <i class="bi bi-chat-dots me-2"></i>${stage}
            </h3>
            <div class="utterances-container">
                ${utterances.length > 0 ? utterances.map(utterance => `
                    <div class="utterance ${utterance.speaker.toLowerCase()}">
                        <div class="speaker-info">
                            <span class="speaker-name ${utterance.speaker.toLowerCase()}">
                                <i class="bi bi-${utterance.speaker === 'Tech' ? 'person-gear' : 'person'} me-1"></i>
                                ${utterance.speaker}
                            </span>
                            <span class="timestamp">
                                ${Math.round(utterance.start)}s - ${Math.round(utterance.end)}s
                            </span>
                        </div>
                        <p class="utterance-text">${utterance.text}</p>
                    </div>
                `).join('') : `
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        No utterances found for this stage.
                    </div>
                `}
            </div>
        </div>
    `;
}

function generateAnalysisSection(stage, stageNumber, compliance, customAnalysis) {
    return `
        <div class="analysis-section" id="analysis-${stageNumber}">
            <div class="analysis-header">
                <div class="section-indicator">
                    <h4 class="section-title">
                        <i class="bi bi-chat-dots me-2"></i>${stage}
                    </h4>
                    <p class="section-subtitle">Stage ${stageNumber} Analysis</p>
                </div>
                <div class="connection-line"></div>
            </div>
            <div class="analysis-content">
                ${compliance ? generateComplianceCard(compliance) : ''}
                ${customAnalysis ? generateCustomAnalysisCards(customAnalysis) : generateNoDataCard()}
            </div>
        </div>
    `;
}

function generateComplianceCard(compliance) {
    const scoreClass = compliance.score >= 4 ? 'rating-good' : compliance.score >= 2 ? 'rating-medium' : 'rating-poor';
    const fillClass = compliance.score >= 4 ? 'good' : compliance.score >= 2 ? 'medium' : 'poor';
    const percentage = Math.round((compliance.score / compliance.max_score) * 100);
    
    return `
        <div class="compliance-rating-card">
            <div class="rating-header">
                <h5><i class="bi bi-clipboard-check me-2"></i>Compliance Rating</h5>
                <div class="rating-score ${scoreClass}">
                    ${compliance.score}/${compliance.max_score}
                </div>
            </div>
            <div class="rating-bar">
                <div class="rating-fill ${fillClass}" style="width: ${percentage}%"></div>
            </div>
        </div>
    `;
}

function generateCustomAnalysisCards(analysis) {
    let html = '';
    
    if (analysis.analysis) {
        html += `
            <div class="analysis-card">
                <h5><i class="bi bi-search me-2"></i>Analysis Summary</h5>
                <div class="analysis-text">${analysis.analysis}</div>
            </div>
        `;
    }
    
    if (analysis.key_points && analysis.key_points.length > 0) {
        html += `
            <div class="key-points-card">
                <h5><i class="bi bi-check-circle me-2"></i>Key Observations</h5>
                <ul class="key-points-list">
                    ${analysis.key_points.map(point => `
                        <li><i class="bi bi-arrow-right-circle me-2"></i>${point}</li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
    
    if (analysis.recommendations && analysis.recommendations.length > 0) {
        html += `
            <div class="improvement-opportunities-card">
                <h5><i class="bi bi-lightbulb me-2"></i>Improvement Opportunities</h5>
                <ul class="improvement-opportunities-list">
                    ${analysis.recommendations.map(rec => `
                        <li><i class="bi bi-plus-circle me-2"></i>${rec}</li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
    
    return html || generateNoDataCard();
}

function generateNoDataCard() {
    return `
        <div class="no-data-card">
            <i class="bi bi-info-circle me-2"></i>
            <span>No analysis data available for this stage.</span>
        </div>
    `;
}