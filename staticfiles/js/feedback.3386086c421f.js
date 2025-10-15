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

let feedbackHideTimer;

function showFeedbackMessage(message, type = 'info') {
    const msgBox = document.getElementById('feedbackMessage');
    if (!msgBox) return;

    if (feedbackHideTimer) {
        clearTimeout(feedbackHideTimer);
        feedbackHideTimer = null;
    }

    msgBox.textContent = message;
    msgBox.setAttribute('role', 'alert');
    msgBox.setAttribute('aria-live', 'assertive');
    msgBox.style.display = 'block';
    msgBox.classList.remove('success', 'error');
    if (type === 'error') {
        msgBox.classList.add('error');
    } else if (type === 'success') {
        msgBox.classList.add('success');
    }

    feedbackHideTimer = setTimeout(() => {
        msgBox.style.display = 'none';
        msgBox.classList.remove('success', 'error');
    }, 6000);
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
    const originalLabel = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Sending…';
    try {
        const formData = new FormData(form);
        const response = await fetch('/submit-feedback/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        });
        let data;
        try {
            data = await response.json();
        } catch (err) {
            data = { status: 'error', message: 'Unexpected response from the server.' };
        }

        if (response.ok && data.status === 'success') {
            // Hide form, show thank you animation
            form.style.display = 'none';
            document.getElementById('thankYouAnimation').style.display = 'flex';
            setTimeout(() => {
                closeFeedback();
                // Reset for next time
                document.getElementById('thankYouAnimation').style.display = 'none';
                form.style.display = '';
                form.reset();
                const msgBox = document.getElementById('feedbackMessage');
                if (msgBox) {
                    msgBox.style.display = 'none';
                    msgBox.classList.remove('success', 'error');
                }
            }, 2500);
            showFeedbackMessage('Thank you for sharing your feedback!', 'success');
        } else {
            const errorMessage = data && data.message ? data.message : 'Sorry, something went wrong. Please try again.';
            showFeedbackMessage(errorMessage, 'error');
        }
    } catch (error) {
        console.error('Feedback submission failed:', error);
        showFeedbackMessage('We could not submit your feedback right now. Please try again shortly.', 'error');
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = originalLabel;
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
