console.log('Viewer_reservations.js loaded');

document.addEventListener('DOMContentLoaded', async function() {
    loadReservations();
});

async function loadReservations() {
    try {
        const response = await fetch('/api/my-reservations');
        if (!response.ok) {
            throw new Error('Failed to load reservations');
        }
        const data = await response.json();
        displayReservations(data.reservations);
    } catch (error) {
        console.error('Error loading reservations:', error);
        showError('Failed to load reservations. Please try again later.', document.getElementById('reservations-container'));
    }
}

function displayReservations(reservations) {
    const container = document.getElementById('reservations-container');
    container.innerHTML = '';
    
    if (reservations.length === 0) {
        container.innerHTML = '<div class="col-12"><p class="text-center">You have no reservations yet.</p></div>';
        return;
    }
    
    reservations.forEach(reservation => {
        const card = document.createElement('div');
        card.className = 'col-md-6 col-lg-4 mb-4';
        card.innerHTML = `
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">${reservation.activity.title}</h5>
                    <p class="card-text">${reservation.activity.description}</p>
                    <div class="mb-3">
                        <strong>Date:</strong> <span>${reservation.activity.date}</span>
                    </div>
                    <div class="mb-3">
                        <strong>Time:</strong> <span>${reservation.activity.start_time}</span>
                    </div>
                    <div class="mb-3">
                        <strong>Location:</strong> <span>${reservation.activity.location}</span>
                    </div>
                    <div class="mb-3">
                        <strong>Status:</strong> 
                        <span class="badge ${getStatusClass(reservation.status)}">${reservation.status}</span>
                    </div>
                    <hr>
                    <h6 class="mb-3">Organizer contact information:</h6>
                    <div class="mb-2">
                        <strong>Name:</strong> <span>${reservation.organizer.name} ${reservation.organizer.surname}</span>
                    </div>
                    <div class="mb-2">
                        <strong>Email:</strong> <span>${reservation.organizer.email}</span>
                    </div>
                    <div class="mb-2">
                        <strong>Phone:</strong> <span>${reservation.organizer.telephone_number}</span>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

function getStatusClass(status) {
    switch(status) {
        case 'Pending': return 'bg-warning';
        case 'Completed': return 'bg-info';
        case 'Cancelled': return 'bg-danger';
        default: return 'bg-secondary';
    }
}