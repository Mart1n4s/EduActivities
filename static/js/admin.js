console.log('Admin.js loaded');

async function handleAddUser(e) {
    e.preventDefault();
    const form = document.getElementById('addUserForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/admin/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess('User added successfully!', form);
            form.reset();
            setTimeout(() => {
                bootstrap.Modal.getInstance(document.getElementById('addUserModal')).hide();
                loadUsers();
            }, 1500);
        } else {
            showError(result.detail || 'Error adding user', form);
        }
    } catch (error) {
        console.error('Error adding user:', error);
        showError('Error adding user. Please try again.', form);
    }
}

async function handleEditUser(e) {
    e.preventDefault();
    const form = document.getElementById('editUserForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const userId = data.user_id;
    
    try {
        const response = await fetch(`/api/admin/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess('User updated successfully!', form);
            setTimeout(() => {
                bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
                loadUsers();
            }, 1500);
        } else {
            showError(result.detail || 'Error updating user', form);
        }
    } catch (error) {
        console.error('Error updating user:', error);
        showError('Error updating user. Please try again.', form);
    }
}

async function deleteUser(userId) {   
    try {
        const response = await fetch(`/api/admin/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            loadUsers();
            loadActivities();
        }
    } catch (error) {
        console.error('Error deleting user:', error);
    }
}

async function handleAddActivity(e) {
    e.preventDefault();
    const form = document.getElementById('addActivityForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    const categories = Array.from(form.querySelectorAll('input[name="category"]:checked'))
        .map(checkbox => checkbox.value);

    data.categories = categories;    

    const organizerSelect = form.querySelector('select[name="organizerId"]');    
    data.organizer_id = organizerSelect.value;
    
    try {
        const response = await fetch('/api/admin/activities', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess('Activity added successfully!', form);
            form.reset();
            setTimeout(() => {
                bootstrap.Modal.getInstance(document.getElementById('addActivityModal')).hide();
                loadActivities();
            }, 1500);
        } else {
            showError(result.detail || 'Error adding activity', form);
        }
    } catch (error) {
        console.error('Error adding activity:', error);
        showError('Error adding activity. Please try again.', form);
    }
}

async function handleEditActivity(e) {
    e.preventDefault();
    const form = document.getElementById('editActivityForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const activityId = data.activity_id;
    
    const currentActivityResponse = await fetch(`/api/admin/activities/${activityId}`, {
        credentials: 'include'
    });
    
    if (!currentActivityResponse.ok) {
        showError('Failed to get current activity data');
        return;
    }
    
    const currentActivity = await currentActivityResponse.json();
    
    const categories = Array.from(form.querySelectorAll('input[name="category"]:checked'))
        .map(checkbox => checkbox.value);
    
    const organizerSelect = form.querySelector('select[name="organizerId"]');
    
    const statusSelect = form.querySelector('select[name="status"]');
    
    const cleanData = {
        title: data.title,
        description: data.description,
        categories: categories,
        date: data.date,
        start_time: data.start_time,
        duration: data.duration,
        location: data.location,
        price: parseInt(data.price),
        max_participants: parseInt(data.max_participants),
        current_participants: currentActivity.current_participants || 0,
        status: statusSelect.value,
        instructor: data.instructor,
        organizer_id: organizerSelect.value,
        liked_by: currentActivity.liked_by || []
    };
    
    try {
        const response = await fetch(`/api/admin/activities/${activityId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(cleanData),
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess('Activity updated successfully!', form);
            setTimeout(() => {
                bootstrap.Modal.getInstance(document.getElementById('editActivityModal')).hide();
                loadActivities();
            }, 1500);
        } else {
            console.error('Error response:', result);
            if (response.status === 404) {
                showError('Activity not found. It may have been deleted.', form);
            } else {
                showError(result.detail || 'Error updating activity', form);
            }
        }
    } catch (error) {
        console.error('Error updating activity:', error);
        showError('Error updating activity. Please try again.', form);
    }
}

async function deleteActivity(activityId) {   
    try {
        const response = await fetch(`/api/admin/activities/${activityId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            loadActivities();
        }

    } catch (error) {
        console.error('Error deleting activity:', error);
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/api/admin/users', {
            credentials: 'include'
        });
        
        const users = await response.json();
        const filteredUsers = users.filter(user => user.role !== 'admin');
        const usersTableBody = document.getElementById('users-table-body');
        
        if (filteredUsers.length === 0) {
            usersTableBody.innerHTML = '<tr><td colspan="7" class="text-center">No users found</td></tr>';
            return;
        }
        
        usersTableBody.innerHTML = filteredUsers.map(user => `
            <tr>
                <td>${user.username}</td>
                <td>${user.name}</td>
                <td>${user.surname}</td>
                <td>${user.telephone_number}</td>
                <td>${user.email}</td>
                <td>${user.role}</td>
                <td>
                    <div class="btn-group" role="group">
                        <button class="btn btn-primary btn-sm edit-user-btn" data-user-id="${user._id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-danger btn-sm delete-user-btn" data-user-id="${user._id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        usersTableBody.querySelectorAll('.edit-user-btn').forEach(btn => {
            btn.addEventListener('click', () => editUser(btn.dataset.userId));
        });
        usersTableBody.querySelectorAll('.delete-user-btn').forEach(btn => {
            btn.addEventListener('click', () => deleteUser(btn.dataset.userId));
        });
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

async function loadActivities() {
    try {
        const response = await fetch('/api/admin/activities', {
            credentials: 'include'
        });
        
        const activities = await response.json();
        const activitiesTableBody = document.getElementById('activities-table-body');
        
        if (activities.length === 0) {
            activitiesTableBody.innerHTML = '<tr><td colspan="7" class="text-center">No activities found</td></tr>';
            return;
        }
        
        activitiesTableBody.innerHTML = activities.map(activity => {
            let categories = [];
            if (activity.categories) {
                categories = Array.isArray(activity.categories) ? activity.categories : [activity.categories];
            } else {
                categories = ['Uncategorized'];
            }

            return `
                <tr>
                    <td>${activity.title}</td>
                    <td><span class="category-badge">${categories.join(', ')}</span></td>
                    <td>${new Date(activity.date).toLocaleDateString()}</td>
                    <td>${activity.location}</td>
                    <td>${activity.organizer_name || 'N/A'}</td>
                    <td>
                        <span class="status-badge status-${activity.status.toLowerCase()}">
                            ${activity.status}
                        </span>
                    </td>
                    <td>
                        <div class="btn-group" role="group">
                            <button class="btn btn-primary btn-sm edit-activity-btn" data-activity-id="${activity._id}">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-danger btn-sm delete-activity-btn" data-activity-id="${activity._id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        activitiesTableBody.querySelectorAll('.edit-activity-btn').forEach(btn => {
            btn.addEventListener('click', () => editActivity(btn.dataset.activityId));
        });
        activitiesTableBody.querySelectorAll('.delete-activity-btn').forEach(btn => {
            btn.addEventListener('click', () => deleteActivity(btn.dataset.activityId));
        });
    } catch (error) {
        console.error('Error loading activities:', error);
    }
}

async function loadOrganizers() {
    try {
        const response = await fetch('/api/admin/users', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to load organizers');
        }
        
        const users = await response.json();
        const organizers = users.filter(user => user.role === 'organizer');
        
        const organizerSelects = document.querySelectorAll('select[name="organizerId"]');
        organizerSelects.forEach(select => {
            const currentValue = select.value;
            select.innerHTML = `
                <option value="">Select Organizer</option>
                ${organizers.map(org => `
                    <option value="${org._id}">${org.name} ${org.surname}</option>
                `).join('')}
            `;
            select.value = currentValue;
        });
    } catch (error) {
        console.error('Error loading organizers:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    loadUsers();
    loadActivities();
    
    document.getElementById('submitUserBtn')?.addEventListener('click', handleAddUser);
    document.getElementById('submitActivityBtn')?.addEventListener('click', handleAddActivity);
    
    const activityModal = document.getElementById('addActivityModal');
    if (activityModal) {
        activityModal.addEventListener('show.bs.modal', loadOrganizers);
    }
    
    document.getElementById('submitEditUserBtn')?.addEventListener('click', handleEditUser);
    document.getElementById('submitEditActivityBtn')?.addEventListener('click', handleEditActivity);
});

window.editUser = async function(userId) {
    try {
        const response = await fetch(`/api/admin/users/${userId}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to load user data');
        }
        
        const user = await response.json();
        
        if (!user || !user._id) {
            throw new Error('Invalid user data received');
        }
        
        document.getElementById('edit_user_id').value = user._id;
        document.getElementById('edit_username').value = user.username;
        document.getElementById('edit_password').value = '';
        document.getElementById('edit_name').value = user.name;
        document.getElementById('edit_surname').value = user.surname;
        document.getElementById('edit_telephone_number').value = user.telephone_number;
        document.getElementById('edit_email').value = user.email;
        document.getElementById('edit_role').value = user.role;
        
        const editModal = new bootstrap.Modal(document.getElementById('editUserModal'));
        editModal.show();
    } catch (error) {
        console.error('Error loading user data:', error);
        showError(error.message || 'Error loading user data. Please try again.');
    }
};

window.editActivity = async function(activityId) {
    try {
        const response = await fetch(`/api/admin/activities/${activityId}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to load activity data');
        }
        
        const activity = await response.json();
        
        if (!activity || !activity._id) {
            throw new Error('Invalid activity data received');
        }
        
        document.getElementById('edit_activity_id').value = activity._id;
        document.getElementById('edit_title').value = activity.title;
        document.getElementById('edit_description').value = activity.description;
        document.getElementById('edit_date').value = activity.date;
        document.getElementById('edit_start_time').value = activity.start_time;
        document.getElementById('edit_duration').value = activity.duration;
        document.getElementById('edit_location').value = activity.location;
        document.getElementById('edit_price').value = activity.price;
        document.getElementById('edit_max_participants').value = activity.max_participants;
        document.getElementById('edit_status').value = activity.status || 'available';
        document.getElementById('edit_instructor').value = activity.instructor;
        
        await loadOrganizers();
        document.getElementById('edit_organizerId').value = activity.organizer_id;
        
        const categoriesContainer = document.getElementById('edit_categories');
        const allCategories = ['Art', 'Music', 'Dance', 'Sports', 'Technology', 'Science', 'Language', 'Social', 'Outdoors', 'Indoors'];
        const activityCategories = Array.isArray(activity.categories) ? activity.categories : [activity.categories];
        
        categoriesContainer.innerHTML = allCategories.map(category => `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" name="category" value="${category}" 
                    id="edit_category${category}" ${activityCategories.includes(category) ? 'checked' : ''}>
                <label class="form-check-label" for="edit_category${category}">${category}</label>
            </div>
        `).join('');
        
        const editModal = new bootstrap.Modal(document.getElementById('editActivityModal'));
        editModal.show();
    } catch (error) {
        console.error('Error loading activity data:', error);
        showError(error.message || 'Error loading activity data. Please try again.');
    }
};
