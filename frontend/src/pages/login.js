document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');
    const loginBtn = loginForm.querySelector('.btn-primary');
    const btnText = loginBtn.querySelector('.btn-text');
    const btnLoader = loginBtn.querySelector('.btn-loader');

    // Check if user is already logged in
    if (authService.isAuthenticated()) {
        checkUserAndRedirect();
    }

    async function checkUserAndRedirect() {
        try {
            const user = await authService.getCurrentUser();
            if (user.is_admin) {
                window.location.href = 'admin-dashboard.html';
            } else {
                window.location.href = 'student-dashboard.html';
            }
        } catch (error) {
            // Token might be expired, stay on login page
            authService.logout();
        }
    }

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        if (!username || !password) {
            showError('Please enter both username and password');
            return;
        }

        setLoading(true);
        hideError();

        try {
            await authService.login(username, password);

            // Get user info to determine redirect
            const user = await authService.getCurrentUser();

            if (user.is_admin) {
                window.location.href = 'admin-dashboard.html';
            } else {
                window.location.href = 'student-dashboard.html';
            }
        } catch (error) {
            showError(error.message);
            setLoading(false);
        }
    });

    function setLoading(loading) {
        loginBtn.classList.toggle('loading', loading);
        loginBtn.disabled = loading;

        if (loading) {
            btnText.style.display = 'none';
            btnLoader.style.display = 'block';
        } else {
            btnText.style.display = 'block';
            btnLoader.style.display = 'none';
        }
    }

    function showError(message) {
        loginError.textContent = message;
        loginError.style.display = 'block';
        loginError.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideError() {
        loginError.style.display = 'none';
    }

    // Handle Enter key on form elements
    document.getElementById('username').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('password').focus();
        }
    });

    document.getElementById('password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            loginForm.dispatchEvent(new Event('submit'));
        }
    });
});