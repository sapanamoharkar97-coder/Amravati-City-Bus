/**
 * Amravati City Bus Management System
 * Fleet Management Controller
 */

let allBuses = [];

document.addEventListener('DOMContentLoaded', async () => {
    const user = requireAuth('admin');
    if (!user) return;

    await loadBuses();

    // Search and Filter Listeners
    document.getElementById('searchInput')?.addEventListener('input', applyFilters);
    document.getElementById('statusFilter')?.addEventListener('change', applyFilters);
    document.getElementById('typeFilter')?.addEventListener('change', applyFilters);

    // Save Bus Form Listener
    document.getElementById('busForm')?.addEventListener('submit', handleSaveBus);
});

async function loadBuses() {
    try {
        const response = await apiRequest('/buses');
        allBuses = response.data || [];
        renderBusesTable(allBuses);
    } catch (error) {
        showToast(`Failed to load buses: ${error.message}`, 'danger');
    }
}

function applyFilters() {
    const search = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const status = document.getElementById('statusFilter')?.value || '';
    const type = document.getElementById('typeFilter')?.value || '';

    const filtered = allBuses.filter(b => {
        const matchesSearch = b.bus_number.toLowerCase().includes(search) || 
                              b.registration_number.toLowerCase().includes(search);
        const matchesStatus = !status || b.status === status;
        const matchesType = !type || b.bus_type === type;
        return matchesSearch && matchesStatus && matchesType;
    });

    renderBusesTable(filtered);
}

function renderBusesTable(buses) {
    const tbody = document.getElementById('busesTableBody');
    if (!tbody) return;

    if (buses.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No buses found matching your criteria.</td></tr>`;
        return;
    }

    tbody.innerHTML = buses.map(b => {
        const statusBadge = b.status === 'active' 
            ? '<span class="badge badge-active">Active</span>'
            : b.status === 'maintenance' 
            ? '<span class="badge badge-maintenance">Maintenance</span>'
            : '<span class="badge badge-cancelled">Retired</span>';

        return `
            <tr>
                <td><strong>#${b.bus_id}</strong></td>
                <td><span class="fw-semibold text-primary">${b.bus_number}</span></td>
                <td><code>${b.registration_number}</code></td>
                <td><span class="badge bg-light text-dark border">${b.bus_type}</span></td>
                <td>${b.capacity} seats</td>
                <td>${statusBadge}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditBusModal(${b.bus_id})" title="Edit Bus">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteBus(${b.bus_id}, '${b.bus_number}')" title="Delete Bus">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function openAddBusModal() {
    document.getElementById('busModalTitle').textContent = 'Add New Bus';
    document.getElementById('busId').value = '';
    document.getElementById('busForm').reset();
    new bootstrap.Modal(document.getElementById('busModal')).show();
}

function openEditBusModal(busId) {
    const bus = allBuses.find(b => b.bus_id === busId);
    if (!bus) return;

    document.getElementById('busModalTitle').textContent = 'Edit Bus Details';
    document.getElementById('busId').value = bus.bus_id;
    document.getElementById('busNumber').value = bus.bus_number;
    document.getElementById('regNumber').value = bus.registration_number;
    document.getElementById('busType').value = bus.bus_type;
    document.getElementById('busCapacity').value = bus.capacity;
    document.getElementById('busStatus').value = bus.status;

    new bootstrap.Modal(document.getElementById('busModal')).show();
}

async function handleSaveBus(e) {
    e.preventDefault();
    const busId = document.getElementById('busId').value;
    const isEdit = Boolean(busId);

    const payload = {
        bus_number: document.getElementById('busNumber').value.trim(),
        registration_number: document.getElementById('regNumber').value.trim(),
        bus_type: document.getElementById('busType').value,
        capacity: parseInt(document.getElementById('busCapacity').value, 10),
        status: document.getElementById('busStatus').value
    };

    try {
        const endpoint = isEdit ? `/buses/${busId}` : '/buses';
        const method = isEdit ? 'PUT' : 'POST';
        const res = await apiRequest(endpoint, method, payload);

        if (res.success) {
            showToast(res.message || 'Bus saved successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('busModal'))?.hide();
            await loadBuses();
        }
    } catch (error) {
        showToast(error.message, 'danger');
    }
}

async function deleteBus(busId, busNumber) {
    if (!confirm(`Are you sure you want to delete bus ${busNumber}? This action cannot be undone.`)) {
        return;
    }

    try {
        const res = await apiRequest(`/buses/${busId}`, 'DELETE');
        if (res.success) {
            showToast(res.message, 'success');
            await loadBuses();
        }
    } catch (error) {
        showToast(error.message, 'danger');
    }
}
