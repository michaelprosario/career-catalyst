// Main application JavaScript

// Global configuration
const API_BASE_URL = '/api/user-opportunities';
const DEFAULT_USER_ID = 'user123'; // TODO: Replace with actual user authentication

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert after the first container div
    alertContainer.insertBefore(alertDiv, alertContainer.firstChild.nextSibling);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv && alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function showLoading(element, show = true) {
    if (show) {
        element.classList.add('loading');
        const spinner = element.querySelector('.spinner-border');
        if (!spinner) {
            const loadingSpinner = document.createElement('span');
            loadingSpinner.className = 'spinner-border spinner-border-sm me-2';
            loadingSpinner.setAttribute('role', 'status');
            element.insertBefore(loadingSpinner, element.firstChild);
        }
    } else {
        element.classList.remove('loading');
        const spinner = element.querySelector('.spinner-border');
        if (spinner) {
            spinner.remove();
        }
    }
}

// API functions
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Form validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Clear form validation
function clearFormValidation(form) {
    const fields = form.querySelectorAll('.is-invalid');
    fields.forEach(field => {
        field.classList.remove('is-invalid');
    });
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Format status for display
function formatStatus(status) {
    return status.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
}

// Get status badge class
function getStatusBadgeClass(status) {
    const statusColors = {
        'SAVED': 'secondary',
        'APPLIED': 'primary',
        'SCREENING': 'info',
        'INTERVIEWING': 'warning',
        'OFFER': 'success',
        'REJECTED': 'danger',
        'WITHDRAWN': 'dark',
        'ACCEPTED': 'success',
        'ACTIVE': 'success',
        'EXPIRED': 'warning',
        'FILLED': 'danger',
        'CANCELLED': 'secondary'
    };
    return statusColors[status] || 'secondary';
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    
    // Initialize form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
        
        // Clear validation on input
        const fields = form.querySelectorAll('input, textarea, select');
        fields.forEach(field => {
            field.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    this.classList.remove('is-invalid');
                }
            });
        });
    });
});

// Export functions for use in other files
window.CareerCatalyst = {
    showAlert,
    showLoading,
    apiRequest,
    validateForm,
    clearFormValidation,
    formatDate,
    formatStatus,
    getStatusBadgeClass,
    API_BASE_URL,
    DEFAULT_USER_ID
};