console.log('Organizer.js loaded');

const searchInput = document.getElementById('search-input');
const categoryFilter = document.getElementById('category-filter');
const activitiesTableBody = document.getElementById('activities-table-body');
const noActivities = document.getElementById('no-activities');
const activityForm = document.getElementById('activityForm');
const submitActivityBtn = document.getElementById('submitActivityBtn');
const modalTitle = document.getElementById('modalTitle');
const activityId = document.getElementById('activityId');

let activities = [];

document.addEventListener('DOMContentLoaded', () => {
    loadActivities();
    setupEventListeners();
});

function setupEventListeners() {
    searchInput.addEventListener('input', filterActivities);
    categoryFilter.addEventListener('change', filterActivities);
    document.getElementById('submitActivityBtn').addEventListener('click', handleAddActivity);
    document.getElementById('submitEditActivityBtn').addEventListener('click', handleEditActivity);
}

async function loadActivities() {
    try {
        const response = await fetch('/api/activities/organizer', {
            credentials: 'include'
        });
        
        if (response.status === 401) {
            window.location.href = '/auth/login';
            return;
        }
        
        const activities = await response.json();
        const activitiesTableBody = document.getElementById('activities-table-body');
        const noActivities = document.getElementById('no-activities');
        
        if (activities.length === 0) {
            activitiesTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No activities found</td></tr>';
            noActivities.classList.remove('d-none');
            return;
        }
        
        noActivities.classList.add('d-none');
        
        activitiesTableBody.innerHTML = activities.map(activity => `
            <tr>
                <td>${activity.title}</td>
                <td><span class="category-badge">${activity.categories.join(', ')}</span></td>
                <td>${formatDate(activity.date)}</td>
                <td>${activity.location}</td>
                <td>
                    <span class="status-badge status-${activity.status.toLowerCase()}">
                        ${activity.status}
                    </span>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <button class="btn btn-primary btn-sm" onclick="viewActivity('${activity._id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteActivity('${activity._id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading activities:', error);
    }
}

function filterActivities() {
    const searchTerm = searchInput.value.toLowerCase();
    const selectedCategory = categoryFilter.value.toLowerCase();

    const filtered = activities.filter(activity => {
        const matchesSearch = activity.title.toLowerCase().includes(searchTerm) ||
                activity.description.toLowerCase().includes(searchTerm);
        const matchesCategory = !selectedCategory || 
                activity.categories.some(cat => cat.toLowerCase() === selectedCategory);
        return matchesSearch && matchesCategory;
    });

    if (filtered.length === 0) {
        activitiesTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No activities found</td></tr>';
        noActivities.classList.remove('d-none');
        return;
    }
    
    noActivities.classList.add('d-none');
    
    activitiesTableBody.innerHTML = filtered.map(activity => `
        <tr>
            <td>${activity.title}</td>
            <td><span class="category-badge">${activity.categories.join(', ')}</span></td>
            <td>${formatDate(activity.date)}</td>
            <td>${activity.location}</td>
            <td>
                <span class="status-badge status-${activity.status.toLowerCase()}">
                    ${activity.status}
                </span>
            </td>
            <td>
                <div class="btn-group" role="group">
                    <button class="btn btn-primary btn-sm" onclick="viewActivity('${activity._id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteActivity('${activity._id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function handleAddActivity(e) {
    e.preventDefault();
    try {
        const form = document.getElementById('activityForm');
        const formData = new FormData(form);
        
        const categories = Array.from(form.querySelectorAll('input[name="category"]:checked'))
            .map(checkbox => checkbox.value);
        
        if (categories.length === 0) {
            showError('Please select at least one category', form);
            return;
        }
        
        const activityData = {
            title: formData.get('title'),
            description: formData.get('description'),
            categories: categories,
            date: formData.get('date'),
            start_time: formData.get('start_time'),
            duration: formData.get('duration'),
            location: formData.get('location'),
            price: parseInt(formData.get('price')),
            max_participants: parseInt(formData.get('max_participants')),
            current_participants: 0,
            status: formData.get('status'),
            instructor: formData.get('instructor'),
            liked_by: []
        };

        console.log(activityData);
        
        const response = await fetch('/api/organizer/activities', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(activityData),
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess('Activity created successfully!', form);
            form.reset();
            setTimeout(() => {
                bootstrap.Modal.getInstance(document.getElementById('activityModal')).hide();
                loadActivities();
            }, 1500);
        } else {
            showError(result.detail || 'Failed to create activity', form);
        }
    } catch (error) {
        console.error('Error creating activity:', error);
        showError('Error creating activity. Please try again.', form);
    }
}

async function handleEditActivity() {
    const form = document.getElementById('editActivityForm');
    const formData = new FormData(form);
    const activityId = formData.get('activity_id');
    
    if (!activityId) {
        showError('Activity ID is missing', form);
        return;
    }
    
    const categories = Array.from(form.querySelectorAll('input[name="category"]:checked'))
        .map(checkbox => checkbox.value);
    
    if (categories.length === 0) {
        showError('Please select at least one category', form);
        return;
    }
    
    try {
        const currentActivityResponse = await fetch(`/api/activities/${activityId}`, {
            credentials: 'include'
        });
        
        if (!currentActivityResponse.ok) {
            showError('Failed to get current activity data');
            return;
        }
        
        const currentActivity = await currentActivityResponse.json();
        
        const activityData = {
            title: formData.get('title'),
            description: formData.get('description'),
            categories: categories,
            date: formData.get('date'),
            start_time: formData.get('start_time'),
            duration: formData.get('duration'),
            location: formData.get('location'),
            price: parseInt(formData.get('price')),
            max_participants: parseInt(formData.get('max_participants')),
            current_participants: currentActivity.current_participants,
            status: formData.get('status'),
            instructor: formData.get('instructor'),
            organizer_id: currentActivity.organizer_id,
            liked_by: currentActivity.liked_by || []
        };
        
        const response = await fetch(`/api/organizer/activities/${activityId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(activityData),
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
            showError(result.detail || 'Failed to update activity', form);
        }
    } catch (error) {
        console.error('Error updating activity:', error);
        showError('Error updating activity. Please try again.', form);
    }
}

async function editActivity(id) {
    if (!id) {
        showError('Invalid activity ID');
        return;
    }
    
    try {
        const response = await fetch(`/api/activities/${id}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to load activity details');
        }
        
        const activity = await response.json();
        
        if (!activity || !activity._id) {
            showError('Invalid activity data received');
            return;
        }

        const form = document.getElementById('editActivityForm');
        form.activity_id.value = id;
        form.title.value = activity.title;
        form.description.value = activity.description;
        form.date.value = activity.date;
        form.start_time.value = activity.start_time;
        form.duration.value = activity.duration;
        form.location.value = activity.location;
        form.price.value = activity.price;
        form.max_participants.value = activity.max_participants;
        form.status.value = activity.status;
        form.instructor.value = activity.instructor;
        
        const categoriesContainer = document.getElementById('edit_categories');
        const allCategories = ['Art', 'Music', 'Dance', 'Sports', 'Technology', 'Science', 'Language', 'Social', 'Outdoors', 'Indoors'];
        let activityCategories;
        if (Array.isArray(activity.categories)) {
            activityCategories = activity.categories;
        } else {
            activityCategories = [activity.categories];
        }
        
        categoriesContainer.innerHTML = allCategories.map(category => {
            let checked = '';
            if (activityCategories.includes(category)) {
                checked = 'checked';
            }
            return `
                <div class="form-check mb-2">
                    <input class="form-check-input" type="checkbox" name="category" value="${category}" 
                        id="edit_category${category}" ${checked}>
                    <label class="form-check-label" for="edit_category${category}">${category}</label>
                </div>
            `;
        }).join('');
        
        const modal = new bootstrap.Modal(document.getElementById('editActivityModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading activity:', error);
        showError(error.message || 'Error loading activity. Please try again.');
    }
}

async function viewActivity(id) {
    if (!id) {
        showError('Invalid activity ID');
        return;
    }
    
    try {
        const response = await fetch(`/api/activities/${id}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to load activity details');
        }
        
        const activity = await response.json();
        
        if (!activity || !activity._id) {
            throw new Error('Invalid activity data received');
        }

        let status = 'danger';
        if (activity.status === 'available') {
            status = 'success';
        }
        const modalHtml = `
            <div class="modal fade" id="viewActivityModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${activity.title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p><strong>Description:</strong> ${activity.description}</p>
                            <p><strong>Categories:</strong> ${activity.categories.join(', ')}</p>
                            <p><strong>Date:</strong> ${formatDate(activity.date)}</p>
                            <p><strong>Time:</strong> ${activity.start_time}</p>
                            <p><strong>Duration:</strong> ${activity.duration}</p>
                            <p><strong>Location:</strong> ${activity.location}</p>
                            <p><strong>Price:</strong> $${activity.price}</p>
                            <p><strong>Max Participants:</strong> ${activity.max_participants}</p>
                            <p><strong>Status:</strong> <span class="badge bg-${status}">${activity.status}</span></p>
                            <p><strong>Instructor:</strong> ${activity.instructor}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-warning" onclick="editActivity('${activity._id}')" data-bs-dismiss="modal">
                                <i class="fas fa-edit me-2"></i>Edit Activity
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        const existingModal = document.getElementById('viewActivityModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        const modal = new bootstrap.Modal(document.getElementById('viewActivityModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading activity:', error);
        showError(error.message || 'Error loading activity. Please try again.');
    }
}

async function deleteActivity(id) {    
    try {
        const response = await fetch(`/api/activities/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            await loadActivities();
        }
    } catch (error) {
        console.error('Error deleting activity:', error);
    }
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

