// AMC Website - Mobile Navigation and Interactive Features

document.addEventListener('DOMContentLoaded', function() {
    
    // Mobile Navigation Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileNav = document.querySelector('.mobile-nav');
    const mobileNavClose = document.querySelector('.mobile-nav-close');
    const body = document.body;

    if (menuToggle && mobileNav) {
        menuToggle.addEventListener('click', function() {
            mobileNav.classList.add('active');
            body.style.overflow = 'hidden'; // Prevent scrolling when menu is open
        });
    }

    if (mobileNavClose && mobileNav) {
        mobileNavClose.addEventListener('click', closeMobileNav);
    }

    // Close mobile nav when clicking outside or on a link
    if (mobileNav) {
        mobileNav.addEventListener('click', function(e) {
            if (e.target === mobileNav) {
                closeMobileNav();
            }
        });

        // Close when clicking on navigation links
        const mobileNavLinks = mobileNav.querySelectorAll('a');
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', closeMobileNav);
        });
    }

    function closeMobileNav() {
        if (mobileNav) {
            mobileNav.classList.remove('active');
            body.style.overflow = ''; // Restore scrolling
        }
    }

    // Form Enhancement
    enhanceForms();

    // Flash Message Auto-Dismiss
    autoHideFlashMessages();
});

// Form validation and enhancement
function enhanceForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('.form-input');
        
        inputs.forEach(input => {
            // Add focus/blur effects
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
                if (this.value.trim() !== '') {
                    this.parentElement.classList.add('filled');
                } else {
                    this.parentElement.classList.remove('filled');
                }
            });

            // Basic client-side validation
            if (input.type === 'email') {
                input.addEventListener('blur', validateEmail);
            }
            
            if (input.hasAttribute('required')) {
                input.addEventListener('blur', validateRequired);
            }
        });

        // Handle form submission
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = submitBtn.textContent.replace(/Sign|Log|Register|Submit/i, function(match) {
                    return match + 'ing...';
                });
                
                // Re-enable after 3 seconds to prevent permanent lock
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = submitBtn.textContent.replace('ing...', '');
                }, 3000);
            }
        });
    });
}

// Email validation
function validateEmail(e) {
    const email = e.target.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        showFieldError(e.target, 'Please enter a valid email address');
    } else {
        clearFieldError(e.target);
    }
}

// Required field validation
function validateRequired(e) {
    const value = e.target.value.trim();
    
    if (!value) {
        showFieldError(e.target, 'This field is required');
    } else {
        clearFieldError(e.target);
    }
}

// Show field error
function showFieldError(input, message) {
    clearFieldError(input);
    
    input.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.textContent = message;
    
    input.parentElement.appendChild(errorDiv);
}

// Clear field error
function clearFieldError(input) {
    input.classList.remove('error');
    
    const existingError = input.parentElement.querySelector('.form-error');
    if (existingError) {
        existingError.remove();
    }
}

// Auto-hide flash messages after 5 seconds
function autoHideFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.className = 'flash-close';
        closeBtn.style.cssText = `
            float: right;
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            margin-left: 10px;
            opacity: 0.7;
        `;
        
        closeBtn.addEventListener('click', function() {
            message.style.transition = 'opacity 0.3s ease';
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        });
        
        message.appendChild(closeBtn);
        
        // Auto-hide after 5 seconds (except errors)
        if (!message.classList.contains('flash-error')) {
            setTimeout(() => {
                if (message.parentElement) {
                    message.style.transition = 'opacity 0.3s ease';
                    message.style.opacity = '0';
                    setTimeout(() => message.remove(), 300);
                }
            }, 5000);
        }
    });
}

// Utility function for AJAX requests (for future RSVP functionality)
function makeRequest(url, options = {}) {
    const defaults = {
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    const config = { ...defaults, ...options };
    
    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Request failed:', error);
            throw error;
        });
}

// Smooth scroll for anchor links
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && e.target.getAttribute('href').startsWith('#')) {
        e.preventDefault();
        const targetId = e.target.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});
