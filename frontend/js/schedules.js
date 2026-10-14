/**
 * Amravati City Bus Management System
 * Schedules & Crew Assignments Controller
 */

let allSchedules = [];
let availableRoutes = [];
let availableBuses = [];
let availableDrivers = [];
let availableConductors = [];

document.addEventListener('DOMContentLoaded', async () => {
    const user = requireAuth('admin');
    if (!user) return;

    await Promise.all([
        loadSchedules(),
        loadRoutesList(),
        loadBusesList(),
        loadDriversList(),
        loadConductorsList()
    ]);

    document.getElementById('scheduleForm')?.addEventListener('submit', handleSaveSchedule);
    document.getElementById('assignStaffForm')?.addEventListener('submit', handleSaveStaffAssignment);
});

async function loadSchedules() {
    try {
        const res = await apiRequest('/schedules');
        allSchedules = res.data || [];
        renderSchedulesTable(allSchedules);
    } catch (e) {
        showToast(`Failed to load schedules: ${e.message}`, 'danger');
    }
}

async function loadRoutesList() {
    try {
        const res = await apiRequest('/routes');
        availableRoutes = res.data || [];
        const sel = document.getElementById('schedRouteId');
        if (sel) {
            sel.innerHTML = `<option value="">Select Route</option>` + 
                availableRoutes.map(r => `<option value="${r.route_id}">${r.route_number} - ${r.route_name}</option>`).join('');
        }
    } catch (e) {}
}

async function loadBusesList() {
    try {
        const res = await apiRequest('/buses?status=active');
        availableBuses = res.data || [];
        const sel = document.getElementById('schedBusId');
        if (sel) {
            sel.innerHTML = `<option value="">Select Bus</option>` + 
                availableBuses.map(b => `<option value="${b.bus_id}">${b.bus_number} (${b.bus_type}, Cap: ${b.capacity})</option>`).join('');
        }
    } catch (e) {}
}

async function loadDriversList() {
    try {
        const res = await apiRequest('/staff/drivers?status=active');
        availableDrivers = res.data || [];
        const sel = document.getElementById('assignDriverId');
        if (sel) {
            sel.innerHTML = `<option value="">Select Driver</option>` + 
                availableDrivers.map(d => `<option value="${d.driver_id}">${d.full_name} (${d.phone})</option>`).join('');
        }
    } catch (e) {}
}

async function loadConductorsList() {
    try {
        const res = await apiRequest('/staff/conductors?status=active');
        availableConductors = res.data || [];
        const sel = document.getElementById('assignConductorId');
        if (sel) {
            sel.innerHTML = `<option value="">Select Conductor</option>` + 
                availableConductors.map(c => `<option value="${c.conductor_id}">${c.full_name} (Badge: ${c.badge_number})</option>`).join('');
        }
    } catch (e) {}
}

function renderSchedulesTable(schedules) {
    const tbody = document.getElementById('schedulesTableBody');
    if (!tbody) return;

    if (schedules.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No schedules found.</td></tr>`;
        return;
    }

    tbody.innerHTML = schedules.map(s => {
        const statusBadge = s.status === 'scheduled' 
            ? '<span class="badge badge-active">Scheduled</span>' 
            : s.status === 'cancelled' 
            ? '<span class="badge badge-cancelled">Cancelled</span>' 
            : `<span class="badge bg-secondary">${s.status}</span>`;

        return `
            <tr>
                <td><strong>#${s.schedule_id}</strong></td>
                <td>
                    <span class="badge bg-primary">${s.route_number}</span><br>
                    <small class="text-muted">${s.route_name}</small>
                </td>
                <td>
                    <strong>${s.bus_number}</strong><br>
                    <small class="text-muted">${s.bus_type} (${s.capacity} seats)</small>
                </td>
                <td>
                    <strong>${formatDate(s.journey_date)}</strong><br>
                    <small>${formatTime(s.departure_time)} - ${formatTime(s.arrival_time)}</small>
                </td>
                <td><strong>${formatCurrency(s.fare)}</strong></td>
                <td>
                    <small class="d-block"><i class="fas fa-id-card-alt me-1 text-primary"></i> ${s.driver_name || '<em class="text-warning">Unassigned</em>'}</small>
                    <small class="d-block"><i class="fas fa-ticket-alt me-1 text-teal"></i> ${s.conductor_name || '<em class="text-warning">Unassigned</em>'}</small>
                </td>
                <td>${statusBadge}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="openAssignStaffModal(${s.schedule_id})" title="Assign Staff">
                        <i class="fas fa-user-tag"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteSchedule(${s.schedule_id})" title="Cancel/Delete Schedule">
                        <i class="fas fa-times-circle"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function openAddScheduleModal() {
    document.getElementById('scheduleForm').reset();
    document.getElementById('schedDate').value = new Date().toISOString().split('T')[0];
    new bootstrap.Modal(document.getElementById('scheduleModal')).show();
}

function openAssignStaffModal(scheduleId) {
    document.getElementById('assignScheduleId').value = scheduleId;
    document.getElementById('assignStaffForm').reset();
    new bootstrap.Modal(document.getElementById('assignStaffModal')).show();
}

async function handleSaveSchedule(e) {
    e.preventDefault();
    const payload = {
        route_id: parseInt(document.getElementById('schedRouteId').value, 10),
        bus_id: parseInt(document.getElementById('schedBusId').value, 10),
        journey_date: document.getElementById('schedDate').value,
        departure_time: document.getElementById('schedDeparture').value,
        arrival_time: document.getElementById('schedArrival').value,
        fare: parseFloat(document.getElementById('schedFare').value),
        frequency: document.getElementById('schedFrequency').value,
        status: 'scheduled'
    };

    try {
        const res = await apiRequest('/schedules', 'POST', payload);
        if (res.success) {
            showToast('Schedule created successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('scheduleModal'))?.hide();
            await loadSchedules();
        }
    } catch (e) {
        showToast(e.message, 'danger');
    }
}

async function handleSaveStaffAssignment(e) {
    e.preventDefault();
    const payload = {
        schedule_id: parseInt(document.getElementById('assignScheduleId').value, 10),
        driver_id: parseInt(document.getElementById('assignDriverId').value, 10),
        conductor_id: parseInt(document.getElementById('assignConductorId').value, 10)
    };

    try {
        const res = await apiRequest('/staff/assignments', 'POST', payload);
        if (res.success) {
            showToast('Driver and Conductor successfully assigned!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('assignStaffModal'))?.hide();
            await loadSchedules();
        }
    } catch (e) {
        showToast(e.message, 'danger');
    }
}

async function deleteSchedule(scheduleId) {
    if (!confirm(`Cancel/Delete schedule #${scheduleId}?`)) return;
    try {
        const res = await apiRequest(`/schedules/${scheduleId}`, 'DELETE');
        if (res.success) {
            showToast(res.message, 'success');
            await loadSchedules();
        }
    } catch (e) {
        showToast(e.message, 'danger');
    }
}
