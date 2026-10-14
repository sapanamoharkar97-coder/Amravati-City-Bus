/**
 * Amravati City Bus Management System
 * Authentication & Session Controller
 */

function getStoredUser() {
    try {
        const u = localStorage.getItem('amravati_bus_user');
        return u ? JSON.parse(u) : null;
    } catch {
        return null;
    }
}

function setStoredUser(user, token) {
    if (user) localStorage.setItem('amravati_bus_user', JSON.stringify(user));
    if (token) localStorage.setItem('amravati_bus_token', token);
}

function clearSession() {
    localStorage.removeItem('amravati_bus_user');
    localStorage.removeItem('amravati_bus_token');
}

/**
 * Validates user authentication status and enforces role authorization.
 */
function requireAuth(allowedRole = null) {
    const user = getStoredUser();
    const token = localStorage.getItem('amravati_bus_token');

    if (!user || !token) {
        window.location.href = 'login.html';
        return null;
    }

    if (allowedRole && user.role !== allowedRole) {
        if (user.role === 'admin') {
            window.location.href = 'dashboard.html';
        } else {
            window.location.href = 'passenger_dashboard.html';
        }
        return null;
    }

    // Populate header details if elements exist
    updateHeaderUserUI(user);
    return user;
}

function updateHeaderUserUI(user) {
    const nameEl = document.getElementById('headerUserName');
    const roleEl = document.getElementById('headerUserRole');
    const avatarEl = document.getElementById('headerUserAvatar');

    if (nameEl && user.full_name) nameEl.textContent = user.full_name;
    if (roleEl && user.role) roleEl.textContent = user.role.toUpperCase();
    if (avatarEl && user.full_name) {
        const initials = user.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        avatarEl.textContent = initials;
    }
}

async function handleLogout() {
    try {
        await apiRequest('/auth/logout', 'POST');
    } catch (e) {
        console.warn('Logout API notification error:', e);
    } finally {
        clearSession();
        showToast('Logged out successfully.', 'info');
        setTimeout(() => window.location.href = 'login.html', 800);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Bind all logout buttons on page
    document.querySelectorAll('.btn-logout').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    });
});
