document.addEventListener('DOMContentLoaded', () => {
    console.log('Script loaded and ready.');
});

/**
 * Example function to demonstrate basic functionality
 * @param {string} message - The message to display
 */
function displayMessage(message) {
    const outputElement = document.getElementById('output');
    if (outputElement) {
        outputElement.textContent = message;
    } else {
        console.log(message);
    }
}

/**
 * Adds micro-animations to elements with the 'animate-hover' class
 */
function initMicroAnimations() {
    const animatedElements = document.querySelectorAll('.animate-hover, button, img');

    animatedElements.forEach(element => {
        element.style.transition = 'transform 0.2s ease-in-out, filter 0.2s ease-in-out';

        element.addEventListener('mouseenter', () => {
            element.style.transform = 'scale(1.05)';
            element.style.filter = 'brightness(1.1)';
        });

        element.addEventListener('mouseleave', () => {
            element.style.transform = 'scale(1)';
            element.style.filter = 'brightness(1)';
        });

        element.addEventListener('mousedown', () => {
            element.style.transform = 'scale(0.95)';
        });

        element.addEventListener('mouseup', () => {
            element.style.transform = 'scale(1.05)';
        });
    });
}

// Initialize animations when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initMicroAnimations);
