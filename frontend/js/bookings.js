/**
 * Amravati City Bus Management System
 * Bookings Management & History Controller
 */

let allBookings = [];
let currentUser = null;

document.addEventListener('DOMContentLoaded', async () => {
    currentUser = requireAuth();
    if (!currentUser) return;

    await loadBookings();

    document.getElementById('bookingSearchInput')?.addEventListener('input', applySearch);
    document.getElementById('bookingStatusFilter')?.addEventListener('change', applySearch);
    document.getElementById('cancelBookingForm')?.addEventListener('submit', handleConfirmCancellation);
});

async function loadBookings() {
    try {
        const res = await apiRequest('/bookings');
        allBookings = res.data || [];
        renderBookingsTable(allBookings);
    } catch (e) {
        showToast(`Failed to load bookings: ${e.message}`, 'danger');
    }
}

function applySearch() {
    const q = document.getElementById('bookingSearchInput')?.value.toLowerCase() || '';
    const status = document.getElementById('bookingStatusFilter')?.value || '';

    const filtered = allBookings.filter(b => {
        const matchesQ = b.booking_reference.toLowerCase().includes(q) || 
                         (b.passenger_name && b.passenger_name.toLowerCase().includes(q)) ||
                         b.route_number.toLowerCase().includes(q);
        const matchesStatus = !status || b.booking_status === status;
        return matchesQ && matchesStatus;
    });

    renderBookingsTable(filtered);
}

function renderBookingsTable(bookings) {
    const tbody = document.getElementById('bookingsTableBody');
    if (!tbody) return;

    if (bookings.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No booking records found.</td></tr>`;
        return;
    }

    tbody.innerHTML = bookings.map(b => {
        const statusBadge = b.booking_status === 'confirmed' 
            ? '<span class="badge badge-confirmed">Confirmed</span>' 
            : '<span class="badge badge-cancelled">Cancelled</span>';

        const isEligibleForCancel = b.booking_status === 'confirmed';

        return `
            <tr>
                <td><strong>${b.booking_reference}</strong></td>
                <td>
                    <strong>${b.passenger_name}</strong><br>
                    <small class="text-muted">${b.passenger_phone || ''}</small>
                </td>
                <td>
                    <span class="badge bg-primary">${b.route_number}</span><br>
                    <small>${b.boarding_stop} &rarr; ${b.dropoff_stop}</small>
                </td>
                <td>
                    <strong>${formatDate(b.journey_date)}</strong><br>
                    <small>${formatTime(b.departure_time)}</small>
                </td>
                <td>${b.total_passengers} seat(s)</td>
                <td><strong>${formatCurrency(b.total_amount)}</strong></td>
                <td>${statusBadge}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-info me-1" onclick="viewBookingDetails(${b.booking_id})" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    ${b.ticket_id ? `
                        <a href="tickets.html?ticket_id=${b.ticket_id}" class="btn btn-sm btn-outline-success me-1" title="View Boarding Pass">
                            <i class="fas fa-ticket-alt"></i>
                        </a>
                    ` : ''}
                    ${isEligibleForCancel ? `
                        <button class="btn btn-sm btn-outline-danger" onclick="openCancelModal(${b.booking_id}, '${b.booking_reference}')" title="Cancel Booking">
                            <i class="fas fa-ban"></i>
                        </button>
                    ` : ''}
                </td>
            </tr>
        `;
    }).join('');
}

async function viewBookingDetails(bookingId) {
    try {
        const res = await apiRequest(`/bookings/${bookingId}`);
        const b = res.data;

        document.getElementById('detailBookingRef').textContent = b.booking_reference;
        document.getElementById('detailPassenger').textContent = `${b.passenger_name} (${b.passenger_phone || b.passenger_email})`;
        document.getElementById('detailRoute').textContent = `${b.route_number}: ${b.route_name}`;
        document.getElementById('detailStops').textContent = `${b.boarding_stop} to ${b.dropoff_stop}`;
        document.getElementById('detailJourney').textContent = `${formatDate(b.journey_date)} at ${formatTime(b.departure_time)}`;
        document.getElementById('detailBus').textContent = `${b.bus_number} (${b.bus_type})`;
        document.getElementById('detailTotal').textContent = formatCurrency(b.total_amount);
        document.getElementById('detailStatus').textContent = b.booking_status.toUpperCase();

        const seatsContainer = document.getElementById('detailSeatsList');
        if (seatsContainer && b.seats) {
            seatsContainer.innerHTML = b.seats.map(s => `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-teal me-2">Seat #${s.seat_number}</span>
                        <strong>${s.passenger_name}</strong> (${s.passenger_gender}, Age: ${s.passenger_age})
                    </div>
                    <div>
                        <span class="badge ${s.status === 'booked' ? 'bg-success' : 'bg-danger'}">${s.status}</span>
                        <strong class="ms-2">${formatCurrency(s.fare)}</strong>
                    </div>
                </li>
            `).join('');
        }

        const ticketBtn = document.getElementById('btnGoToTicket');
        if (ticketBtn) {
            if (b.ticket_id) {
                ticketBtn.href = `tickets.html?ticket_id=${b.ticket_id}`;
                ticketBtn.classList.remove('d-none');
            } else {
                ticketBtn.classList.add('d-none');
            }
        }

        new bootstrap.Modal(document.getElementById('bookingDetailsModal')).show();
    } catch (e) {
        showToast(`Failed to load booking details: ${e.message}`, 'danger');
    }
}

function openCancelModal(bookingId, bookingRef) {
    document.getElementById('cancelBookingId').value = bookingId;
    document.getElementById('cancelBookingRef').textContent = bookingRef;
    document.getElementById('cancelReason').value = '';
    new bootstrap.Modal(document.getElementById('cancelBookingModal')).show();
}

async function handleConfirmCancellation(e) {
    e.preventDefault();
    const bookingId = document.getElementById('cancelBookingId').value;
    const reason = document.getElementById('cancelReason').value.trim() || 'Passenger Cancellation';

    try {
        const res = await apiRequest(`/bookings/${bookingId}/cancel`, 'POST', { reason });
        if (res.success) {
            showToast('Booking cancelled successfully and seats released.', 'success');
            bootstrap.Modal.getInstance(document.getElementById('cancelBookingModal'))?.hide();
            await loadBookings();
        }
    } catch (e) {
        showToast(e.message, 'danger');
    }
}
