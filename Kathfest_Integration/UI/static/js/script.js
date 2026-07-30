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

/**
 * showNotification() - Display a temporary notification to the user.
 * Used by all pages for success/error feedback.
 */
function showNotification(message, type) {
    const container = document.getElementById('notification-container');
    if (!container) {
        alert(message);
        return;
    }
    const div = document.createElement('div');
    div.className = `notification notification-${type}`;
    div.textContent = message;
    container.appendChild(div);
    setTimeout(() => div.remove(), 5000);
}

/**
 * handleApiError() - Centralized error handler for fetch() calls.
 * Logs the error and displays a user-friendly message.
 */
function handleApiError(error) {
    console.error('API Error:', error);
    showNotification('An error occurred. Please try again.', 'error');
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
