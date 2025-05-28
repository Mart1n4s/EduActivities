console.log('Register.js loaded');

async function handleRegister(e) {
    e.preventDefault();
   
    const registerForm = document.getElementById('register-form');
    const formData = new FormData(registerForm);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            credentials: 'include'
        });

        const result = await response.json();

        if (response.ok) {
            showSuccess('Registration successful! Redirecting to login...', registerForm);
            setTimeout(() => {
                window.location.href = '/auth/login';
            }, 1500);
        } else {
            const errorMessage = result.detail || 'Registration failed. Please try again.';
            showError(errorMessage, registerForm);
        }
    } catch (error) {
        console.error('Registration error:', error);
        showError('An error occurred. Please try again.', registerForm);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    } else {
        console.error('Register form not found');
    }
}); 