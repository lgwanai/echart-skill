/**
 * Dashboard Interaction Script
 * Provides interactive features: theme toggle, refresh, export, filters
 */

class DashboardController {
  constructor(options = {}) {
    this.charts = options.charts || [];
    this.config = options.config || {};
    this.theme = localStorage.getItem('dashboard-theme') || 'light';
    this.autoRefreshInterval = null;
    
    this.init();
  }
  
  init() {
    this.applyTheme(this.theme);
    this.setupEventListeners();
    this.startAutoRefresh();
  }
  
  /**
   * Apply theme (light/dark)
   */
  applyTheme(theme) {
    this.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('dashboard-theme', theme);
    
    // Update ECharts theme
    this.charts.forEach(chart => {
      const option = chart.getOption();
      chart.dispose();
      const newChart = echarts.init(chart.getDom(), theme);
      newChart.setOption(option);
    });
  }
  
  /**
   * Toggle theme
   */
  toggleTheme() {
    const newTheme = this.theme === 'light' ? 'dark' : 'light';
    this.applyTheme(newTheme);
    this.showToast(`Switched to ${newTheme} theme`, 'info');
  }
  
  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => this.toggleTheme());
    }
    
    // Refresh button
    const refreshBtn = document.getElementById('refresh-dashboard');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this.refreshAllCharts());
    }
    
    // Export button
    const exportBtn = document.getElementById('export-dashboard');
    if (exportBtn) {
      exportBtn.addEventListener('click', () => this.exportDashboard());
    }
    
    // Auto-refresh toggle
    const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
    if (autoRefreshToggle) {
      autoRefreshToggle.addEventListener('change', (e) => {
        if (e.target.checked) {
          this.startAutoRefresh();
        } else {
          this.stopAutoRefresh();
        }
      });
    }
    
    // Resize handler
    window.addEventListener('resize', () => {
      this.resizeCharts();
    });
  }
  
  /**
   * Refresh all charts
   */
  async refreshAllCharts() {
    this.showLoading();
    
    try {
      // Emit custom event for data refresh
      const event = new CustomEvent('dashboard-refresh', { detail: { charts: this.charts } });
      window.dispatchEvent(event);
      
      this.showToast('Charts refreshed successfully', 'success');
      this.updateTimestamp();
    } catch (error) {
      this.showToast('Failed to refresh charts', 'error');
      console.error('Refresh error:', error);
    } finally {
      this.hideLoading();
    }
  }
  
  /**
   * Start auto-refresh
   */
  startAutoRefresh() {
    if (this.autoRefreshInterval) {
      clearInterval(this.autoRefreshInterval);
    }
    
    const interval = this.config.autoRefreshInterval || 30000; // Default 30 seconds
    this.autoRefreshInterval = setInterval(() => {
      this.refreshAllCharts();
    }, interval);
  }
  
  /**
   * Stop auto-refresh
   */
  stopAutoRefresh() {
    if (this.autoRefreshInterval) {
      clearInterval(this.autoRefreshInterval);
      this.autoRefreshInterval = null;
    }
  }
  
  /**
   * Export dashboard as PDF
   */
  async exportDashboard() {
    this.showToast('Preparing export...', 'info');
    
    try {
      // Use html2canvas and jsPDF if available
      if (typeof html2canvas !== 'undefined' && typeof jsPDF !== 'undefined') {
        const element = document.querySelector('.dashboard-container');
        const canvas = await html2canvas(element);
        const imgData = canvas.toDataURL('image/png');
        
        const pdf = new jsPDF('l', 'mm', 'a4');
        const imgWidth = 297;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        
        pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
        pdf.save(`${this.config.title || 'dashboard'}_${Date.now()}.pdf`);
        
        this.showToast('Dashboard exported successfully', 'success');
      } else {
        // Fallback: print
        window.print();
      }
    } catch (error) {
      this.showToast('Failed to export dashboard', 'error');
      console.error('Export error:', error);
    }
  }
  
  /**
   * Resize all charts
   */
  resizeCharts() {
    this.charts.forEach(chart => {
      chart.resize();
    });
  }
  
  /**
   * Show toast notification
   */
  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type]}</span>
      <span class="toast-message">${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 5000);
  }
  
  /**
   * Show loading overlay
   */
  showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
      overlay.classList.remove('visually-hidden');
    }
  }
  
  /**
   * Hide loading overlay
   */
  hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
      overlay.classList.add('visually-hidden');
    }
  }
  
  /**
   * Update timestamp
   */
  updateTimestamp() {
    const timestamp = document.getElementById('dashboard-timestamp');
    if (timestamp) {
      const now = new Date();
      timestamp.textContent = `Last updated: ${now.toLocaleString()}`;
    }
  }
  
  /**
   * Filter charts by keyword
   */
  filterCharts(keyword) {
    this.charts.forEach(chart => {
      const card = chart.getDom().closest('.chart-card');
      if (card) {
        const title = card.querySelector('.chart-card-title').textContent.toLowerCase();
        if (keyword === '' || title.includes(keyword.toLowerCase())) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      }
    });
  }
  
  /**
   * Sort charts by title
   */
  sortCharts(order = 'asc') {
    const container = document.querySelector('.dashboard-grid');
    if (!container) return;
    
    const cards = Array.from(container.children);
    cards.sort((a, b) => {
      const titleA = a.querySelector('.chart-card-title').textContent;
      const titleB = b.querySelector('.chart-card-title').textContent;
      return order === 'asc' ? titleA.localeCompare(titleB) : titleB.localeCompare(titleA);
    });
    
    cards.forEach(card => container.appendChild(card));
  }
  
  /**
   * Get chart by ID
   */
  getChart(id) {
    return this.charts.find(chart => chart.getDom().id === `chart_${id}`);
  }
  
  /**
   * Download chart as image
   */
  downloadChart(id, filename) {
    const chart = this.getChart(id);
    if (chart) {
      const url = chart.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: this.theme === 'dark' ? '#1e293b' : '#fff'
      });
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || `chart_${id}.png`;
      link.click();
    }
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DashboardController;
}