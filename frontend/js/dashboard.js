/**
 * Amravati City Bus Management System
 * Admin Dashboard Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
    const user = requireAuth('admin');
    if (!user) return;

    await loadDashboardData();

    const refreshBtn = document.getElementById('btnRefreshDashboard');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Refreshing...';
            await loadDashboardData();
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-1"></i> Refresh';
            showToast('Dashboard metrics refreshed from MySQL database.', 'success');
        });
    }
});

async function loadDashboardData() {
    try {
        const response = await apiRequest('/admin/dashboard');
        if (!response.success) {
            showToast(response.message, 'danger');
            return;
        }

        const data = response.data;

        // Populate KPI Counters
        document.getElementById('statTotalBuses').textContent = data.total_buses || 0;
        document.getElementById('statActiveBuses').textContent = data.active_buses || 0;
        document.getElementById('statTotalRoutes').textContent = data.total_routes || 0;
        document.getElementById('statTotalStops').textContent = data.total_stops || 0;
        document.getElementById('statTotalSchedules').textContent = data.today_schedules || 0;
        document.getElementById('statActiveDrivers').textContent = data.active_drivers || 0;
        document.getElementById('statTotalBookings').textContent = data.total_bookings || 0;
        document.getElementById('statRevenue').textContent = formatCurrency(data.total_revenue || 0);

        // Populate Recent Bookings Table
        renderRecentBookings(data.recent_bookings || []);

        // Populate Recent Audit Logs Table
        renderRecentAudit(data.recent_audit || []);

    } catch (error) {
        showToast(`Failed to load dashboard: ${error.message}`, 'danger');
    }
}

function renderRecentBookings(bookings) {
    const tbody = document.getElementById('recentBookingsTableBody');
    if (!tbody) return;

    if (bookings.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No recent bookings recorded.</td></tr>`;
        return;
    }

    tbody.innerHTML = bookings.map(b => {
        const statusBadge = b.booking_status === 'confirmed' 
            ? '<span class="badge badge-confirmed">Confirmed</span>'
            : '<span class="badge badge-cancelled">Cancelled</span>';

        return `
            <tr>
                <td><strong>${b.booking_reference}</strong></td>
                <td>${b.passenger_name}</td>
                <td><span class="badge bg-secondary">${b.route_number}</span></td>
                <td>${formatDate(b.journey_date)}</td>
                <td>${formatCurrency(b.total_amount)}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
    }).join('');
}

function renderRecentAudit(logs) {
    const tbody = document.getElementById('recentAuditTableBody');
    if (!tbody) return;

    if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-muted">No audit trail logs recorded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = logs.map(l => `
        <tr>
            <td><span class="badge bg-light text-dark border">${l.action}</span></td>
            <td><small class="text-muted">${l.table_name}</small></td>
            <td><small>${l.details || '-'}</small></td>
            <td><small class="text-muted">${l.created_at ? new Date(l.created_at).toLocaleTimeString() : '-'}</small></td>
        </tr>
    `).join('');
}
