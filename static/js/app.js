/**
 * FleetFlow - Main Application JavaScript
 * Handles theme toggling, dropdowns, modals, notifications, and global interactions
 */

(function() {
    'use strict';

    // ==========================================================================
    // State Management
    // ==========================================================================

    const state = {
        theme: 'dark',
        sidebarOpen: false,
        sidebarCollapsed: false,
        activeDropdown: null
    };

    // ==========================================================================
    // DOM Elements
    // ==========================================================================

    const elements = {
        themeToggle: document.getElementById('themeToggle'),
        sidebarToggle: document.getElementById('sidebarToggle'),
        mobileMenuBtn: document.getElementById('mobileMenuBtn'),
        sidebar: document.querySelector('.sidebar'),
        sidebarOverlay: document.getElementById('sidebarOverlay'),
        notificationBtn: document.getElementById('notificationBtn'),
        notificationDropdown: document.getElementById('notificationDropdown'),
        userMenuBtn: document.getElementById('userMenuBtn'),
        userMenuDropdown: document.getElementById('userMenuDropdown'),
        confirmModal: document.getElementById('confirmModal'),
        confirmModalTitle: document.getElementById('confirmModalTitle'),
        confirmModalMessage: document.getElementById('confirmModalMessage'),
        confirmModalConfirm: document.getElementById('confirmModalConfirm'),
        confirmModalCancel: document.getElementById('confirmModalCancel'),
        loadingModal: document.getElementById('loadingModal'),
        loadingMessage: document.getElementById('loadingMessage'),
        flashContainer: document.getElementById('flashContainer')
    };

    // ==========================================================================
    // Utility Functions
    // ==========================================================================

    function $(selector, context = document) {
        return context.querySelector(selector);
    }

    function $$(selector, context = document) {
        return Array.from(context.querySelectorAll(selector));
    }

    function on(event, selector, handler) {
        document.addEventListener(event, function(e) {
            const target = e.target.closest(selector);
            if (target) handler.call(target, e);
        });
    }

    function toggleClass(el, className, force) {
        if (!el) return;
        el.classList.toggle(className, force);
    }

    function show(el) {
        if (!el) return;
        el.hidden = false;
        // Force reflow for animation
        el.offsetHeight;
        el.classList.add('is-visible');
    }

    function hide(el) {
        if (!el) return;
        el.classList.remove('is-visible');
        setTimeout(() => { el.hidden = true; }, 200);
    }

    // ==========================================================================
    // Theme Management
    // ==========================================================================

    function initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        state.theme = savedTheme;
        updateThemeIcons();
    }

    function updateThemeIcons() {
        const isDark = state.theme === 'dark';
        $$('.theme-icon-light').forEach(el => el.style.display = isDark ? 'none' : 'block');
        $$('.theme-icon-dark').forEach(el => el.style.display = isDark ? 'block' : 'none');
    }

    function toggleTheme() {
        state.theme = state.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', state.theme);
        localStorage.setItem('theme', state.theme);
        updateThemeIcons();
    }

    // ==========================================================================
    // Sidebar Management
    // ==========================================================================

    function openSidebar() {
        state.sidebarOpen = true;
        elements.sidebar?.classList.add('open');
        elements.sidebarOverlay?.classList.add('visible');
        elements.mobileMenuBtn?.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        state.sidebarOpen = false;
        elements.sidebar?.classList.remove('open');
        elements.sidebarOverlay?.classList.remove('visible');
        elements.mobileMenuBtn?.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    }

    function toggleSidebar() {
        if (state.sidebarOpen) closeSidebar();
        else openSidebar();
    }

    function toggleSidebarCollapse() {
        state.sidebarCollapsed = !state.sidebarCollapsed;
        elements.sidebar?.classList.toggle('collapsed', state.sidebarCollapsed);
        localStorage.setItem('sidebarCollapsed', state.sidebarCollapsed);
    }

    function initSidebarCollapse() {
        const saved = localStorage.getItem('sidebarCollapsed');
        if (saved === 'true') {
            state.sidebarCollapsed = true;
            elements.sidebar?.classList.add('collapsed');
        }
    }

    // ==========================================================================
    // Dropdown Management
    // ==========================================================================

    function closeAllDropdowns() {
        $$('.notification-dropdown, .user-menu-dropdown').forEach(d => hide(d));
        $$('.notification-btn, .user-menu-btn').forEach(b => b.setAttribute('aria-expanded', 'false'));
        state.activeDropdown = null;
    }

    function toggleDropdown(btn, dropdown) {
        if (state.activeDropdown === dropdown) {
            closeAllDropdowns();
            return;
        }
        closeAllDropdowns();
        const isOpen = !dropdown.hidden;
        if (isOpen) {
            show(dropdown);
            btn.setAttribute('aria-expanded', 'true');
            state.activeDropdown = dropdown;
        } else {
            hide(dropdown);
            btn.setAttribute('aria-expanded', 'false');
            state.activeDropdown = null;
        }
    }

    // ==========================================================================
    // Modal Management
    // ==========================================================================

    let confirmCallback = null;

    function showConfirmModal(title, message, onConfirm) {
        elements.confirmModalTitle.textContent = title;
        elements.confirmModalMessage.textContent = message;
        confirmCallback = onConfirm;
        show(elements.confirmModal);
        elements.confirmModalConfirm.focus();
    }

    function hideConfirmModal() {
        hide(elements.confirmModal);
        confirmCallback = null;
    }

    function showLoadingModal(message = 'Processing...') {
        elements.loadingMessage.textContent = message;
        show(elements.loadingModal);
    }

    function hideLoadingModal() {
        hide(elements.loadingModal);
    }

    // ==========================================================================
    // Flash Messages
    // ==========================================================================

    function initFlashMessages() {
        on('click', '.flash-close', function() {
            const flash = this.closest('.flash-message');
            if (flash) {
                flash.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => flash.remove(), 300);
            }
        });

        // Auto-dismiss after 5 seconds
        $$('.flash-message').forEach(flash => {
            setTimeout(() => {
                if (flash.parentNode) {
                    flash.style.animation = 'slideOut 0.3s ease forwards';
                    setTimeout(() => flash.remove(), 300);
                }
            }, 5000);
        });
    }

    // Add slideOut animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOut {
            from { opacity: 1; transform: translateX(0); }
            to { opacity: 0; transform: translateX(100%); }
        }
    `;
    document.head.appendChild(style);

    // ==========================================================================
    // Lucide Icons
    // ==========================================================================

    function initIcons() {
        if (window.lucide) {
            window.lucide.createIcons({
                attrs: {
                    'stroke-width': 2,
                    'stroke-linecap': 'round',
                    'stroke-linejoin': 'round'
                }
            });
        }
    }

    function refreshIcons() {
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    // ==========================================================================
    // Form Validation Helpers
    // ==========================================================================

    function validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            const error = validateField(field);
            if (error) {
                showFieldError(field, error);
                isValid = false;
            } else {
                clearFieldError(field);
            }
        });

        return isValid;
    }

    function validateField(field) {
        if (field.required && !field.value.trim()) {
            return `${field.labels[0]?.textContent?.replace('*', '').trim() || 'This field'} is required`;
        }

        if (field.type === 'email' && field.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value)) {
            return 'Please enter a valid email address';
        }

        if (field.type === 'number' && field.value) {
            const min = parseFloat(field.min);
            const max = parseFloat(field.max);
            const val = parseFloat(field.value);
            if (!isNaN(min) && val < min) return `Value must be at least ${min}`;
            if (!isNaN(max) && val > max) return `Value must be at most ${max}`;
        }

        if (field.type === 'date' && field.value) {
            const today = new Date().toISOString().split('T')[0];
            if (field.min && field.value < field.min) {
                return 'Date cannot be in the past';
            }
        }

        return null;
    }

    function showFieldError(field, message) {
        clearFieldError(field);
        field.style.borderColor = '#F87171';
        const errorEl = document.createElement('div');
        errorEl.className = 'form-error';
        errorEl.textContent = message;
        field.parentNode.appendChild(errorEl);
    }

    function clearFieldError(field) {
        field.style.borderColor = '';
        const errorEl = field.parentNode.querySelector('.form-error');
        if (errorEl) errorEl.remove();
    }

    // ==========================================================================
    // Global Confirm Function
    // ==========================================================================

    window.confirmAction = function(title, message) {
        return new Promise((resolve) => {
            showConfirmModal(title, message, () => {
                resolve(true);
                hideConfirmModal();
            });
            elements.confirmModalCancel.onclick = () => {
                resolve(false);
                hideConfirmModal();
            };
            elements.confirmModal.querySelector('.modal-close').onclick = () => {
                resolve(false);
                hideConfirmModal();
            };
        });
    };

    // ==========================================================================
    // Event Listeners
    // ==========================================================================

    function initEventListeners() {
        // Theme toggle
        elements.themeToggle?.addEventListener('click', toggleTheme);

        // Sidebar toggle (desktop collapse)
        elements.sidebarToggle?.addEventListener('click', toggleSidebarCollapse);

        // Mobile menu button
        elements.mobileMenuBtn?.addEventListener('click', toggleSidebar);

        // Sidebar overlay click to close
        elements.sidebarOverlay?.addEventListener('click', closeSidebar);

        // Notification dropdown
        elements.notificationBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleDropdown(elements.notificationBtn, elements.notificationDropdown);
        });

        // User menu dropdown
        elements.userMenuBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleDropdown(elements.userMenuBtn, elements.userMenuDropdown);
        });

        // Close dropdowns on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.notifications') && !e.target.closest('.user-menu')) {
                closeAllDropdowns();
            }
        });

        // Close dropdowns on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeAllDropdowns();
                if (state.sidebarOpen) closeSidebar();
                if (!elements.confirmModal?.hidden) hideConfirmModal();
                if (!elements.loadingModal?.hidden) hideLoadingModal();
            }
        });

        // Modal close buttons
        elements.confirmModalCancel?.addEventListener('click', hideConfirmModal);
        elements.confirmModal?.querySelector('.modal-close')?.addEventListener('click', hideConfirmModal);
        elements.confirmModal?.addEventListener('click', (e) => {
            if (e.target === elements.confirmModal) hideConfirmModal();
        });

        elements.confirmModalConfirm?.addEventListener('click', () => {
            if (confirmCallback) confirmCallback();
        });

        // Flash messages
        initFlashMessages();

        // Form validation
        on('submit', 'form[novalidate]', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                const firstError = this.querySelector('.form-error');
                if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });

        on('input', 'form[novalidate] [required]', function() {
            clearFieldError(this);
        });

        on('blur', 'form[novalidate] [required]', function() {
            const error = validateField(this);
            if (error) showFieldError(this, error);
        });

        // Keyboard navigation for dropdowns
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab' && state.activeDropdown) {
                const focusable = state.activeDropdown.querySelectorAll(
                    'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                const first = focusable[0];
                const last = focusable[focusable.length - 1];
                if (e.shiftKey && document.activeElement === first) {
                    e.preventDefault();
                    last.focus();
                } else if (!e.shiftKey && document.activeElement === last) {
                    e.preventDefault();
                    first.focus();
                }
            }
        });
    }

    // ==========================================================================
    // Initialize
    // ==========================================================================

    function init() {
        initTheme();
        initSidebarCollapse();
        initIcons();
        initEventListeners();

        // Re-initialize icons after dynamic content
        const observer = new MutationObserver(() => {
            refreshIcons();
        });
        observer.observe(document.body, { childList: true, subtree: true });

        // Expose globally for other scripts
        window.FleetFlow = {
            state,
            elements,
            showConfirmModal,
            hideConfirmModal,
            showLoadingModal,
            hideLoadingModal,
            refreshIcons,
            validateForm,
            closeAllDropdowns,
            closeSidebar,
            toggleSidebar,
            toggleSidebarCollapse
        };
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();