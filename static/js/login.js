console.log('Login script loaded');

async function handleLogin(event) {
    event.preventDefault();

    const loginForm = document.getElementById('login-form');
    const formData = new FormData(loginForm);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            credentials: 'include'
        });

        const result = await response.json();

        if (response.ok) {
            showSuccess('Login successful! Redirecting...', loginForm);
            setTimeout(() => {
                const redirectUrl = response.headers.get('X-Redirect-URL') || '/viewer';
                window.location.href = redirectUrl;
            }, 1500);
        } else {
            showError(result.detail || 'An error occurred during login', loginForm);
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('An error occurred during login', loginForm);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    } else {
        console.error('Login form not found');
    }
}); 