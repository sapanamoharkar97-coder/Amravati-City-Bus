/**
 * Amravati City Bus Management System
 * Bus Stops Management Controller
 */

let allStops = [];

document.addEventListener('DOMContentLoaded', async () => {
    const user = requireAuth('admin');
    if (!user) return;

    await loadStops();

    document.getElementById('searchInput')?.addEventListener('input', applySearch);
    document.getElementById('stopForm')?.addEventListener('submit', handleSaveStop);
});

async function loadStops() {
    try {
        const response = await apiRequest('/stops');
        allStops = response.data || [];
        renderStopsTable(allStops);
    } catch (error) {
        showToast(`Failed to load stops: ${error.message}`, 'danger');
    }
}

function applySearch() {
    const query = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const filtered = allStops.filter(s => 
        s.stop_name.toLowerCase().includes(query) || 
        (s.landmark && s.landmark.toLowerCase().includes(query))
    );
    renderStopsTable(filtered);
}

function renderStopsTable(stops) {
    const tbody = document.getElementById('stopsTableBody');
    if (!tbody) return;

    if (stops.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No stops found.</td></tr>`;
        return;
    }

    tbody.innerHTML = stops.map(s => `
        <tr>
            <td><strong>#${s.stop_id}</strong></td>
            <td><span class="fw-semibold text-primary">${s.stop_name}</span></td>
            <td>${s.landmark || '-'}</td>
            <td><code>${s.latitude || '20.93'}, ${s.longitude || '77.75'}</code></td>
            <td><span class="badge ${s.is_active ? 'badge-active' : 'badge-cancelled'}">${s.is_active ? 'Active' : 'Inactive'}</span></td>
            <td class="text-end">
                <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditStopModal(${s.stop_id})" title="Edit Stop">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteStop(${s.stop_id}, '${s.stop_name}')" title="Delete Stop">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function openAddStopModal() {
    document.getElementById('stopModalTitle').textContent = 'Add Bus Stop';
    document.getElementById('stopId').value = '';
    document.getElementById('stopForm').reset();
    new bootstrap.Modal(document.getElementById('stopModal')).show();
}

function openEditStopModal(stopId) {
    const stop = allStops.find(s => s.stop_id === stopId);
    if (!stop) return;

    document.getElementById('stopModalTitle').textContent = 'Edit Bus Stop';
    document.getElementById('stopId').value = stop.stop_id;
    document.getElementById('stopName').value = stop.stop_name;
    document.getElementById('landmark').value = stop.landmark || '';
    document.getElementById('latitude').value = stop.latitude || '';
    document.getElementById('longitude').value = stop.longitude || '';

    new bootstrap.Modal(document.getElementById('stopModal')).show();
}

async function handleSaveStop(e) {
    e.preventDefault();
    const stopId = document.getElementById('stopId').value;
    const isEdit = Boolean(stopId);

    const payload = {
        stop_name: document.getElementById('stopName').value.trim(),
        landmark: document.getElementById('landmark').value.trim(),
        latitude: parseFloat(document.getElementById('latitude').value) || null,
        longitude: parseFloat(document.getElementById('longitude').value) || null,
        city: 'Amravati'
    };

    try {
        const endpoint = isEdit ? `/stops/${stopId}` : '/stops';
        const method = isEdit ? 'PUT' : 'POST';
        const res = await apiRequest(endpoint, method, payload);

        if (res.success) {
            showToast(res.message || 'Stop saved successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('stopModal'))?.hide();
            await loadStops();
        }
    } catch (error) {
        showToast(error.message, 'danger');
    }
}

async function deleteStop(stopId, stopName) {
    if (!confirm(`Delete bus stop "${stopName}"?`)) return;

    try {
        const res = await apiRequest(`/stops/${stopId}`, 'DELETE');
        if (res.success) {
            showToast(res.message, 'success');
            await loadStops();
        }
    } catch (error) {
        showToast(error.message, 'danger');
    }
}
