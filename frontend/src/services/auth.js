class AuthService {
    constructor() {
        this.baseURL = 'http://localhost:8000/api';
        this.token = localStorage.getItem('token');
    }

    async login(username, password) {
        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${this.baseURL}/auth/token`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();
            this.token = data.access_token;
            localStorage.setItem('token', this.token);

            return data;
        } catch (error) {
            throw error;
        }
    }

    async getCurrentUser() {
        if (!this.token) {
            throw new Error('No token available');
        }

        try {
            const response = await fetch(`${this.baseURL}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to get user info');
            }

            return await response.json();
        } catch (error) {
            this.logout();
            throw error;
        }
    }

    logout() {
        this.token = null;
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    }

    isAuthenticated() {
        return !!this.token;
    }

    getAuthHeaders() {
        if (!this.token) {
            throw new Error('No authentication token');
        }
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    async makeAuthenticatedRequest(url, options = {}) {
        if (!this.token) {
            throw new Error('Not authenticated');
        }

        const headers = {
            ...this.getAuthHeaders(),
            ...options.headers
        };

        try {
            const response = await fetch(`${this.baseURL}${url}`, {
                ...options,
                headers
            });

            if (response.status === 401) {
                this.logout();
                throw new Error('Session expired');
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Request failed');
            }

            return await response.json();
        } catch (error) {
            throw error;
        }
    }
}

const authService = new AuthService();