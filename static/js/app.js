// Modern Interactive JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar functionality
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileToggle = document.getElementById('mobileToggle');
    
    // Toggle sidebar on desktop
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
    }
    
    // Toggle sidebar on mobile
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    // Restore sidebar state
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed');
    if (sidebarCollapsed === 'true') {
        sidebar.classList.add('collapsed');
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(event.target) && !mobileToggle.contains(event.target)) {
                sidebar.classList.remove('show');
            }
        }
    });
    
    // Initialize modern features
    initializeOfflineMode();
    initializeKeyboardShortcuts();
    initializeDragDrop();
    initializeTooltips();
    initializeAccessibility();
    initializeSmartSearch();
    
    // Auto-hide flash messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        }, 5000);
    });
    
    // Add loading states to buttons
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && this.form.checkValidity()) {
                this.innerHTML = '<span class="loading"></span> Processing...';
                this.disabled = true;
            }
        });
    });
    
    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
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
            
            if (!isValid) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });
    });
    
    // Real-time form validation
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.hasAttribute('required') && !this.value.trim()) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid') && this.value.trim()) {
                this.classList.remove('is-invalid');
            }
        });
    });
    
    // Interactive table rows
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Dynamic search functionality
    const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
    searchInputs.forEach(input => {
        let searchTimeout;
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, this.dataset.target);
            }, 300);
        });
    });
    
    // Notification system
    function showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
        notification.innerHTML = `
            <i class="bi bi-${getIconForType(type)}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to page
        const container = document.querySelector('.flash-messages') || document.querySelector('.page-content');
        container.insertBefore(notification, container.firstChild);
        
        // Auto-remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                notification.style.transform = 'translateY(-20px)';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    }
    
    function getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'danger': 'exclamation-triangle'
        };
        return icons[type] || 'info-circle';
    }
    
    // Search functionality
    function performSearch(query, target) {
        if (!target) return;
        
        const targetElement = document.querySelector(target);
        if (!targetElement) return;
        
        const items = targetElement.querySelectorAll('tr, .card, .list-item');
        
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            
            item.style.display = matches || !query ? '' : 'none';
            
            if (matches && query) {
                item.classList.add('search-highlight');
            } else {
                item.classList.remove('search-highlight');
            }
        });
    }
    
    // Enhanced dropdown functionality
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function() {
            // Close other dropdowns
            dropdowns.forEach(other => {
                if (other !== this) {
                    other.classList.remove('show');
                    const menu = other.nextElementSibling;
                    if (menu) menu.classList.remove('show');
                }
            });
        });
    });
    
    
    // Lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
    
    // Progressive enhancement for forms
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Add date picker enhancement if needed
        if (!input.type || input.type !== 'date') {
            // Fallback for browsers that don't support date input
            input.placeholder = 'YYYY-MM-DD';
        }
    });
    
    // Auto-save form data
    const autoSaveForms = document.querySelectorAll('form[data-autosave]');
    autoSaveForms.forEach(form => {
        const formId = form.id || 'form_' + Math.random().toString(36).substr(2, 9);
        
        // Load saved data
        const savedData = localStorage.getItem('autosave_' + formId);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(key => {
                    const field = form.querySelector(`[name="${key}"]`);
                    if (field && field.type !== 'password') {
                        field.value = data[key];
                    }
                });
            } catch (e) {
                console.warn('Failed to restore form data:', e);
            }
        }
        
        // Save data on change
        form.addEventListener('input', debounce(function() {
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                if (form.querySelector(`[name="${key}"]`).type !== 'password') {
                    data[key] = value;
                }
            }
            localStorage.setItem('autosave_' + formId, JSON.stringify(data));
        }, 1000));
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            localStorage.removeItem('autosave_' + formId);
        });
    });
    
    // Utility function for debouncing
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Theme switcher (if implemented)
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
        });
        
        // Restore theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
        }
    }
    
    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData.loadEventEnd - perfData.loadEventStart > 3000) {
                    console.warn('Page load time is slow:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
                }
            }, 0);
        });
    }
});

// Modern Features Implementation

// Offline Mode Detection
function initializeOfflineMode() {
    const offlineIndicator = document.createElement('div');
    offlineIndicator.className = 'offline-indicator';
    offlineIndicator.innerHTML = '<i class="bi bi-wifi-off"></i> You are offline';
    document.body.appendChild(offlineIndicator);
    
    function updateOnlineStatus() {
        if (navigator.onLine) {
            offlineIndicator.classList.remove('show');
        } else {
            offlineIndicator.classList.add('show');
        }
    }
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
}

// Enhanced Keyboard Shortcuts
function initializeKeyboardShortcuts() {
    const shortcuts = {
        'ctrl+k': () => openCommandPalette(),
        'ctrl+/': () => showShortcutsHelp(),
        'ctrl+shift+d': () => toggleDarkMode(),
        'ctrl+shift+n': () => showNotifications(),
        'escape': () => closeModalsAndDropdowns(),
        'ctrl+s': (e) => {
            e.preventDefault();
            saveCurrentForm();
        }
    };
    
    document.addEventListener('keydown', function(e) {
        const key = [];
        if (e.ctrlKey || e.metaKey) key.push('ctrl');
        if (e.shiftKey) key.push('shift');
        if (e.altKey) key.push('alt');
        key.push(e.key.toLowerCase());
        
        const shortcut = key.join('+');
        if (shortcuts[shortcut]) {
            shortcuts[shortcut](e);
        }
    });
}

// Drag and Drop Functionality
function initializeDragDrop() {
    const dropZones = document.querySelectorAll('.drag-drop-zone');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        zone.addEventListener('dragleave', function() {
            this.classList.remove('drag-over');
        });
        
        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const files = Array.from(e.dataTransfer.files);
            handleFileUpload(files, this);
        });
        
        zone.addEventListener('click', function() {
            const input = document.createElement('input');
            input.type = 'file';
            input.multiple = true;
            input.onchange = (e) => handleFileUpload(Array.from(e.target.files), this);
            input.click();
        });
    });
}

// Smart Search with Fuzzy Matching
function initializeSmartSearch() {
    const searchInputs = document.querySelectorAll('.smart-search');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function() {
            const query = this.value.toLowerCase();
            const results = performFuzzySearch(query);
            displaySearchResults(results, this);
        }, 300));
    });
}

function performFuzzySearch(query) {
    // Implement fuzzy search algorithm
    const searchableItems = document.querySelectorAll('[data-searchable]');
    const results = [];
    
    searchableItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        const score = calculateFuzzyScore(query, text);
        if (score > 0.3) {
            results.push({ element: item, score });
        }
    });
    
    return results.sort((a, b) => b.score - a.score);
}

function calculateFuzzyScore(query, text) {
    if (!query) return 1;
    if (text.includes(query)) return 1;
    
    // Simple fuzzy matching algorithm
    let score = 0;
    let queryIndex = 0;
    
    for (let i = 0; i < text.length && queryIndex < query.length; i++) {
        if (text[i] === query[queryIndex]) {
            score++;
            queryIndex++;
        }
    }
    
    return score / query.length;
}

// Enhanced Tooltips and Help System
function initializeTooltips() {
    // Create dynamic tooltips for complex UI elements
    const complexElements = document.querySelectorAll('[data-help]');
    
    complexElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showContextualHelp(this);
        });
        
        element.addEventListener('mouseleave', function() {
            hideContextualHelp();
        });
    });
}

// Accessibility Enhancements
function initializeAccessibility() {
    // Add ARIA labels dynamically
    const buttons = document.querySelectorAll('button:not([aria-label])');
    buttons.forEach(button => {
        if (!button.textContent.trim()) {
            const icon = button.querySelector('i');
            if (icon) {
                const iconClass = icon.className;
                button.setAttribute('aria-label', getAriaLabelFromIcon(iconClass));
            }
        }
    });
    
    // Enhance focus management
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', function() {
        document.body.classList.remove('keyboard-navigation');
    });
}

function getAriaLabelFromIcon(iconClass) {
    const iconMap = {
        'bi-plus': 'Add',
        'bi-pencil': 'Edit',
        'bi-trash': 'Delete',
        'bi-eye': 'View',
        'bi-download': 'Download',
        'bi-upload': 'Upload',
        'bi-search': 'Search',
        'bi-filter': 'Filter',
        'bi-gear': 'Settings'
    };
    
    for (const [icon, label] of Object.entries(iconMap)) {
        if (iconClass.includes(icon)) {
            return label;
        }
    }
    
    return 'Button';
}

// Command Palette
function openCommandPalette() {
    let palette = document.getElementById('commandPalette');
    if (!palette) {
        palette = createCommandPalette();
        document.body.appendChild(palette);
    }
    palette.classList.add('active');
    palette.querySelector('input').focus();
}

function createCommandPalette() {
    const palette = document.createElement('div');
    palette.id = 'commandPalette';
    palette.className = 'command-palette';
    palette.innerHTML = `
        <div class="command-search">
            <i class="bi bi-search"></i>
            <input type="text" placeholder="Type a command or search...">
        </div>
        <div class="command-results">
            <div class="command-section">
                <div class="command-section-title">Quick Actions</div>
                <div class="command-item" data-action="add-product">
                    <i class="bi bi-plus-circle"></i>
                    <span>Add Product</span>
                </div>
                <div class="command-item" data-action="create-project">
                    <i class="bi bi-kanban"></i>
                    <span>Create Project</span>
                </div>
            </div>
        </div>
    `;
    
    palette.addEventListener('click', function(e) {
        if (e.target === this) {
            this.classList.remove('active');
        }
    });
    
    return palette;
}

// Utility Functions
function toggleDarkMode() {
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
}

function showNotifications() {
    // Open notifications panel
    const notificationBtn = document.querySelector('[data-bs-toggle="dropdown"]');
    if (notificationBtn) {
        notificationBtn.click();
    }
}

function closeModalsAndDropdowns() {
    // Close all open modals and dropdowns
    const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
    openDropdowns.forEach(dropdown => {
        dropdown.classList.remove('show');
    });
    
    const openModals = document.querySelectorAll('.modal.show');
    openModals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) modalInstance.hide();
    });
    
    const commandPalette = document.getElementById('commandPalette');
    if (commandPalette) {
        commandPalette.classList.remove('active');
    }
}

function saveCurrentForm() {
    const activeForm = document.querySelector('form:focus-within');
    if (activeForm) {
        const submitBtn = activeForm.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.click();
        }
    }
}

function handleFileUpload(files, dropZone) {
    files.forEach(file => {
        console.log('Uploading file:', file.name);
        // Implement file upload logic
    });
}

function showContextualHelp(element) {
    const helpText = element.dataset.help;
    if (helpText) {
        // Show contextual help tooltip
        console.log('Showing help:', helpText);
    }
}

function hideContextualHelp() {
    // Hide contextual help
}

function showShortcutsHelp() {
    // Show keyboard shortcuts modal
    console.log('Showing shortcuts help');
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
// Global utility functions
window.IMS = {
    showNotification: function(message, type = 'info', duration = 5000) {
        // Implementation moved to main scope
    },
    
    confirmAction: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },
    
    formatDate: function(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }).format(new Date(date));
    }
};