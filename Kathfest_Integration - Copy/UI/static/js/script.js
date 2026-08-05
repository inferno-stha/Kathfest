/**
 * script.js - Global JavaScript for Smart Student Attendance System
 * 
 * This file now works with the fully integrated Flask backend.
 * Each function communicates with the backend API endpoints defined
 * in routes.py.
 * 
 * How the frontend communicates with the backend:
 *   - All data exchange uses the Fetch API (AJAX)
 *   - Requests are sent as JSON (Content-Type: application/json)
 *   - Responses are received as JSON
 *   - Errors are caught and displayed to the user
 */

/* ============================================================
   TOAST NOTIFICATIONS (v2)
   ============================================================ */

/**
 * showNotification() - Display a temporary toast notification.
 * Types: 'success' | 'error' | 'info' | 'warning'
 */
function showNotification(message, type) {
    const container = document.getElementById('notification-container');
    if (!container) {
        alert(message);
        return;
    }
    const div = document.createElement('div');
    div.className = `toast toast-${type || 'info'}`;
    div.textContent = message;
    container.appendChild(div);
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (div.parentNode) div.remove();
    }, 5000);
}

/**
 * toastSuccess / toastError - Convenience wrappers.
 */
function toastSuccess(message) { showNotification(message, 'success'); }
function toastError(message)   { showNotification(message, 'error'); }
function toastInfo(message)    { showNotification(message, 'info'); }
function toastWarning(message) { showNotification(message, 'warning'); }

/**
 * handleApiError() - Centralized error handler for fetch() calls.
 * Logs the error and displays a user-friendly toast.
 */
function handleApiError(error) {
    console.error('API Error:', error);
    showNotification(error.message || 'An error occurred. Please try again.', 'error');
}

/**
 * handleApiResponse() - Checks if a fetch response is OK and parses JSON.
 * Shows error notification if the request failed.
 */
async function handleApiResponse(response) {
    if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `HTTP ${response.status}`);
    }
    return response.json();
}

/**
 * formatTime12hr() - Convert 24-hour time to 12-hour display format.
 */
function formatTime12hr(timeStr) {
    if (!timeStr || timeStr === '--') return '--';
    const parts = timeStr.split(':');
    if (parts.length < 2) return timeStr;
    let h = parseInt(parts[0], 10);
    const m = parts[1];
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12 || 12;
    return `${h}:${m} ${ampm}`;
}

/* ============================================================
   VALIDATION HELPERS (v2)
   Mirrors backend/validation.py so frontend & backend agree.
   ============================================================ */

/**
 * isValidName() - Alphabets, spaces, hyphen, apostrophe only.
 */
function isValidName(name) {
    return /^[A-Za-zÀ-ÿ' -]{2,60}$/.test((name || '').trim());
}

/**
 * isValidRollNumber() - Positive integer or college format (BCT001).
 */
function isValidRollNumber(roll) {
    return /^(?:\d+|[A-Z]{2,6}\d{3,}|[A-Z]{2,6}\d+[A-Z]{2,6}\d+)$/.test((roll || '').trim());
}

/**
 * isValidDepartment() - Letters, spaces, hyphen, ampersand, period.
 */
function isValidDepartment(dept) {
    return /^[A-Za-zÀ-ÿ &.'-]{2,60}$/.test((dept || '').trim());
}

/* ============================================================
   SHOW/HIDE LOADING SPINNER (v2)
   ============================================================ */

function showSpinner(containerId, show) {
    const container = document.getElementById(containerId);
    if (!container) return;
    let spinner = container.querySelector('.spinner-overlay');
    if (show && !spinner) {
        spinner = document.createElement('div');
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = '<div class="spinner"></div>';
        container.appendChild(spinner);
    } else if (!show && spinner) {
        spinner.remove();
    }
}
