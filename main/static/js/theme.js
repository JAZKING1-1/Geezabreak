// Theme management
function toggleDarkMode() {
    const body = document.body;
    const isDarkMode = body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
    
    // Update button text/icon
    const darkModeBtn = document.querySelector('[aria-label="Toggle dark mode"]');
    if (darkModeBtn) {
        darkModeBtn.innerHTML = isDarkMode ? '☀️ Light Mode' : '🌙 Dark Mode';
    }

    // Dispatch event for other scripts that might need to know about theme changes
    window.dispatchEvent(new CustomEvent('themeChange', { detail: { isDarkMode } }));
}

// Initialize theme based on user's preference
document.addEventListener('DOMContentLoaded', () => {
    // Check if user has a saved preference
    const savedDarkMode = localStorage.getItem('darkMode');
    
    // Check system preference if no saved preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Apply dark mode if either saved preference or system preference is dark
    if (savedDarkMode === 'true' || (savedDarkMode === null && prefersDark)) {
        document.body.classList.add('dark-mode');
        const darkModeBtn = document.querySelector('[aria-label="Toggle dark mode"]');
        if (darkModeBtn) {
            darkModeBtn.innerHTML = '☀️ Light Mode';
        }
    }

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (localStorage.getItem('darkMode') === null) {  // Only auto-switch if user hasn't set a preference
            if (e.matches) {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
        }
    });
});
