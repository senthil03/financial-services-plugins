// Antigravity Financial Dashboard Controller

const metaDataConfig = {
    'AMZN': { beta: 'Moderate', sentiment: 'Relief Tech Rotation' },
    'GOOG': { beta: 'Moderate', sentiment: 'Relief Tech Rotation' },
    'NFLX': { beta: 'Low', sentiment: 'Safe-Haven Resilience' },
    'BETA': { beta: 'High', sentiment: 'Post-Rotation Stability' },
    'INFY': { beta: 'Moderate', sentiment: 'Bullish India Bias (PCR 1.26)' },
    'IONQ': { beta: 'High', sentiment: 'High-Beta Rebound' },
    'ACHR': { beta: 'High', sentiment: 'Speculative Interest' },
    'NTLA': { beta: 'High', sentiment: 'Relief Momentum' },
    'JOBY': { beta: 'High', sentiment: 'Speculative Interest' }
};

let portfolioData = {
    totalValue: 0,
    cash: 0,
    assets: []
};

// --- Countdown Timer ---
function updateCountdown() {
    // Islamabad Talks Start: April 10, 2026, 08:00 AM ET (12:00 UTC)
    const targetDate = new Date('April 10, 2026 12:00:00 UTC').getTime();
    const now = new Date().getTime();
    const difference = targetDate - now;

    if (difference < 0) {
        document.getElementById('countdown').innerHTML = "DEADLINE REACHED";
        return;
    }

    const days = Math.floor(difference / (1000 * 60 * 60 * 24));
    const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((difference % (1000 * 60)) / 1000);

    document.getElementById('days').innerText = days.toString().padStart(2, '0');
    document.getElementById('hours').innerText = hours.toString().padStart(2, '0');
    document.getElementById('minutes').innerText = minutes.toString().padStart(2, '0');
    document.getElementById('seconds').innerText = seconds.toString().padStart(2, '0');
}

setInterval(updateCountdown, 1000);
updateCountdown();

// --- Charts ---
let diversificationChart, weightingChart;

function initCharts() {
    const ctx1 = document.getElementById('diversificationChart').getContext('2d');
    diversificationChart = new Chart(ctx1, {
        type: 'doughnut',
        data: {
            labels: ['Big Tech', 'High Beta', 'India', 'Cash'],
            datasets: [{
                data: [13549, 6535, 1760, 1768],
                backgroundColor: ['#7c4dff', '#00e5ff', '#ffb100', 'rgba(255,255,255,0.2)'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            cutout: '70%'
        }
    });

    const ctx2 = document.getElementById('weightingChart').getContext('2d');
    weightingChart = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: portfolioData.assets.map(a => a.ticker),
            datasets: [{
                label: 'Position Value ($)',
                data: portfolioData.assets.map(a => a.value),
                backgroundColor: 'rgba(124, 77, 255, 0.4)',
                borderColor: '#7c4dff',
                borderWidth: 1,
                borderRadius: 8
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, border: { display: false } },
                x: { grid: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

// --- Data Retrieval ---
async function loadPortfolioData() {
    try {
        // Cache-busting ensures that browser-refresh always pulls latest file
        const response = await fetch('./portfolio_result.json?t=' + Date.now());
        const raw = await response.json();
        
        // Parse raw JSON to internal format
        portfolioData.assets = raw.summary.map(item => {
            const meta = metaDataConfig[item.Asset] || { beta: 'Unknown', sentiment: 'No Data' };
            return {
                ticker: item.Asset,
                name: item.Name,
                value: item['Net Value'],
                price: item.Price,
                beta: meta.beta,
                sentiment: meta.sentiment
            };
        });

        // Calculate total value and cash dynamically from JSON
        portfolioData.cash = raw.available_credit || 0;
        portfolioData.totalValue = portfolioData.assets.reduce((sum, a) => sum + a.value, 0) + portfolioData.cash;

        // Update UI Timestamp
        const now = new Date();
        document.getElementById('last-updated').innerText = `LAST SYNC: ${now.toLocaleTimeString()}`;

        renderAssets();
        initCharts();
    } catch (e) {
        console.error("Dashboard Sync Failed:", e);
        document.getElementById('last-updated').innerText = "SYNC FAILED";
    }
}
function renderAssets(isCrisis = false) {
    const grid = document.getElementById('asset-grid');
    grid.innerHTML = '';
    
    let simulatedTotal = portfolioData.cash;

    portfolioData.assets.forEach(asset => {
        let displayValue = asset.value;
        let deltaClass = 'positive';
        let deltaText = 'STABLE';

        if (isCrisis) {
            displayValue = asset.value * 0.88;
            deltaClass = 'negative';
            deltaText = 'STALL -12%';
        }

        simulatedTotal += displayValue;

        const card = document.createElement('div');
        card.className = 'asset-card glass';
        card.innerHTML = `
            <div class="asset-info-header">
                <div>
                    <span class="asset-ticker">${asset.ticker}</span>
                    <span class="asset-name">/ ${asset.name}</span>
                </div>
                <span class="status-pill ${deltaClass}" style="font-size: 8px; font-weight: 800; border: 1px solid; padding: 2px 6px; border-radius: 10px;">${deltaText}</span>
            </div>
            <div class="asset-price-main">$${displayValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
            <div class="card-label" style="font-weight: 600; color: var(--accent-secondary); margin-bottom: 5px;">Share Price: $${asset.price.toFixed(2)}</div>
            <div class="card-label">RISK: ${asset.beta}</div>
            <div class="options-sentiment" style="margin-top: 10px; font-size: 10px; color: var(--accent-secondary); font-weight: 600;">
                <span style="color: var(--text-secondary); font-weight: 400; font-size: 9px; display: block; margin-bottom: 2px;">SMART MONEY SENTIMENT:</span>
                ${asset.sentiment} <span style="color: var(--text-primary); opacity: 0.8;">[P/C Ratio: ${asset.pcRatio}]</span>
            </div>
        `;
        grid.appendChild(card);
    });

    document.getElementById('total-net-value').innerText = `$${simulatedTotal.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
}

// --- Event Listeners ---
document.getElementById('crisis-toggle').addEventListener('change', (e) => {
    renderAssets(e.target.checked);
});

// --- Initialize ---
window.onload = () => {
    loadPortfolioData();
    // Auto-poll for new data every 30 seconds
    setInterval(loadPortfolioData, 30000);
};
