/* Centre for Development of Advanced Computing (C-DAC) — Global JavaScript */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Menu Toggle
    const mobileToggle = document.getElementById('mobile-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // 2. Client-side Course Filtering (Progressive Enhancement)
    const courseSearchInput = document.getElementById('course-search-input');
    const courseCards = document.querySelectorAll('.course-card');

    if (courseSearchInput && courseCards.length > 0) {
        courseSearchInput.addEventListener('keyup', (e) => {
            const query = e.target.value.toLowerCase().trim();
            courseCards.forEach(card => {
                const title = card.getAttribute('data-course-name') || card.querySelector('.course-title')?.textContent || '';
                const description = card.querySelector('.course-description')?.textContent || '';
                if (title.toLowerCase().includes(query) || description.toLowerCase().includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // 3. Client-side Form Validation Helper
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            let valid = true;
            const requiredInputs = form.querySelectorAll('[required]');
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            const password = form.querySelector('input[name="password"]');
            const confirmPassword = form.querySelector('input[name="confirm_password"]');
            if (password && confirmPassword && password.value !== confirmPassword.value) {
                valid = false;
                confirmPassword.classList.add('is-invalid');
                alert('Passwords do not match.');
            }

            if (!valid) {
                e.preventDefault();
            }
        });
    });
});
