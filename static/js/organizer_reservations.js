console.log('Organizer_reservations.js loaded');

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Invalid Date';
    
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'Pending':
            return 'bg-warning';
        case 'Completed':
            return 'bg-info';
        case 'Cancelled':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

async function loadReservations() {
    try {
        const response = await fetch('/api/organizer/reservations', {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });

        const responseText = await response.text();

        if (!response.ok) {
            throw new Error(`Failed to load reservations: ${response.status} ${responseText}`);
        }

        let data = JSON.parse(responseText);

        const tbody = document.querySelector('#reservationsTable tbody');
        tbody.innerHTML = '';

        if (!data.reservations || data.reservations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No reservations found</td></tr>';
            return;
        }

        data.reservations.forEach(reservation => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${reservation.activity.title}</td>
                <td>${reservation.user.name} ${reservation.user.surname}</td>
                <td>${reservation.user.email}</td>
                <td>${reservation.user.telephone_number}</td>
                <td>
                    <span class="badge ${getStatusBadgeClass(reservation.status)}">
                        ${reservation.status}
                    </span>
                </td>
                <td>${formatDate(reservation.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="updateStatus('${reservation._id}', '${reservation.status}')">
                        <i class="fas fa-edit"></i> Update Status
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading reservations:', error);
    }
}

async function updateStatus(reservationId, currentStatus) {
    document.getElementById('reservationId').value = reservationId;
    document.getElementById('statusSelect').value = currentStatus;
    
    const modal = new bootstrap.Modal(document.getElementById('updateStatusModal'));
    modal.show();
}

async function saveStatusUpdate() {
    const reservationId = document.getElementById('reservationId').value;
    const newStatus = document.getElementById('statusSelect').value;

    try {
        const response = await fetch(`/api/reservations/${reservationId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus }),
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to update status');
        }

        const modal = bootstrap.Modal.getInstance(document.getElementById('updateStatusModal'));
        modal.hide();
        loadReservations();
    } catch (error) {
        console.error('Failed to update status. Please try again.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadReservations();
    
    document.getElementById('saveStatusBtn').addEventListener('click', saveStatusUpdate);
}); 