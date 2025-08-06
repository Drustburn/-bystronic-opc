/**
 * Bystronic OPC Dashboard JavaScript
 * Handles real-time updates, WebSocket connections, and UI interactions
 */

class BystronicDashboard {
    constructor() {
        this.socket = null;
        this.charts = {};
        this.updateInterval = 30000; // 30 seconds
        this.isConnected = false;
        
        this.init();
    }
    
    init() {
        console.log('Initializing Bystronic Dashboard...');
        
        // Initialize Socket.IO connection
        this.initializeSocket();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Start periodic updates
        this.startPeriodicUpdates();
        
        console.log('Dashboard initialized successfully');
    }
    
    initializeSocket() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Connected to server');
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.subscribeToMachineUpdates();
            });
            
            this.socket.on('disconnect', () => {
                console.log('Disconnected from server');
                this.isConnected = false;
                this.updateConnectionStatus(false);
            });
            
            this.socket.on('machine_update', (data) => {
                this.handleMachineUpdate(data);
            });
            
            this.socket.on('summary_update', (data) => {
                this.handleSummaryUpdate(data);
            });
            
            this.socket.on('error', (error) => {
                console.error('Socket error:', error);
                this.showNotification('Connection error occurred', 'error');
            });
        } else {
            console.warn('Socket.IO not available, falling back to polling');
            this.setupPolling();
        }
    }
    
    subscribeToMachineUpdates() {
        // Subscribe to updates for all machines on the page
        const machineCards = document.querySelectorAll('.machine-card');
        machineCards.forEach(card => {
            const machineName = card.getAttribute('data-machine');
            if (machineName && this.socket) {
                this.socket.emit('subscribe_machine', { machine_name: machineName });
            }
        });
    }
    
    setupEventListeners() {
        // Refresh buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="refresh"]')) {
                const machineName = e.target.getAttribute('data-machine');
                this.refreshMachine(machineName);
            }
            
            if (e.target.matches('[data-action="screenshot"]')) {
                const machineName = e.target.getAttribute('data-machine');
                this.getScreenshot(machineName);
            }
        });
        
        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startPeriodicUpdates();
                } else {
                    this.stopPeriodicUpdates();
                }
            });
        }
        
        // Page visibility change handling
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopPeriodicUpdates();
            } else {
                this.startPeriodicUpdates();
            }
        });
    }
    
    setupPolling() {
        // Fallback to HTTP polling if WebSocket is not available
        this.startPeriodicUpdates();
    }
    
    startPeriodicUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
        }
        
        this.updateTimer = setInterval(() => {
            this.loadAllMachineStatus();
        }, this.updateInterval);
        
        // Initial load
        this.loadAllMachineStatus();
    }
    
    stopPeriodicUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }
    
    async loadAllMachineStatus() {
        try {
            const response = await fetch('/api/machines/status');
            if (!response.ok) throw new Error('Failed to fetch status');
            
            const data = await response.json();
            this.updateAllMachineCards(data);
            
        } catch (error) {
            console.error('Error loading machine status:', error);
            this.showNotification('Failed to load machine status', 'error');
        }
    }
    
    updateAllMachineCards(statusData) {
        let connectedCount = 0;
        let activeJobs = 0;
        
        Object.entries(statusData).forEach(([machineName, status]) => {
            this.updateMachineCard({
                machine_name: machineName,
                ...status
            });
            
            if (status.is_connected) connectedCount++;
            if (status.current_job) activeJobs++;
        });
        
        this.updateSummaryCards({
            total_machines: Object.keys(statusData).length,
            connected_machines: connectedCount,
            active_jobs: activeJobs
        });
    }
    
    updateMachineCard(data) {
        const machineName = data.machine_name;
        const card = document.querySelector(`[data-machine="${machineName}"]`);
        if (!card) return;
        
        // Add updating animation
        card.classList.add('updating');
        setTimeout(() => card.classList.remove('updating'), 1000);
        
        // Update status badge
        const statusBadge = card.querySelector(`#status-${machineName}`);
        if (statusBadge) {
            if (data.is_connected) {
                statusBadge.className = 'badge bg-success machine-status-badge';
                statusBadge.innerHTML = '<i class="bi bi-check-circle"></i> Online';
                card.setAttribute('data-status', 'online');
            } else {
                statusBadge.className = 'badge bg-danger machine-status-badge';
                statusBadge.innerHTML = '<i class="bi bi-x-circle"></i> Offline';
                card.setAttribute('data-status', 'offline');
            }
        }
        
        // Update connection status
        const connectionEl = card.querySelector(`#connection-${machineName}`);
        if (connectionEl) {
            if (data.is_connected) {
                connectionEl.textContent = 'Connected';
                connectionEl.className = 'text-success';
            } else {
                connectionEl.textContent = 'Disconnected';
                connectionEl.className = 'text-danger';
            }
        }
        
        // Update current job
        const jobEl = card.querySelector(`#job-${machineName}`);
        if (jobEl) {
            if (data.current_job) {
                jobEl.textContent = data.current_job;
                jobEl.className = 'text-success fw-bold';
            } else {
                jobEl.textContent = 'No active job';
                jobEl.className = 'text-muted';
            }
        }
        
        // Update laser power
        if (data.laser_parameters) {
            const powerBar = card.querySelector(`#power-bar-${machineName}`);
            if (powerBar) {
                const power = data.laser_parameters.current_power || 0;
                const maxPower = 6000; // Assume max 6kW
                const percentage = Math.min((power / maxPower) * 100, 100);
                
                powerBar.style.width = `${percentage}%`;
                powerBar.textContent = `${power}W`;
                
                if (percentage > 80) {
                    powerBar.className = 'progress-bar bg-danger';
                } else if (percentage > 50) {
                    powerBar.className = 'progress-bar bg-warning';
                } else {
                    powerBar.className = 'progress-bar bg-success';
                }
            }
            
            // Update gas pressure
            const pressureEl = card.querySelector(`#pressure-${machineName}`);
            if (pressureEl) {
                const pressure = data.laser_parameters.gas_pressure || 0;
                pressureEl.textContent = `${pressure} bar`;
            }
        }
        
        // Update last update time
        const updateEl = card.querySelector(`#update-${machineName}`);
        if (updateEl && data.last_update) {
            const updateTime = new Date(data.last_update);
            updateEl.textContent = updateTime.toLocaleTimeString();
        }
    }
    
    updateSummaryCards(data) {
        const elements = {
            'total-machines': data.total_machines,
            'connected-machines': data.connected_machines,
            'active-jobs': data.active_jobs || 0,
            'connected-count': data.connected_machines
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element && value !== undefined) {
                element.textContent = value;
            }
        });
        
        // Update efficiency
        const efficiencyEl = document.getElementById('efficiency');
        if (efficiencyEl && data.total_machines > 0) {
            const efficiency = Math.round((data.connected_machines / data.total_machines) * 100);
            efficiencyEl.textContent = `${efficiency}%`;
        }
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (!statusElement) return;
        
        if (connected) {
            statusElement.className = 'badge bg-success';
            statusElement.innerHTML = '<i class="bi bi-wifi"></i> Connected';
        } else {
            statusElement.className = 'badge bg-danger';
            statusElement.innerHTML = '<i class="bi bi-wifi-off"></i> Disconnected';
        }
    }
    
    async refreshMachine(machineName) {
        try {
            this.showNotification(`Refreshing ${machineName}...`, 'info');
            
            const response = await fetch(`/api/machine/${machineName}/status`);
            if (!response.ok) throw new Error('Failed to refresh machine');
            
            const data = await response.json();
            this.updateMachineCard({
                machine_name: machineName,
                ...data
            });
            
            this.showNotification(`${machineName} refreshed successfully`, 'success');
            
        } catch (error) {
            console.error('Error refreshing machine:', error);
            this.showNotification(`Error refreshing ${machineName}`, 'error');
        }
    }
    
    async getScreenshot(machineName) {
        try {
            const modal = new bootstrap.Modal(document.getElementById('screenshotModal'));
            const image = document.getElementById('screenshotImage');
            const loading = document.getElementById('screenshotLoading');
            
            modal.show();
            image.style.display = 'none';
            loading.style.display = 'block';
            
            const response = await fetch(`/api/machine/${machineName}/screen`);
            if (!response.ok) throw new Error('Failed to get screenshot');
            
            const blob = await response.blob();
            const imageUrl = URL.createObjectURL(blob);
            
            image.src = imageUrl;
            image.style.display = 'block';
            loading.style.display = 'none';
            
        } catch (error) {
            console.error('Error getting screenshot:', error);
            const loading = document.getElementById('screenshotLoading');
            if (loading) {
                loading.innerHTML = '<p class="text-danger">Error loading screenshot</p>';
            }
        }
    }
    
    showNotification(message, type = 'info') {
        // Remove existing notifications
        document.querySelectorAll('.notification-toast').forEach(toast => {
            toast.remove();
        });
        
        // Create new notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${this.getAlertClass(type)} alert-dismissible fade show position-fixed notification-toast`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-${this.getIconClass(type)} me-2"></i>
                <div>${message}</div>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
    
    getAlertClass(type) {
        const classes = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return classes[type] || 'info';
    }
    
    getIconClass(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    handleMachineUpdate(data) {
        this.updateMachineCard(data);
    }
    
    handleSummaryUpdate(data) {
        this.updateSummaryCards(data);
    }
    
    // Chart utilities
    createChart(canvasId, config) {
        const ctx = document.getElementById(canvasId);
        if (ctx) {
            this.charts[canvasId] = new Chart(ctx, config);
            return this.charts[canvasId];
        }
        return null;
    }
    
    updateChart(chartId, data) {
        const chart = this.charts[chartId];
        if (chart) {
            chart.data = data;
            chart.update();
        }
    }
    
    // Utility functions
    formatDuration(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes % 60}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds % 60}s`;
        } else {
            return `${seconds}s`;
        }
    }
    
    formatFileSize(bytes) {
        const sizes = ['B', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 B';
        
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
    }
    
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }
}

// Global functions for backward compatibility
function refreshMachine(machineName) {
    if (window.dashboard) {
        window.dashboard.refreshMachine(machineName);
    }
}

function getScreenshot(machineName) {
    if (window.dashboard) {
        window.dashboard.getScreenshot(machineName);
    }
}

function showToast(message, type) {
    if (window.dashboard) {
        window.dashboard.showNotification(message, type);
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new BystronicDashboard();
    
    // Update clock
    function updateClock() {
        const now = new Date();
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            timeElement.textContent = now.toLocaleString('de-DE');
        }
    }
    
    updateClock();
    setInterval(updateClock, 1000);
});