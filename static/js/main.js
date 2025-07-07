// Employee Management System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize confirmation dialogs
    initializeConfirmations();
    
    // Initialize auto-dismiss alerts
    initializeAlerts();
    
    // Initialize table sorting
    initializeTableSorting();
    
    console.log('Employee Management System initialized successfully');
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// Initialize form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Real-time validation for email field
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateEmail(this);
        });
    });
    
    // Real-time validation for salary field
    const salaryInputs = document.querySelectorAll('input[name="salary"]');
    salaryInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateSalary(this);
        });
    });
}

// Email validation
function validateEmail(input) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValid = emailRegex.test(input.value);
    
    if (input.value && !isValid) {
        input.setCustomValidity('Please enter a valid email address');
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
    }
}

// Salary validation
function validateSalary(input) {
    const salary = parseFloat(input.value);
    
    if (input.value && (isNaN(salary) || salary < 0)) {
        input.setCustomValidity('Please enter a valid positive number');
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
    }
}

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    const searchForm = document.querySelector('form[action*="search"]');
    
    if (searchInput && searchForm) {
        // Add search icon toggle
        const searchButton = searchForm.querySelector('button[type="submit"]');
        const searchIcon = searchButton.querySelector('i');
        
        searchInput.addEventListener('input', function() {
            if (this.value.length > 0) {
                searchIcon.className = 'fas fa-times me-1';
                searchButton.onclick = function(e) {
                    e.preventDefault();
                    searchInput.value = '';
                    window.location.href = searchForm.action.replace('/search', '');
                };
            } else {
                searchIcon.className = 'fas fa-search me-1';
                searchButton.onclick = null;
            }
        });
        
        // Auto-search with debounce
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    searchForm.submit();
                }, 1000);
            }
        });
    }
}

// Initialize confirmation dialogs
function initializeConfirmations() {
    const deleteButtons = document.querySelectorAll('a[onclick*="confirm"]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const employeeName = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            const deleteUrl = this.getAttribute('href');
            
            showConfirmDialog(
                'Delete Employee',
                `Are you sure you want to delete ${employeeName}? This action cannot be undone.`,
                'Delete',
                'btn-danger',
                function() {
                    window.location.href = deleteUrl;
                }
            );
        });
    });
}

// Show custom confirmation dialog
function showConfirmDialog(title, message, confirmText, confirmClass, onConfirm) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn ${confirmClass}" id="confirmAction">${confirmText}</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    document.getElementById('confirmAction').addEventListener('click', function() {
        onConfirm();
        bootstrapModal.hide();
    });
    
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

// Initialize auto-dismiss alerts
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Initialize table sorting
function initializeTableSorting() {
    const tables = document.querySelectorAll('table.table');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        
        headers.forEach((header, index) => {
            if (header.textContent.trim() && !header.querySelector('.btn')) {
                header.style.cursor = 'pointer';
                header.style.userSelect = 'none';
                
                header.addEventListener('click', function() {
                    sortTable(table, index);
                });
                
                // Add sort indicator
                const sortIcon = document.createElement('i');
                sortIcon.className = 'fas fa-sort ms-2 text-muted';
                header.appendChild(sortIcon);
            }
        });
    });
}

// Sort table by column
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const header = table.querySelectorAll('th')[columnIndex];
    const sortIcon = header.querySelector('i');
    
    // Determine sort direction
    const isAscending = sortIcon.classList.contains('fa-sort') || sortIcon.classList.contains('fa-sort-down');
    
    // Reset all sort icons
    table.querySelectorAll('th i').forEach(icon => {
        icon.className = 'fas fa-sort ms-2 text-muted';
    });
    
    // Set current sort icon
    sortIcon.className = `fas fa-sort-${isAscending ? 'up' : 'down'} ms-2 text-primary`;
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        // Check if values are numbers
        const aNum = parseFloat(aValue.replace(/[^0-9.-]+/g, ''));
        const bNum = parseFloat(bValue.replace(/[^0-9.-]+/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // String comparison
        return isAscending ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
    });
    
    // Reorder rows in DOM
    rows.forEach(row => tbody.appendChild(row));
    
    // Add animation
    tbody.style.opacity = '0.5';
    setTimeout(() => {
        tbody.style.opacity = '1';
    }, 150);
}

// Utility function to show loading state
function showLoading(element) {
    element.classList.add('loading');
    const spinner = document.createElement('span');
    spinner.className = 'spinner-border spinner-border-sm me-2';
    spinner.setAttribute('role', 'status');
    element.insertBefore(spinner, element.firstChild);
}

// Utility function to hide loading state
function hideLoading(element) {
    element.classList.remove('loading');
    const spinner = element.querySelector('.spinner-border');
    if (spinner) {
        spinner.remove();
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

// Export data to CSV
function exportToCSV(data, filename) {
    const csv = data.map(row => Object.values(row).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Print functionality
function printPage() {
    window.print();
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    
    // Show user-friendly error message
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        Something went wrong. Please refresh the page and try again.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+N or Cmd+N for new employee
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        const addButton = document.querySelector('a[href*="add"]');
        if (addButton) {
            addButton.click();
        }
    }
    
    // Escape key to close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        });
    }
});
