/**
 * Amravati City Bus Management System
 * Ticket Viewer & Printable Boarding Pass Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
    const user = requireAuth();
    if (!user) return;

    const urlParams = new URLSearchParams(window.location.search);
    const ticketId = urlParams.get('ticket_id');
    const bookingId = urlParams.get('booking_id');

    if (ticketId) {
        await loadTicketById(ticketId);
    } else if (bookingId) {
        await loadTicketByBookingId(bookingId);
    } else {
        await loadMostRecentTicket();
    }

    document.getElementById('btnPrintTicket')?.addEventListener('click', () => {
        window.print();
    });
});

async function loadTicketById(ticketId) {
    try {
        const res = await apiRequest(`/tickets/${ticketId}`);
        renderTicketUI(res.data);
    } catch (e) {
        showToast(`Failed to load ticket: ${e.message}`, 'danger');
        displayTicketError(e.message);
    }
}

async function loadTicketByBookingId(bookingId) {
    try {
        const res = await apiRequest(`/tickets/booking/${bookingId}`);
        renderTicketUI(res.data);
    } catch (e) {
        showToast(`Failed to load ticket: ${e.message}`, 'danger');
        displayTicketError(e.message);
    }
}

async function loadMostRecentTicket() {
    try {
        const res = await apiRequest('/bookings');
        const bookings = res.data || [];
        const confirmed = bookings.find(b => b.booking_status === 'confirmed' && b.ticket_id);
        if (confirmed) {
            await loadTicketById(confirmed.ticket_id);
        } else {
            displayTicketError("No active tickets found. Please search routes and book a bus seat first.");
        }
    } catch (e) {
        displayTicketError(e.message);
    }
}

function renderTicketUI(t) {
    document.getElementById('ticketPlaceholder')?.classList.add('d-none');
    document.getElementById('ticketContainer')?.classList.remove('d-none');

    document.getElementById('tktNumber').textContent = t.ticket_number;
    document.getElementById('tktBookingRef').textContent = t.booking_reference;
    document.getElementById('tktRoute').textContent = `${t.route_number}: ${t.route_name}`;
    document.getElementById('tktBoarding').textContent = t.boarding_stop;
    document.getElementById('tktDropoff').textContent = t.dropoff_stop;
    document.getElementById('tktJourneyDate').textContent = formatDate(t.journey_date);
    document.getElementById('tktDepartureTime').textContent = formatTime(t.departure_time);
    document.getElementById('tktBus').textContent = `${t.bus_number} (${t.bus_type})`;
    document.getElementById('tktTotalPaid').textContent = formatCurrency(t.total_amount);
    document.getElementById('tktPaymentRef').textContent = t.payment_reference || 'DEMO-TXN-SUCCESS';
    document.getElementById('tktIssuedAt').textContent = t.issued_at ? new Date(t.issued_at).toLocaleString() : new Date().toLocaleString();

    const statusBadge = document.getElementById('tktStatusBadge');
    if (statusBadge) {
        statusBadge.textContent = t.ticket_status ? t.ticket_status.toUpperCase() : 'VALID';
        statusBadge.className = `badge ${t.ticket_status === 'valid' ? 'bg-success' : 'bg-danger'}`;
    }

    // Render Passengers and Seat Table
    const seatsBody = document.getElementById('tktSeatsList');
    if (seatsBody && t.seats) {
        seatsBody.innerHTML = t.seats.map((s, idx) => `
            <tr>
                <td>${idx + 1}</td>
                <td><strong>${s.passenger_name}</strong></td>
                <td>${s.passenger_age} / ${s.passenger_gender}</td>
                <td><span class="badge bg-teal fs-6">Seat #${s.seat_number}</span></td>
                <td class="text-end">${formatCurrency(s.fare)}</td>
            </tr>
        `).join('');
    }

    // Render Visual QR Code representation
    const qrContainer = document.getElementById('tktQrContainer');
    if (qrContainer) {
        const qrData = encodeURIComponent(t.qr_code_data || t.ticket_number);
        qrContainer.innerHTML = `
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=130x130&data=${qrData}" 
                 alt="Ticket QR Code" 
                 class="ticket-qr-print img-fluid border p-1 rounded" 
                 onerror="this.onerror=null; this.src=''; this.parentElement.innerHTML='<div class=\\'p-3 border bg-light text-center small\\'><i class=\\'fas fa-qrcode fa-3x text-muted\\'></i><br><code>${t.ticket_number}</code></div>';" />
        `;
    }
}

function displayTicketError(msg) {
    const placeholder = document.getElementById('ticketPlaceholder');
    if (placeholder) {
        placeholder.innerHTML = `
            <div class="card p-5 text-center shadow-sm">
                <i class="fas fa-ticket-alt fa-3x text-muted mb-3"></i>
                <h5>Ticket Not Found</h5>
                <p class="text-muted">${msg}</p>
                <div>
                    <a href="passenger_dashboard.html" class="btn btn-teal">
                        <i class="fas fa-search me-1"></i> Search Schedules & Book
                    </a>
                </div>
            </div>
        `;
    }
}
