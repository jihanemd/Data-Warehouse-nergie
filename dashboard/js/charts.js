// ====================================
// CONFIGURATION CHART.JS GLOBAL
// ====================================

Chart.defaults.color = '#a0aec0';
Chart.defaults.borderColor = '#2d3e6f';
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.plugins.legend.labels.usePointStyle = true;

// Couleurs du projet
const chartColors = {
  cyan: '#00d4ff',
  pink: '#ff4d7d',
  purple: '#9d5bff',
  green: '#00ff7f',
  orange: '#ffa500',
  blue: '#4a9eff',
};

// ====================================
// PRODUCTION PAR TYPE (BAR CHART)
// ====================================

const productionCtx = document.getElementById('productionChart')?.getContext('2d');
if (productionCtx) {
  new Chart(productionCtx, {
    type: 'bar',
    data: {
      labels: ['Solaire', 'Éolien', 'Hydro', 'Thermique', 'Autres'],
      datasets: [
        {
          label: 'Production (MW)',
          data: [342, 567, 298, 145, 82],
          backgroundColor: [
            chartColors.orange,
            chartColors.purple,
            chartColors.cyan,
            chartColors.pink,
            chartColors.green,
          ],
          borderRadius: 6,
          borderSkipped: false,
          hoverBackgroundColor: [
            '#ffb84d',
            '#b385ff',
            '#33e5ff',
            '#ff6d95',
            '#33ff99',
          ],
          borderColor: 'transparent',
          barPercentage: 0.7,
          categoryPercentage: 0.8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return context.parsed.y + ' MW';
            },
          },
          backgroundColor: 'rgba(15, 27, 61, 0.9)',
          padding: 12,
          borderColor: chartColors.cyan,
          borderWidth: 1,
          titleColor: chartColors.cyan,
          bodyColor: '#ffffff',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(45, 62, 111, 0.3)',
            drawBorder: false,
          },
          ticks: {
            callback: function (value) {
              return value + ' MW';
            },
          },
        },
        x: {
          grid: {
            display: false,
          },
        },
      },
    },
  });
}

// ====================================
// PRODUCTION HORAIRE (LINE CHART)
// ====================================

const hourlyCtx = document.getElementById('hourlyChart')?.getContext('2d');
if (hourlyCtx) {
  new Chart(hourlyCtx, {
    type: 'line',
    data: {
      labels: [
        '00h',
        '01h',
        '02h',
        '03h',
        '04h',
        '05h',
        '06h',
        '07h',
        '08h',
        '09h',
        '10h',
        '11h',
        '12h',
        '13h',
        '14h',
        '15h',
        '16h',
        '17h',
        '18h',
        '19h',
        '20h',
        '21h',
        '22h',
        '23h',
      ],
      datasets: [
        {
          label: 'Production totale',
          data: [
            850, 820, 780, 750, 740, 760, 810, 920, 1050, 1150, 1220, 1280, 1300, 1310, 1290,
            1250, 1180, 1100, 1020, 950, 900, 880, 850, 830,
          ],
          borderColor: chartColors.cyan,
          backgroundColor: 'rgba(0, 212, 255, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: chartColors.cyan,
          pointBorderColor: '#1e2e5f',
          pointBorderWidth: 2,
          borderWidth: 2,
        },
        {
          label: 'Consommation',
          data: [
            1100, 1080, 1050, 1020, 1000, 1050, 1150, 1250, 1350, 1400, 1420, 1380, 1350, 1320,
            1300, 1320, 1350, 1380, 1400, 1350, 1280, 1200, 1150, 1100,
          ],
          borderColor: chartColors.pink,
          backgroundColor: 'rgba(255, 77, 125, 0.05)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: chartColors.pink,
          pointBorderColor: '#1e2e5f',
          pointBorderWidth: 2,
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            boxWidth: 12,
            padding: 15,
            font: {
              size: 12,
              weight: '600',
            },
          },
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(15, 27, 61, 0.9)',
          padding: 12,
          borderColor: chartColors.cyan,
          borderWidth: 1,
          titleColor: chartColors.cyan,
          bodyColor: '#ffffff',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(45, 62, 111, 0.3)',
            drawBorder: false,
          },
          ticks: {
            callback: function (value) {
              return value + ' MW';
            },
          },
        },
        x: {
          grid: {
            display: false,
          },
        },
      },
    },
  });
}

// ====================================
// CAPACITÉ PAR RÉGION (HORIZONTAL BAR)
// ====================================

const capacityCtx = document.getElementById('capacityChart')?.getContext('2d');
if (capacityCtx) {
  new Chart(capacityCtx, {
    type: 'bar',
    data: {
      labels: [
        'Hauts-de-France',
        'Auvergne-Rhône-Alpes',
        'Occitanie',
        'Nouvelle-Aquitaine',
        'PACA',
        'Grand-Est',
        'Bretagne',
      ],
      datasets: [
        {
          label: 'Capacité (GW)',
          data: [4.5, 3.8, 3.2, 2.9, 2.6, 2.3, 2.1],
          backgroundColor: chartColors.purple,
          borderRadius: 6,
          borderSkipped: false,
          hoverBackgroundColor: chartColors.pink,
        },
      ],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return context.parsed.x + ' GW';
            },
          },
          backgroundColor: 'rgba(15, 27, 61, 0.9)',
          padding: 12,
          borderColor: chartColors.cyan,
          borderWidth: 1,
          bodyColor: '#ffffff',
        },
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: {
            color: 'rgba(45, 62, 111, 0.3)',
            drawBorder: false,
          },
          ticks: {
            callback: function (value) {
              return value + ' GW';
            },
          },
        },
        y: {
          grid: {
            display: false,
          },
        },
      },
    },
  });
}

// ====================================
// RÉPARTITION ÉNERGIES (DOUGHNUT CHART)
// ====================================

const pieCtx = document.getElementById('pieChart')?.getContext('2d');
if (pieCtx) {
  new Chart(pieCtx, {
    type: 'doughnut',
    data: {
      labels: ['Solaire', 'Éolien', 'Hydro', 'Thermique', 'Autres'],
      datasets: [
        {
          data: [28, 36, 19, 9, 8],
          backgroundColor: [
            chartColors.orange,
            chartColors.purple,
            chartColors.cyan,
            chartColors.pink,
            chartColors.green,
          ],
          borderColor: '#1e2e5f',
          borderWidth: 2,
          hoverBorderColor: '#ffffff',
          hoverBorderWidth: 3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            padding: 15,
            font: {
              size: 12,
              weight: '500',
            },
          },
        },
        tooltip: {
          backgroundColor: 'rgba(15, 27, 61, 0.9)',
          padding: 12,
          borderColor: chartColors.cyan,
          borderWidth: 1,
          callbacks: {
            label: function (context) {
              return context.label + ': ' + context.parsed + '%';
            },
          },
        },
      },
    },
  });
}

// ====================================
// PRODUCTION PAR ANNÉE (LINE CHART)
// ====================================

const yearlyCtx = document.getElementById('yearlyChart')?.getContext('2d');
if (yearlyCtx) {
  new Chart(yearlyCtx, {
    type: 'line',
    data: {
      labels: ['2018', '2019', '2020', '2021', '2022', '2023', '2024'],
      datasets: [
        {
          label: 'Production totale',
          data: [450, 512, 598, 687, 756, 842, 945],
          borderColor: chartColors.cyan,
          backgroundColor: 'rgba(0, 212, 255, 0.1)',
          borderWidth: 3,
          fill: true,
          pointRadius: 5,
          pointBackgroundColor: chartColors.cyan,
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointHoverRadius: 7,
          tension: 0.4,
        },
        {
          label: 'Production solaire',
          data: [45, 62, 89, 125, 178, 245, 342],
          borderColor: chartColors.orange,
          backgroundColor: 'rgba(255, 165, 0, 0.1)',
          borderWidth: 2,
          fill: true,
          pointRadius: 4,
          pointBackgroundColor: chartColors.orange,
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          tension: 0.4,
          borderDash: [5, 5],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            padding: 10,
            font: {
              size: 11,
            },
          },
        },
        tooltip: {
          backgroundColor: 'rgba(15, 27, 61, 0.9)',
          padding: 12,
          borderColor: chartColors.cyan,
          borderWidth: 1,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return value + ' MW';
            },
          },
        },
      },
    },
  });
}

// ====================================
// CROISSANCE ANNUELLE (COLUMN CHART)
// ====================================

const growthCtx = document.getElementById('growthChart')?.getContext('2d');
if (growthCtx) {
  new Chart(growthCtx, {
    type: 'bar',
    data: {
      labels: ['2019', '2020', '2021', '2022', '2023', '2024'],
      datasets: [
        {
          label: 'Croissance (%)',
          data: [13.8, 16.8, 14.9, 10.0, 11.4, 12.2],
          backgroundColor: [
            'rgba(0, 212, 255, 0.7)',
            'rgba(0, 212, 255, 0.75)',
            'rgba(0, 212, 255, 0.8)',
            'rgba(0, 212, 255, 0.85)',
            'rgba(0, 212, 255, 0.9)',
            'rgba(0, 212, 255, 0.95)',
          ],
          borderColor: chartColors.cyan,
          borderWidth: 1.5,
          borderRadius: 4,
          hoverBackgroundColor: chartColors.cyan,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: 'rgba(15, 27, 61, 0.9)',
          padding: 12,
          borderColor: chartColors.cyan,
          borderWidth: 1,
          callbacks: {
            label: function (context) {
              return context.parsed.x.toFixed(1) + '%';
            },
          },
        },
      },
      scales: {
        x: {
          ticks: {
            callback: function (value) {
              return value.toFixed(0) + '%';
            },
          },
        },
      },
    },
  });
}

// ====================================
// CARTE SIG (LEAFLET MAP)
// ====================================

function initMap() {
  const mapContainer = document.getElementById('map-container');
  if (!mapContainer) return;

  // Créer la carte centrée sur la France
  const map = L.map('map-container', {
    center: [46.5, 2.0],
    zoom: 6,
    scrollWheelZoom: false,
    attributionControl: true,
  });

  // Couche de tuiles (dark theme)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap © CartoDB',
    subdomains: 'abcd',
    maxZoom: 20,
    className: 'leaflet-dark-tiles',
  }).addTo(map);

  // Données d'installations énergétiques
  const installations = [
    {
      name: 'Centrale Solaire Nord',
      type: 'Solaire',
      lat: 50.5,
      lng: 3.5,
      capacity: 125.5,
      color: chartColors.orange,
      icon: '☀️',
    },
    {
      name: 'Parc Éolien Est',
      type: 'Éolien',
      lat: 48.5,
      lng: 6.0,
      capacity: 234.2,
      color: chartColors.purple,
      icon: '💨',
    },
    {
      name: 'Barrage Hydro Centre',
      type: 'Hydro',
      lat: 46.0,
      lng: 2.5,
      capacity: 156.8,
      color: chartColors.cyan,
      icon: '💧',
    },
    {
      name: 'Parc Solaire Ouest',
      type: 'Solaire',
      lat: 45.0,
      lng: -0.5,
      capacity: 198.3,
      color: chartColors.orange,
      icon: '☀️',
    },
    {
      name: 'Éolien offshore Sud',
      type: 'Éolien',
      lat: 43.0,
      lng: 5.0,
      capacity: 287.5,
      color: chartColors.purple,
      icon: '💨',
    },
  ];

  // Ajouter les marqueurs
  installations.forEach((inst) => {
    const marker = L.circleMarker([inst.lat, inst.lng], {
      radius: 10,
      fillColor: inst.color,
      color: '#ffffff',
      weight: 2.5,
      opacity: 0.9,
      fillOpacity: 0.8,
    }).addTo(map);

    // Popup avec infos
    const popupContent = `
      <div style="font-size: 12px; color: #a0aec0;">
        <strong style="color: #00d4ff;">${inst.icon} ${inst.name}</strong><br>
        Type: <strong>${inst.type}</strong><br>
        Capacité: <strong>${inst.capacity} MW</strong>
      </div>
    `;

    marker.bindPopup(popupContent);
  });

  // Bouton de contrôle personnalisé
  const controlDiv = document.createElement('div');
  controlDiv.style.backgroundColor = '#1e2e5f';
  controlDiv.style.border = '1px solid #2d3e6f';
  controlDiv.style.borderRadius = '4px';
  controlDiv.style.padding = '10px';
  controlDiv.style.cursor = 'pointer';
  controlDiv.style.color = '#00d4ff';
  controlDiv.style.fontSize = '12px';
  controlDiv.style.fontWeight = 'bold';
  controlDiv.innerHTML = '🔄 Réinitialiser';
  controlDiv.onclick = () => map.setView([46.5, 2.0], 6);

  const control = L.Control.extend({
    onAdd: () => controlDiv,
  });

  map.addControl(new control({ position: 'topleft' }));

  // Redimensionner la carte après chargement
  setTimeout(() => map.invalidateSize(), 200);
}

// Initialiser la carte au chargement
window.addEventListener('load', initMap);

// ====================================
// CONSOMMATION PAR SECTEUR (BAR)
// ====================================

const consumptionSectorCtx = document.getElementById('consumptionSectorChart')?.getContext('2d');
if (consumptionSectorCtx) {
  new Chart(consumptionSectorCtx, {
    type: 'bar',
    data: {
      labels: ['Industrie', 'Résidentiel', 'Tertiaire', 'Agriculture', 'Transport'],
      datasets: [
        {
          label: 'Consommation (TWh)',
          data: [189, 152, 98, 42, 67],
          backgroundColor: [
            chartColors.pink,
            chartColors.cyan,
            chartColors.purple,
            chartColors.green,
            chartColors.orange,
          ],
          borderRadius: 6,
          borderSkipped: false,
          hoverBackgroundColor: [
            '#ff6d95',
            '#33e5ff',
            '#b385ff',
            '#33ff99',
            '#ffb84d',
          ],
          borderColor: 'transparent',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: 'rgba(15, 27, 61, 0.9)',
          padding: 12,
          borderColor: chartColors.pink,
          borderWidth: 1,
          callbacks: {
            label: function (context) {
              return context.parsed.x.toFixed(1) + ' TWh';
            },
          },
        },
      },
      scales: {
        x: {
          ticks: {
            callback: function (value) {
              return value + ' TWh';
            },
          },
        },
      },
    },
  });
}

// ====================================
// CONSOMMATION PAR RÉGION (RADAR)
// ====================================

const consumptionRegionCtx = document.getElementById('consumptionRegionChart')?.getContext('2d');
if (consumptionRegionCtx) {
  new Chart(consumptionRegionCtx, {
    type: 'radar',
    data: {
      labels: ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Hauts-de-France', 'Nouvelle-Aquitaine', 'Provence-Alpes-Côte d\'Azur'],
      datasets: [
        {
          label: 'Consommation (TWh)',
          data: [152, 98, 87, 76, 64],
          borderColor: chartColors.cyan,
          backgroundColor: 'rgba(0, 212, 255, 0.2)',
          borderWidth: 2,
          pointBackgroundColor: chartColors.cyan,
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
        },
        tooltip: {
          backgroundColor: 'rgba(15, 27, 61, 0.9)',
          padding: 12,
          borderColor: chartColors.cyan,
          borderWidth: 1,
        },
      },
      scales: {
        r: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return value + ' TWh';
            },
          },
        },
      },
    },
  });
}

// ====================================
// CONSOMMATION HORAIRE (LINE)
// ====================================

const consumptionHourlyCtx = document.getElementById('consumptionHourlyChart')?.getContext('2d');
if (consumptionHourlyCtx) {
  new Chart(consumptionHourlyCtx, {
    type: 'line',
    data: {
      labels: ['00h', '02h', '04h', '06h', '08h', '10h', '12h', '14h', '16h', '18h', '20h', '22h'],
      datasets: [
        {
          label: 'Consommation (GW)',
          data: [32.5, 28.1, 24.3, 26.8, 42.1, 51.2, 58.9, 56.3, 62.1, 68.5, 65.2, 48.9],
          borderColor: chartColors.pink,
          backgroundColor: 'rgba(255, 77, 125, 0.1)',
          borderWidth: 2.5,
          fill: true,
          pointRadius: 4,
          pointBackgroundColor: chartColors.pink,
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: 'rgba(15, 27, 61, 0.9)',
          padding: 12,
          borderColor: chartColors.pink,
          borderWidth: 1,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return value + ' GW';
            },
          },
        },
      },
    },
  });
}

// ====================================
// TENDANCE CONSOMMATION 12 MOIS (LINE)
// ====================================

const consumptionTrendCtx = document.getElementById('consumptionTrendChart')?.getContext('2d');
if (consumptionTrendCtx) {
  new Chart(consumptionTrendCtx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec'],
      datasets: [
        {
          label: 'Consommation 2024',
          data: [548, 521, 478, 421, 365, 342, 378, 385, 412, 468, 521, 562],
          borderColor: chartColors.orange,
          backgroundColor: 'rgba(255, 165, 0, 0.1)',
          borderWidth: 2.5,
          fill: true,
          pointRadius: 4,
          pointBackgroundColor: chartColors.orange,
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          tension: 0.4,
        },
        {
          label: 'Moyenne 2023',
          data: [542, 515, 472, 428, 372, 348, 385, 392, 418, 475, 528, 555],
          borderColor: chartColors.green,
          borderWidth: 2,
          borderDash: [5, 5],
          fill: false,
          pointRadius: 3,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            padding: 10,
          },
        },
        tooltip: {
          backgroundColor: 'rgba(15, 27, 61, 0.9)',
          padding: 12,
          borderColor: chartColors.orange,
          borderWidth: 1,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return value + ' TWh';
            },
          },
        },
      },
    },
  });
}

// ====================================
// CONSOMMATION VS PRODUCTION (AREA CHART)
// ====================================

const balanceCtx = document.getElementById('balanceChart')?.getContext('2d');
if (balanceCtx) {
  new Chart(balanceCtx, {
    type: 'line',
    data: {
      labels: ['00h', '02h', '04h', '06h', '08h', '10h', '12h', '14h', '16h', '18h', '20h', '22h'],
      datasets: [
        {
          label: 'Production (GW)',
          data: [38.2, 35.8, 32.1, 36.5, 45.2, 58.3, 72.1, 68.9, 75.3, 82.1, 78.5, 58.2],
          borderColor: chartColors.cyan,
          backgroundColor: 'rgba(0, 212, 255, 0.15)',
          borderWidth: 2.5,
          fill: true,
          pointRadius: 3,
          tension: 0.4,
        },
        {
          label: 'Consommation (GW)',
          data: [32.5, 28.1, 24.3, 26.8, 42.1, 51.2, 58.9, 56.3, 62.1, 68.5, 65.2, 48.9],
          borderColor: chartColors.pink,
          backgroundColor: 'rgba(255, 77, 125, 0.15)',
          borderWidth: 2.5,
          fill: true,
          pointRadius: 3,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            padding: 10,
          },
        },
        tooltip: {
          backgroundColor: 'rgba(15, 27, 61, 0.9)',
          padding: 12,
          borderColor: chartColors.cyan,
          borderWidth: 1,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return value + ' GW';
            },
          },
        },
      },
    },
  });
}

console.log('✅ Tous les graphiques, consommation et carte SIG sont chargés!');


