// Theme toggle functionality with session persistence and server sync
document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const sunIcon = document.getElementById('sun-icon');
    const moonIcon = document.getElementById('moon-icon');

    // Retrieve initial theme from attribute set by Jinja context
    let currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';

    const updateIcons = (theme) => {
        if (theme === 'dark') {
            sunIcon.classList.remove('d-none');
            moonIcon.classList.add('d-none');
        } else {
            sunIcon.classList.add('d-none');
            moonIcon.classList.remove('d-none');
        }
    };

    updateIcons(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Update UI immediately
            document.documentElement.setAttribute('data-theme', nextTheme);
            currentTheme = nextTheme;
            updateIcons(nextTheme);

            // Sync with Server (saves preference to DB for logged in user)
            fetch('/dashboard/toggle-theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(res => res.json())
            .then(data => {
                if (!data.success) {
                    console.error("Failed to sync theme preference with server.");
                }
            })
            .catch(err => console.error("Theme toggle network error:", err));
        });
    }
});
