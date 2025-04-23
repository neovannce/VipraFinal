// This script can be expanded to add more interactivity or form validation as needed.
document.addEventListener("DOMContentLoaded", function() {
    // You can add additional scripts here for form validation or user interactivity.
});
document.querySelector('form').addEventListener('input', function () {
    const allFilled = [...document.querySelectorAll('input[required]')].every(input => input.value.trim() !== '');
    const submitButton = document.querySelector('.btn-primary');
    if (allFilled) {
        submitButton.classList.add('active');
        submitButton.removeAttribute('disabled');
    } else {
        submitButton.classList.remove('active');
        submitButton.setAttribute('disabled', true);
    }
});
