/**
 * Amravati City Bus Management System
 * Route Management Controller
 */

let allRoutes = [];
let availableStops = [];

document.addEventListener('DOMContentLoaded', async () => {
    const user = requireAuth('admin');
    if (!user) return;

    await Promise.all([loadRoutes(), loadStopsDropdown()]);

    document.getElementById('searchInput')?.addEventListener('input', applySearch);
    document.getElementById('routeForm')?.addEventListener('submit', handleSaveRoute);
});

async function loadRoutes() {
    try {
        const response = await apiRequest('/routes');
        allRoutes = response.data || [];
        renderRoutesTable(allRoutes);
    } catch (error) {
        showToast(`Failed to load routes: ${error.message}`, 'danger');
    }
}

async function loadStopsDropdown() {
    try {
        const response = await apiRequest('/stops');
        availableStops = response.data || [];
        
        const startSelect = document.getElementById('startStopId');
        const endSelect = document.getElementById('endStopId');
        if (startSelect && endSelect) {
            const options = availableStops.map(s => `<option value="${s.stop_id}">${s.stop_name}</option>`).join('');
            startSelect.innerHTML = `<option value="">Select Origin Stop</option>` + options;
            endSelect.innerHTML = `<option value="">Select Destination Stop</option>` + options;
        }
    } catch (e) {
        console.error('Error loading stops for dropdown:', e);
    }
}

function applySearch() {
    const q = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const filtered = allRoutes.filter(r => 
        r.route_number.toLowerCase().includes(q) || 
        r.route_name.toLowerCase().includes(q)
    );
    renderRoutesTable(filtered);
}

function renderRoutesTable(routes) {
    const tbody = document.getElementById('routesTableBody');
    if (!tbody) return;

    if (routes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No routes found.</td></tr>`;
        return;
    }

    tbody.innerHTML = routes.map(r => `
        <tr>
            <td><strong>#${r.route_id}</strong></td>
            <td><span class="badge bg-primary fs-6">${r.route_number}</span></td>
            <td><strong>${r.route_name}</strong></td>
            <td>
                <small class="text-muted">From:</small> ${r.start_stop_name}<br>
                <small class="text-muted">To:</small> ${r.end_stop_name}
            </td>
            <td>${r.total_distance_km} km (${r.estimated_duration_mins} min)</td>
            <td><strong>${formatCurrency(r.base_fare)}</strong></td>
            <td class="text-end">
                <button class="btn btn-sm btn-outline-info me-1" onclick="viewRouteHalts(${r.route_id})" title="View Halts">
                    <i class="fas fa-list-ol"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteRoute(${r.route_id}, '${r.route_number}')" title="Delete Route">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function openAddRouteModal() {
    document.getElementById('routeModalTitle').textContent = 'Create New Route';
    document.getElementById('routeId').value = '';
    document.getElementById('routeForm').reset();
    new bootstrap.Modal(document.getElementById('routeModal')).show();
}

async function viewRouteHalts(routeId) {
    try {
        const res = await apiRequest(`/routes/${routeId}`);
        const r = res.data;
        document.getElementById('haltsModalTitle').textContent = `Stops on ${r.route_number}: ${r.route_name}`;
        
        const listContainer = document.getElementById('haltsListContainer');
        if (r.halts && r.halts.length > 0) {
            listContainer.innerHTML = `
                <div class="list-group list-group-flush">
                    ${r.halts.map(h => `
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <span class="badge bg-secondary me-2">#${h.stop_sequence}</span>
                                <strong>${h.stop_name}</strong>
                                <small class="text-muted d-block ms-4">${h.landmark || ''}</small>
                            </div>
                            <div class="text-end">
                                <span class="badge bg-light text-dark border">${h.distance_from_source_km} km</span>
                                <span class="badge bg-success">${formatCurrency(h.fare_from_source)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            listContainer.innerHTML = '<div class="alert alert-info">No intermediate halts configured.</div>';
        }

        new bootstrap.Modal(document.getElementById('haltsModal')).show();
    } catch (e) {
        showToast(`Failed to load route stops: ${e.message}`, 'danger');
    }
}

async function handleSaveRoute(e) {
    e.preventDefault();
    const payload = {
        route_number: document.getElementById('routeNumber').value.trim(),
        route_name: document.getElementById('routeName').value.trim(),
        start_stop_id: parseInt(document.getElementById('startStopId').value, 10),
        end_stop_id: parseInt(document.getElementById('endStopId').value, 10),
        total_distance_km: parseFloat(document.getElementById('totalDistance').value),
        estimated_duration_mins: parseInt(document.getElementById('estimatedDuration').value, 10),
        base_fare: parseFloat(document.getElementById('baseFare').value)
    };

    try {
        const res = await apiRequest('/routes', 'POST', payload);
        if (res.success) {
            showToast('Route created successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('routeModal'))?.hide();
            await loadRoutes();
        }
    } catch (e) {
        showToast(e.message, 'danger');
    }
}

async function deleteRoute(routeId, routeNumber) {
    if (!confirm(`Delete route ${routeNumber}?`)) return;
    try {
        const res = await apiRequest(`/routes/${routeId}`, 'DELETE');
        if (res.success) {
            showToast(res.message, 'success');
            await loadRoutes();
        }
    } catch (e) {
        showToast(e.message, 'danger');
    }
}
