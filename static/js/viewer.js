console.log('Viewer.js loaded');

function createLikeButton(activity, likeButtonClass = 'btn-outline-secondary', heartIconClass = 'fas fa-heart') {
    const likeCount = activity.liked_by ? activity.liked_by.length : 0;
    return `
        <button class="btn ${likeButtonClass} btn-like" data-activity-id="${activity._id}">
            <i class="${heartIconClass}"></i>
            <span class="like-count">${likeCount}</span>
        </button>
    `;
}

async function handleLikeClick(activityId) {
    try {
        const response = await fetch(`/api/activities/${activityId}/like`, {
            method: 'POST',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to like activity');
        }

        await loadActivities();
        
    } catch (error) {
        console.error('Error liking activity:', error);
    }
}

async function loadActivities() {
    const response = await fetch('/api/activities', {
        credentials: 'include'
    });

    const data = await response.json();
    const activities = data.activities;
    const userRole = data.user_role;
    console.log('Activities loaded:', activities);
    
    const activitiesGrid = document.getElementById('activities-grid');
    const noActivities = document.getElementById('no-activities');
    
    if (activities.length === 0) {
        activitiesGrid.innerHTML = '';
        noActivities.classList.remove('d-none');
        return;
    }
    
    noActivities.classList.add('d-none');
    activitiesGrid.innerHTML = activities.map(activity => `
        <div class="col-md-6 col-lg-4">
            <div class="card activity-card h-100">
                <div class="card-body d-flex flex-column">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <h5 class="card-title mb-0">${activity.title}</h5>
                        <div class="d-flex align-items-center gap-2">
                            <small class="text-muted">
                                <i class="fas fa-users"></i> ${activity.current_participants || 0}/${activity.max_participants}
                            </small>
                            <span class="badge ${activity.status === 'available' ? 'bg-success' : 'bg-danger'}">
                                ${activity.status === 'available' ? 'Available' : 'Full'}
                            </span>
                        </div>
                    </div>
                    <p class="card-text flex-grow-1" style="overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">
                        ${activity.description}
                    </p>
                    <div class="mb-3">
                        <span class="category-badge">${activity.categories?.join(', ') || 'General'}</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center gap-3 mt-auto">
                        <button class="btn btn-primary btn-view-details" data-activity-id="${activity._id}">View Details</button>
                        ${userRole === 'viewer' ? createLikeButton(activity) : ''}
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    document.querySelectorAll('.btn-view-details').forEach(button => {
        button.addEventListener('click', () => {
            const activityId = button.getAttribute('data-activity-id');
            showActivityDetails(activityId);
        });
    });

    if (userRole === 'viewer') {
        document.querySelectorAll('.btn-like').forEach(button => {
            button.addEventListener('click', () => {
                const activityId = button.getAttribute('data-activity-id');
                handleLikeClick(activityId);
            });
        });
    }
    
}

function createActivityDetailsHtml(activity, organizer) {
    const activityDetailsTemplate = `
        <div class="activity-header mb-4">
            <h4 class="mb-3">${activity.title}</h4>
            <div class="detail-item">
                <div class="detail-label">Description</div>
                <div class="detail-value text-wrap" style="white-space: pre-wrap; word-break: break-word;">
                    ${activity.description}
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="detail-item">
                    <div class="detail-label">Categories</div>
                    <div class="detail-value">
                        ${activity.categories?.join(', ') || 'General'}
                    </div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Date</div>
                    <div class="detail-value">${activity.date}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Start Time</div>
                    <div class="detail-value">${activity.start_time || 'Not specified'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Duration</div>
                    <div class="detail-value">${activity.duration || 'N/A'}</div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="detail-item">
                    <div class="detail-label">Instructor</div>
                    <div class="detail-value">${activity.instructor || 'TBD'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Location</div>
                    <div class="detail-value">${activity.location}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Price per person</div>
                    <div class="detail-value">$${activity.price || '0'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Status</div>
                    <div class="detail-value">
                        <span class="badge ${activity.status === 'available' ? 'bg-success' : 'bg-danger'}">
                            ${activity.status === 'available' ? 'Available' : 'Full'}
                        </span>
                    </div>
                </div>
            </div>
        </div>
        <div class="organizer-info mt-4">
            <h5 class="mb-3">Organizer Information</h5>
            <div class="detail-item">
                <div class="detail-label">Name</div>
                <div class="detail-value">${organizer.name} ${organizer.surname}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Email</div>
                <div class="detail-value">${organizer.email}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Phone</div>
                <div class="detail-value">${organizer.telephone_number}</div>
            </div>
        </div>
    `;
    return activityDetailsTemplate;
}

async function showActivityDetails(activityId) {
    try {
        const response = await fetch(`/api/activities/${activityId}`, {
            credentials: 'include'
        });

        const activity = await response.json();
        let organizer = { name: 'none', surname: 'none', email: 'none', telephone_number: 'none' };
        console.log(activity);
        if (activity.organizer_id) {
            try {
                const response = await fetch(`/api/organizers/${activity.organizer_id}`, { credentials: 'include' });
                if (response.ok) {
                    organizer = await response.json();
                }
            } catch (e) {
                console.error('Error loading organizer information:', e);
            }
        }
        const modalBody = document.querySelector('.activity-details');
        modalBody.innerHTML = createActivityDetailsHtml(activity, organizer);
        
        const reserveButton = document.getElementById('reserveButton');
        const userRole = document.body.getAttribute('data-user-role') || 'viewer';
        const currentUserId = document.body.getAttribute('data-user-id');
        
        console.log('Current User ID:', currentUserId);
        console.log('Activity Organizer ID:', activity.organizer_id);
        
        if (activity.organizer_id === currentUserId) {
            console.log('Hiding button - user is organizer of this activity');
            reserveButton.style.display = 'none';
        } else if (activity.has_reserved) {
            console.log('Showing reserved button');
            reserveButton.style.display = 'block';
            reserveButton.disabled = true;
            reserveButton.innerHTML = '<i class="fas fa-check"></i> Reserved';
            reserveButton.classList.remove('btn-success');
            reserveButton.classList.add('btn-secondary');
        } else if (activity.status === 'available') {
            console.log('Showing available button');
            reserveButton.style.display = 'block';
            reserveButton.disabled = false;
            reserveButton.innerHTML = '<i class="fas fa-calendar-check"></i> Reserve';
            reserveButton.classList.remove('btn-secondary');
            reserveButton.classList.add('btn-success');
            reserveButton.onclick = () => reserveActivity(activityId);
        } else {
            console.log('Hiding button - activity not available');
            reserveButton.style.display = 'none';
        }
        
        const modal = new bootstrap.Modal(document.getElementById('activityModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading activity details:', error);
    }
}

document.getElementById('search-input').addEventListener('input', filterActivities);
document.getElementById('category-filter').addEventListener('change', filterActivities);

function filterActivities() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const category = document.getElementById('category-filter').value;
    
    const cards = document.querySelectorAll('#activities-grid .card');
    cards.forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        const description = card.querySelector('.card-text').textContent.toLowerCase();
        const activityCategory = card.querySelector('.badge').textContent.toLowerCase();
        
        const matchesSearch = title.includes(searchTerm) || description.includes(searchTerm);
        const matchesCategory = !category || activityCategory === category.toLowerCase();
        
        card.closest('.col-md-6').style.display = matchesSearch && matchesCategory ? 'block' : 'none';
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    loadActivities();
});

function displayActivityDetails(activity) {
    const detailsContainer = document.querySelector('.activity-details');
    const reserveButton = document.getElementById('reserveButton');
    
    detailsContainer.innerHTML = `
        <div class="row">
            <div class="col-md-8">
                <h4>${activity.title}</h4>
                <p class="text-muted">${activity.description}</p>
                <div class="mb-3">
                    <strong>Date:</strong> ${activity.date}
                </div>
                <div class="mb-3">
                    <strong>Time:</strong> ${activity.start_time}
                </div>
                <div class="mb-3">
                    <strong>Location:</strong> ${activity.location}
                </div>
                <div class="mb-3">
                    <strong>Categories:</strong>
                    <div class="mt-1">
                        ${activity.categories.map(category => 
                            `<span class="badge bg-primary me-1">${category}</span>`
                        ).join('')}
                    </div>
                </div>
                <div class="mb-3">
                    <strong>Participants:</strong> ${activity.current_participants}/${activity.max_participants}
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Organizer Information</h5>
                        <p class="card-text">
                            <strong>Name:</strong> <span class="organizer-name"></span><br>
                            <strong>Email:</strong> <span class="organizer-email"></span><br>
                            <strong>Phone:</strong> <span class="organizer-phone"></span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    loadOrganizerInfo(activity.organizer_id);
    
    if (activity.status === 'available' && activity.current_participants < activity.max_participants) {
        reserveButton.style.display = 'block';
        reserveButton.dataset.activityId = activity._id;
        reserveButton.onclick = () => reserveActivity(activity._id);
    } else {
        reserveButton.style.display = 'none';
    }
}

async function loadOrganizerInfo(organizerId) {
    try {
        const response = await fetch(`/api/organizers/${organizerId}`);
        if (!response.ok) {
            throw new Error('Failed to load organizer information');
        }
        const organizer = await response.json();
        
        document.querySelector('.organizer-name').textContent = `${organizer.name} ${organizer.surname}`;
        document.querySelector('.organizer-email').textContent = organizer.email;
        document.querySelector('.organizer-phone').textContent = organizer.telephone_number;
    } catch (error) {
        console.error('Error loading organizer information:', error);
    }
}

async function reserveActivity(activityId) {
    try {
        const response = await fetch(`/reserve/${activityId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to reserve activity');
        }

        showSuccess('Activity reserved successfully!', document.querySelector('.activity-details'));

        setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('activityModal'));
            if (modal) {
                modal.hide();
            }
            loadActivities();
        }, 1500); 

    } catch (error) {
        console.error('Error reserving activity:', error);
        showError('Failed to reserve activity.', document.querySelector('.activity-details'));
    }
} 