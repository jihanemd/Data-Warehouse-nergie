// ====================================
// APPLICATION DASHBOARD - APP.JS
// ====================================

console.log('🚀 Dashboard Énergie France - Démarrage...');

// ====================================
// NAVIGATION
// ====================================

function navigate(page) {
  console.log(`📍 Navigation vers: ${page}`);
  
  // Mettre à jour les nav-items actifs
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active');
  });
  event.target.closest('.nav-item')?.classList.add('active');
  
  // Afficher notification simple
  showNotification(`Redirection vers ${page}...`, 'info');
}

// ====================================
// NOTIFICATIONS
// ====================================

function showNotification(message, type = 'success') {
  // Créer la notification
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === 'success' ? 'rgba(0, 255, 127, 0.2)' : 'rgba(0, 212, 255, 0.2)'};
    border: 1px solid ${type === 'success' ? '#00ff7f' : '#00d4ff'};
    color: ${type === 'success' ? '#00ff7f' : '#00d4ff'};
    padding: 15px 20px;
    border-radius: 8px;
    z-index: 9999;
    animation: slideIn 0.3s ease-out;
    font-size: 14px;
    font-weight: 500;
  `;
  
  notification.textContent = message;
  document.body.appendChild(notification);
  
  // Supprimer après 3 secondes
  setTimeout(() => {
    notification.style.animation = 'fadeOut 0.3s ease-out';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// ====================================
// ACTUALISATION DES DONNÉES
// ====================================

function refreshDashboard() {
  console.log('🔄 Actualisation du dashboard...');
  
  // Animation du bouton
  const btn = event.target.closest('.btn-primary');
  if (btn) {
    const icon = btn.querySelector('i');
    icon.style.animation = 'spin 0.6s ease-in-out';
    
    setTimeout(() => {
      icon.style.animation = 'none';
    }, 600);
  }
  
  // Simuler un appel API
  setTimeout(() => {
    showNotification('✅ Dashboard actualisé avec succès!', 'success');
  }, 500);
}

// Ajouter l'événement au bouton Actualiser
document.addEventListener('DOMContentLoaded', function() {
  const refreshBtn = document.querySelector('.btn-primary');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', refreshDashboard);
  }
});

// ====================================
// ANIMATIONS SPINNER
// ====================================

const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
  
  @keyframes fadeOut {
    from {
      opacity: 1;
      transform: translateX(0);
    }
    to {
      opacity: 0;
      transform: translateX(20px);
    }
  }
`;
document.head.appendChild(style);

// ====================================
// HOVER EFFECTS SUR LES CARTES
// ====================================

document.querySelectorAll('.kpi-card').forEach(card => {
  card.addEventListener('mouseenter', function() {
    this.style.transform = 'translateY(-4px)';
  });
  
  card.addEventListener('mouseleave', function() {
    this.style.transform = 'translateY(0)';
  });
});

// ====================================
// ANIMATIONS DES GRAPHIQUES
// ====================================

function animateValue(element, start, end, duration = 1000) {
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    const value = Math.floor(progress * (end - start) + start);
    element.textContent = value;
    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
}

// Animer les KPI values au chargement
document.addEventListener('DOMContentLoaded', function() {
  const kpiValues = document.querySelectorAll('.kpi-value');
  
  kpiValues.forEach((element, index) => {
    // Extraire le nombre de la valeur
    const text = element.textContent.trim();
    const numberMatch = text.match(/\d+/);
    
    if (numberMatch) {
      const targetValue = parseInt(numberMatch[0]);
      // Délai escalonné
      setTimeout(() => {
        animateValue(element, 0, targetValue, 1000);
      }, index * 100);
    }
  });
});

// ====================================
// INDICATEURS EN TEMPS RÉEL
// ====================================

function updateRealTimeIndicators() {
  // Simulation de mise à jour temps réel
  setInterval(() => {
    const randomChange = (Math.random() - 0.5) * 5; // ±2.5%
    const randomValue = Math.floor(Math.random() * 100) + 1100;
    
    // Mettre à jour la production totale (simulation)
    const productionElement = document.querySelector('.kpi-value');
    if (productionElement) {
      const current = parseInt(productionElement.textContent);
      const newValue = current + Math.floor(randomChange);
      // Optionnel: uncomment pour voir les changements
      // productionElement.textContent = newValue + ' MW';
    }
  }, 5000); // Update toutes les 5 secondes
}

// Lancer les mises à jour temps réel
updateRealTimeIndicators();

// ====================================
// EXPORT DE DONNÉES
// ====================================

function exportDashboardData() {
  const data = {
    timestamp: new Date().toISOString(),
    production: {
      total: 1234,
      solar: 342,
      wind: 567,
      hydro: 298,
      thermal: 145,
      other: 82,
    },
    capacity: {
      total: 28.5,
      installed: [
        { region: 'Hauts-de-France', capacity: 4.5 },
        { region: 'Auvergne-Rhône-Alpes', capacity: 3.8 },
        { region: 'Occitanie', capacity: 3.2 },
      ],
    },
    efficiency: {
      networkUsage: 87,
      availableCapacity: 64,
      solarPerformance: 79,
    },
  };
  
  return JSON.stringify(data, null, 2);
}

// ====================================
// THÈME SOMBRE/CLAIR
// ====================================

function toggleTheme() {
  const isDark = document.body.style.filter === 'invert(1)';
  document.body.style.filter = isDark ? 'none' : 'invert(1)';
  localStorage.setItem('dashboardTheme', isDark ? 'light' : 'dark');
}

// Charger le thème sauvegardé
window.addEventListener('DOMContentLoaded', function() {
  const savedTheme = localStorage.getItem('dashboardTheme');
  if (savedTheme === 'light') {
    document.body.style.filter = 'invert(1)';
  }
});

// ====================================
// DEBUG INFO
// ====================================

console.log('✅ Dashboard initialisé avec succès!');
console.log('📊 Données disponibles:');
console.log('   - 4 KPI cards');
console.log('   - 4 graphiques interactifs');
console.log('   - Table des installations');
console.log('   - 1 carte de régions');
console.log('📱 Responsive: Desktop, Tablet, Mobile');
console.log('🎨 Thème: Dark Mode Cyan/Rose/Violet');

// ====================================
// EVENT LISTENERS GLOBAUX
// ====================================

// Ctrl+P pour exporter
document.addEventListener('keydown', function(event) {
  if (event.ctrlKey && event.key === 'p') {
    event.preventDefault();
    const data = exportDashboardData();
    console.log('📥 Données exportées:', data);
    showNotification('✅ Données exportées en console');
  }
});

// Ctrl+D pour dark/light mode
document.addEventListener('keydown', function(event) {
  if (event.ctrlKey && event.key === 'd') {
    event.preventDefault();
    toggleTheme();
    showNotification('🎨 Thème changé');
  }
});

console.log('💡 Raccourcis clavier:');
console.log('   Ctrl+P: Exporter données');
console.log('   Ctrl+D: Changer thème');
