/**
 * Amravati City Bus Management System
 * Client-side Form Validation Helpers
 */

const FormValidator = {
    isValidEmail(email) {
        return /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/.test(email.trim());
    },

    isValidPhone(phone) {
        const cleaned = phone.replace(/[\s\-\+]/g, '');
        return /^[6-9]\d{9}$/.test(cleaned.length === 12 && cleaned.startsWith('91') ? cleaned.slice(2) : cleaned);
    },

    isValidUsername(username) {
        return /^[a-zA-Z0-9_]{3,50}$/.test(username.trim());
    },

    isNonEmpty(value) {
        return value !== null && value !== undefined && value.toString().trim().length > 0;
    },

    isValidPositiveNumber(val) {
        const num = parseFloat(val);
        return !isNaN(num) && num > 0;
    },

    showInputError(inputEl, message) {
        inputEl.classList.add('is-invalid');
        let feedback = inputEl.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            inputEl.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;
    },

    clearInputError(inputEl) {
        inputEl.classList.remove('is-invalid');
        const feedback = inputEl.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.textContent = '';
        }
    }
};
