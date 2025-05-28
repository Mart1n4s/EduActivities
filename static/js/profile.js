console.log("Profile.js loaded");

const profileForm = document.getElementById('profileForm');
const editProfileBtn = document.getElementById('editProfileBtn');
const saveProfileBtn = document.getElementById('saveProfileBtn');
const inputs = profileForm.querySelectorAll('input:not([readonly])');

let originalValues = {};

inputs.forEach(input => {
    input.disabled = true;
});

editProfileBtn.addEventListener('click', () => {
    inputs.forEach(input => {
        input.disabled = false;
    });
    editProfileBtn.classList.add('d-none');
    saveProfileBtn.classList.remove('d-none');
});

saveProfileBtn.addEventListener('click', async () => {
    if (!hasChanges()) {
        inputs.forEach(input => {
            input.disabled = true;
        });
        editProfileBtn.classList.remove('d-none');
        saveProfileBtn.classList.add('d-none');
        return;
    }

    const formData = new FormData(profileForm);
    const data = Object.fromEntries(formData.entries());
    try {
        const response = await fetch('/api/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const responseData = await response.json();
            throw new Error(responseData.detail || 'Failed to update profile');
        }

        originalValues = {
            name: data.name,
            surname: data.surname,
            email: data.email,
            telephone_number: data.telephone_number
        };

        inputs.forEach(input => {
            input.disabled = true;
        });
        editProfileBtn.classList.remove('d-none');
        saveProfileBtn.classList.add('d-none');
        showSuccess('Profile updated successfully!', profileForm);
    } catch (error) {
        console.error('Error updating profile:', error);
        showError(error.message, profileForm);
    }
});

function hasChanges() {
    const formData = new FormData(profileForm);
    const currentValues = Object.fromEntries(formData.entries());
    
    return Object.keys(originalValues).some(key => 
        currentValues[key] !== originalValues[key]
    );
}

async function fetchProfileData() {
    try {
        const response = await fetch('/api/profile', {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to fetch profile data');
        }
        
        const data = await response.json();
        console.log("Profile data:", data);

        document.getElementById('username').value = data.username;
        document.getElementById('name').value = data.name;
        document.getElementById('surname').value = data.surname;
        document.getElementById('email').value = data.email;
        document.getElementById('telephone_number').value = data.telephone_number;

        originalValues = {
            name: data.name,
            surname: data.surname,
            email: data.email,
            telephone_number: data.telephone_number
        };
    } catch (error) {
        console.error('Error fetching profile:', error);
        window.location.href = '/auth/login';
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await fetchProfileData();
}); 
