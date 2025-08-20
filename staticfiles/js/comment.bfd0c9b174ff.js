// Comment AJAX for home page
async function submitComment(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const msgBox = document.getElementById('commentMessage');
    msgBox.style.display = 'none';
    try {
        const response = await fetch('/submit-comment/', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });
        const data = await response.json();
        if (data.status === 'success') {
            msgBox.textContent = 'Thank you for your comment!';
            msgBox.style.display = 'block';
            msgBox.className = 'text-success text-center mt-2';
            // Prepend new comment to list
            const commentsList = document.getElementById('commentsList');
            const newComment = document.createElement('div');
            newComment.className = 'card mb-2';
            newComment.innerHTML = `<div class="card-body"><strong>${data.name}</strong> <span class="text-muted small">just now</span><p class="mb-0">${data.message}</p></div>`;
            commentsList.prepend(newComment);
            form.reset();
        } else {
            msgBox.textContent = data.message;
            msgBox.style.display = 'block';
            msgBox.className = 'text-danger text-center mt-2';
        }
    } catch (error) {
        msgBox.textContent = 'An error occurred. Please try again.';
        msgBox.style.display = 'block';
        msgBox.className = 'text-danger text-center mt-2';
    }
}
// Reuse getCookie from feedback.js if available
