/**
 * FIFA World Cup Analytics Dashboard
 * Frontend Application - Chart.js Visualizations
 */

// API Base URL
const API_BASE = '';

// Chart color palette
const COLORS = {
    primary: '#22c55e',
    secondary: '#3b82f6',
    accent: '#d4af37',
    warning: '#f59e0b',
    danger: '#ef4444',
    purple: '#8b5cf6',
    pink: '#ec4899',
    teal: '#14b8a6',
    
    // Gradient arrays
    gradient: {
        green: ['rgba(34, 197, 94, 0.8)', 'rgba(34, 197, 94, 0.2)'],
        blue: ['rgba(59, 130, 246, 0.8)', 'rgba(59, 130, 246, 0.2)'],
        gold: ['rgba(212, 175, 55, 0.8)', 'rgba(212, 175, 55, 0.2)']
    },
    
    // Pie chart colors
    pie: [
        '#22c55e', '#3b82f6', '#f59e0b', '#ef4444', 
        '#8b5cf6', '#ec4899', '#14b8a6', '#6366f1'
    ]
};

// Chart.js default configuration
Chart.defaults.color = '#a0aec0';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.08)';
Chart.defaults.font.family = "'Inter', sans-serif";

// Store chart instances
const charts = {};

// ==================================
// API Functions
// ==================================

async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

// ==================================
// Goals Per World Cup Line Chart
// ==================================

async function initGoalsLineChart() {
    const result = await fetchAPI('/api/goals-per-worldcup');
    if (!result || !result.success) return;
    
    const data = result.data;
    const ctx = document.getElementById('goalsLineChart').getContext('2d');
    
    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 350);
    gradient.addColorStop(0, COLORS.gradient.green[0]);
    gradient.addColorStop(1, COLORS.gradient.green[1]);
    
    charts.goalsLine = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.year),
            datasets: [
                {
                    label: 'Total Goals',
                    data: data.map(d => d.total_goals),
                    borderColor: COLORS.primary,
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: COLORS.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                },
                {
                    label: 'Avg Goals/Match',
                    data: data.map(d => d.avg_goals_per_match),
                    borderColor: COLORS.accent,
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: COLORS.accent,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 15, 26, 0.95)',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 },
                    borderColor: COLORS.accent,
                    borderWidth: 1,
                    callbacks: {
                        afterBody: function(context) {
                            const i = context[0].dataIndex;
                            const d = data[i];
                            return `\nHost: ${d.host}\nWinner: ${d.winner}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'World Cup Year',
                        color: '#a0aec0',
                        font: { size: 12, weight: 'bold' }
                    },
                    grid: { display: false }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Total Goals',
                        color: '#a0aec0',
                        font: { size: 12, weight: 'bold' }
                    },
                    beginAtZero: true
                },
                y1: {
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Avg Goals/Match',
                        color: '#a0aec0',
                        font: { size: 12, weight: 'bold' }
                    },
                    grid: { drawOnChartArea: false },
                    min: 0,
                    max: 6
                }
            }
        }
    });
    
    // Update insight
    updateInsight('insight-goals', result.insight);
}

// ==================================
// Top Teams Bar Chart
// ==================================

async function initTopTeamsChart(metric = 'wins') {
    const result = await fetchAPI(`/api/top-teams?metric=${metric}&limit=10`);
    if (!result || !result.success) return;
    
    const data = result.data;
    const ctx = document.getElementById('topTeamsChart').getContext('2d');
    
    // Determine value field based on metric
    const valueField = metric === 'titles' ? 'titles' : metric;
    
    // Create gradient for bars
    const gradients = data.map((_, i) => {
        const grad = ctx.createLinearGradient(0, 0, 0, 350);
        const hue = 140 + (i * 15); // Green to blue gradient
        grad.addColorStop(0, `hsla(${hue}, 70%, 50%, 0.9)`);
        grad.addColorStop(1, `hsla(${hue}, 70%, 30%, 0.6)`);
        return grad;
    });
    
    // Destroy existing chart
    if (charts.topTeams) charts.topTeams.destroy();
    
    charts.topTeams = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.team),
            datasets: [{
                label: metric.charAt(0).toUpperCase() + metric.slice(1),
                data: data.map(d => d[valueField]),
                backgroundColor: gradients,
                borderColor: COLORS.primary,
                borderWidth: 0,
                borderRadius: 8,
                barThickness: 40
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(10, 15, 26, 0.95)',
                    padding: 12,
                    borderColor: COLORS.accent,
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: metric.charAt(0).toUpperCase() + metric.slice(1),
                        color: '#a0aec0',
                        font: { size: 12, weight: 'bold' }
                    },
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y: {
                    grid: { display: false }
                }
            }
        }
    });
    
    updateInsight('insight-teams', result.insight);
}

// ==================================
// Goals by Stage Grouped Bar Chart
// ==================================

async function initStageChart() {
    const result = await fetchAPI('/api/goals-by-stage');
    if (!result || !result.success) return;
    
    const data = result.data;
    const ctx = document.getElementById('stageChart').getContext('2d');
    
    charts.stage = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.years,
            datasets: [
                {
                    label: 'Group Stage',
                    data: data.group_avg,
                    backgroundColor: COLORS.primary,
                    borderRadius: 4,
                    barPercentage: 0.8,
                    categoryPercentage: 0.7
                },
                {
                    label: 'Knockout Stage',
                    data: data.knockout_avg,
                    backgroundColor: COLORS.secondary,
                    borderRadius: 4,
                    barPercentage: 0.8,
                    categoryPercentage: 0.7
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: { usePointStyle: true }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 15, 26, 0.95)',
                    padding: 12,
                    borderColor: COLORS.accent,
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw.toFixed(2)} goals/match`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'World Cup Year',
                        color: '#a0aec0',
                        font: { size: 11, weight: 'bold' }
                    },
                    grid: { display: false },
                    ticks: { maxRotation: 45, minRotation: 45 }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Avg Goals per Match',
                        color: '#a0aec0',
                        font: { size: 11, weight: 'bold' }
                    },
                    beginAtZero: true,
                    max: 6
                }
            }
        }
    });
    
    updateInsight('insight-stage', result.insight);
}

// ==================================
// Goals by Continent Pie Chart
// ==================================

async function initContinentChart() {
    const result = await fetchAPI('/api/goals-by-continent');
    if (!result || !result.success) return;
    
    const data = result.data;
    const ctx = document.getElementById('continentChart').getContext('2d');
    
    charts.continent = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.continent),
            datasets: [{
                data: data.map(d => d.goals),
                backgroundColor: COLORS.pie,
                borderColor: 'rgba(10, 15, 26, 0.8)',
                borderWidth: 3,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '55%',
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 15, 26, 0.95)',
                    padding: 12,
                    borderColor: COLORS.accent,
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((context.raw / total) * 100).toFixed(1);
                            return `${context.label}: ${context.raw} goals (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
    
    updateInsight('insight-continent', result.insight);
}

// ==================================
// Team Comparison Chart
// ==================================

async function initComparisonChart(team1 = 'Brazil', team2 = 'Germany') {
    const result = await fetchAPI(`/api/team-comparison?team1=${encodeURIComponent(team1)}&team2=${encodeURIComponent(team2)}`);
    if (!result || !result.success) return;
    
    const data = result.data;
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    
    const metrics = ['matches', 'wins', 'goals_scored', 'titles', 'finals'];
    const metricLabels = ['Matches', 'Wins', 'Goals', 'Titles', 'Finals'];
    
    // Destroy existing chart
    if (charts.comparison) charts.comparison.destroy();
    
    charts.comparison = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: metricLabels,
            datasets: [
                {
                    label: data.team1.team,
                    data: metrics.map(m => data.team1[m]),
                    backgroundColor: COLORS.primary,
                    borderRadius: 6
                },
                {
                    label: data.team2.team,
                    data: metrics.map(m => data.team2[m]),
                    backgroundColor: COLORS.secondary,
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: { usePointStyle: true }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 15, 26, 0.95)',
                    padding: 12,
                    borderColor: COLORS.accent,
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                }
            }
        }
    });
    
    // Update H2H stats
    updateH2HStats(data);
    updateInsight('insight-comparison', result.insight);
}

function updateH2HStats(data) {
    const h2h = data.head_to_head;
    const container = document.getElementById('h2h-stats');
    
    container.innerHTML = `
        <div class="h2h-stat">
            <span class="h2h-stat-value">${h2h.team1_wins}</span>
            <span class="h2h-stat-label">${data.team1.team} Wins</span>
        </div>
        <div class="h2h-stat">
            <span class="h2h-stat-value">${h2h.draws}</span>
            <span class="h2h-stat-label">Draws</span>
        </div>
        <div class="h2h-stat">
            <span class="h2h-stat-value">${h2h.team2_wins}</span>
            <span class="h2h-stat-label">${data.team2.team} Wins</span>
        </div>
    `;
}

// ==================================
// Utility Functions
// ==================================

function updateInsight(elementId, text) {
    const el = document.getElementById(elementId);
    if (el) {
        el.querySelector('.insight-text').textContent = text;
    }
}

async function populateTeamSelectors() {
    const result = await fetchAPI('/api/available-teams');
    if (!result || !result.success) return;
    
    const teams = result.data;
    const select1 = document.getElementById('team1-select');
    const select2 = document.getElementById('team2-select');
    
    // Popular teams first
    const popular = ['Brazil', 'Germany', 'Argentina', 'France', 'Italy', 'Spain', 'England', 'Netherlands'];
    const sortedTeams = [...popular.filter(t => teams.includes(t)), ...teams.filter(t => !popular.includes(t))];
    
    const optionsHTML = sortedTeams.map(team => `<option value="${team}">${team}</option>`).join('');
    
    select1.innerHTML = optionsHTML;
    select2.innerHTML = optionsHTML;
    
    // Set defaults
    select1.value = 'Brazil';
    select2.value = 'Germany';
}

// ==================================
// Event Listeners
// ==================================

function setupEventListeners() {
    // Metric toggle buttons
    document.querySelectorAll('.metric-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Update active state
            document.querySelectorAll('.metric-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            // Reload chart with new metric
            initTopTeamsChart(e.target.dataset.metric);
        });
    });
    
    // Compare button
    document.getElementById('compare-btn').addEventListener('click', () => {
        const team1 = document.getElementById('team1-select').value;
        const team2 = document.getElementById('team2-select').value;
        initComparisonChart(team1, team2);
    });
    
    // Smooth scroll for nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').slice(1);
            const target = document.getElementById(targetId);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            
            // Update active state
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

// ==================================
// Initialize Dashboard
// ==================================

async function initDashboard() {
    console.log('🏆 Initializing FIFA World Cup Analytics Dashboard...');
    
    // Populate team selectors first
    await populateTeamSelectors();
    
    // Initialize all charts in parallel
    await Promise.all([
        initGoalsLineChart(),
        initTopTeamsChart('wins'),
        initStageChart(),
        initContinentChart(),
        initComparisonChart('Brazil', 'Germany')
    ]);
    
    // Setup event listeners
    setupEventListeners();
    
    console.log('✅ Dashboard initialized successfully!');
}

// Start the dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', initDashboard);
