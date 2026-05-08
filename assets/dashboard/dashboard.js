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
    this._refreshing = false;
    this._listeners = {};
    
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
    
    const newCharts = [];
    this.charts.forEach(chart => {
      try {
        const option = chart.getOption();
        const dom = chart.getDom();
        chart.dispose();
        const newChart = echarts.init(dom, theme);
        newChart.setOption(option);
        newCharts.push(newChart);
      } catch (e) {
        console.warn('Failed to re-init chart with new theme:', e);
      }
    });
    this.charts = newCharts;
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
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      const handler = () => this.toggleTheme();
      themeToggle.addEventListener('click', handler);
      this._listeners.themeToggle = { el: themeToggle, handler: handler };
    }
    
    const refreshBtn = document.getElementById('refresh-dashboard');
    if (refreshBtn) {
      const handler = () => this.refreshAllCharts();
      refreshBtn.addEventListener('click', handler);
      this._listeners.refreshBtn = { el: refreshBtn, handler: handler };
    }
    
    const exportBtn = document.getElementById('export-dashboard');
    if (exportBtn) {
      const handler = () => this.exportDashboard();
      exportBtn.addEventListener('click', handler);
      this._listeners.exportBtn = { el: exportBtn, handler: handler };
    }
    
    const resizeHandler = () => { this.resizeCharts(); };
    window.addEventListener('resize', resizeHandler);
    this._listeners.resizeHandler = resizeHandler;
  }
  
  /**
   * Refresh all charts
   */
  async refreshAllCharts() {
    if (this._refreshing) return;
    this._refreshing = true;
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
      this._refreshing = false;
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
      if (typeof html2canvas !== 'undefined' && (typeof jsPDF !== 'undefined' || (typeof jspdf !== 'undefined' && jspdf.jsPDF))) {
        const JsPDF = typeof jsPDF !== 'undefined' ? jsPDF : jspdf.jsPDF;
        const element = document.querySelector('.dashboard-container');
        const canvas = await html2canvas(element);
        const imgData = canvas.toDataURL('image/png');
        
        const pdf = new JsPDF('l', 'mm', 'a4');
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
    const iconSpan = document.createElement('span');
    iconSpan.className = 'toast-icon';
    iconSpan.textContent = icons[type];
    const msgSpan = document.createElement('span');
    msgSpan.className = 'toast-message';
    msgSpan.textContent = message;
    const closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.textContent = '\u00d7';
    closeBtn.addEventListener('click', function() { toast.remove(); });
    toast.appendChild(iconSpan);
    toast.appendChild(msgSpan);
    toast.appendChild(closeBtn);
    
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
      try {
        const card = chart.getDom().closest('.chart-card');
        if (card) {
          const titleEl = card.querySelector('.chart-card-title');
          if (titleEl) {
            const title = titleEl.textContent.toLowerCase();
            if (keyword === '' || title.includes(keyword.toLowerCase())) {
              card.style.display = '';
            } else {
              card.style.display = 'none';
            }
          }
        }
      } catch (e) {
        console.warn('filterCharts error:', e);
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
      const titleA = a.querySelector('.chart-card-title');
      const titleB = b.querySelector('.chart-card-title');
      const textA = titleA ? titleA.textContent : '';
      const textB = titleB ? titleB.textContent : '';
      return order === 'asc' ? textA.localeCompare(textB) : textB.localeCompare(textA);
    });
    
    cards.forEach(card => container.appendChild(card));
  }
  
  /**
   * Destroy the dashboard instance, clean up listeners and intervals
   */
  destroy() {
    this.stopAutoRefresh();
    
    Object.values(this._listeners).forEach(entry => {
      if (entry.el) {
        entry.el.removeEventListener('click', entry.handler);
      }
    });
    if (this._listeners.resizeHandler) {
      window.removeEventListener('resize', this._listeners.resizeHandler);
    }
    this._listeners = {};
    
    this.charts.forEach(chart => {
      try { chart.dispose(); } catch (e) { /* ignore */ }
    });
    this.charts = [];
    const toastContainer = document.getElementById('toast-container');
    if (toastContainer) toastContainer.innerHTML = '';
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