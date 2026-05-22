// API Configuration
const API_BASE = '';  // Relative URLs — works on any deployment

// Authentication API
class AuthAPI {
    static async register(userData) {
        const response = await fetch(`${API_BASE}/api/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        return await response.json();
    }

    static async login(credentials) {
        const response = await fetch(`${API_BASE}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(credentials)
        });
        return await response.json();
    }

    static async logout() {
        const response = await fetch(`${API_BASE}/api/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        return await response.json();
    }

    static async checkAuth() {
        const response = await fetch(`${API_BASE}/api/check-auth`, {
            credentials: 'include'
        });
        return await response.json();
    }
}

// Bookings API
class BookingAPI {
    static async create(bookingData) {
        const response = await fetch(`${API_BASE}/api/bookings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(bookingData)
        });
        return await response.json();
    }

    static async getAll() {
        const response = await fetch(`${API_BASE}/api/bookings`);
        return await response.json();
    }
}

// Customization API
class CustomizationAPI {
    static async create(customizationData) {
        const response = await fetch(`${API_BASE}/api/customizations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(customizationData)
        });
        return await response.json();
    }

    static async getAll() {
        const response = await fetch(`${API_BASE}/api/customizations`);
        return await response.json();
    }
}

// Reviews API
class ReviewAPI {
    static async create(reviewData) {
        const response = await fetch(`${API_BASE}/api/reviews`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(reviewData)
        });
        return await response.json();
    }

    static async getAll() {
        const response = await fetch(`${API_BASE}/api/reviews`);
        return await response.json();
    }
}