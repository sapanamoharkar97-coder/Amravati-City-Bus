/**
 * Amravati City Bus Management System
 * Reports & Analytics Controller with Chart.js
 */

let revenueChartInstance = null;
let popularRoutesChartInstance = null;
let occupancyChartInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
    const user = requireAuth('admin');
    if (!user) return;

    await loadAllReports();

    document.getElementById('btnExportRoutesCSV')?.addEventListener('click', () => {
        window.location.href = '/api/reports/export-csv?type=routes';
    });

    document.getElementById('btnExportRevenueCSV')?.addEventListener('click', () => {
        window.location.href = '/api/reports/export-csv?type=revenue';
    });

    document.getElementById('btnExportOccupancyCSV')?.addEventListener('click', () => {
        window.location.href = '/api/reports/export-csv?type=occupancy';
    });
});

async function loadAllReports() {
    try {
        await Promise.all([
            loadRevenueReport(),
            loadPopularRoutesReport(),
            loadOccupancyReport()
        ]);
    } catch (e) {
        showToast(`Failed loading analytics: ${e.message}`, 'danger');
    }
}

async function loadRevenueReport() {
    const res = await apiRequest('/reports/revenue');
    const data = res.data || {};
    const byMethod = data.by_method || [];

    const ctx = document.getElementById('revenueChart')?.getContext('2d');
    if (!ctx) return;

    if (revenueChartInstance) revenueChartInstance.destroy();

    const labels = byMethod.map(m => m.payment_method.replace('DEMO_', ''));
    const values = byMethod.map(m => parseFloat(m.total_revenue));

    revenueChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.length > 0 ? labels : ['No Data'],
            datasets: [{
                data: values.length > 0 ? values : [1],
                backgroundColor: ['#0d9488', '#38bdf8', '#f59e0b', '#6366f1'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

async function loadPopularRoutesReport() {
    const res = await apiRequest('/reports/popular-routes');
    const routes = res.data || [];

    const ctx = document.getElementById('popularRoutesChart')?.getContext('2d');
    if (!ctx) return;

    if (popularRoutesChartInstance) popularRoutesChartInstance.destroy();

    const labels = routes.map(r => r.route_number);
    const bookings = routes.map(r => r.total_bookings);
    const revenue = routes.map(r => parseFloat(r.total_revenue));

    popularRoutesChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Confirmed Bookings',
                    data: bookings,
                    backgroundColor: '#1a365d',
                    borderRadius: 6
                },
                {
                    label: 'Revenue (₹)',
                    data: revenue,
                    backgroundColor: '#0d9488',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Populate Popular Routes Table
    const tbody = document.getElementById('popularRoutesTableBody');
    if (tbody) {
        tbody.innerHTML = routes.map(r => `
            <tr>
                <td><strong>${r.route_number}</strong></td>
                <td>${r.route_name}</td>
                <td><span class="badge bg-secondary">${r.total_bookings}</span></td>
                <td>${r.total_passengers}</td>
                <td><strong>${formatCurrency(r.total_revenue)}</strong></td>
            </tr>
        `).join('');
    }
}

async function loadOccupancyReport() {
    const res = await apiRequest('/reports/bus-occupancy');
    const list = res.data || [];

    const ctx = document.getElementById('occupancyChart')?.getContext('2d');
    if (!ctx) return;

    if (occupancyChartInstance) occupancyChartInstance.destroy();

    const labels = list.map(s => `${s.route_number} (${formatTime(s.departure_time)})`);
    const rates = list.map(s => parseFloat(s.occupancy_percentage || 0));

    occupancyChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Occupancy %',
                data: rates,
                backgroundColor: rates.map(r => r > 70 ? '#10b981' : r > 30 ? '#38bdf8' : '#f59e0b'),
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 100 }
            }
        }
    });

    // Populate Occupancy Table
    const tbody = document.getElementById('occupancyTableBody');
    if (tbody) {
        tbody.innerHTML = list.map(o => `
            <tr>
                <td>#${o.schedule_id}</td>
                <td><strong>${o.route_number}</strong> (${o.route_name})</td>
                <td>${o.bus_number} (${o.bus_type})</td>
                <td>${o.booked_seats} / ${o.total_capacity}</td>
                <td>
                    <div class="progress" style="height: 18px;">
                        <div class="progress-bar ${o.occupancy_percentage > 70 ? 'bg-success' : 'bg-info'}" 
                             role="progressbar" style="width: ${o.occupancy_percentage}%;">
                            ${o.occupancy_percentage}%
                        </div>
                    </div>
                </td>
            </tr>
        `).join('');
    }
}
