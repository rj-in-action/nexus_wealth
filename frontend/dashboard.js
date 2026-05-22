// Nexus Wealth - Advisor Dashboard Frontend Logic
const API_BASE = 'http://localhost:8000/api';
let currentClientId = null;
let currentRunId = null;

// DOM Elements
const clientListEl = document.getElementById('client-list');
const clientSearchEl = document.getElementById('client-search');
const clientCountEl = document.getElementById('client-count');
const emptyStateEl = document.getElementById('empty-state');
const clientViewEl = document.getElementById('client-view');
const runPipelineBtn = document.getElementById('run-pipeline-btn');
const helpBtn = document.getElementById('help-btn');
const helpModal = document.getElementById('help-modal');
const helpModalOverlay = document.getElementById('help-modal-overlay');
const helpModalClose = document.getElementById('help-modal-close');

// Colors for Asset Classes
const ASSET_COLORS = {
    'US Equity': '#4A90E2',
    'Intl Equity': '#8B5CF6',
    'Fixed Income': '#10B981',
    'REITs': '#F59E0B',
    'Commodities': '#F97316',
    'Crypto': '#EC4899',
    'Alternatives': '#6366F1',
    'Cash': '#64748B',
    'Other': '#9CA3AF'
};

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

async function initDashboard() {
    try {
        const response = await fetch(`${API_BASE}/clients`);
        if (!response.ok) throw new Error('Failed to fetch clients');
        const data = await response.json();
        
        renderClientList(data.clients);
        
        clientSearchEl.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const filtered = data.clients.filter(c => 
                c.first_name.toLowerCase().includes(term) || 
                c.last_name.toLowerCase().includes(term) ||
                c.id.toLowerCase().includes(term)
            );
            renderClientList(filtered);
        });

        runPipelineBtn.addEventListener('click', runPipeline);
        document.getElementById('approve-btn').addEventListener('click', () => handleApproval(true));
        document.getElementById('reject-btn').addEventListener('click', () => handleApproval(false));
        helpBtn.addEventListener('click', openHelpModal);
        helpModalOverlay.addEventListener('click', closeHelpModal);
        helpModalClose.addEventListener('click', closeHelpModal);

        // Theme Toggle Logic
        const themeToggleBtn = document.getElementById('theme-toggle');
        const savedTheme = localStorage.getItem('nexus-theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        themeToggleBtn.textContent = savedTheme === 'dark' ? '☀️' : '🌙';

        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('nexus-theme', newTheme);
            themeToggleBtn.textContent = newTheme === 'dark' ? '☀️' : '🌙';
        });

    } catch (err) {
        console.error(err);
        document.getElementById('api-status').querySelector('.status-dot').className = 'status-dot offline';
        document.getElementById('api-status').querySelector('span:last-child').textContent = 'Engine Offline';
    }
}

function renderClientList(clients) {
    clientCountEl.textContent = clients.length;
    clientListEl.innerHTML = '';
    
    clients.forEach(client => {
        const el = document.createElement('div');
        el.className = 'client-item';
        el.dataset.id = client.id;
        
        const formatMoney = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
        
        el.innerHTML = `
            <div class="client-item-header">
                <span class="client-item-name">${client.first_name} ${client.last_name}</span>
                <span class="client-item-aum">${formatMoney(client.total_aum)}</span>
            </div>
            <div class="client-item-meta">
                <span class="tag tag-segment">${client.segment}</span>
                <span class="tag tag-risk">${client.risk_tolerance}</span>
            </div>
        `;
        
        el.addEventListener('click', () => loadClient(client.id, el));
        clientListEl.appendChild(el);
    });
}

async function loadClient(clientId, element) {
    document.querySelectorAll('.client-item').forEach(el => el.classList.remove('active'));
    element.classList.add('active');
    
    currentClientId = clientId;
    emptyStateEl.style.display = 'none';
    clientViewEl.style.display = 'flex';
    
    // Reset Pipeline & Panels
    resetPipeline();
    document.getElementById('recommendations-section').style.display = 'none';
    document.getElementById('compliance-section').style.display = 'none';
    document.getElementById('audit-section').style.display = 'none';

    try {
        const res = await fetch(`${API_BASE}/clients/${clientId}`);
        const data = await res.json();
        const c = data.client;
        const s = data.summary;

        // Populate Header
        document.getElementById('client-avatar').textContent = `${c.first_name[0]}${c.last_name[0]}`;
        document.getElementById('client-name').textContent = `${c.first_name} ${c.last_name}`;
        document.getElementById('client-occupation').textContent = c.occupation;
        document.getElementById('client-segment').textContent = c.segment;
        document.getElementById('client-risk-tag').textContent = `${c.risk_tolerance} Risk`;
        document.getElementById('client-age-tag').textContent = `${c.age} yrs`;

        const formatMoney = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
        
        document.getElementById('stat-aum').textContent = formatMoney(s.total_value);
        document.getElementById('stat-pnl').textContent = formatMoney(s.total_unrealized_gain);
        document.getElementById('stat-pnl').style.color = s.total_unrealized_gain >= 0 ? 'var(--status-online)' : 'var(--status-error)';
        document.getElementById('stat-outside').textContent = formatMoney(s.outside_assets_total);
        document.getElementById('stat-outside-sub').textContent = `${data.outside_assets.length} accounts detected`;
        document.getElementById('stat-income').textContent = formatMoney(c.annual_income);

        renderDonutChart(s.allocation);

    } catch (err) {
        console.error(err);
    }
}

function renderDonutChart(allocation) {
    const chart = document.getElementById('donut-chart');
    const legend = document.getElementById('allocation-legend');
    legend.innerHTML = '';
    
    let conicStr = '';
    let startPct = 0;
    
    const sorted = Object.entries(allocation).sort((a,b) => b[1] - a[1]);
    
    sorted.forEach(([type, pct]) => {
        const color = ASSET_COLORS[type] || ASSET_COLORS['Other'];
        conicStr += `${color} ${startPct}% ${startPct + pct}%, `;
        startPct += pct;
        
        legend.innerHTML += `
            <div class="legend-item">
                <div class="legend-label">
                    <div class="legend-color" style="background: ${color}"></div>
                    <span>${type}</span>
                </div>
                <div class="legend-value">${pct.toFixed(1)}%</div>
            </div>
        `;
    });
    
    chart.style.background = `conic-gradient(${conicStr.slice(0, -2)})`;
}

function resetPipeline() {
    runPipelineBtn.disabled = false;
    runPipelineBtn.innerHTML = '<span class="btn-icon">▶</span> Run Pipeline';
    
    document.querySelectorAll('.pipeline-node').forEach(n => {
        const isSmall = n.classList.contains('node-sm');
        const isHitl = n.classList.contains('node-hitl');
        n.className = 'pipeline-node';
        if (isSmall) n.classList.add('node-sm');
        if (isHitl) n.classList.add('node-hitl');
        n.querySelector('.node-status').textContent = 'Pending';
    });
    
    document.querySelectorAll('.pipeline-connector').forEach(c => c.className = 'pipeline-connector');
    document.getElementById('audit-trail').innerHTML = '';
}

function openHelpModal() {
    helpModal.classList.add('open');
    helpModal.setAttribute('aria-hidden', 'false');
}

function closeHelpModal() {
    helpModal.classList.remove('open');
    helpModal.setAttribute('aria-hidden', 'true');
}

async function runPipeline() {
    if (!currentClientId) return;
    
    resetPipeline();
    runPipelineBtn.disabled = true;
    runPipelineBtn.innerHTML = 'Running...';
    
    document.getElementById('audit-section').style.display = 'block';
    
    try {
        const res = await fetch(`${API_BASE}/pipeline/run/${currentClientId}`, { method: 'POST' });
        const data = await res.json();
        currentRunId = data.run_id;
        document.getElementById('run-id-display').textContent = currentRunId;
        
        listenToPipeline(currentRunId);
    } catch (err) {
        console.error(err);
        runPipelineBtn.disabled = false;
        runPipelineBtn.innerHTML = 'Run Failed';
    }
}

function listenToPipeline(runId) {
    const evtSource = new EventSource(`${API_BASE}/pipeline/status/${runId}`);
    
    evtSource.onmessage = (e) => {
        const event = JSON.parse(e.data);
        console.log(event);
        
        if (event.step > 0 && event.step <= 11) {
            const state = event.status === 'completed' ? 'completed' : (event.status === 'error' ? 'failed' : 'running');
            updateNodeState(event.step, state);
            if (event.step > 1) updateNodeState(event.step - 1, 'completed');
            
            // Add audit entry
            addAuditEntry(event);
        }
        
        if (event.status === 'done') {
            evtSource.close();
            runPipelineBtn.innerHTML = '<span class="btn-icon">✓</span> Pipeline Complete';
            fetchPipelineResults(runId);
        }
        
        if (event.status === 'error' && event.step <= 0) {
            evtSource.close();
            runPipelineBtn.disabled = false;
            runPipelineBtn.innerHTML = 'Run Failed';
            addAuditEntry(event);
        }
    };
    
    evtSource.onerror = (err) => {
        console.error("SSE Error:", err);
        evtSource.close();
    };
}

function updateNodeState(step, state) {
    const node = document.querySelector(`.pipeline-node[data-step="${step}"]`);
    if (node) {
        node.classList.add('active');
        node.classList.remove('running', 'completed', 'failed');
        node.classList.add(state);
        
        const statusEl = node.querySelector('.node-status');
        if(state === 'running') statusEl.textContent = 'Running...';
        else if(state === 'completed') statusEl.textContent = 'Complete';
        else if(state === 'failed') statusEl.textContent = 'Failed';
        
        // Update connector before this node
        const prevConnector = node.previousElementSibling;
        if (prevConnector && prevConnector.classList.contains('pipeline-connector')) {
            if(state === 'running') prevConnector.classList.add('active');
            if(state === 'completed') prevConnector.classList.add('completed');
        }
    }
}

function addAuditEntry(event) {
    const trail = document.getElementById('audit-trail');
    const el = document.createElement('div');
    el.className = `audit-item status-${event.status === 'error' ? 'error' : 'completed'}`;
    
    el.innerHTML = `
        <div class="audit-meta">${event.timestamp}</div>
        <div class="audit-content">
            <div class="audit-header">
                <span class="audit-agent">Step ${event.step}: ${event.name}</span>
                <span class="audit-duration">${event.duration_ms ? event.duration_ms + 'ms' : ''}</span>
            </div>
            <div class="audit-reasoning">${event.reasoning || ''}</div>
        </div>
    `;
    trail.insertBefore(el, trail.firstChild);
}

async function fetchPipelineResults(runId) {
    try {
        const res = await fetch(`${API_BASE}/pipeline/result/${runId}`);
        const data = await res.json();
        
        renderRecommendations(data);
        renderCompliance(data.compliance_results);
        
        runPipelineBtn.innerHTML = '<span class="btn-icon">✓</span> Pipeline Complete';
        
    } catch (err) {
        console.error(err);
    }
}

function renderRecommendations(data) {
    const sec = document.getElementById('recommendations-section');
    const grid = document.getElementById('recommendations-grid');
    const allRecs = [
        ...(data.tax_recommendations || []),
        ...(data.portfolio_recommendations || []),
        ...(data.alt_asset_recommendations || []),
        ...((data.outside_asset_analysis?.migration_strategies || []).map(s => ({
            type: 'outside_asset',
            title: `Migrate ${s.institution} ${s.account_type}`,
            description: `Recommend ${s.recommended_action}. ${s.tax_impact}.`,
            priority: s.priority,
            projected_impact: `$${s.fee_savings} annual fee savings`
        })))
    ];
    
    if (allRecs.length === 0) return;
    
    sec.style.display = 'block';
    document.getElementById('rec-count').textContent = `${allRecs.length} recommendations`;
    grid.innerHTML = '';
    
    // Sort high priority first
    allRecs.sort((a, b) => (a.priority === 'high' ? -1 : 1));
    
    allRecs.forEach(rec => {
        const formatType = (type) => type.replace(/_/g, ' ');
        grid.innerHTML += `
            <div class="rec-card priority-${rec.priority}">
                <div class="rec-header">
                    <div class="rec-title">${rec.title}</div>
                    <div class="rec-type-tag">${formatType(rec.type)}</div>
                </div>
                <div class="rec-desc">${rec.description}</div>
                ${rec.projected_impact ? `<div class="rec-impact">${rec.projected_impact}</div>` : ''}
            </div>
        `;
    });
}

function renderCompliance(compData) {
    const sec = document.getElementById('compliance-section');
    const checksEl = document.getElementById('compliance-checks');
    
    sec.style.display = 'block';
    checksEl.innerHTML = '';
    
    if (!compData.checks) return;
    
    compData.checks.forEach(check => {
        const icon = check.status === 'PASS' ? '✓' : (check.status === 'WARNING' ? '⚠' : '✕');
        const cssClass = check.status.toLowerCase();
        
        checksEl.innerHTML += `
            <div class="check-item ${cssClass}">
                <div class="check-icon">${icon}</div>
                <div class="check-content">
                    <h4>${check.rule_id}</h4>
                    <div class="check-detail">${check.detail}</div>
                </div>
            </div>
        `;
    });
}

async function handleApproval(isApproved) {
    if (!currentRunId) return;
    const notes = document.getElementById('advisor-notes').value;
    
    try {
        const res = await fetch(`${API_BASE}/pipeline/approve/${currentRunId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ approved: isApproved, advisor_notes: notes })
        });
        
        if (res.ok) {
            alert(`Recommendations ${isApproved ? 'Approved & Delivered' : 'Rejected'}.`);
            // Update node 8 visually
            const hitlNode = document.querySelector('.node-hitl');
            hitlNode.classList.remove('running');
            hitlNode.classList.add('completed');
            hitlNode.querySelector('.node-status').textContent = isApproved ? 'Approved' : 'Rejected';
            hitlNode.querySelector('.node-indicator').style.borderColor = isApproved ? 'var(--status-online)' : 'var(--status-error)';
            
            document.getElementById('approve-btn').disabled = true;
            document.getElementById('reject-btn').disabled = true;
        }
    } catch (err) {
        console.error(err);
    }
}
