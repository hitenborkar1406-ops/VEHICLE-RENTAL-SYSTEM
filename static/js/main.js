/**
 * Vehicle Rental System — Main JavaScript
 * ========================================
 * Handles: theme toggle, mobile navigation toggle, flash message auto-dismiss
 */

document.addEventListener('DOMContentLoaded', function () {

    // ========== Theme Toggle ==========
    const themeToggle = document.getElementById('themeToggle');
    const themeIconSun = document.getElementById('themeIconSun');
    const themeIconMoon = document.getElementById('themeIconMoon');
    const html = document.documentElement;

    // Initialize theme from localStorage or system preference
    function initTheme() {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme) {
            html.setAttribute('data-theme', savedTheme);
        } else if (prefersDark) {
            html.setAttribute('data-theme', 'dark');
        } else {
            html.setAttribute('data-theme', 'light');
        }
        updateThemeIcons();
    }

    function updateThemeIcons() {
        const isDark = html.getAttribute('data-theme') === 'dark';
        if (themeIconSun && themeIconMoon) {
            themeIconSun.style.display = isDark ? 'block' : 'none';
            themeIconMoon.style.display = isDark ? 'none' : 'block';
        }
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcons();
        });
    }

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
        if (!localStorage.getItem('theme')) {
            html.setAttribute('data-theme', e.matches ? 'dark' : 'light');
            updateThemeIcons();
        }
    });

    initTheme();

    // ========== Mobile Navigation Toggle ==========
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            const isOpen = navLinks.classList.toggle('open');
            navToggle.setAttribute('aria-expanded', isOpen);
        });

        // Close nav when clicking a link
        navLinks.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                navLinks.classList.remove('open');
                navToggle.setAttribute('aria-expanded', 'false');
            });
        });

        // Close nav when clicking outside
        document.addEventListener('click', function (e) {
            if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('open');
                navToggle.setAttribute('aria-expanded', 'false');
            }
        });

        // Close nav on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && navLinks.classList.contains('open')) {
                navLinks.classList.remove('open');
                navToggle.setAttribute('aria-expanded', 'false');
                navToggle.focus();
            }
        });
    }

    // ========== Flash Messages Auto-dismiss ==========
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-8px)';
            setTimeout(function () {
                msg.remove();
            }, 400);
        }, 6000);
    });

    // ========== Form Loading States ==========
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && !submitBtn.classList.contains('btn-ghost')) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
    });

    // ========== Confirm Delete Improvements ==========
    document.querySelectorAll('form[onsubmit*="confirm"]').forEach(function (form) {
        const originalOnSubmit = form.onsubmit;
        form.addEventListener('submit', function (e) {
            if (originalOnSubmit && !originalOnSubmit.call(form, e)) {
                e.preventDefault();
            }
        });
    });

    // ========== Smooth Scroll for Anchor Links ==========
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                target.focus({ preventScroll: true });
            }
        });
    });

    // ========== Table Row Click for Detail ==========
    document.querySelectorAll('.data-table tbody tr[data-href]').forEach(function (row) {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function (e) {
            // Don't navigate if clicking on a button or link
            if (e.target.closest('button, a, input, select')) return;
            window.location.href = this.dataset.href;
        });

        row.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                window.location.href = this.dataset.href;
            }
        });
    });
});

/**
 * Utility: Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - 'success' | 'error' | 'info'
 */
function showToast(message, type = 'info') {
    const container = document.querySelector('.flash-messages') || (function () {
        const div = document.createElement('div');
        div.className = 'flash-messages';
        document.querySelector('.container').prepend(div);
        return div;
    })();

    const toast = document.createElement('div');
    toast.className = `flash-message flash-${type}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <span class="flash-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
        <span class="flash-text">${message}</span>
        <button class="flash-close" onclick="this.parentElement.remove()" aria-label="Close">&times;</button>
    `;
    container.appendChild(toast);

    setTimeout(function () {
        toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-8px)';
        setTimeout(function () {
            toast.remove();
        }, 400);
    }, 6000);
}