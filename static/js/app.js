// Main JavaScript for Valet Parking System

// API Configuration
const API_BASE_URL = '/api';
const API_ENDPOINTS = {
    companies: `${API_BASE_URL}/companies/`,
    parking: `${API_BASE_URL}/parking/slots/`,
    transactions: `${API_BASE_URL}/parking/transactions/`,
    auth: `${API_BASE_URL}-auth/`,
};

// Global variables
let authToken = localStorage.getItem('authToken');
let currentUser = JSON.parse(localStorage.getItem('user') || '{}');
let currentCompany = JSON.parse(localStorage.getItem('company') || '{}');

// Utility Functions
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
}

function showAlert(message, type = 'info', containerId = 'alerts') {
    const alertContainer = document.getElementById(containerId);
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// API Helper Functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    // Add CSRF token for POST, PUT, PATCH, DELETE requests
    if (options.method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(options.method.toUpperCase())) {
        defaultOptions.headers['X-CSRFToken'] = getCookie('csrftoken');
    }

    // Include credentials for session-based authentication
    defaultOptions.credentials = 'include';

    const finalOptions = { ...defaultOptions, ...options };

    try {
        const response = await fetch(url, finalOptions);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Authentication Functions
async function login(username, password) {
    try {
        const response = await fetch(`${API_ENDPOINTS.auth}login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        
        if (response.ok) {
            const data = await response.json();
            authToken = data.token;
            localStorage.setItem('authToken', authToken);
            return true;
        } else {
            throw new Error('Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        return false;
    }
}

async function logout() {
    try {
        // Call backend logout endpoint to clear session
        await fetch('/api/auth/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        // Clear frontend storage regardless of backend response
        authToken = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        localStorage.removeItem('company');
        window.location.href = '/login/';
    }
}

// Function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Data Loading Functions
async function loadCompanies() {
    try {
        const companies = await apiRequest(API_ENDPOINTS.companies);
        return companies;
    } catch (error) {
        showAlert('Failed to load companies', 'danger');
        return [];
    }
}

async function loadParkingSlots() {
    try {
        const slots = await apiRequest(API_ENDPOINTS.parking);
        return slots;
    } catch (error) {
        showAlert('Failed to load parking slots', 'danger');
        return [];
    }
}

async function loadTransactions() {
    try {
        const transactions = await apiRequest(API_ENDPOINTS.transactions);
        return transactions;
    } catch (error) {
        showAlert('Failed to load transactions', 'danger');
        return [];
    }
}

async function updateTransactionStatus(transactionId, newStatus) {
    try {
        const response = await apiRequest(`${API_ENDPOINTS.transactions}${transactionId}/update-status/`, {
            method: 'POST',
            body: JSON.stringify({ status: newStatus }),
        });
        return response;
    } catch (error) {
        showAlert('Failed to update transaction status', 'danger');
        throw error;
    }
}

// Form Handlers
function handleCompanyForm(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const companyData = Object.fromEntries(formData);
    
    // Add company via API
    apiRequest(API_ENDPOINTS.companies, {
        method: 'POST',
        body: JSON.stringify(companyData),
    })
    .then(() => {
        showAlert('Company created successfully!', 'success');
        event.target.reset();
        loadCompanies(); // Refresh the list
    })
    .catch(() => {
        showAlert('Failed to create company', 'danger');
    });
}

function handleParkingSlotForm(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const slotData = Object.fromEntries(formData);
    
    // Add parking slot via API
    apiRequest(API_ENDPOINTS.parking, {
        method: 'POST',
        body: JSON.stringify(slotData),
    })
    .then(() => {
        showAlert('Parking slot created successfully!', 'success');
        event.target.reset();
        loadParkingSlots(); // Refresh the list
    })
    .catch(() => {
        showAlert('Failed to create parking slot', 'danger');
    });
}

// Status Badge Helper
function getStatusBadge(status) {
    const statusClasses = {
        'pending_park': 'status-pending',
        'parked': 'status-parked',
        'pending_retrieve': 'status-pending',
        'delivered': 'status-delivered',
        'occupied': 'status-occupied',
        'available': 'status-available',
    };
    
    const statusLabels = {
        'pending_park': 'Pending Park',
        'parked': 'Parked',
        'pending_retrieve': 'Pending Retrieve',
        'delivered': 'Delivered',
        'occupied': 'Occupied',
        'available': 'Available',
    };
    
    const className = statusClasses[status] || 'status-pending';
    const label = statusLabels[status] || status;
    
    return `<span class="status-badge ${className}">${label}</span>`;
}

// Initialize page-specific functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Export functions for global use
window.login = login;
window.logout = logout;
window.showAlert = showAlert;
window.apiRequest = apiRequest;
