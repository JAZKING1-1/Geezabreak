// Feedback form functionality
function openFeedback() {
    const modal = document.getElementById('feedbackModal');
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    // Focus first input for accessibility
    setTimeout(() => {
        const firstInput = modal.querySelector('input, textarea, select, button');
        if (firstInput) firstInput.focus();
    }, 100);
}

function closeFeedback() {
    const modal = document.getElementById('feedbackModal');
    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    // Return focus to button
    const triggerBtn = document.querySelector('.feedback-trigger');
    if (triggerBtn) triggerBtn.focus();
}

// Trap focus inside modal for accessibility
window.addEventListener('keydown', function(e) {
    const modal = document.getElementById('feedbackModal');
    if (modal.style.display === 'flex' && e.key === 'Tab') {
        const focusable = modal.querySelectorAll('input, textarea, select, button, .close-button');
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey ? document.activeElement === first : document.activeElement === last) {
            e.preventDefault();
            (e.shiftKey ? last : first).focus();
        }
    }
    if (modal.style.display === 'flex' && (e.key === 'Escape' || e.key === 'Esc')) {
        closeFeedback();
    }
});

function showFeedbackMessage(message, type) {
    const msgBox = document.getElementById('feedbackMessage');
    msgBox.textContent = "✨ " + message + " ✨";
    msgBox.classList.remove('hidden');
    setTimeout(() => {
        msgBox.classList.add('hidden');
    }, 4000);
}

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

async function submitFeedback(event) {
    event.preventDefault();
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    try {
        const formData = new FormData(form);
        const response = await fetch('/submit-feedback/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        const data = await response.json();
        if (data.status === 'success') {
            // Hide form, show thank you animation
            form.style.display = 'none';
            document.getElementById('thankYouAnimation').style.display = 'flex';
            setTimeout(() => {
                closeFeedback();
                // Reset for next time
                document.getElementById('thankYouAnimation').style.display = 'none';
                form.style.display = '';
                form.reset();
                document.getElementById('feedbackMessage').classList.add('hidden');
            }, 2500);
        } else {
            showFeedbackMessage(data.message, 'error');
        }
    } catch (error) {
        showFeedbackMessage('An error occurred. Please try again.', 'error');
    } finally {
        submitButton.disabled = false;
    }
}

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    const modal = document.getElementById('feedbackModal');
    if (event.target === modal) {
        closeFeedback();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeFeedback();
    }
});
