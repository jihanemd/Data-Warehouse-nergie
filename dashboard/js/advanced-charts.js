// ====================================
// GRAPHES AVANCÉS - DONNÉES COMPLEXES
// Utilise l'API Flask pour les données PostgreSQL
// ====================================

const API_BASE = 'http://localhost:5000/api';
const chartColors = {
  cyan: '#00d4ff',
  pink: '#ff4d7d',
  purple: '#9d5bff',
  green: '#00ff7f',
  orange: '#ffa500',
  blue: '#4a9eff',
  red: '#ff3333',
  yellow: '#ffdd00',
};

// ====================================
// 1. PRODUCTION PAR RÉGION (2020-2024)
// ====================================

async function loadProductionByCity() {
  try {
    const response = await fetch(`${API_BASE}/production-by-city-year`);
    const data = await response.json();

    // Grouper par année et région
    const years = new Set();
    const regions = new Set();
    const matrix = {};

    data.forEach(row => {
      years.add(row.year);
      regions.add(row.city);
      if (!matrix[row.city]) matrix[row.city] = {};
      matrix[row.city][row.year] = row.production_mw || 0;
    });

    const yearArray = Array.from(years).sort();
    const regionArray = Array.from(regions).sort();
    const colors = [chartColors.cyan, chartColors.pink, chartColors.purple, chartColors.orange, chartColors.green];

    const ctx = document.getElementById('productionCityYearChart')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: yearArray,
        datasets: regionArray.slice(0, 5).map((region, idx) => ({
          label: region,
          data: yearArray.map(year => matrix[region]?.[year] || 0),
          backgroundColor: colors[idx % colors.length],
          borderColor: 'transparent',
          borderRadius: 4,
        })),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 10, padding: 10, font: { size: 10 } } },
          tooltip: { backgroundColor: 'rgba(15, 27, 61, 0.9)', padding: 10, borderColor: chartColors.cyan, borderWidth: 1 },
        },
        scales: {
          y: { stacked: false, ticks: { callback: v => v + ' MW' } },
        },
      },
    });
  } catch (error) {
    console.error('Erreur production par ville:', error);
  }
}

// ====================================
// 2. COMPARAISON RÉGIONALE 2024
// ====================================

async function loadCityComparison() {
  try {
    const response = await fetch(`${API_BASE}/city-comparison`);
    const data = await response.json();

    data.sort((a, b) => b.total_production - a.total_production);
    const topRegions = data.slice(0, 8);

    const ctx = document.getElementById('cityComparisonChart')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: topRegions.map(r => r.region),
        datasets: [
          {
            label: 'Production totale (MW)',
            data: topRegions.map(r => r.total_production),
            backgroundColor: chartColors.cyan,
            borderRadius: 4,
          },
          {
            label: 'Installations',
            data: topRegions.map(r => r.nb_installations / 50), // Normalisé pour visualisation
            backgroundColor: chartColors.pink,
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: { position: 'bottom' },
          tooltip: { backgroundColor: 'rgba(15, 27, 61, 0.9)', padding: 10, borderColor: chartColors.cyan, borderWidth: 1 },
        },
      },
    });
  } catch (error) {
    console.error('Erreur comparaison régionale:', error);
  }
}

// ====================================
// 3. TENDANCE PRODUCTION 5 ANS
// ====================================

async function loadProductionTrend() {
  try {
    const response = await fetch(`${API_BASE}/production-trend-5years`);
    const data = await response.json();

    data.sort((a, b) => a.year - b.year || a.month - b.month);

    const labels = data.map(d => `${d.year}-${String(d.month).padStart(2, '0')}`);
    const productions = data.map(d => d.avg_production);

    const ctx = document.getElementById('productionTrendChart')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Production moyenne (MW)',
            data: productions,
            borderColor: chartColors.green,
            backgroundColor: 'rgba(0, 255, 127, 0.1)',
            borderWidth: 2.5,
            fill: true,
            pointRadius: 2,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
          tooltip: { backgroundColor: 'rgba(15, 27, 61, 0.9)', padding: 10 },
        },
        scales: {
          y: { ticks: { callback: v => v + ' MW' } },
        },
      },
    });
  } catch (error) {
    console.error('Erreur tendance production:', error);
  }
}

// ====================================
// 4. MIX ÉNERGÉTIQUE PAR RÉGION
// ====================================

async function loadEnergyMixByCity() {
  try {
    const response = await fetch(`${API_BASE}/energy-mix-by-city`);
    const data = await response.json();

    // Prendre les 3 premières régions
    const regions = Array.from(new Set(data.map(d => d.region))).slice(0, 3);
    const energyTypes = Array.from(new Set(data.map(d => d.energy_type)));
    const colors = [chartColors.orange, chartColors.cyan, chartColors.purple, chartColors.green, chartColors.pink];

    const ctx = document.getElementById('energyMixCityChart')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: data.map(d => `${d.energy_type} (${d.region})`).slice(0, 8),
        datasets: [
          {
            data: data.map(d => d.production_mw).slice(0, 8),
            backgroundColor: colors,
            borderColor: '#1e2e5f',
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 9 } } },
          tooltip: { callbacks: { label: ctx => ctx.label + ': ' + ctx.parsed + ' MW' } },
        },
      },
    });
  } catch (error) {
    console.error('Erreur mix énergétique:', error);
  }
}

// ====================================
// 5. ANALYSE OPTIMISATION
// ====================================

async function loadOptimization() {
  try {
    const response = await fetch(`${API_BASE}/optimization-analysis`);
    const data = await response.json();

    data.sort((a, b) => b.capacity_factor - a.capacity_factor);
    const top = data.slice(0, 15);

    const ctx = document.getElementById('optimizationChart')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: top.map(d => d.plant_name.substring(0, 15)),
        datasets: [
          {
            label: 'Capacity Factor (%)',
            data: top.map(d => d.capacity_factor),
            backgroundColor: top.map((d, i) => i % 2 === 0 ? chartColors.cyan : chartColors.purple),
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => ctx.parsed.x.toFixed(1) + '%' } },
        },
        scales: { x: { ticks: { callback: v => v + '%' } } },
      },
    });
  } catch (error) {
    console.error('Erreur optimisation:', error);
  }
}

// ====================================
// 6. EFFICACITÉ DISTRIBUTION
// ====================================

async function loadDistributionEfficiency() {
  try {
    const response = await fetch(`${API_BASE}/distribution-analysis`);
    const data = await response.json();

    data.sort((a, b) => b.total_production - a.total_production);
    const top = data.slice(0, 10);

    const ctx = document.getElementById('distributionEfficiencyChart')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'scatter',
      data: {
        datasets: top.map((d, idx) => ({
          label: d.region,
          data: [{ x: d.total_production, y: d.distribution_efficiency }],
          backgroundColor: [chartColors.cyan, chartColors.pink, chartColors.purple, chartColors.green, chartColors.orange][idx % 5],
          pointRadius: 12,
          pointHoverRadius: 15,
        })),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 8, font: { size: 9 } } },
          tooltip: {
            callbacks: {
              label: ctx => ctx.raw.x.toFixed(0) + ' MW @ ' + ctx.raw.y.toFixed(1) + '%',
            },
          },
        },
        scales: {
          x: { title: { display: true, text: 'Production (MW)' } },
          y: { title: { display: true, text: 'Efficacité (%)' }, min: 90, max: 100 },
        },
      },
    });
  } catch (error) {
    console.error('Erreur efficacité distribution:', error);
  }
}

// ====================================
// 7. CAPACITÉ INSTALLÉE PAR TYPE
// ====================================

async function loadCapacityByType() {
  try {
    const response = await fetch(`${API_BASE}/capacity-installed`);
    const data = await response.json();

    // Grouper par type d'énergie
    const byType = {};
    data.forEach(d => {
      if (!byType[d.energy_type]) byType[d.energy_type] = 0;
      byType[d.energy_type] += d.capacity_mw;
    });

    const types = Object.keys(byType);
    const capacities = Object.values(byType);
    const colors = [chartColors.orange, chartColors.cyan, chartColors.purple, chartColors.green, chartColors.pink];

    const ctx = document.getElementById('capacityByTypeChart')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'polarArea',
      data: {
        labels: types,
        datasets: [
          {
            data: capacities,
            backgroundColor: colors.slice(0, types.length),
            borderColor: '#ffffff',
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
          tooltip: { callbacks: { label: ctx => ctx.parsed.r.toFixed(0) + ' MW' } },
        },
      },
    });
  } catch (error) {
    console.error('Erreur capacité:', error);
  }
}

// ====================================
// 8. RÉSUMÉ MENSUEL 3 ANS
// ====================================

async function loadMonthlySummary() {
  try {
    const response = await fetch(`${API_BASE}/monthly-summary`);
    const data = await response.json();

    const labels = data.map(d => `${d.year}-${String(d.month).padStart(2, '0')}`);
    const productions = data.map(d => d.production);
    const capacityFactors = data.map(d => d.capacity_factor * 100); // Convertir en %

    const ctx = document.getElementById('monthlySummaryChart')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Production (MW)',
            data: productions,
            borderColor: chartColors.cyan,
            backgroundColor: 'rgba(0, 212, 255, 0.1)',
            borderWidth: 2,
            yAxisID: 'y',
          },
          {
            label: 'Capacity Factor (%)',
            data: capacityFactors,
            borderColor: chartColors.green,
            backgroundColor: 'rgba(0, 255, 127, 0.1)',
            borderWidth: 2,
            yAxisID: 'y1',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { position: 'bottom' } },
        scales: {
          y: { position: 'left', ticks: { callback: v => v + ' MW' } },
          y1: { position: 'right', ticks: { callback: v => v + '%' } },
        },
      },
    });
  } catch (error) {
    console.error('Erreur résumé mensuel:', error);
  }
}

// ====================================
// 9. ANALYSE DISTRIBUTION COMPLÈTE
// ====================================

async function loadDistributionAnalysis() {
  try {
    const response = await fetch(`${API_BASE}/distribution-analysis`);
    const data = await response.json();

    data.sort((a, b) => b.total_production - a.total_production);
    const top = data.slice(0, 8);

    const ctx = document.getElementById('distributionAnalysisChart')?.getContext('2d');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: top.map(d => d.region),
        datasets: [
          {
            label: 'Production totale (MW)',
            data: top.map(d => d.total_production),
            backgroundColor: chartColors.cyan,
            borderRadius: 4,
          },
          {
            label: 'Pertes estimées (MW)',
            data: top.map(d => d.estimated_losses),
            backgroundColor: chartColors.red,
            borderRadius: 4,
          },
          {
            label: 'Distribution nette (MW)',
            data: top.map(d => d.net_distribution),
            backgroundColor: chartColors.green,
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
          tooltip: { backgroundColor: 'rgba(15, 27, 61, 0.9)', padding: 10 },
        },
        scales: {
          y: { stacked: false, ticks: { callback: v => v + ' MW' } },
        },
      },
    });
  } catch (error) {
    console.error('Erreur analyse distribution:', error);
  }
}

// ====================================
// INITIALISATION
// ====================================

window.addEventListener('load', () => {
  console.log('📊 Chargement des graphes avancés...');
  loadProductionByCity();
  loadCityComparison();
  loadProductionTrend();
  loadEnergyMixByCity();
  loadOptimization();
  loadDistributionEfficiency();
  loadCapacityByType();
  loadMonthlySummary();
  loadDistributionAnalysis();
  console.log('✅ Graphes avancés chargés!');
});
